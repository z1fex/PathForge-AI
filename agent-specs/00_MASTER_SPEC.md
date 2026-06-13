# ðŸŽ¯ CareerPath â€” Backend Master Spec (THE INSTRUCTOR)

> **Read this first, every session.** This is the central brief that governs all 4 build agents.
> Hackathon: **VibeThon 2026** Â· Problem statement: **PS01 â€” Create Something Innovative**
> Time budget: **~1 hour** for the backend. Frontend is built in parallel by our partner (Lovable â†’ GitHub).

---

## 1. The Product
**CareerPath** â€” a student types a **target job title** and instantly gets a **visual career roadmap**:
- Visual **milestones** (stages from beginner â†’ hired)
- **Skills**, **certifications**, and **background** required at each stage
- **Salary expectations** per milestone + an overall entry/mid/senior overview
- **Companies currently hiring** for that role
- **Recommended courses + YouTube channels**
- A **RAG chatbot** to ask anything about the path

## 2. Our Scope vs Partner's Scope
| We build (backend, ~1h) | Partner builds (parallel) |
|---|---|
| FastAPI REST API: `/roadmap`, `/chat`, `/health` | Frontend in **Lovable** |
| n8n RAG workflow | Pushes to **GitHub** when done |
| Mock-mode + tests + prompts | We **pull her repo & integrate** at the end |

The frontend talks to our backend **only through the [API_CONTRACT.md](API_CONTRACT.md)**. Contract is law.

## 3. Stack (free tools only)
| Layer | Choice | Free? |
|---|---|---|
| API framework | **FastAPI + Uvicorn** (Python 3.10+) | âœ… |
| LLM | **Google Gemini 2.5 Flash** (`gemini-2.5-flash`) via `google-generativeai` | âœ… free tier |
| Live web data | **Tavily** + **Firecrawl** (keys provided) | âœ… dev tier |
| Jobs | **Remotive** + **Arbeitnow** public APIs (no key) | âœ… |
| Courses/YouTube | Tavily search (+ optional YouTube Data API) | âœ… |
| RAG | **n8n** (webhook â†’ AI Agent + Gemini + knowledge base) | âœ… self-host/free |
| Embeddings (if needed) | Gemini `text-embedding-004` | âœ… |

## 4. Environment / Keys  â†’ `app/.env`
```env
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>   # set & verified working
GEMINI_MODEL=gemini-2.5-flash         # IMPORTANT: 2.0 models = limit:0 on this account. Use 2.5.
GEMINI_MODEL_FALLBACK=gemini-2.5-flash-lite
TAVILY_API_KEY=<YOUR_TAVILY_API_KEY>
FIRECRAWL_API_KEY=<YOUR_FIRECRAWL_API_KEY>
N8N_WEBHOOK_URL=       # <-- Agent 4 fills this after building the n8n flow
YOUTUBE_API_KEY=       # optional; if empty, Agent 3 uses Tavily for YouTube
```
> `.env` is already created at `app/.env` and git-ignored. **Always read `GEMINI_MODEL` from env â€” do NOT hardcode `gemini-2.0-flash` (it returns 429 limit:0 on this account).**

## 5. The 4 Agents (one task each â€” full briefs linked)
| Agent | Mission | Brief |
|---|---|---|
| **Agent 1** | API spine + Roadmap engine + assembly + mock-mode + e2e test | [AGENT_1_core_api.md](AGENT_1_core_api.md) |
| **Agent 2** | Companies hiring + Salary data | [AGENT_2_jobs_salary.md](AGENT_2_jobs_salary.md) |
| **Agent 3** | Recommended courses + YouTube | [AGENT_3_learning.md](AGENT_3_learning.md) |
| **Agent 4** | RAG chatbot in n8n + webhook contract | [AGENT_4_rag_n8n.md](AGENT_4_rag_n8n.md) |

**Coordination rule:** Agents 2 & 3 expose pure functions (signatures in the contract). Agent 1 imports and assembles them. Agent 4 is independent and returns a webhook URL that Agent 1 proxies. **No agent edits another agent's files.**

### Target file tree (`app/`)
```
app/
  main.py                 # Agent 1 â€” FastAPI app, routes, CORS, assembly, proxy
  models.py               # Agent 1 â€” Pydantic schemas (the contract types)
  services/
    roadmap.py            # Agent 1 â€” Gemini roadmap generation
    jobs_salary.py        # Agent 2
    learning.py           # Agent 3
  mock_data.py            # Agent 1 â€” cached sample /roadmap payload
  prompts.py              # loads /prompts/*.md (shared)
  tests/
    test_api.py           # Agent 1 â€” e2e
  tasks/lessons.md        # shared lessons log (framework)
  .env                    # keys (git-ignored)
  requirements.txt        # all deps
  README.md               # Agent 4 â€” run + integrate instructions
```

## 6. THE OPERATING FRAMEWORK (every agent obeys)
1. **Plan first.** Any task with 3+ steps â†’ write a short plan before coding. If it goes sideways, stop and re-plan.
2. **One task per agent.** Stay in your lane. Don't touch other agents' files.
3. **Self-improvement loop.** Every correction/gotcha â†’ append a one-line rule to `app/tasks/lessons.md`. Read lessons at start.
4. **Verification before done.** Never mark done without proving it runs. Ask: *"Would a staff engineer approve this?"*
5. **Autonomous bug-fixing.** Given an error/log/failing test, just fix it â€” read the traceback, resolve, re-verify.

## 7. Prompt quality (JUDGED)
All LLM prompts live in [`/prompts`](../prompts/) as documented markdown â€” judges score prompt quality. Code loads them from there via `app/prompts.py`; do **not** inline large prompts in code. See [prompts/README.md](../prompts/README.md).

## 8. Run & Demo
```bash
cd app
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# health:  GET  http://localhost:8000/api/health
# roadmap: POST http://localhost:8000/api/roadmap   {"job_title":"Data Scientist"}
```
- **Mock-mode** (`{"mock": true}` or `MOCK=1`) returns a cached payload instantly â€” use it so the partner's frontend integrates before live calls are ready, and as a **demo safety net**.
- Integration: pull partner's Lovable repo, set its API base to `http://localhost:8000`, run both. Use **ngrok** only if demoing across machines.

## 9. Definition of Done (whole backend)
- [ ] `GET /api/health` â†’ ok
- [ ] `POST /api/roadmap` returns a full, contract-valid payload for 3 different job titles
- [ ] `POST /api/chat` returns a grounded answer via n8n (or graceful stub)
- [ ] Mock-mode works offline
- [ ] No endpoint 500s when a sub-module/API fails (graceful degrade)
- [ ] `prompts/` populated and loaded from disk
- [ ] `README.md` lets a teammate run it in <5 min

