# 🧭 PathForge AI

**Type any job title → get a complete, visual career roadmap.**
Skills, certifications, who's hiring, salary expectations, free courses & YouTube channels — plus an AI advisor you can chat with.

Built at **VibeThon 2026**.

🔗 **Live demo:** https://pathforge-ai-studio.vercel.app

---

## ✨ What it does (in plain words)

You tell PathForge the job you want — e.g. *"Data Scientist"* — and it instantly builds:

| | Feature | What you get |
|---|---|---|
| 🗺️ | **Visual roadmap** | The stages from beginner → hired, each with how long it takes and what to learn |
| 🛠️ | **Skills needed** | The exact skills employers look for |
| 🏅 | **Certifications** | Real certs worth getting, with links |
| 💰 | **Salary expectations** | Entry, mid, and senior pay ranges |
| 🏢 | **Who's hiring** | Companies with open roles for that job right now |
| 📺 | **Learn from the best** | Free courses + top YouTube channels |
| 🤖 | **AI advisor** | Chat and ask anything (*"Do I need a degree?"*) and get an honest, grounded answer |

Everything is generated **live** from the web + AI — nothing is hard-coded.

---

## 🧠 How it works (simple version)

```
You (browser)
  → Frontend  (React website, hosted on Vercel)
      → Backend API  (FastAPI / Python)
          → Google Gemini      → writes the roadmap, skills, salaries
          → Tavily + Firecrawl → search the live web for courses & YouTube
          → Remotive + Arbeitnow (free job boards) → who's hiring
      → AI Advisor → n8n workflow → Gemini → answers your questions
```

The frontend asks the backend one question (*"give me a roadmap for X"*). The backend talks to several free services at the same time, blends the results, and sends back one tidy package the website draws on screen.

---

## 🗂️ What's in this repo

| Folder | What it is |
|---|---|
| `frontend/` | The website users see (React + TanStack Start + Tailwind + shadcn/ui) |
| `backend/` | The brain (FastAPI). Turns a job title into the full roadmap. Includes `backend/n8n/` — the chatbot workflow |
| `prompts/` | **Every AI prompt we wrote, documented.** (Judges: this is our prompt engineering) |
| `agent-specs/` | Our build plan — we split the work across 4 AI coding agents; these are their briefs + the shared API contract |
| `lovable-prompts/` | The prompts my teammate used to build the frontend in Lovable |

---

## 🚀 Run it yourself (local)

### 1) Backend — Python 3.10+
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then fill in your free keys (see below)
uvicorn main:app --port 8000
```
Check it: open **http://localhost:8000/api/health** → you should see `{"status":"ok"}`.

> No keys yet? Set `MOCK=1` in `.env` and the backend serves realistic **sample data offline** — great for a quick look.

### 2) Frontend — Node 18+
```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_URL=http://localhost:8000
npm run dev
```
Open the URL it prints (usually **http://localhost:5173**), type a job title, and hit **Forge My Path 🚀**.

---

## 🔑 Free API keys (all have free tiers)

Put these in `backend/.env` (copy from `backend/.env.example`):

| Key | Where to get it (free) | Used for |
|---|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey | Roadmap, salaries, chat (model: `gemini-2.5-flash`) |
| `TAVILY_API_KEY` | https://tavily.com | Web search for courses, YouTube, salary sources |
| `FIRECRAWL_API_KEY` | https://firecrawl.dev | Web scraping fallback |
| `N8N_WEBHOOK_URL` | your n8n (import `backend/n8n/careerpath_rag.json`) | The AI advisor chatbot |

Companies-hiring uses **Remotive** and **Arbeitnow**, which need **no key**.

---

## 🛟 Built to not break

- If any data source is slow or down, that section **degrades gracefully** — the app never crashes.
- **Two Gemini keys** with automatic failover when one hits its rate limit.
- **Mock mode** (`MOCK=1`) for a guaranteed offline demo.

---

## 🧩 Tech stack

**Frontend:** React 19 · TanStack Start · Tailwind · shadcn/ui · deployed on Vercel
**Backend:** FastAPI (Python) · Google Gemini 2.5 Flash · Tavily · Firecrawl · Remotive + Arbeitnow
**Chatbot:** n8n (Webhook → AI Agent → Gemini)

---

## 👥 Team

Built at **VibeThon 2026**.
- Backend, integration & deployment
- Frontend (built with Lovable)

---

## 📄 License

**Proprietary — All Rights Reserved.** See [LICENSE](LICENSE).
This project may be **viewed for evaluation/judging only**. No copying, modification, distribution, or use of any part (code, prompts, or design) is permitted without the Authors' prior written permission.

*Made with way too much coffee. ☕*
