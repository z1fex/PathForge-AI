# CareerPath — Knowledge Base (`career_kb`)

General, role-agnostic career guidance the RAG chatbot is grounded in. It is **intentionally generic and honest** — no fabricated company names, salary figures, or links. Role-specific facts come from the `/api/roadmap` engine (Gemini + live job/salary/course data); this KB keeps the chatbot's *advice* consistent and trustworthy.

Two ways this content is used:
1. **Shipped (default):** the key points below are embedded in the AI Agent's **system prompt** (`prompts/rag_system_prompt.md` + the `systemMessage` in `careerpath_rag.json`). Robust, zero extra dependencies.
2. **Optional upgrade:** load this file into n8n's **Simple Vector Store (in-memory)** and attach it to the Agent as a retriever tool. See `SETUP.md` → "Optional: vector-store RAG".

---

## Roadmaps
- A career path runs in stages: **foundations → skill-building → portfolio projects → targeted job search → first role → growth.**
- Employers hire on **demonstrable ability**. A focused portfolio of 2–3 real projects usually beats an extra credential.
- Sequence learning: master fundamentals before tools, tools before frameworks, frameworks before niche specialisations.

## Degrees
- For most tech, data, design and creative roles a degree is **helpful but not mandatory** — a strong portfolio + relevant experience can substitute.
- Degrees matter more for **regulated, research, or academic** roles (medicine, law, some ML-research positions) and can help in very competitive markets or for visa/relocation.
- Be explicit with students when a degree is genuinely optional — don't gate-keep.

## Certifications
- Worth it when they are **recognised by employers in that field** or **force you to learn a concrete, testable skill**.
- Recommend only **real, well-known providers**: Coursera, edX, Google Career Certificates, AWS, Microsoft, freeCodeCamp, DataCamp, Udacity.
- A certificate rarely replaces demonstrated work — pair it with a project that uses the skill.

## Salaries
- Vary widely by **country, city, company size, industry, and experience** — always give ranges, never a single number presented as fact.
- Direct students to **live sources** for current, localised numbers: Levels.fyi, Glassdoor, Payscale, and the actual job postings.
- General shape: entry < mid < senior; remote/biotech/finance/big-tech tend to pay above local median.

## Job search
- Apply to **junior/associate/entry** titles first; tailor each application to the posting's keywords.
- Networking and referrals beat cold applications. A visible portfolio (GitHub, personal site, Behance/Dribbble) is a force multiplier.
- Track applications; expect a funnel — many applications → few interviews → offer.

## Switching careers
- Lead with **transferable skills** (communication, domain knowledge, project management) and reframe them for the target role.
- Build **2–3 portfolio projects** in the new field to prove the switch is real.
- Target roles that bridge old + new (e.g. analyst → data scientist within the same industry) before going fully greenfield.

## Honesty rules (the chatbot must follow)
- Never invent certifications, companies, salaries, or URLs.
- If unsure of a current fact, say so and tell the student exactly where to verify it.
- Stay encouraging but realistic — no hype, no false guarantees.
