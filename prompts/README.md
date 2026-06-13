# 🧠 CareerPath — Prompt Library

These are the prompts that power CareerPath. They are **loaded from disk at runtime** (`app/prompts.py`), never inlined in code — so they can be reviewed, versioned, and improved independently of the application logic.

## Our prompt-engineering principles
1. **Role + goal up top.** Every prompt states who the model is and the single outcome we want.
2. **Structured output, enforced.** All data prompts demand strict JSON and run under Gemini **JSON mode** (`response_mime_type: application/json`) so the API never breaks on prose.
3. **Grounding over guessing.** Where facts matter (salary, jobs), we inject real web snippets and instruct the model to use them and cite sources — and to say "estimate" when it must guess.
4. **Anti-hallucination guardrails.** Explicit "do not invent URLs / certifications / numbers" instructions; prefer free, real, well-known resources.
5. **Tight + bounded.** Caps on list lengths and word counts keep responses fast, cheap, and UI-friendly.
6. **Few-shot only where it pays.** We show the exact output shape rather than long examples, to save tokens.

## Index
| File | Used by | Purpose |
|---|---|---|
| [roadmap_generation.md](roadmap_generation.md) | Agent 1 | Turn a job title into milestones, skills, certs, background |
| [salary_synthesis.md](salary_synthesis.md) | Agent 2 | Synthesize entry/mid/senior salary from web snippets |
| [courses_youtube_curation.md](courses_youtube_curation.md) | Agent 3 | Clean + label course/YouTube results |
| [rag_system_prompt.md](rag_system_prompt.md) | Agent 4 (n8n) | System prompt for the RAG career chatbot |
| [query_generation.md](query_generation.md) | Agents 2 & 3 | Turn a job title into sharp web-search queries |

> **Variables** are written as `{{like_this}}` and substituted before the call.
