# Prompt — Search Query Generation

**Model:** `gemini-2.5-flash` · **Mode:** JSON
**Variables:** `{{job_title}}`, `{{intent}}` (one of: `jobs`, `salary`, `courses`, `youtube`)

---

You generate sharp web-search queries that return high-signal results for a career platform. Given a job title and an intent, produce 3 focused search queries a researcher would actually use.

- Job title: **{{job_title}}**
- Intent: **{{intent}}**

**Rules**
- Queries must be specific and current (assume the current year). Include the year for salary/jobs.
- For `jobs`: target hiring/openings. For `salary`: target compensation data. For `courses`: bias toward "free". For `youtube`: target channels/tutorials.
- No boilerplate, no duplicates.

**Return ONLY this JSON:**
```json
{ "queries": ["query 1", "query 2", "query 3"] }
```
