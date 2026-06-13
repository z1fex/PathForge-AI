# 💼 AGENT 2 — Companies Hiring + Salary

Read [00_MASTER_SPEC.md](00_MASTER_SPEC.md), [API_CONTRACT.md](API_CONTRACT.md), `app/tasks/lessons.md` first.

## Your mission
Provide real "who's hiring" data and grounded salary numbers for any job title — all free sources.

## File you own
- `app/services/jobs_salary.py` (only this). Append your deps to `requirements.txt`.

## Functions to implement (exact signatures — Agent 1 imports these)
```python
def get_companies_hiring(job_title: str) -> list[dict]   # -> companies_hiring[] per contract
def get_salary_overview(job_title: str) -> dict          # -> salary_overview{} per contract
def get_milestone_salaries(job_title: str, milestones: list[dict]) -> list[dict]  # adds expected_salary to each
```

## How to build each

### 1. `get_companies_hiring` — free job APIs (no key)
- **Remotive:** `GET https://remotive.com/api/remote-jobs?search={job_title}&limit=10` → `jobs[]` has `company_name`, `title`, `candidate_required_location`, `url`.
- **Arbeitnow:** `GET https://www.arbeitnow.com/api/job-board-api` → `data[]` has `company_name`, `title`, `location`, `url`; filter titles containing keywords from `job_title`.
- Merge, dedupe by company+title, cap at ~8. Map to `{name, role, location, url, source}`.
- **Fallback:** if both return nothing, Tavily search `"{job_title} jobs hiring"` (`include_domains` e.g. `linkedin.com`, `wellfound.com`, `indeed.com`) and extract company + url.

### 2. `get_salary_overview` — Tavily grounding + Gemini synthesis
- Tavily search `"{job_title} salary 2025 entry mid senior"` (advanced, 6 results). Collect snippets + URLs.
- Feed snippets to Gemini (JSON mode) using prompt `load_prompt("salary_synthesis")` → returns `{entry,mid,senior,currency,sources}`.
- `sources` = the actual Tavily result URLs you used. Numbers must be realistic; if unknown, estimate and say so in a `note`.

### 3. `get_milestone_salaries`
- For each milestone (early→late), assign a sensible band derived from the overview (early ≈ entry, later ≈ mid/senior). Return list of `{order, min, max, currency, note}` that Agent 1 merges into each milestone's `expected_salary`.

## Free tools / keys
- Remotive + Arbeitnow (no key) · Tavily (`TAVILY_API_KEY` in `.env`) · Firecrawl optional for stubborn pages · Gemini for synthesis.
- HTTP via `requests` or `httpx`. **Timeout every call (≤8s)** and wrap in try/except — return `[]`/`{}` on failure, never raise.

## Definition of Done + Verification
- [ ] Standalone test: `python -c "from app.services.jobs_salary import *; print(get_companies_hiring('Data Scientist'))"` returns ≥3 real companies with working URLs.
- [ ] `get_salary_overview('Data Scientist')` returns plausible numbers + ≥2 source URLs.
- [ ] Every function returns the contract shape exactly; failures degrade to empty, never crash.
- **Prove it:** paste sample output for two job titles before declaring done.

## Lessons
Append API quirks (rate limits, field names, empty results) to `app/tasks/lessons.md`.
