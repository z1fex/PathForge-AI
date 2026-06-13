"""
Agent 3 — Recommended Courses + YouTube.

Public functions (imported by Agent 1, signatures fixed by API_CONTRACT.md):
    get_courses(job_title: str, skills: list[str]) -> list[dict]   # recommended_courses[]
    get_youtube(job_title: str, skills: list[str]) -> list[dict]   # youtube[]

Rules followed:
- Free-first; never invent links (only URLs that come back from a real search).
- Every external call has a timeout (<= 8s) and try/except; degrades to [] on failure.
  This module must NEVER raise — Agent 1 must not 500 because of us.
- Tavily is called via REST directly (the MCP server 401s on a stale boot key — see lessons.md).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests

# --- Load env (safe no-op if Agent 1 already loaded it) ---------------------
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
# Gemini cleanup is opt-in: off by default to keep this path fast, deterministic,
# and to not burn the shared free-tier quota on every roadmap call.
USE_GEMINI_CURATION = os.getenv("LEARNING_USE_GEMINI", "0").strip() == "1"

TAVILY_URL = "https://api.tavily.com/search"
TIMEOUT = 8  # seconds, per the brief

# domain -> (provider label, is_free). Anything not listed defaults to (derived, False).
_DOMAIN_MAP = {
    "freecodecamp.org": ("freeCodeCamp", True),
    "youtube.com": ("YouTube", True),
    "youtu.be": ("YouTube", True),
    "kaggle.com": ("Kaggle", True),
    "edx.org": ("edX", True),            # audit track is free
    "khanacademy.org": ("Khan Academy", True),
    "developer.mozilla.org": ("MDN", True),
    "docs.python.org": ("Python Docs", True),
    "w3schools.com": ("W3Schools", True),
    "scrimba.com": ("Scrimba", True),
    "coursera.org": ("Coursera", False),   # certs are paid; default to paid
    "udemy.com": ("Udemy", False),
    "udacity.com": ("Udacity", False),
    "datacamp.com": ("DataCamp", False),
    "pluralsight.com": ("Pluralsight", False),
    "codecademy.com": ("Codecademy", False),
}

_COURSE_DOMAINS = [
    "freecodecamp.org", "coursera.org", "udemy.com",
    "edx.org", "youtube.com", "kaggle.com",
]
_YT_DOMAINS = ["youtube.com"]


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #
def _tavily_search(query: str, include_domains: list[str] | None = None,
                   max_results: int = 5) -> list[dict]:
    """One Tavily REST search. Returns [] on any failure (never raises)."""
    if not TAVILY_API_KEY:
        return []
    body = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
    }
    if include_domains:
        body["include_domains"] = include_domains
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    try:
        resp = requests.post(TAVILY_URL, json=body, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results") or []
        return [r for r in results if isinstance(r, dict) and r.get("url")]
    except Exception:
        return []


def _domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def _provider_and_free(url: str) -> tuple[str, bool]:
    host = _domain(url)
    for dom, (prov, free) in _DOMAIN_MAP.items():
        if host == dom or host.endswith("." + dom):
            return prov, free
    root = host.split(".")[0] if host else "Web"
    return (root.capitalize() or "Web"), False


def _norm_url(url: str) -> str:
    """Normalise for dedupe: lowercase host, drop fragment + trailing slash."""
    try:
        p = urlparse(url)
        host = p.netloc.lower()
        path = p.path.rstrip("/")
        norm = f"{p.scheme.lower()}://{host}{path}"
        if p.query:
            norm += f"?{p.query}"
        return norm or url
    except Exception:
        return url


def _clean_title(title: str) -> str:
    if not title:
        return ""
    t = re.sub(r"\s+", " ", title).strip()
    # strip a trailing site tag like " - YouTube" / " | freeCodeCamp.org"
    t = re.sub(r"\s*[-|]\s*(YouTube|freeCodeCamp(\.org)?|Coursera|edX|Udemy|Kaggle)\s*$",
               "", t, flags=re.IGNORECASE).strip()
    return t


def _top_skills(job_title: str, skills: list[str], n: int = 3) -> list[str]:
    clean = [s.strip() for s in (skills or []) if isinstance(s, str) and s.strip()]
    return clean[:n] if clean else [job_title]


# --------------------------------------------------------------------------- #
# get_courses
# --------------------------------------------------------------------------- #
def get_courses(job_title: str, skills: list[str]) -> list[dict]:
    """Free-first courses for a job title + its skills. -> recommended_courses[].

    Shape per item: {title, provider, url, free}. Caps at 6, dedupes by URL,
    free resources first. Returns [] on total failure.
    """
    try:
        queries = [f"best free course to learn {job_title}"]
        queries += [f"best free course to learn {s}" for s in _top_skills(job_title, skills)]

        seen: set[str] = set()
        raw: list[dict] = []
        for q in queries:
            for r in _tavily_search(q, include_domains=_COURSE_DOMAINS, max_results=5):
                url = r.get("url", "")
                key = _norm_url(url)
                if not key or key in seen:
                    continue
                seen.add(key)
                provider, free = _provider_and_free(url)
                title = _clean_title(r.get("title", "")) or f"{provider} course"
                raw.append({
                    "title": title,
                    "provider": provider,
                    "url": url,
                    "free": free,
                })

        if not raw:
            return []

        # optional Gemini pass to clean/label (off by default)
        if USE_GEMINI_CURATION:
            curated = _curate_with_gemini(job_title, skills, raw, kind="recommended_courses")
            if curated:
                raw = curated

        # free first, stable otherwise; cap at 6
        raw.sort(key=lambda c: 0 if c.get("free") else 1)
        return raw[:6]
    except Exception:
        return []


# --------------------------------------------------------------------------- #
# get_youtube
# --------------------------------------------------------------------------- #
def _youtube_channel(url: str, title: str) -> str:
    """Best-effort channel name from a YouTube URL, else fall back to the title."""
    try:
        p = urlparse(url)
        path = p.path
        m = re.match(r"/@([^/]+)", path)
        if m:
            return m.group(1)
        m = re.match(r"/(?:c|user)/([^/]+)", path)
        if m:
            return m.group(1)
        # /channel/UCxxxx has no human name; fall through to title
    except Exception:
        pass
    # derive from title: text before a separator is usually the channel/topic
    t = _clean_title(title)
    if t:
        return re.split(r"\s*[-|:]\s*", t)[0][:60] or "YouTube"
    return "YouTube"


_JUNK_SNIPPETS = ("isn't available", "content isn't available", "video unavailable",
                  "sign in to confirm", "this video is private")


def _why_from_snippet(snippet: str, skill: str) -> str:
    if snippet:
        s = re.sub(r"\s+", " ", snippet).strip()
        if not any(j in s.lower() for j in _JUNK_SNIPPETS):
            first = re.split(r"(?<=[.!?])\s", s)[0]
            if 10 <= len(first) <= 160:
                return first
            if s:
                return s[:140].rstrip() + ("…" if len(s) > 140 else "")
    return f"Highly recommended for learning {skill}."


def get_youtube(job_title: str, skills: list[str]) -> list[dict]:
    """YouTube channels/playlists for the skills. -> youtube[].

    Shape per item: {channel, title, url, why}. Caps at 5, dedupes by URL.
    Returns [] on total failure.
    """
    try:
        skill_list = _top_skills(job_title, skills)
        seen: set[str] = set()
        out: list[dict] = []
        for skill in skill_list:
            for r in _tavily_search(
                f"best YouTube channel to learn {skill}",
                include_domains=_YT_DOMAINS, max_results=5,
            ):
                url = r.get("url", "")
                key = _norm_url(url)
                if not key or key in seen:
                    continue
                seen.add(key)
                title = _clean_title(r.get("title", "")) or f"{skill} tutorials"
                out.append({
                    "channel": _youtube_channel(url, r.get("title", "")),
                    "title": title,
                    "url": url,
                    "why": _why_from_snippet(r.get("content", ""), skill),
                })

        if not out:
            return []

        if USE_GEMINI_CURATION:
            curated = _curate_with_gemini(job_title, skills, out, kind="youtube")
            if curated:
                out = curated

        # Shorts are rarely "channels to learn from" — push them after real
        # channels/playlists (stable, so we don't lose count).
        out.sort(key=lambda y: 1 if "/shorts/" in y.get("url", "") else 0)
        return out[:5]
    except Exception:
        return []


# --------------------------------------------------------------------------- #
# Optional Gemini cleanup (opt-in via LEARNING_USE_GEMINI=1)
# --------------------------------------------------------------------------- #
def _curate_with_gemini(job_title: str, skills: list[str],
                        items: list[dict], kind: str) -> list[dict]:
    """Best-effort: clean/label results using the courses_youtube_curation prompt.
    Returns [] (caller keeps the heuristic list) on any failure. Never raises.
    Only keeps items whose URL was already in the input — never invents links.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    if not api_key or not items:
        return []
    try:
        prompt_path = (Path(__file__).resolve().parents[2]
                       / "prompts" / "courses_youtube_curation.md")
        template = prompt_path.read_text(encoding="utf-8")
        raw_block = "\n".join(
            f"- {i.get('title','')} | {i.get('url','')}" for i in items
        )
        prompt = (template
                  .replace("{{job_title}}", job_title)
                  .replace("{{skills}}", ", ".join(skills or []))
                  .replace("{{raw_results}}", raw_block))

        endpoint = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model}:generateContent")
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"},
        }
        resp = requests.post(endpoint, params={"key": api_key},
                             json=body, timeout=TIMEOUT)
        resp.raise_for_status()
        text = (resp.json()["candidates"][0]["content"]["parts"][0]["text"])
        import json
        parsed = json.loads(text)
        curated = parsed.get(kind) or []

        # guard: only keep URLs that were in our real results (never invent links)
        allowed = {_norm_url(i["url"]) for i in items}
        kept = [c for c in curated
                if isinstance(c, dict) and _norm_url(c.get("url", "")) in allowed]
        return kept if kept else []
    except Exception:
        return []


# --------------------------------------------------------------------------- #
# "Prove it" — run this file directly for sample output
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import json
    import sys

    # Real result titles can contain emoji (e.g. "Learn Python 🐍"); the Windows
    # console defaults to cp1252 and would crash on print. Force UTF-8 stdout.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    samples = [
        ("Data Scientist", ["Python", "Statistics", "Machine Learning"]),
        ("Frontend Developer", ["JavaScript", "React", "CSS"]),
    ]
    for jt, sk in samples:
        print("=" * 70)
        print(f"JOB: {jt}   SKILLS: {sk}")
        courses = get_courses(jt, sk)
        yt = get_youtube(jt, sk)
        print(f"\n  recommended_courses ({len(courses)}):")
        print(json.dumps(courses, indent=2, ensure_ascii=False))
        print(f"\n  youtube ({len(yt)}):")
        print(json.dumps(yt, indent=2, ensure_ascii=False))
        print()
