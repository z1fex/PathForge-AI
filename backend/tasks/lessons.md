# lessons.md — compounding rules (read at session start)

> Every correction or gotcha becomes ONE line here. 100 lines beats 800. Keep it terse.

## Seeded from the research/setup phase
- Firecrawl & Tavily **MCP servers 401 on a stale boot key** — call the REST APIs directly instead (PowerShell `Invoke-RestMethod`, `Authorization: Bearer <key>`). Keys are valid.
- Tavily REST: `POST https://api.tavily.com/search`, body `{query,max_results,search_depth}`; results in `.results[]` (`title,url,content`).
- Firecrawl REST: `POST https://api.firecrawl.dev/v1/search`, body `{query,limit}`; results in `.data[]` (`title,url,description`).
- Gemini structured output: set `generation_config={"response_mime_type":"application/json"}` — far more reliable than asking for JSON in prose.
- **Never let a sub-module crash the API** — wrap every external call in try/except + timeout, return `[]`/`{}` on failure.
- Free job APIs need **no key**: Remotive `remotive.com/api/remote-jobs?search=`, Arbeitnow `arbeitnow.com/api/job-board-api`.
- **Gemini: use `gemini-2.5-flash` (or `-lite`), NOT `gemini-2.0-flash`** — 2.0 returns 429 `limit:0` (no free quota on this account). Read model from `GEMINI_MODEL` env. Auth = `?key=<KEY>` query param or `x-goog-api-key` header (NOT Bearer). Endpoint `https://generativelanguage.googleapis.com/v1beta/models/<model>:generateContent`.

## Build-phase lessons (append below as you go)
- [A3] Tavily REST `/search`: send key BOTH as body `api_key` and `Authorization: Bearer` header — covers old/new tiers; results in `.results[]` (`title,url,content`).
- [A3] Courses `include_domains` includes `youtube.com`, so you can't tell course-vs-YT calls apart by "youtube.com in domains" — key the YT path on the exact list `["youtube.com"]`.
- [A3] YouTube channel name is NOT in Tavily results: derive from URL (`/@handle`, `/c/`, `/user/`); `/channel/UC…` and `/watch?v=` have no name → fall back to the title's lead segment.
- [A3] `free` mapping: freeCodeCamp/YouTube/Kaggle/edX-audit/Khan/MDN/docs = true; Coursera/Udemy/Udacity/DataCamp/etc default false (paid). Unknown domain → free=false.
- [A3] Dedupe courses+YT by NORMALISED url (lowercase host, drop fragment + trailing slash) — Tavily repeats the same link across multiple skill queries.
- [A3] Gemini cleanup is opt-in (`LEARNING_USE_GEMINI=1`) — off by default to keep the path fast/deterministic and not burn shared free-tier quota on every roadmap call; when on, it only keeps URLs already in real results (never invents links).
- [A3] Real result titles contain emoji (freeCodeCamp "Learn Python 🐍"); Windows console is cp1252 and `print()` crashes (UnicodeEncodeError) — `sys.stdout.reconfigure(encoding="utf-8")` in any `__main__`/CLI. Data itself is fine (JSON over HTTP is UTF-8).
- [A3] Tavily YT default-mode quirks: returns Shorts + "top N channels" listicle videos + occasional junk snippets ("This content isn't available."). Mitigate: deprioritize `/shorts/` (stable sort) + junk-snippet→fallback `why`. Real fix = set `YOUTUBE_API_KEY` for `search.list?type=channel`.
- [A2] **Remotive `?search=` is IGNORED** — returns the generic recent feed regardless of query (identical jobs for "Data Scientist" vs "UX Designer"). Filter results client-side by job-title tokens; never trust the API's search.
- [A2] Arbeitnow returns ONE ~100-job page (EU/Berlin-heavy). Token-filter titles; a given role can get 0 matches → the web fallback must cover it.
- [A2] Tavily job fallback: an `include_domains` allow-list floods with near-identical aggregator pages from one board (8× Indeed city pages → dedupe to 1). Use an UNRESTRICTED search, skip reddit/youtube/quora, dedupe by company/board label → variety + ≥3 rows.
- [A2] Gemini `gemini-2.5-flash` frequently exceeds an 8s read timeout on salary JSON synthesis; `-lite` answers in time. Keep `GEMINI_MODEL_FALLBACK` wired — it's load-bearing, not optional.
- [A2] Gemini REST JSON mode field is `generationConfig.responseMimeType` (camelCase), NOT the SDK's `response_mime_type`. Auth via `?key=` query param.
- [A2] Short title tokens (`ux`,`ui`,`qa`) need whole-word regex matching, else they false-match inside longer words (luxury, equality).
- [A2] OS env may already hold the keys — a `_load_env()` that early-returns when keys exist will skip loading `GEMINI_MODEL`. Read the .env once and fill every *missing* key (env still wins over file).
- [A1] Provided Gemini key is the `AQ.*` format — auth via `x-goog-api-key` header on REST (verified 200). roadmap.py calls the REST endpoint with httpx (not the SDK) for Py3.14 robustness + clean auth with this key shape.
- [A1] gemini-2.5-flash burns hidden **thinking tokens** — set `maxOutputTokens` generous (8192) or JSON truncates to empty `parts`; treat empty text (finishReason MAX_TOKENS) as failure → retry on `GEMINI_MODEL_FALLBACK`.
- [A1] Bound EVERY sub-module call with `ThreadPoolExecutor.submit(...).result(timeout=12)`; Agent-2's salary Gemini call degrades to `{}` rather than hanging `/api/roadmap`. Mock-mode AND engine-hard-fail both serve `mock_data` (mock=true) so the demo never dies.
- [A1] main.py imports sub-fns by name (`from services.jobs_salary import get_...`) → in tests monkeypatch `main.get_...` (the bound ref), NOT `services.x.get_...`. Isolate assembly tests by patching ALL 5 sub-calls — once a teammate's real module lands it makes live/slow Gemini calls and breaks "assume empty" assertions.
- [A4] n8n is installed globally (`n8n` v2.19.5) — build webhook flows fully headless, no UI: `import:credentials` → `import:workflow` → `publish:workflow --id=<id>` → `n8n start`. `import:workflow` keeps the JSON `id`; `publish:workflow` is what ACTIVATES (old `update:workflow --active` is deprecated).
- [A4] **NEVER `n8n start` the user's real `~/.n8n`** (huge actively-used DB → would activate THEIR workflows / fire automations). Use a throwaway instance: `N8N_USER_FOLDER=<temp>` + `N8N_PORT=...`. Their data stays untouched.
- [A4] n8n Gemini credential type = `googlePalmApi`, data `{host, apiKey}` (raw key, NOT Bearer). Chat node `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` v1.1 wants `modelName:"models/gemini-2.5-flash"` (keep the `models/` prefix). Reference the imported credential by the same `id`+`name` in the node so they auto-link on import.
- [A4] Working node set for 2.19: webhook `n8n-nodes-base.webhook` v2.1 (`responseMode:"responseNode"`, body under `$json.body.*`), agent `@n8n/n8n-nodes-langchain.agent` v3.1 (`promptType:"define"`, `text`, `options.systemMessage`), set v3.4, respond `respondToWebhook` v1.1 `respondWith:"firstIncomingItem"` → emits the item as a JSON object = the `{answer,sources}` contract.
- [A4] **GOTCHA: HTTP Request Tool is broken as an agent tool in 2.19.5** — when the agent actually calls `@n8n/n8n-nodes-langchain.toolHttpRequest` it throws `"...has a supplyData method but no execute method"` (from `n8n-core/.../workflow-execute.js`). No-tool agent works fine; only live tool-calling trips it. Ground via the system prompt (embedded KB) and document the Tavily tool as an optional upgrade instead of fighting it.
- [A4] n8n webhook URLs: `/webhook-test/<path>` only fires after clicking Listen in the UI (one-shot); the durable one is `/webhook/<path>` and needs the workflow ACTIVE/published. Put the `/webhook/` form in `.env`.
- [QA-INTEGRATION] **Contract mismatch killed the whole roadmap:** main.py did `milestones = get_milestone_salaries(...)`, but that fn returns salary-only dicts `{order,min,max,currency,note}` (no title/duration/description) → every milestone failed `Milestone` validation and got dropped → empty roadmap. FIX: MERGE the bands into each milestone's `expected_salary`; never reassign `milestones`. Lesson: when one module "enriches" another's data, MERGE by key, don't REPLACE the list.
- [QA-INTEGRATION] `/api/roadmap` sub-calls ran SEQUENTIALLY (~40s) despite a "concurrent" comment, and `get_courses` (≈5 Tavily calls) blew the per-call 12s `_safe` timeout → courses came back []. FIX: `_executor.submit(...)` ALL five first, then `_gather(future, default, timeout=20-25)` → 29.8s and courses populated. Submit-then-gather ≠ submit-and-block-immediately.
