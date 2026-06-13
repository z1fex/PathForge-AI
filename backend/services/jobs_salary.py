"""Agent 2 — Companies hiring + grounded salary data.

Public API (imported & assembled by Agent 1, signatures fixed by API_CONTRACT.md):

    get_companies_hiring(job_title) -> list[dict]            # companies_hiring[]
    get_salary_overview(job_title)  -> dict                  # salary_overview{}
    get_milestone_salaries(job_title, milestones) -> list[dict]   # per-milestone expected_salary

Framework rules honored here:
  * Every external call has a timeout (<=8s) and a try/except.
  * On ANY failure we degrade to [] / {} — this module NEVER raises to Agent 1.
  * Self-contained: loads keys from app/.env and the prompt from /prompts via __file__
    paths, so it works standalone (the contract's verification command) regardless of cwd.
  * Gemini is called over plain REST (per app/tasks/lessons.md) — no SDK dependency,
    auth via ?key= query param, model read from GEMINI_MODEL env (2.5, never 2.0).
"""

from __future__ import annotations

import os
import re
import json
import logging
from pathlib import Path

import requests

log = logging.getLogger("jobs_salary")

# Public API imported & assembled by Agent 1 (keeps `import *` clean).
__all__ = ["get_companies_hiring", "get_salary_overview", "get_milestone_salaries"]

# --------------------------------------------------------------------------- #
# Config / endpoints
# --------------------------------------------------------------------------- #
HTTP_TIMEOUT = 8  # seconds — brief mandates <=8s on every external call
GEMINI_TIMEOUT = 7  # tighter: salary synthesis runs inside Agent 1's 12s wrapper
MAX_COMPANIES = 8

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"
TAVILY_URL = "https://api.tavily.com/search"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

_HEADERS = {"User-Agent": "CareerPath/1.0 (+hackathon)", "Accept": "application/json"}

_HERE = Path(__file__).resolve()
_APP_DIR = _HERE.parents[1]          # .../VibeTHON PW/app
_ROOT_DIR = _HERE.parents[2]         # .../VibeTHON PW
_ENV_PATH = _APP_DIR / ".env"
_PROMPTS_DIR = _ROOT_DIR / "prompts"

_STOPWORDS = {"a", "an", "the", "of", "and", "or", "for", "to", "in", "at",
              "senior", "junior", "lead", "staff", "i", "ii", "iii"}

# Used when live salary data is unavailable so the visual still renders.
DEFAULT_OVERVIEW = {
    "entry": {"min": 45000, "max": 70000},
    "mid": {"min": 80000, "max": 115000},
    "senior": {"min": 125000, "max": 175000},
    "currency": "USD",
}

# Cache overview per job title so get_milestone_salaries doesn't re-hit the web
# when Agent 1 calls both functions for the same role.
_salary_cache: dict[str, dict] = {}
_env_loaded = False


# --------------------------------------------------------------------------- #
# Tiny self-contained helpers (no extra deps)
# --------------------------------------------------------------------------- #
def _load_env() -> None:
    """Populate os.environ from app/.env for any key not already set (read once).

    Existing OS env vars win over the file; all other keys (incl. GEMINI_MODEL)
    are loaded. Lets the module work in the standalone verification command
    without the SDK or python-dotenv.
    """
    global _env_loaded
    if _env_loaded:
        return
    try:
        if _ENV_PATH.exists():
            for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
        _env_loaded = True
    except Exception as exc:  # pragma: no cover - defensive
        log.warning("could not load .env: %s", exc)


def _load_prompt(name: str) -> str:
    """Read a prompt markdown from /prompts and return the body after the
    metadata block (everything past the first '---' separator). Falls back to
    the whole file if no separator is present."""
    try:
        text = (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
        parts = re.split(r"\n-{3,}\n", text, maxsplit=1)
        return parts[1].strip() if len(parts) == 2 else text.strip()
    except Exception as exc:
        log.warning("could not load prompt %s: %s", name, exc)
        return ""


def _tokens(job_title: str) -> list[str]:
    raw = re.split(r"[^a-zA-Z0-9+#]+", (job_title or "").lower())
    # keep len>=2 so role abbreviations (ux, ui, qa, hr, pm) survive
    return [t for t in raw if len(t) >= 2 and t not in _STOPWORDS]


def _round_k(n: float) -> int:
    """Round to the nearest 1000 (clean salary figures)."""
    try:
        return int(round(float(n) / 1000.0) * 1000)
    except Exception:
        return 0


# --------------------------------------------------------------------------- #
# Shared external-call wrappers (timeout + try/except, return safe defaults)
# --------------------------------------------------------------------------- #
def _get_json(url: str, params: dict | None = None) -> dict | list | None:
    try:
        r = requests.get(url, params=params, headers=_HEADERS, timeout=HTTP_TIMEOUT)
        if r.status_code != 200:
            log.warning("GET %s -> %s", url, r.status_code)
            return None
        return r.json()
    except Exception as exc:
        log.warning("GET %s failed: %s", url, exc)
        return None


def _tavily_search(query: str, max_results: int = 6,
                   search_depth: str = "advanced",
                   include_domains: list[str] | None = None) -> list[dict]:
    """Return Tavily result dicts ({title,url,content}); [] on any failure."""
    _load_env()
    key = os.environ.get("TAVILY_API_KEY", "")
    if not key:
        return []
    body = {"query": query, "max_results": max_results, "search_depth": search_depth,
            "api_key": key}
    if include_domains:
        body["include_domains"] = include_domains
    try:
        r = requests.post(TAVILY_URL, json=body,
                          headers={"Authorization": f"Bearer {key}",
                                   "Content-Type": "application/json"},
                          timeout=HTTP_TIMEOUT)
        if r.status_code != 200:
            log.warning("Tavily -> %s: %s", r.status_code, r.text[:200])
            return []
        return r.json().get("results", []) or []
    except Exception as exc:
        log.warning("Tavily search failed: %s", exc)
        return []


def _gemini_json(prompt_text: str, fast_first: bool = False) -> dict | None:
    """Call Gemini in JSON mode over REST; return parsed dict or None.

    Auth via ?key= (NOT Bearer). Tries GEMINI_MODEL then GEMINI_MODEL_FALLBACK
    on a 429/5xx/timeout. `fast_first` reverses the order to try the lighter
    fallback (e.g. -lite) first — used by the salary path, which must finish
    inside Agent 1's 12s wrapper (full `flash` consistently exceeds the read
    timeout here; `-lite` answers in ~4s). Never raises.
    """
    _load_env()
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key or not prompt_text:
        return None

    models = [m for m in (os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                          os.environ.get("GEMINI_MODEL_FALLBACK", "gemini-2.5-flash-lite"))
              if m]
    if fast_first:
        models = list(reversed(models))
    body = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    for model in models:
        url = f"{GEMINI_BASE}/{model}:generateContent?key={key}"
        try:
            r = requests.post(url, json=body,
                              headers={"Content-Type": "application/json"},
                              timeout=GEMINI_TIMEOUT)
            if r.status_code != 200:
                log.warning("Gemini %s -> %s: %s", model, r.status_code, r.text[:200])
                continue
            text = (r.json().get("candidates", [{}])[0]
                    .get("content", {}).get("parts", [{}])[0].get("text", ""))
            if not text:
                continue
            return json.loads(text)
        except Exception as exc:
            log.warning("Gemini %s failed: %s", model, exc)
            continue
    return None


# --------------------------------------------------------------------------- #
# 1) Companies hiring
# --------------------------------------------------------------------------- #
def _score(role: str, toks: list[str]) -> int:
    """How many job-title tokens appear in this role title (0 = irrelevant).
    Short tokens (<=2 chars like 'ux') must match as whole words to avoid
    false hits inside longer words."""
    rl = role.lower()
    s = 0
    for t in toks:
        if len(t) <= 2:
            if re.search(rf"\b{re.escape(t)}\b", rl):
                s += 1
        elif t in rl:
            s += 1
    return s


def _from_remotive(job_title: str, toks: list[str]) -> list[tuple[int, dict]]:
    # NOTE: Remotive's `search` param is unreliable (returns the generic recent
    # feed regardless of query) — so we fetch and filter by token relevance here.
    data = _get_json(REMOTIVE_URL, params={"search": job_title, "limit": 50})
    if not isinstance(data, dict):
        return []
    scored = []
    for j in data.get("jobs", []) or []:
        name = (j.get("company_name") or "").strip()
        role = (j.get("title") or "").strip()
        url = (j.get("url") or "").strip()
        if not (name and role and url):
            continue
        score = _score(role, toks)
        if score == 0:
            continue
        scored.append((score, {
            "name": name,
            "role": role,
            "location": (j.get("candidate_required_location") or "Remote").strip() or "Remote",
            "url": url,
            "source": "remotive",
        }))
    return scored


def _from_arbeitnow(job_title: str, toks: list[str]) -> list[tuple[int, dict]]:
    data = _get_json(ARBEITNOW_URL)
    if not isinstance(data, dict):
        return []
    scored = []
    for j in data.get("data", []) or []:
        name = (j.get("company_name") or "").strip()
        role = (j.get("title") or "").strip()
        url = (j.get("url") or "").strip()
        if not (name and role and url):
            continue
        score = _score(role, toks)
        if score == 0:
            continue
        loc = j.get("location")
        if isinstance(loc, list):
            loc = ", ".join(loc)
        scored.append((score, {
            "name": name,
            "role": role,
            "location": (loc or "See listing").strip() or "See listing",
            "url": url,
            "source": "arbeitnow",
        }))
    return scored


_SKIP_DOMAINS = ("reddit.com", "youtube.com", "quora.com", "medium.com",
                 "facebook.com", "twitter.com", "x.com")
_BOARD_LABELS = {
    "linkedin.com": "LinkedIn", "indeed.com": "Indeed", "glassdoor.com": "Glassdoor",
    "wellfound.com": "Wellfound", "ziprecruiter.com": "ZipRecruiter",
    "simplify.jobs": "Simplify Jobs", "builtinnyc.com": "Built In NYC",
    "builtin.com": "Built In", "uiuxjobsboard.com": "UI/UX Jobs Board",
    "dice.com": "Dice", "monster.com": "Monster",
}


def _domain(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url or "").split("/")[0].lower()


def _board_label(url: str) -> str:
    d = _domain(url)
    if d in _BOARD_LABELS:
        return _BOARD_LABELS[d]
    name = d.split(":")[0].rsplit(".", 1)[0].replace("-", " ").replace(".", " ").strip()
    return name.title() or (d or "See listing")


def _company_from_result(r: dict) -> str:
    """Best-effort company / job-board name from a Tavily web result.
    Accept a 'Role at Company' split only if it looks like a real company,
    otherwise fall back to a clean board label from the domain."""
    title = (r.get("title") or "").strip()
    for sep in (" at ", " - ", " | ", " – "):
        if sep in title:
            cand = title.split(sep)[-1].strip(" -|–,")
            if (2 <= len(cand) <= 50
                    and not re.search(r"\b(job|jobs|employment|hiring|career|careers|"
                                      r"salary|posted|remote)\b", cand, re.I)):
                return cand
    return _board_label(r.get("url", ""))


def _from_tavily_jobs(job_title: str) -> list[dict]:
    # Unrestricted search gives more variety than a 4-domain include list
    # (which floods with near-identical aggregator pages from one board).
    results = _tavily_search(f"{job_title} jobs hiring", max_results=10,
                             search_depth="basic")
    out, seen = [], set()
    for r in results:
        url = (r.get("url") or "").strip()
        if not url or any(_domain(url).endswith(s) for s in _SKIP_DOMAINS):
            continue
        name = _company_from_result(r)
        if name.lower() in seen:   # one entry per company/board so we don't repeat
            continue
        seen.add(name.lower())
        out.append({
            "name": name,
            "role": job_title,
            "location": "See listing",
            "url": url,
            "source": "web",
        })
        if len(out) >= MAX_COMPANIES:
            break
    return out


def get_companies_hiring(job_title: str) -> list[dict]:
    """Real 'who's hiring' rows for `job_title`, ranked by title relevance.
    Returns [] on total failure (Agent 1 degrades gracefully)."""
    try:
        toks = _tokens(job_title)
        scored: list[tuple[int, dict]] = []
        if toks:
            for fn in (_from_remotive, _from_arbeitnow):
                try:
                    scored.extend(fn(job_title, toks))
                except Exception as exc:
                    log.warning("%s failed: %s", fn.__name__, exc)

        # Best title matches first (e.g. "Data Scientist" before "Data Analyst").
        scored.sort(key=lambda x: x[0], reverse=True)
        merged = [item for _, item in scored]

        # Fallback: live job APIs had no relevant match -> Tavily web search.
        if not merged and (job_title or "").strip():
            try:
                merged = _from_tavily_jobs(job_title)
            except Exception as exc:
                log.warning("tavily jobs fallback failed: %s", exc)

        seen_url, seen_pair, deduped = set(), set(), []
        for c in merged:
            pair = (c["name"].lower(), c["role"].lower())
            if c["url"] in seen_url or pair in seen_pair:
                continue
            seen_url.add(c["url"])
            seen_pair.add(pair)
            deduped.append(c)
            if len(deduped) >= MAX_COMPANIES:
                break
        return deduped
    except Exception as exc:  # absolute backstop — never raise
        log.warning("get_companies_hiring fatal: %s", exc)
        return []


# --------------------------------------------------------------------------- #
# 2) Salary overview
# --------------------------------------------------------------------------- #
def _coerce_band(d) -> dict | None:
    if not isinstance(d, dict):
        return None
    try:
        lo, hi = _round_k(d.get("min", 0)), _round_k(d.get("max", 0))
    except Exception:
        return None
    if lo <= 0 and hi <= 0:
        return None
    if hi < lo:
        lo, hi = hi, lo
    return {"min": lo, "max": hi}


def _normalize_overview(d: dict, fallback_sources: list[str]) -> dict | None:
    """Coerce a raw LLM/extraction dict into the exact contract shape, or None
    if it has no usable numbers."""
    if not isinstance(d, dict):
        return None
    entry = _coerce_band(d.get("entry"))
    mid = _coerce_band(d.get("mid"))
    senior = _coerce_band(d.get("senior"))
    if not (entry and mid and senior):
        return None
    srcs = d.get("sources")
    if not isinstance(srcs, list) or not srcs:
        srcs = fallback_sources
    srcs = [s for s in srcs if isinstance(s, str) and s.startswith("http")][:5]
    return {
        "entry": entry,
        "mid": mid,
        "senior": senior,
        "currency": (d.get("currency") or "USD").strip()[:8] or "USD",
        "sources": srcs or fallback_sources[:5],
        "note": (d.get("note") or "").strip()[:240],
    }


def _extract_from_snippets(snippets_text: str, sources: list[str]) -> dict | None:
    """Regex fallback: pull salary figures from the search snippets and bucket
    them into entry/mid/senior. Used only when Gemini synthesis is unavailable."""
    nums: list[int] = []
    for m in re.finditer(r"\$?\s?(\d{1,3}(?:,\d{3})+)", snippets_text):  # 90,000
        nums.append(int(m.group(1).replace(",", "")))
    for m in re.finditer(r"\$\s?(\d{2,3})\s?[kK]\b", snippets_text):      # $120k
        nums.append(int(m.group(1)) * 1000)
    nums = sorted(n for n in nums if 20000 <= n <= 600000)
    if len(nums) < 3:
        return None
    n = len(nums)
    raw = {
        "entry": {"min": nums[0], "max": nums[max(0, n // 3 - 1)]},
        "mid": {"min": nums[n // 3], "max": nums[max(n // 3, 2 * n // 3 - 1)]},
        "senior": {"min": nums[2 * n // 3], "max": nums[-1]},
        "currency": "USD",
        "sources": sources,
        "note": "Estimated from search snippets (LLM synthesis unavailable).",
    }
    return _normalize_overview(raw, sources)


def get_salary_overview(job_title: str) -> dict:
    """Grounded entry/mid/senior salary bands for `job_title`. Returns {} only
    if literally nothing (no web, no LLM, no defaults) — otherwise a usable shape."""
    cache_key = (job_title or "").strip().lower()
    if cache_key in _salary_cache:
        return _salary_cache[cache_key]

    result: dict = {}
    try:
        results = _tavily_search(f"{job_title} salary 2025 entry mid senior",
                                 max_results=6, search_depth="advanced")
        sources = [r.get("url") for r in results
                   if isinstance(r.get("url"), str) and r["url"].startswith("http")]
        snippets = "\n\n".join(
            f"[{i+1}] {r.get('title','')}\nURL: {r.get('url','')}\n{(r.get('content') or '')[:600]}"
            for i, r in enumerate(results)
        )

        if snippets:
            prompt = _load_prompt("salary_synthesis")
            if prompt:
                filled = (prompt.replace("{{job_title}}", job_title)
                          .replace("{{snippets}}", snippets)
                          .replace("{{region}}", "global / USD"))
                norm = _normalize_overview(_gemini_json(filled, fast_first=True) or {}, sources)
                if norm:
                    result = norm
            # Gemini unavailable/garbled -> regex extraction from the same snippets
            if not result:
                ext = _extract_from_snippets(snippets, sources)
                if ext:
                    result = ext

        # Nothing usable from the web -> labelled default estimate so the UI renders
        if not result:
            result = dict(DEFAULT_OVERVIEW)
            result["sources"] = []
            result["note"] = "Rough estimate — live salary data was unavailable."
    except Exception as exc:  # absolute backstop — never raise
        log.warning("get_salary_overview fatal: %s", exc)
        result = {}

    _salary_cache[cache_key] = result
    return result


# --------------------------------------------------------------------------- #
# 3) Per-milestone salary bands
# --------------------------------------------------------------------------- #
def _interp(f: float, points: list[tuple[float, float]]) -> float:
    """Piecewise-linear interpolation of y at x=f over sorted (x,y) points."""
    if f <= points[0][0]:
        return points[0][1]
    if f >= points[-1][0]:
        return points[-1][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= f <= x1:
            t = 0.0 if x1 == x0 else (f - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return points[-1][1]


def _band_for_fraction(f: float, ov: dict) -> tuple[int, int]:
    """Map career-progress fraction f∈[0,1] onto a salary band, ramping
    pre-entry → entry → mid → senior."""
    e, m, s = ov["entry"], ov["mid"], ov["senior"]
    lo_pts = [(0.0, 0), (0.34, e["min"]), (0.67, m["min"]), (1.0, s["min"])]
    hi_pts = [(0.0, e["min"]), (0.34, e["max"]), (0.67, m["max"]), (1.0, s["max"])]
    return _round_k(_interp(f, lo_pts)), _round_k(_interp(f, hi_pts))


def _note_for_fraction(f: float) -> str:
    if f < 0.34:
        return "intern / entry-level while building skills"
    if f < 0.67:
        return "entry to mid-level range"
    return "mid to senior-level range"


def get_milestone_salaries(job_title: str, milestones: list[dict]) -> list[dict]:
    """Return [{order,min,max,currency,note}] aligned to each milestone, with
    bands rising from pre-entry to senior. Returns [] on failure."""
    try:
        if not milestones:
            return []
        ov = get_salary_overview(job_title) or {}
        estimated = False
        if not all(k in ov for k in ("entry", "mid", "senior")):
            ov = dict(DEFAULT_OVERVIEW)
            estimated = True
        currency = ov.get("currency", "USD")

        n = len(milestones)
        out = []
        for i, ms in enumerate(milestones):
            f = i / (n - 1) if n > 1 else 0.0
            lo, hi = _band_for_fraction(f, ov)
            note = _note_for_fraction(f)
            if estimated:
                note += " (estimate)"
            out.append({
                "order": ms.get("order", i + 1) if isinstance(ms, dict) else i + 1,
                "min": lo,
                "max": hi,
                "currency": currency,
                "note": note,
            })
        return out
    except Exception as exc:  # absolute backstop — never raise
        log.warning("get_milestone_salaries fatal: %s", exc)
        return []


# --------------------------------------------------------------------------- #
# Manual "prove it" harness
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys

    titles = sys.argv[1:] or ["Data Scientist", "UX Designer"]
    demo_milestones = [
        {"order": 1, "title": "Foundations"},
        {"order": 2, "title": "Building Projects"},
        {"order": 3, "title": "First Role"},
        {"order": 4, "title": "Senior"},
    ]
    for t in titles:
        print(f"\n{'='*70}\n{t}\n{'='*70}")
        comps = get_companies_hiring(t)
        print(f"companies_hiring ({len(comps)}):")
        print(json.dumps(comps, indent=2)[:1500])
        print("\nsalary_overview:")
        print(json.dumps(get_salary_overview(t), indent=2))
        print("\nmilestone_salaries:")
        print(json.dumps(get_milestone_salaries(t, demo_milestones), indent=2))
