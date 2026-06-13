# 🎓 AGENT 3 — Recommended Courses + YouTube

Read [00_MASTER_SPEC.md](00_MASTER_SPEC.md), [API_CONTRACT.md](API_CONTRACT.md), `app/tasks/lessons.md` first.

## Your mission
For a job title + its skills, return the best **free-first** courses and YouTube channels — real, working links.

## File you own
- `app/services/learning.py` (only this). Append your deps to `requirements.txt`.

## Functions to implement (exact signatures — Agent 1 imports these)
```python
def get_courses(job_title: str, skills: list[str]) -> list[dict]   # -> recommended_courses[] per contract
def get_youtube(job_title: str, skills: list[str]) -> list[dict]   # -> youtube[] per contract
```

## How to build each

### 1. `get_courses` — Tavily, free-first
- For the top 3–4 skills (or the job title), Tavily search e.g. `"best free course to learn {skill}"`, `include_domains` = `freecodecamp.org`, `coursera.org`, `udemy.com`, `edx.org`, `youtube.com`, `kaggle.com`.
- Map to `{title, provider, url, free}`. Set `free=true` for freeCodeCamp/YouTube/Kaggle/edX-audit; mark paid ones `false`.
- Cap ~6, prefer free, dedupe by URL. Optionally pass titles through Gemini (`courses_youtube_curation` prompt) to clean/label.

### 2. `get_youtube`
- **Default (no extra key):** Tavily search `"best YouTube channel to learn {skill}"` restricted to `include_domains=["youtube.com"]`; extract channel/video title + url, and a one-line `why`.
- **Optional upgrade (if `YOUTUBE_API_KEY` set):** YouTube Data API v3 `search.list?q={skill} tutorial&type=channel` for cleaner results.
- Map to `{channel, title, url, why}`. Cap ~5.

## Free tools / keys
- Tavily (`TAVILY_API_KEY`) · Gemini (optional cleanup) · YouTube Data API (optional, free).
- **Timeout every call (≤8s)**, try/except → return `[]` on failure. Never raise (Agent 1 must not 500 because of you).

## Definition of Done + Verification
- [ ] `get_courses('Data Scientist', ['Python','Statistics'])` → ≥4 items, links resolve, free flags correct.
- [ ] `get_youtube('Data Scientist', ['Machine Learning'])` → ≥3 channels with real URLs + a useful `why`.
- [ ] Contract shape exact; graceful empty on failure.
- **Prove it:** paste sample output for two job titles before declaring done.

## Lessons
Append quirks (Tavily domain filters, dead links, dedupe) to `app/tasks/lessons.md`.
