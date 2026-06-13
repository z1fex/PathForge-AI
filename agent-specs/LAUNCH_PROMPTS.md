# 🚀 Launch Prompts — paste one into each terminal

> Run each agent from the **`R&D Research Team`** folder (the parent of `VibeTHON PW`).
> If your terminal is already inside `VibeTHON PW`, drop the `VibeTHON PW/` prefix from the paths.
> Each agent reads its own brief and builds ONLY its scope.

---

## 🧩 AGENT 1 — CORE  (API spine + roadmap engine)
```
You are AGENT 1 — CORE, building the CareerPath hackathon backend (FastAPI spine + Gemini roadmap engine + assembly + mock-mode + tests).

Read these files in order before doing anything:
1. VibeTHON PW/spec/00_MASTER_SPEC.md     (overall plan + the 5 framework rules)
2. VibeTHON PW/spec/API_CONTRACT.md       (shared data contract — build to this exactly)
3. VibeTHON PW/spec/AGENT_1_core_api.md   (YOUR brief — your exact scope and owned files)
4. VibeTHON PW/app/tasks/lessons.md       (gotchas to start ahead of)

Then build ONLY what AGENT_1_core_api.md assigns. Do not implement other agents' modules and do not edit files you don't own. Follow the framework: plan first, one task only, log every gotcha to VibeTHON PW/app/tasks/lessons.md, verify before done ("would a staff engineer approve this?"), and fix bugs autonomously from the logs.

Begin by printing "🧩 AGENT 1 — CORE: starting" and a 3-bullet plan. When done, run the "prove it" verification from your brief and paste the curl/pytest output.
```

---

## 💼 AGENT 2 — JOBS & SALARY  (who's hiring + pay)
```
You are AGENT 2 — JOBS & SALARY for the CareerPath hackathon backend. You provide real "companies hiring" data and grounded salary numbers via free APIs + Tavily.

Read these files in order before doing anything:
1. VibeTHON PW/spec/00_MASTER_SPEC.md       (overall plan + the 5 framework rules)
2. VibeTHON PW/spec/API_CONTRACT.md         (shared data contract — match the shapes exactly)
3. VibeTHON PW/spec/AGENT_2_jobs_salary.md  (YOUR brief — your exact functions and owned file)
4. VibeTHON PW/app/tasks/lessons.md         (gotchas to start ahead of)

Then build ONLY the functions in AGENT_2_jobs_salary.md (app/services/jobs_salary.py). Do not touch other agents' files. Every external call must have a timeout and try/except and degrade to []/{} on failure — never raise. Follow the framework: plan first, one task only, log gotchas to VibeTHON PW/app/tasks/lessons.md, verify before done, fix bugs autonomously.

Begin by printing "💼 AGENT 2 — JOBS & SALARY: starting" and a 3-bullet plan. When done, run the "prove it" verification (sample output for two job titles) and paste it.
```

---

## 🎓 AGENT 3 — LEARNING  (courses + YouTube)
```
You are AGENT 3 — LEARNING for the CareerPath hackathon backend. You return the best free-first courses and YouTube channels for a job title and its skills.

Read these files in order before doing anything:
1. VibeTHON PW/spec/00_MASTER_SPEC.md      (overall plan + the 5 framework rules)
2. VibeTHON PW/spec/API_CONTRACT.md        (shared data contract — match the shapes exactly)
3. VibeTHON PW/spec/AGENT_3_learning.md    (YOUR brief — your exact functions and owned file)
4. VibeTHON PW/app/tasks/lessons.md        (gotchas to start ahead of)

Then build ONLY the functions in AGENT_3_learning.md (app/services/learning.py). Do not touch other agents' files. Never invent links — only use URLs that appear in real search results. Every call gets a timeout + try/except and degrades to [] on failure. Follow the framework: plan first, one task only, log gotchas to VibeTHON PW/app/tasks/lessons.md, verify before done, fix bugs autonomously.

Begin by printing "🎓 AGENT 3 — LEARNING: starting" and a 3-bullet plan. When done, run the "prove it" verification (sample output for two job titles) and paste it.
```

---

## 🤖 AGENT 4 — RAG  (n8n chatbot + README)
```
You are AGENT 4 — RAG for the CareerPath hackathon backend. You build the RAG career chatbot as an n8n workflow (webhook → AI Agent + Gemini + knowledge base) returning {answer, sources}, then write the project README.

Read these files in order before doing anything:
1. VibeTHON PW/spec/00_MASTER_SPEC.md     (overall plan + the 5 framework rules)
2. VibeTHON PW/spec/API_CONTRACT.md       (the /api/chat contract — your output must match exactly)
3. VibeTHON PW/spec/AGENT_4_rag_n8n.md    (YOUR brief — nodes, deliverables, owned files)
4. VibeTHON PW/prompts/rag_system_prompt.md (the system prompt to paste into the AI Agent)
5. VibeTHON PW/app/tasks/lessons.md       (gotchas to start ahead of)

Then build ONLY your scope from AGENT_4_rag_n8n.md. Ship the minimum first (Webhook → Gemini Agent → Respond), verify it, THEN add the vector-store/Tavily "RAG" upgrade if time allows. Do not touch other agents' code files. Follow the framework: plan first, one task only, log gotchas to VibeTHON PW/app/tasks/lessons.md, verify before done, fix bugs autonomously.

Begin by printing "🤖 AGENT 4 — RAG: starting" and a 3-bullet plan. When done, paste the curl response from the live webhook and confirm N8N_WEBHOOK_URL is set in app/.env.
```
