# 🤖 AGENT 4 — RAG Chatbot in n8n + Webhook Contract + README

Read [00_MASTER_SPEC.md](00_MASTER_SPEC.md), [API_CONTRACT.md](API_CONTRACT.md), `app/tasks/lessons.md` first.

## Your mission
Build the **RAG chatbot as an n8n workflow** triggered by a webhook. It answers a student's question about a career path, grounded in a knowledge base, and returns `{answer, sources[]}`. Then document the webhook URL so Agent 1 can proxy it, and write the project README.

## Deliverables you own
- `app/n8n/careerpath_rag.json` — exported n8n workflow (importable).
- `app/n8n/SETUP.md` — how to import, set the Gemini credential, activate, and get the webhook URL.
- `app/README.md` — run + integrate instructions for the whole backend.
- Fill `N8N_WEBHOOK_URL` in `app/.env` once live.

## The n8n workflow (nodes)
1. **Webhook** (POST, path `/careerpath-chat`) — receives `{ job_title, message, history }`.
2. **AI Agent** node (LangChain Agent) wired to:
   - **Chat model:** Google Gemini Chat Model (`gemini-2.5-flash`) — add Google Gemini (PaLM) API credential using `GEMINI_API_KEY`.
   - **System prompt:** paste from [prompts/rag_system_prompt.md](../prompts/rag_system_prompt.md). It must use `{{$json.job_title}}` as context and keep answers short, practical, honest.
   - **Memory:** Window Buffer Memory keyed by session (optional, uses `history`).
   - **Knowledge base (the "RAG"):** use n8n's **Simple Vector Store** (in-memory) loaded from a small `career_kb` doc (general advice on roadmaps, certs, salaries, switching careers), attached to the Agent as a **Vector Store retriever tool**. If time is tight, fall back to giving the Agent a **Tavily/HTTP Request tool** so it can fetch live facts instead.
3. **Respond to Webhook** — return JSON **exactly**: `{ "answer": "<agent output>", "sources": [ {"title":"","url":""} ] }`. If you used a retriever/web tool, populate `sources`; else `sources: []`.

> Keep it shippable: the minimum viable version is **Webhook → AI Agent (Gemini + system prompt) → Respond**. The vector store / Tavily tool is the "RAG" upgrade — add it only after the minimum works.

## Verification
- [ ] `curl -X POST <webhook-url> -H "Content-Type: application/json" -d '{"job_title":"Data Scientist","message":"Do I need a master's?"}'` → returns `{answer, sources}`.
- [ ] Answer is relevant, short, and honest (no hallucinated certs).
- [ ] Response JSON matches the contract exactly (Agent 1's proxy depends on it).
- [ ] `N8N_WEBHOOK_URL` set in `.env`; Agent 1's `/api/chat` returns the same payload end-to-end.
- **Prove it:** paste the curl response before declaring done.

## README.md must cover
Run FastAPI (venv, deps, uvicorn) · set `.env` keys · import + activate the n8n flow · how to switch mock-mode · how to point the partner's Lovable frontend at `http://localhost:8000` · the 60-second demo script.

## Lessons
Append n8n gotchas (credential setup, webhook test vs production URL, AI Agent output parsing) to `app/tasks/lessons.md`.
