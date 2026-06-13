# CareerPath — Backend

A student types a **target job title** and gets a **visual career roadmap** — milestones, skills, certifications, salaries, companies hiring, courses + YouTube — plus a **RAG chatbot** to ask follow-ups.

This repo is the **backend**: a FastAPI REST API + an n8n RAG chatbot. The frontend (built in Lovable by our partner) talks to it only through [`spec/API_CONTRACT.md`](../spec/API_CONTRACT.md).

```
Frontend (Lovable)  ──HTTP──►  FastAPI :8000  ──►  Gemini 2.5 Flash  (roadmap, /api/roadmap)
                                      │
                                      └──proxy──►  n8n :5678 webhook  (RAG chat, /api/chat)
```

---

## 1. Run the API (under 5 minutes)

Requires **Python 3.10+**. From `app/`:

```bash
# Windows (PowerShell)
python -m venv .venv ; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# macOS / Linux
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Smoke-test:

```bash
curl http://localhost:8000/api/health
# {"status":"ok","version":"1.0","mock_mode":false}

curl -X POST http://localhost:8000/api/roadmap \
  -H "Content-Type: application/json" -d '{"job_title":"Data Scientist"}'
```

### Endpoints (full shapes in `spec/API_CONTRACT.md`)
| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/api/health`  | liveness + whether mock-mode is on |
| `POST` | `/api/roadmap` | the full visual payload (Gemini roadmap + jobs/salary + courses/YouTube) |
| `POST` | `/api/chat`    | RAG chatbot — thin proxy to the n8n webhook, returns `{answer, sources}` |

CORS is open (`*`) for the hackathon. No endpoint 500s if a sub-module fails — it degrades to `[]`/`{}`.

---

## 2. Configure `.env`

`app/.env` already exists (git-ignored). Keys:

```env
GEMINI_API_KEY=…                 # required — Google Gemini 2.5 Flash
GEMINI_MODEL=gemini-2.5-flash    # do NOT use 2.0 (429 limit:0 on this account)
GEMINI_MODEL_FALLBACK=gemini-2.5-flash-lite
TAVILY_API_KEY=…                 # live web data (courses, jobs, salary)
FIRECRAWL_API_KEY=…              # live web data (optional)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/careerpath-chat   # the RAG chatbot (see §4)
YOUTUBE_API_KEY=                 # optional; empty → YouTube via Tavily
MOCK=0                           # 1 = force mock-mode (see §3)
```

---

## 3. Mock-mode (offline demo safety net)

Mock-mode returns a cached, contract-valid roadmap instantly — **no external calls**. Use it so the frontend can integrate before live calls are ready, and as a live-demo fallback.

- **Per request:** `POST /api/roadmap` with `{"job_title":"…","mock":true}`.
- **Globally:** set `MOCK=1` in `.env` (or the environment) and restart uvicorn. `/api/health` then shows `"mock_mode": true`.

`/api/chat` has its own built-in fallback: if `N8N_WEBHOOK_URL` is empty or n8n is unreachable, it returns a friendly stub instead of erroring.

---

## 4. RAG chatbot (n8n) — import & activate

The chatbot is an n8n workflow at [`n8n/careerpath_rag.json`](n8n/careerpath_rag.json). Full instructions: [`n8n/SETUP.md`](n8n/SETUP.md). Quick version:

1. `n8n start` → open <http://localhost:5678>.
2. **Import from File** → `app/n8n/careerpath_rag.json`.
3. On the **Google Gemini Chat Model** node, create a **Google Gemini(PaLM) API** credential with your `GEMINI_API_KEY`.
4. Toggle the workflow **Active**. The webhook goes live at `http://localhost:5678/webhook/careerpath-chat`.
5. Confirm it's wired: `N8N_WEBHOOK_URL` in `.env` points at that URL (already set).

Verify directly:

```bash
curl -X POST http://localhost:5678/webhook/careerpath-chat \
  -H "Content-Type: application/json" \
  -d '{"job_title":"Data Scientist","message":"Do I need a master'\''s degree?"}'
# {"answer":"…","sources":[]}
```

…and end-to-end through the API:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"job_title":"Data Scientist","message":"Do I need a master'\''s degree?","history":[]}'
```

> The shipped workflow grounds answers in an embedded career knowledge base ([`n8n/career_kb.md`](n8n/career_kb.md)) and returns `sources: []`. Adding a live web-search tool to populate `sources` is documented as an optional upgrade in `n8n/SETUP.md` (note the n8n 2.19 HTTP-Request-Tool caveat there).

---

## 5. Connect the Lovable frontend

1. Pull the partner's Lovable repo (she pushes it to GitHub when ready).
2. Set its API base URL to **`http://localhost:8000`** (look for an `API_BASE` / `VITE_API_URL` / `.env` value).
3. Run both: this backend on `:8000`, the frontend on its dev port. CORS is already open.
4. Demoing across machines? Expose the API with `ngrok http 8000` and use the ngrok URL as the frontend's API base.

---

## 6. 60-second demo script

1. **Health** — `GET /api/health` → `ok` (point out `mock_mode`). *(5s)*
2. **Roadmap** — in the frontend, type **"Data Scientist"** → the visual roadmap renders: milestones, skills, certs, salary overview, companies hiring, courses + YouTube. *(20s)*
3. **Second role** — try **"UX Designer"** to show it generalises. *(10s)*
4. **Chatbot** — ask **"Do I need a master's degree?"** → short, honest, grounded answer from the n8n RAG flow. Ask a follow-up to show memory. *(20s)*
5. **Safety net** — flip `mock:true` (or `MOCK=1`) to show it runs instantly offline if the network dies mid-demo. *(5s)*

---

## Project layout

```
app/
  main.py            FastAPI app: routes, CORS, assembly, /api/chat proxy   (Agent 1)
  models.py          Pydantic schemas = the contract types                  (Agent 1)
  mock_data.py       cached sample /roadmap payload                         (Agent 1)
  prompts.py         loads /prompts/*.md                                    (shared)
  services/
    roadmap.py       Gemini roadmap generation                             (Agent 1)
    jobs_salary.py   companies hiring + salary data                        (Agent 2)
    learning.py      recommended courses + YouTube                         (Agent 3)
  n8n/
    careerpath_rag.json   importable RAG chatbot workflow                  (Agent 4)
    career_kb.md          knowledge base the chatbot is grounded in        (Agent 4)
    SETUP.md              import / credential / activate guide              (Agent 4)
  tests/test_api.py  end-to-end API tests                                  (Agent 1)
  prompts/  (../prompts)  all LLM prompts as documented markdown
  .env               keys (git-ignored)
  requirements.txt   deps
```

Prompts live in [`../prompts`](../prompts/) as documented markdown and are loaded from disk — see `prompts.py`.
