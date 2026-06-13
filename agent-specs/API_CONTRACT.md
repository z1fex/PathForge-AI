# API Contract — CareerPath Backend (SHARED SOURCE OF TRUTH)

> Every agent builds **to this contract**. Do not change a field name without updating this file and pinging the team.
> The Lovable frontend (built by partner) consumes exactly these shapes.

- **Base URL (local):** `http://localhost:8000`
- **CORS:** allow all origins (`*`) for the hackathon.
- **Content-Type:** `application/json` on all POST.
- **All LLM JSON is produced via Gemini JSON mode** (`response_mime_type: application/json`) for reliability.

---

## 1. `GET /api/health`
```json
{ "status": "ok", "version": "1.0", "mock_mode": false }
```

## 2. `POST /api/roadmap`  (the main payload — powers the whole visual page)
**Request**
```json
{ "job_title": "Data Scientist", "mock": false }
```
**Response 200**
```json
{
  "job_title": "Data Scientist",
  "summary": "2-3 sentence overview of the role and the path.",
  "background_required": "e.g. Bachelor's in CS/Stats helpful but not required; self-taught viable.",
  "milestones": [
    {
      "order": 1,
      "title": "Foundations",
      "duration": "0-3 months",
      "description": "What you do in this phase.",
      "skills": ["Python", "Statistics"],
      "certifications": ["Google Data Analytics"],
      "expected_salary": { "min": 0, "max": 45000, "currency": "USD", "note": "intern/entry while learning" }
    }
  ],
  "skills": [
    { "name": "Python", "level": "Beginner", "why": "Core language for data work." }
  ],
  "certifications": [
    { "name": "Google Data Analytics", "provider": "Coursera", "url": "https://...", "free": false }
  ],
  "companies_hiring": [
    { "name": "Acme", "role": "Junior Data Scientist", "location": "Remote", "url": "https://...", "source": "remotive" }
  ],
  "recommended_courses": [
    { "title": "Python for Everybody", "provider": "freeCodeCamp", "url": "https://...", "free": true }
  ],
  "youtube": [
    { "channel": "StatQuest", "title": "Machine Learning playlist", "url": "https://...", "why": "Best intuition for ML stats." }
  ],
  "salary_overview": {
    "entry":  { "min": 60000, "max": 90000 },
    "mid":    { "min": 95000, "max": 130000 },
    "senior": { "min": 140000, "max": 200000 },
    "currency": "USD",
    "sources": ["https://levels.fyi/...", "https://..."]
  },
  "generated_at": "2026-06-13T00:00:00Z",
  "mock": false
}
```

### Who fills which part of `/api/roadmap`
| Field | Owner |
|-------|-------|
| `summary`, `background_required`, `milestones`, `skills`, `certifications` | **Agent 1** (Gemini roadmap engine) |
| `companies_hiring`, `salary_overview`, per-milestone `expected_salary` | **Agent 2** |
| `recommended_courses`, `youtube` | **Agent 3** |
| Assembly into final response + `mock`, `generated_at` | **Agent 1** |

Agent 1 calls Agent 2 & Agent 3 functions and merges. Signatures (Python):
```python
# Agent 2 — module: services/jobs_salary.py
def get_companies_hiring(job_title: str) -> list[dict]: ...      # -> companies_hiring[]
def get_salary_overview(job_title: str) -> dict: ...            # -> salary_overview{}
def get_milestone_salaries(job_title: str, milestones: list[dict]) -> list[dict]: ...  # fills expected_salary

# Agent 3 — module: services/learning.py
def get_courses(job_title: str, skills: list[str]) -> list[dict]: ...   # -> recommended_courses[]
def get_youtube(job_title: str, skills: list[str]) -> list[dict]: ...   # -> youtube[]
```
> If any module fails or times out, return `[]`/`{}` gracefully — Agent 1 must never 500 because a sub-module failed. Degrade, don't crash.

## 3. `POST /api/chat`  (RAG — proxied to n8n)
**Request**
```json
{ "job_title": "Data Scientist", "message": "Do I need a master's degree?", "history": [] }
```
**Response 200**
```json
{ "answer": "Short, grounded answer.", "sources": [ { "title": "Source title", "url": "https://..." } ] }
```
- **Implementation:** Agent 1 exposes `/api/chat` as a thin proxy that POSTs the body to the **n8n webhook URL** (provided by Agent 4) and returns its JSON unchanged.
- **Fallback:** if `N8N_WEBHOOK_URL` is unset, `/api/chat` returns a friendly stub so the frontend never breaks.
- Agent 4's n8n workflow MUST return exactly `{ "answer": "...", "sources": [...] }`.

---

## Error shape (all endpoints)
```json
{ "error": "human-readable message", "detail": "optional" }
```
HTTP 200 for success; 4xx for bad input; never leak stack traces to the client.
