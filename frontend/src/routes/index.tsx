import { createFileRoute } from "@tanstack/react-router";
import { useRef, useState } from "react";
import { PillButton } from "@/components/PillButton";
import { WaveDivider } from "@/components/WaveDivider";
import { Reveal } from "@/components/Reveal";
import { FloatingChatbot } from "@/components/FloatingChatbot";
import { FaqAccordion } from "@/components/FaqAccordion";
import { SiteFooter } from "@/components/SiteFooter";
import { SalaryBars } from "@/components/SalaryBars";
import { getRoadmap, type Roadmap, type SalaryOverview } from "@/lib/api/pathforge";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "PathForge AI — Your Dream Job Is One Roadmap Away" },
      {
        name: "description",
        content:
          "Get a personalized visual roadmap, certifications, salary insights, and top companies hiring for any job title.",
      },
      { property: "og:title", content: "PathForge AI" },
      {
        property: "og:description",
        content: "Personalized visual career roadmaps powered by AI.",
      },
    ],
  }),
  component: Index,
});

type MNode = {
  n: number; label: string; time: string; skill: string; color: string;
  salaryMin?: number; salaryMax?: number;
};

const PALETTE = ["var(--pink)", "var(--mint)", "var(--sky)", "var(--lavender)", "var(--periwinkle)", "var(--yellow)"];

// ---- Sample data (shown until the first search; keeps the page beautiful when idle) ----
const SAMPLE_MILESTONES: MNode[] = [
  { n: 1, label: "CS Fundamentals", time: "1–2 months", skill: "Algorithms, OS basics", color: "var(--pink)" },
  { n: 2, label: "Python & DSA", time: "2 months", skill: "Python, Data Structures", color: "var(--mint)" },
  { n: 3, label: "Statistics & ML", time: "2–3 months", skill: "Probability, scikit-learn", color: "var(--sky)" },
  { n: 4, label: "Deep Learning", time: "2 months", skill: "PyTorch, Neural Nets", color: "var(--lavender)" },
  { n: 5, label: "ML Projects", time: "1–2 months", skill: "End-to-end portfolio", color: "var(--periwinkle)" },
  { n: 6, label: "Interview Prep", time: "1 month", skill: "System design, MLOps", color: "var(--pink)" },
];
const SAMPLE_SKILLS = ["Python", "TensorFlow", "SQL", "Docker", "Git", "Cloud"];
// Turn a cert into an always-working link: real URL if we have one, else a Google search.
const certHref = (name: string, provider: string, url?: string) =>
  url && url.startsWith("http")
    ? url
    : `https://www.google.com/search?q=${encodeURIComponent(`${name} ${provider} certification`)}`;

const SAMPLE_CERTS = [
  { name: "TensorFlow Developer", issuer: "Google", time: "3 mo", url: certHref("TensorFlow Developer", "Google") },
  { name: "AWS ML Specialty", issuer: "Amazon", time: "2 mo", url: certHref("AWS Certified Machine Learning Specialty", "Amazon") },
  { name: "Deep Learning Spec.", issuer: "Coursera", time: "4 mo", url: "https://www.coursera.org/specializations/deep-learning" },
  { name: "Azure AI Engineer", issuer: "Microsoft", time: "2 mo", url: "https://learn.microsoft.com/credentials/certifications/azure-ai-engineer/" },
];
const SAMPLE_BACKGROUND =
  "A solid grasp of math and programming will fast-track you. Don't have a CS degree? Self-taught works too — projects beat paper.";
const SAMPLE_COMPANIES = [
  { name: "Google", role: "ML Engineer II", location: "Mountain View, CA", url: "#", bg: "var(--sky)" },
  { name: "Meta", role: "AI Research Eng", location: "Menlo Park, CA", url: "#", bg: "var(--lavender)" },
  { name: "Amazon", role: "Applied Scientist", location: "Seattle, WA", url: "#", bg: "var(--yellow)" },
  { name: "Microsoft", role: "ML Engineer", location: "Redmond, WA", url: "#", bg: "var(--mint)" },
  { name: "OpenAI", role: "Research Engineer", location: "San Francisco, CA", url: "#", bg: "var(--cream)" },
  { name: "Apple", role: "ML Platform Eng", location: "Cupertino, CA", url: "#", bg: "var(--periwinkle)" },
];
const SAMPLE_ALSO = ["Netflix", "Stripe", "Airbnb", "Spotify", "Uber", "Nvidia"];
const SAMPLE_TIERS = [
  { tier: "Entry", range: "$75K – $110K", header: "var(--sky)", rot: "-2deg", note: "0–2 yrs experience" },
  { tier: "Mid", range: "$110K – $160K", header: "var(--yellow)", rot: "0deg", note: "3–5 yrs · most common", badge: true },
  { tier: "Senior", range: "$160K – $250K+", header: "var(--pink)", rot: "2deg", note: "6+ yrs · staff & lead" },
];
const SAMPLE_VIDEOS = [
  { channel: "StatQuest", title: "Statistics Fundamentals", url: "#", why: "Best ML stats intuition", thumb: "var(--yellow)" },
  { channel: "3Blue1Brown", title: "Neural Networks Visualized", url: "#", why: "Visual deep learning", thumb: "var(--sky)" },
  { channel: "Andrej Karpathy", title: "Neural Nets: Zero to Hero", url: "#", why: "Build NNs from scratch", thumb: "var(--pink)" },
  { channel: "CS50 Harvard", title: "Intro to Computer Science", url: "#", why: "CS foundations", thumb: "var(--mint)" },
  { channel: "fast.ai", title: "Practical Deep Learning", url: "#", why: "Hands-on projects", thumb: "var(--cream)" },
  { channel: "Andrew Ng", title: "ML Specialization", url: "#", why: "The classic ML course", thumb: "var(--periwinkle)" },
];

const k = (v: number) => `$${Math.round(v / 1000)}K`;

function Index() {
  const [query, setQuery] = useState("");
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const resultsRef = useRef<HTMLElement>(null);

  const runSearch = async () => {
    const jt = query.trim();
    if (!jt) return;
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getRoadmap(jt);
      setRoadmap(data);
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 120);
    } catch {
      setError("Couldn't reach the backend. Make sure it's running on http://localhost:8000.");
    } finally {
      setLoading(false);
    }
  };

  // ---- Derived display data: live when available, sample otherwise ----
  const jobLabel = roadmap?.job_title || "Machine Learning Engineer";

  const milestones: MNode[] =
    roadmap?.milestones?.length
      ? roadmap.milestones.map((m, i) => ({
          n: m.order || i + 1,
          label: m.title,
          time: m.duration,
          skill: (m.skills || []).slice(0, 3).join(", "),
          color: PALETTE[i % PALETTE.length],
          salaryMin: m.expected_salary?.min,
          salaryMax: m.expected_salary?.max,
        }))
      : SAMPLE_MILESTONES;

  const skills = roadmap?.skills?.length ? roadmap.skills.map((s) => s.name) : SAMPLE_SKILLS;

  const certs =
    roadmap?.certifications?.length
      ? roadmap.certifications.map((c) => ({
          name: c.name,
          issuer: c.provider || "",
          time: c.free ? "Free" : "",
          url: certHref(c.name, c.provider || "", c.url),
        }))
      : SAMPLE_CERTS;

  const background = roadmap?.background_required || SAMPLE_BACKGROUND;

  const companies =
    (roadmap?.companies_hiring?.length
      ? roadmap.companies_hiring.map((c, i) => ({
          name: c.name, role: c.role, location: c.location || "Remote", url: c.url || "#", bg: PALETTE[i % PALETTE.length],
        }))
      : SAMPLE_COMPANIES
    ).slice(0, 6);

  const alsoHiring =
    roadmap?.companies_hiring && roadmap.companies_hiring.length > 6
      ? roadmap.companies_hiring.slice(6, 12).map((c) => c.name)
      : roadmap
        ? []
        : SAMPLE_ALSO;

  const so: SalaryOverview | undefined = roadmap?.salary_overview;
  const salaryTiers =
    so && (so.entry?.max || so.mid?.max || so.senior?.max)
      ? [
          { tier: "Entry", range: `${k(so.entry.min)} – ${k(so.entry.max)}`, header: "var(--sky)", rot: "-2deg", note: "0–2 yrs experience", badge: false },
          { tier: "Mid", range: `${k(so.mid.min)} – ${k(so.mid.max)}`, header: "var(--yellow)", rot: "0deg", note: "most common", badge: true },
          { tier: "Senior", range: `${k(so.senior.min)} – ${k(so.senior.max)}+`, header: "var(--pink)", rot: "2deg", note: "6+ yrs · staff & lead", badge: false },
        ]
      : SAMPLE_TIERS;

  const videos =
    roadmap?.youtube?.length
      ? roadmap.youtube.map((y, i) => ({
          channel: y.channel || "YouTube",
          title: y.title || y.channel || "Watch",
          url: y.url || "#",
          why: y.why || "",
          thumb: PALETTE[i % PALETTE.length],
        }))
      : SAMPLE_VIDEOS;

  const courses = roadmap?.recommended_courses ?? [];

  return (
    <main className="min-h-screen">
      {/* SECTION 1 — HERO */}
      <section style={{ backgroundColor: "var(--lavender)" }} className="relative">
        {/* Navbar */}
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="font-display uppercase text-2xl text-ink">
            PathForge <span className="text-ink/70">AI</span>
          </div>
          <PillButton className="text-sm px-6 py-2.5" onClick={runSearch}>Get Started →</PillButton>
        </nav>

        <div className="mx-auto max-w-5xl px-6 pt-10 pb-28 text-center">
          <h1
            className="font-display uppercase text-ink leading-[0.95] mb-8"
            style={{ fontSize: "clamp(40px, 7.5vw, 72px)" }}
          >
            Your Dream Job<br />Is One Roadmap Away.
          </h1>
          <p className="font-sans text-lg md:text-xl max-w-2xl mx-auto mb-10 text-ink/80">
            Input your target job title and get a personalized visual roadmap,
            certifications, salary insights, and top companies hiring now.
          </p>

          {/* Search bar */}
          <form
            onSubmit={(e) => { e.preventDefault(); runSearch(); }}
            className="mx-auto flex max-w-2xl items-center gap-2 rounded-full border-[2.5px] border-ink bg-white p-2 shadow-[6px_8px_0_0_rgba(26,26,26,0.9)]"
          >
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Machine Learning Engineer..."
              className="flex-1 bg-transparent px-5 py-2 font-sans text-base text-ink placeholder:text-ink/50 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-full border-[2.5px] border-ink bg-yellow px-5 py-3 font-display uppercase text-sm text-ink transition-transform hover:scale-105 disabled:opacity-60"
            >
              {loading ? "Forging…" : "Forge My Path 🚀"}
            </button>
          </form>

          {error && (
            <p className="mt-4 inline-block rounded-full border-[2px] border-ink bg-white px-4 py-2 font-sans text-sm text-ink">
              ⚠️ {error}
            </p>
          )}
          {roadmap && (
            <p className="mt-4 font-display uppercase text-sm text-ink/70">
              Showing live roadmap for <span className="text-ink">{roadmap.job_title}</span>
              {roadmap.mock ? " (demo data)" : ""}
            </p>
          )}

          {/* Floating badges */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-4">
            {[
              { label: "🎯 Visual Milestones", bg: "var(--pink)", delay: "0s" },
              { label: "💰 Salary Insights", bg: "var(--mint)", delay: "0.6s" },
              { label: "🏢 Top Hiring Companies", bg: "var(--cream)", delay: "1.2s" },
            ].map((b) => (
              <span
                key={b.label}
                className="rounded-full border-[2px] border-ink px-5 py-2.5 font-display uppercase text-sm text-ink shadow-[3px_4px_0_0_rgba(26,26,26,0.9)] animate-bob"
                style={{ backgroundColor: b.bg, animationDelay: b.delay }}
              >
                {b.label}
              </span>
            ))}
          </div>
        </div>
      </section>

      <WaveDivider topColor="var(--lavender)" bottomColor="var(--sky)" />

      {/* SECTION 2 — HOW IT WORKS */}
      <section style={{ backgroundColor: "var(--sky)" }} className="px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <h2 className="section-heading text-center mb-16">How It Works</h2>
          <div className="grid gap-10 md:grid-cols-3">
            {[
              { icon: "🎯", title: "Tell Us Your Goal", body: "Type your dream job, we do the rest.", bg: "var(--cream)", rot: "-2deg" },
              { icon: "🗺️", title: "Get Your Roadmap", body: "AI generates milestones, skills, certs, prerequisites.", bg: "var(--pink)", rot: "0deg" },
              { icon: "🚀", title: "Land The Job", body: "See who's hiring, expected salary, and curated courses.", bg: "var(--yellow)", rot: "2deg" },
            ].map((c, i) => (
              <div
                key={c.title}
                className="border-[2.5px] border-ink rounded-2xl p-8 shadow-[6px_8px_0_0_rgba(26,26,26,0.9)] transition-transform hover:rotate-0 hover:scale-[1.03]"
                style={{ backgroundColor: c.bg, transform: `rotate(${c.rot})` }}
              >
                <div className="text-5xl mb-4">{c.icon}</div>
                <div className="font-display uppercase text-xs tracking-widest text-ink/60 mb-2">
                  Step {i + 1}
                </div>
                <h3 className="font-display uppercase text-2xl mb-3 leading-tight">{c.title}</h3>
                <p className="text-ink/80">{c.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <WaveDivider topColor="var(--sky)" bottomColor="var(--yellow)" />

      {/* SECTION 3 — VISUAL ROADMAP */}
      <section ref={resultsRef} style={{ backgroundColor: "var(--yellow)" }} className="px-6 py-24">
        <div className="mx-auto max-w-7xl">
          <h2 className="section-heading text-center mb-4">Your Visual Roadmap</h2>
          <p className="text-center font-sans text-lg text-ink/70 mb-14">
            {roadmap ? "Your path for" : "Sample path for"}{" "}
            <span className="font-display uppercase">{jobLabel}</span>
          </p>

          {roadmap?.summary && (
            <p className="mx-auto max-w-3xl text-center font-sans text-base text-ink/80 mb-12 -mt-6">
              {roadmap.summary}
            </p>
          )}

          {/* Timeline */}
          <div className="overflow-visible pb-6 pt-6">
            <div className="flex items-start gap-0 px-2 flex-wrap md:flex-nowrap justify-center">
              {milestones.map((m, idx) => (
                <div key={`${m.n}-${m.label}`} className="flex items-start flex-1 min-w-[140px]">
                  <MilestoneNode m={m} />

                  {/* Dashed connector */}
                  {idx < milestones.length - 1 && (
                    <div
                      className="mt-10 flex-shrink-0 hidden md:block"
                      style={{ width: 40, borderTop: "4px dashed var(--ink)" }}
                      aria-hidden="true"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="mt-16 text-center">
            <PillButton onClick={runSearch}>
              {loading ? "Forging…" : "Generate My Roadmap →"}
            </PillButton>
          </div>
        </div>
      </section>

      <WaveDivider topColor="var(--yellow)" bottomColor="var(--cream)" />

      {/* SECTION 4 — WHAT YOU'LL NEED */}
      <section style={{ backgroundColor: "var(--cream)" }} className="px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <h2 className="section-heading text-center mb-16">What You'll Need</h2>
          <div className="grid gap-10 md:grid-cols-3">
            {/* Skills */}
            <PolaroidCard rotation="-2deg" headerBg="var(--lavender)" headerLabel="🛠️ Skills Needed">
              <div className="flex flex-wrap gap-2">
                {skills.map((s) => (
                  <span
                    key={s}
                    className="rounded-full border-[2px] border-ink bg-white px-3 py-1.5 font-display uppercase text-xs text-ink"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </PolaroidCard>

            {/* Certifications */}
            <PolaroidCard rotation="1deg" headerBg="var(--sky)" headerLabel="🏅 Certifications">
              {certs.length ? (
                <ol className="space-y-3">
                  {certs.map((c, i) => (
                    <li key={`${c.name}-${i}`} className="border-b border-ink/15 pb-2 last:border-0">
                      <div className="flex items-baseline gap-2">
                        <span className="font-display text-ink/60 text-sm">{i + 1}.</span>
                        <div className="flex-1">
                          <div className="font-display uppercase text-sm text-ink leading-tight">{c.name}</div>
                          <div className="text-xs text-ink/70">{[c.issuer, c.time].filter(Boolean).join(" · ")}</div>
                        </div>
                      </div>
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noreferrer"
                        className="ml-6 mt-1 inline-block font-display uppercase text-[11px] text-ink underline"
                      >
                        View Cert →
                      </a>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="text-sm text-ink/70">No specific certifications required — focus on projects.</p>
              )}
            </PolaroidCard>

            {/* Background */}
            <PolaroidCard rotation="-1deg" headerBg="var(--pink)" headerLabel="📚 Background Needed">
              <p className="text-sm text-ink/80 mb-4">{background}</p>
              {!roadmap && (
                <div className="flex flex-wrap gap-2">
                  {["Linear Algebra", "Calculus", "Stats 101"].map((s) => (
                    <span
                      key={s}
                      className="rounded-full border-[2px] border-ink bg-yellow px-3 py-1.5 font-display uppercase text-xs text-ink"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </PolaroidCard>
          </div>
        </div>
      </section>

      <WaveDivider topColor="var(--cream)" bottomColor="var(--pink)" />

      {/* SECTION 5 — WHO'S HIRING */}
      <HiringSection companies={companies} alsoHiring={alsoHiring} />

      <WaveDivider topColor="var(--pink)" bottomColor="var(--mint)" />

      {/* SECTION 6 — SALARY EXPECTATIONS */}
      <section style={{ backgroundColor: "var(--mint)" }} className="px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <h2 className="section-heading text-center mb-16">What To Expect 💰</h2>

          <div className="grid gap-10 md:grid-cols-3 mb-20">
            {salaryTiers.map((t) => (
              <div
                key={t.tier}
                className="border-[2.5px] border-ink rounded-2xl bg-white shadow-[6px_8px_0_0_rgba(26,26,26,0.9)] overflow-hidden"
                style={{ transform: `rotate(${t.rot})` }}
              >
                <div
                  className="flex items-center justify-between px-6 py-4 border-b-[2.5px] border-ink font-display uppercase text-xl text-ink"
                  style={{ backgroundColor: t.header }}
                >
                  {t.tier}
                  {t.badge && (
                    <span className="rounded-full bg-ink px-[10px] py-[3px] font-sans text-[11px] font-bold text-white">
                      MOST COMMON
                    </span>
                  )}
                </div>
                <div className="p-6 text-center">
                  <div className="font-display text-3xl text-ink mb-2">{t.range}</div>
                  <div className="text-sm text-ink/70">{t.note}</div>
                </div>
              </div>
            ))}
          </div>

          <SalaryBars overview={so} />
        </div>
      </section>

      <WaveDivider topColor="var(--mint)" bottomColor="var(--lavender)" />

      {/* SECTION 7 — LEARN FROM THE BEST */}
      <section style={{ backgroundColor: "var(--lavender)" }} className="px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <h2 className="section-heading text-center mb-16">Learn From The Best 📺</h2>
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {videos.map((c, i) => (
              <a
                key={`${c.title}-${i}`}
                href={c.url || "#"}
                target={c.url && c.url !== "#" ? "_blank" : undefined}
                rel="noreferrer"
                className="block border-[2.5px] border-ink rounded-2xl bg-white p-4 shadow-[6px_8px_0_0_rgba(26,26,26,0.9)] transition-transform hover:rotate-0 hover:-translate-y-1"
                style={{ transform: `rotate(${i % 2 === 0 ? "-1.5deg" : "1.5deg"})` }}
              >
                <div
                  className="relative flex items-center justify-center rounded-xl border-[2.5px] border-ink mb-4"
                  style={{ backgroundColor: c.thumb, aspectRatio: "16 / 9" }}
                >
                  <div className="flex h-14 w-14 items-center justify-center rounded-full border-[2.5px] border-ink bg-white text-2xl shadow-[2px_3px_0_0_rgba(26,26,26,0.9)]">
                    ▶️
                  </div>
                </div>
                <div className="font-display uppercase text-xs text-ink/60 mb-1">{c.channel}</div>
                <h3 className="font-display uppercase text-lg text-ink mb-3 leading-tight">{c.title}</h3>
                {c.why && <p className="text-xs text-ink/70 mb-3">{c.why}</p>}
                <span className="inline-block rounded-full border-[2px] border-ink bg-yellow px-4 py-1.5 font-display uppercase text-xs text-ink">
                  Watch Now →
                </span>
              </a>
            ))}
          </div>

          {courses.length > 0 && (
            <div className="mt-12">
              <h3 className="font-display uppercase text-lg text-ink mb-4 text-center">Recommended Courses</h3>
              <div className="flex flex-wrap justify-center gap-3">
                {courses.map((c, i) => (
                  <a
                    key={`${c.title}-${i}`}
                    href={c.url || "#"}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-full border-[2px] border-ink bg-white px-4 py-2 font-display uppercase text-[11px] text-ink shadow-[2px_3px_0_0_rgba(26,26,26,0.9)] transition-transform hover:scale-105"
                  >
                    {c.free ? "🆓 " : ""}{c.title} · {c.provider}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      <WaveDivider topColor="var(--lavender)" bottomColor="var(--pink)" />

      {/* SECTION 9 — FAQ */}
      <section style={{ backgroundColor: "var(--pink)" }} className="px-4 sm:px-6 py-20 sm:py-24">
        <div className="mx-auto max-w-4xl">
          <h2 className="section-heading text-center mb-12">Got Questions? 🙋</h2>
          <Reveal>
            <FaqAccordion />
          </Reveal>
        </div>
      </section>

      <WaveDivider topColor="var(--pink)" bottomColor="var(--periwinkle)" />

      <SiteFooter />

      <FloatingChatbot jobTitle={roadmap?.job_title} />
    </main>
  );
}

function MilestoneNode({ m }: { m: MNode }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [below, setBelow] = useState(false);

  const onEnter = () => {
    const el = wrapRef.current;
    if (!el) return;
    const top = el.getBoundingClientRect().top;
    setBelow(top < 200);
  };

  const hasSalary = !!m.salaryMax && m.salaryMax > 0;

  return (
    <div
      ref={wrapRef}
      onMouseEnter={onEnter}
      className="group relative flex flex-col items-center w-full"
    >
      <div
        className="relative z-10 flex h-20 w-20 items-center justify-center rounded-full border-[2.5px] border-ink font-display text-3xl text-ink transition-transform group-hover:scale-110"
        style={{
          backgroundColor: m.color,
          animation: "soft-pulse 2.6s ease-in-out infinite",
          animationDelay: `${m.n * 200}ms`,
        }}
      >
        {m.n}
      </div>
      <div className="mt-4 text-center font-display uppercase text-sm text-ink px-2 leading-tight">
        {m.label}
      </div>

      {/* Tooltip polaroid */}
      <div
        className={`pointer-events-none absolute left-1/2 z-50 w-56 rounded-2xl border-[2.5px] border-ink bg-cream p-4 opacity-0 shadow-[6px_8px_0_0_rgba(26,26,26,0.9)] transition-opacity duration-200 group-hover:opacity-100 ${
          below ? "top-full mt-3" : "bottom-full mb-3"
        }`}
        style={{ transform: `translateX(-50%) rotate(${below ? "2deg" : "-2deg"})` }}
      >
        <div className="font-display uppercase text-base text-ink mb-1">{m.label}</div>
        {m.time && <div className="text-xs text-ink/70 mb-2">⏱ {m.time}</div>}
        {m.skill && <div className="text-sm text-ink mb-1">🔑 {m.skill}</div>}
        {hasSalary && (
          <div className="text-sm text-ink">💰 {k(m.salaryMin || 0)}–{k(m.salaryMax || 0)}</div>
        )}
      </div>
    </div>
  );
}

function PolaroidCard({
  rotation,
  headerBg,
  headerLabel,
  children,
}: {
  rotation: string;
  headerBg: string;
  headerLabel: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className="border-[2.5px] border-ink rounded-2xl bg-white shadow-[6px_8px_0_0_rgba(26,26,26,0.9)] overflow-hidden"
      style={{ transform: `rotate(${rotation})` }}
    >
      <div
        className="px-5 py-3 border-b-[2.5px] border-ink font-display uppercase text-lg text-ink"
        style={{ backgroundColor: headerBg }}
      >
        {headerLabel}
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}

function HiringSection({
  companies,
  alsoHiring,
}: {
  companies: { name: string; role: string; location: string; url: string; bg: string }[];
  alsoHiring: string[];
}) {
  return (
    <section style={{ backgroundColor: "var(--pink)" }} className="py-24">
      <div className="mx-auto max-w-7xl px-6">
        <h2 className="section-heading text-center mb-12">Who's Hiring Right Now 🔥</h2>

        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {companies.map((c, i) => (
            <div
              key={`${c.name}-${i}`}
              className="border-[2.5px] border-ink rounded-2xl bg-white p-5 shadow-[6px_8px_0_0_rgba(26,26,26,0.9)] transition-transform duration-300 hover:-translate-y-2 hover:rotate-0"
              style={{ transform: `rotate(${i % 2 === 0 ? "-1.5deg" : "1.5deg"})` }}
            >
              <div
                className="flex h-20 w-20 items-center justify-center rounded-2xl border-[2.5px] border-ink font-display text-4xl text-ink mb-4"
                style={{ backgroundColor: c.bg }}
              >
                {c.name[0]}
              </div>
              <h3 className="font-display uppercase text-xl text-ink mb-1">{c.name}</h3>
              <div className="text-sm text-ink/80 mb-3">{c.role || "Open roles"}</div>
              <div className="flex flex-wrap gap-1.5 mb-4">
                <span className="rounded-full border-[2px] border-ink bg-cream px-2.5 py-1 font-display uppercase text-[10px] text-ink">
                  📍 {c.location}
                </span>
                <span className="rounded-full border-[2px] border-ink bg-mint px-2.5 py-1 font-display uppercase text-[10px] text-ink">
                  Hiring
                </span>
              </div>
              <a
                href={c.url || "#"}
                target={c.url && c.url !== "#" ? "_blank" : undefined}
                rel="noreferrer"
                className="inline-block rounded-full border-[2px] border-ink bg-yellow px-4 py-1.5 font-display uppercase text-xs text-ink"
              >
                View Jobs →
              </a>
            </div>
          ))}
        </div>

        {/* Also hiring badges */}
        {alsoHiring.length > 0 && (
          <div className="mt-14 flex flex-wrap justify-center gap-3">
            {alsoHiring.map((name, i) => (
              <span
                key={`${name}-${i}`}
                className="rounded-full border-[2.5px] border-ink px-5 py-2.5 font-display uppercase text-sm text-ink shadow-[3px_4px_0_0_rgba(26,26,26,0.9)]"
                style={{ backgroundColor: PALETTE[i % PALETTE.length] }}
              >
                {name}
              </span>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
