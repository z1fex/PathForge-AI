# 🧩 AGENT 1 — API Spine + Roadmap Engine + Assembly

**You own the backbone.** Everyone else plugs into you. Read [00_MASTER_SPEC.md](00_MASTER_SPEC.md) and [API_CONTRACT.md](API_CONTRACT.md) first, then `app/tasks/lessons.md`.

## Your mission
Build the FastAPI app, the Gemini-powered roadmap generator, the mock-mode, the chat proxy, and assemble Agents 2 & 3 into one `/api/roadmap` response.

## Files you own (do NOT touch others')
- `app/main.py`, `app/models.py`, `app/services/roadmap.py`, `app/mock_data.py`, `app/prompts.py`, `app/requirements.txt`, `app/tests/test_api.py`

## Tasks
1. **Scaffold** FastAPI app with CORS (`allow_origins=["*"]`), and these routes per the contract:
   - `GET /api/health`
   - `POST /api/roadmap`
   - `POST /api/chat` (proxy — see step 5)
2. **Pydantic models** in `models.py` matching every shape in [API_CONTRACT.md](API_CONTRACT.md).
3. **`prompts.py`** — helper `load_prompt(name)` that reads `../prompts/<name>.md`.
4. **Roadmap engine** (`services/roadmap.py`):
   - Use Gemini `gemini-2.5-flash` with **JSON mode** (`generation_config={"response_mime_type":"application/json"}`). Model name comes from `GEMINI_MODEL` in `.env` (fallback `gemini-2.5-flash-lite` if rate-limited).
   - Prompt = `load_prompt("roadmap_generation")` with `{job_title}` injected.
   - Returns `summary`, `background_required`, `milestones[]`, `skills[]`, `certifications[]`.
5. **Assembly** in `/api/roadmap`:
   - Call roadmap engine, then `jobs_salary.get_companies_hiring()`, `get_salary_overview()`, `get_milestone_salaries()`, and `learning.get_courses()`, `get_youtube()`.
   - Run sub-calls with try/except + short timeouts; on failure substitute `[]`/`{}` and continue. **Never 500 because a sub-module failed.**
   - Stamp `generated_at`, `mock`.
6. **Chat proxy** (`/api/chat`): POST body to `N8N_WEBHOOK_URL`, return its JSON. If unset/unreachable → return `{"answer":"Chat is warming up — try again shortly.","sources":[]}`.
7. **Mock-mode** (`mock_data.py`): a realistic, contract-valid sample payload (e.g. "Data Scientist"). Triggered by `{"mock":true}` in body **or** env `MOCK=1`. Must work with **no API keys**.
8. **Integration stubs:** until Agents 2/3 land, import their functions defensively (try/except ImportError → return empty), so you can build and test immediately.

## Free tools
- Gemini only (`google-generativeai`). No other external calls in your code.

## requirements.txt (seed — others append)
```
fastapi
uvicorn[standard]
pydantic
python-dotenv
google-generativeai
httpx
requests
pytest
```

## Definition of Done + Verification
- [ ] `uvicorn main:app` boots with zero errors.
- [ ] `GET /api/health` → `{"status":"ok",...}` (curl it).
- [ ] `POST /api/roadmap {"job_title":"Data Scientist"}` → contract-valid JSON (eyeball all fields present).
- [ ] `POST /api/roadmap {"mock":true}` works with keys removed.
- [ ] `pytest tests/test_api.py` passes (health + roadmap shape + mock).
- [ ] App does not crash if `services/jobs_salary.py` or `learning.py` raise.
- **Prove it:** paste the curl output for a real + a mock call before declaring done.

## Lessons
Append every gotcha to `app/tasks/lessons.md` (e.g. Gemini JSON quirks, CORS, import order).
