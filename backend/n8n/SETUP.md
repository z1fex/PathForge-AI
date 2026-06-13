# n8n RAG Chatbot — Setup (`careerpath_rag.json`)

The CareerPath chatbot is an n8n workflow:

```
Webhook (POST /careerpath-chat)
  -> CareerPath Agent  (Tools Agent)
        - Google Gemini Chat Model  (gemini-2.5-flash, googlePalmApi credential)
        - Window Buffer Memory      (per job_title / sessionId, optional multi-turn)
  -> Format Response   (Set -> { answer, sources })
  -> Respond to Webhook  (returns the JSON object)
```

It returns **exactly** the contract shape:

```json
{ "answer": "…", "sources": [ { "title": "…", "url": "…" } ] }
```

`sources` is `[]` in the shipped version (the agent is grounded in an embedded knowledge base, not a live retriever). See **Optional: live retrieval / sources** at the bottom.

---

## Option A — UI import (recommended for the demo, ~2 min)

1. **Start n8n** (it's installed globally):
   ```bash
   n8n start
   ```
   Open the editor at <http://localhost:5678>. (First run asks you to create an owner account — any email/password; local only.)

2. **Import the workflow:** top-right menu **⋮ → Import from File** → select `app/n8n/careerpath_rag.json`.

3. **Add the Gemini credential:** open the **Google Gemini Chat Model** node → *Credential to connect with* → **Create New** → type **Google Gemini(PaLM) API** → paste your `GEMINI_API_KEY` (from `app/.env`) into **API Key** (leave Host as the default `https://generativelanguage.googleapis.com`) → **Save**. Select that credential on the node.

4. **Activate:** toggle the workflow **Active** (top-right). The production webhook is now live at:
   ```
   http://localhost:5678/webhook/careerpath-chat
   ```

5. **Test:**
   ```bash
   curl -X POST http://localhost:5678/webhook/careerpath-chat \
     -H "Content-Type: application/json" \
     -d '{"job_title":"Data Scientist","message":"Do I need a master'\''s degree?"}'
   ```
   Expect `{"answer":"…","sources":[]}`.

> **Test vs production URL:** the `…/webhook-test/careerpath-chat` URL only works right after you click **"Listen for test event"** in the editor and fires once. The durable URL is `…/webhook/careerpath-chat` and requires the workflow to be **Active**.

---

## Option B — fully headless (no UI; how this was built & verified)

n8n's CLI imports and activates without ever opening the browser. **Use an isolated home folder so your existing `~/.n8n` workflows are never touched/activated.**

```bash
# isolated instance (does NOT touch your real ~/.n8n)
export N8N_USER_FOLDER="$PWD/.n8n-agent4-test"   # any throwaway dir
export N8N_PORT=5678

# 1) credential file (decrypted JSON; deleted after import)
cat > gemini_cred.json <<'JSON'
[{ "id":"careerpath-gemini-cred", "name":"CareerPath Gemini", "type":"googlePalmApi",
   "data": { "host":"https://generativelanguage.googleapis.com", "apiKey":"<GEMINI_API_KEY>" } }]
JSON

# 2) import + activate
n8n import:credentials --input=gemini_cred.json
n8n import:workflow     --input=app/n8n/careerpath_rag.json
n8n publish:workflow    --id=careerpath-rag-001     # activates it
rm gemini_cred.json                                  # don't leave the key on disk

# 3) serve + test
n8n start &                                          # serves the active webhook
curl -X POST http://localhost:$N8N_PORT/webhook/careerpath-chat \
  -H "Content-Type: application/json" \
  -d '{"job_title":"Data Scientist","message":"Do I need a master'\''s?"}'
```

Notes:
- `import:workflow` keeps the JSON `id` (`careerpath-rag-001`) and the credential auto-links by matching `id`+`name`.
- `publish:workflow` is what marks it active (the old `update:workflow --active` is deprecated).
- On Windows PowerShell use `$env:N8N_USER_FOLDER = "…"` etc. instead of `export`.
- To stop the isolated instance and free port 5678: find the listener (`netstat -ano | findstr :5678`) and `taskkill /PID <pid> /F /T`.

---

## Wiring it to the backend

Set in `app/.env`:
```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/careerpath-chat
```
Agent 1's `POST /api/chat` proxies the request body straight to this URL and returns the JSON unchanged. If `N8N_WEBHOOK_URL` is empty or n8n is down, `/api/chat` returns a friendly stub so the frontend never breaks.

---

## Optional: live retrieval / populated `sources` (the "RAG upgrade")

The shipped flow grounds answers in an embedded knowledge base (`career_kb.md`) and returns `sources: []`. Two ways to add live retrieval:

- **Vector store (in-memory):** add an **Embeddings Google Gemini** + **Simple Vector Store** (retrieve-as-tool) loaded from `career_kb.md`, attached to the Agent as a tool. Note: the in-memory store is empty on a fresh process until a one-time "insert" run populates it.
- **Tavily web search:** attach an **HTTP Request Tool** (`POST https://api.tavily.com/search`, key in `Authorization: Bearer` header, `{query}` placeholder) so the agent fetches current facts and cites URLs.

> ⚠️ **Known issue on n8n 2.19.5:** invoking the **HTTP Request Tool** from the Agent throws `"toolHttpRequest has a supplyData method but no execute method"` (an n8n executor bug, not a config error). Until it's fixed upstream, prefer doing Tavily retrieval as a **regular HTTP Request node in the main flow** (before the Agent) and build `sources` deterministically from the results in the **Format Response** node — that avoids the tool path entirely.
