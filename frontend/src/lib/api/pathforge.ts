// PathForge AI — backend API client.
// Talks to the FastAPI backend (see VibeTHON PW/app). CORS is open server-side.
// Base URL is configurable via VITE_API_URL; defaults to local dev.

const API_BASE: string =
  ((import.meta as any).env?.VITE_API_URL as string) || "http://localhost:8000";

// ---- Types: typed mirror of the backend contract (spec/API_CONTRACT.md) ----
export interface ExpectedSalary { min: number; max: number; currency: string; note: string }
export interface Milestone {
  order: number; title: string; duration: string; description: string;
  skills: string[]; certifications: string[]; expected_salary: ExpectedSalary;
}
export interface Skill { name: string; level: string; why: string }
export interface Certification { name: string; provider: string; url: string; free: boolean }
export interface Company { name: string; role: string; location: string; url: string; source: string }
export interface Course { title: string; provider: string; url: string; free: boolean }
export interface YouTubeRec { channel: string; title: string; url: string; why: string }
export interface SalaryRange { min: number; max: number }
export interface SalaryOverview {
  entry: SalaryRange; mid: SalaryRange; senior: SalaryRange; currency: string; sources: string[];
}
export interface Roadmap {
  job_title: string; summary: string; background_required: string;
  milestones: Milestone[]; skills: Skill[]; certifications: Certification[];
  companies_hiring: Company[]; recommended_courses: Course[]; youtube: YouTubeRec[];
  salary_overview: SalaryOverview; generated_at: string; mock: boolean;
}
export interface ChatSource { title: string; url: string }
export interface ChatResponse { answer: string; sources: ChatSource[] }

/** POST /api/roadmap — the full career roadmap for a job title. */
export async function getRoadmap(jobTitle: string): Promise<Roadmap> {
  const res = await fetch(`${API_BASE}/api/roadmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_title: jobTitle }),
  });
  if (!res.ok) throw new Error(`roadmap request failed (${res.status})`);
  return res.json();
}

/** POST /api/chat — RAG career advisor (proxied to n8n). */
export async function sendChat(
  jobTitle: string,
  message: string,
  history: { role: string; content: string }[] = [],
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_title: jobTitle, message, history }),
  });
  if (!res.ok) throw new Error(`chat request failed (${res.status})`);
  return res.json();
}
