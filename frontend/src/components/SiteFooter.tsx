import { MarqueeBanner } from "./MarqueeBanner";

const COLS = [
  {
    title: "Features",
    links: ["Visual Roadmaps", "Salary Insights", "AI Advisor", "Who's Hiring", "Courses"],
  },
  {
    title: "Resources",
    links: ["Blog", "Career Library", "Certifications", "Help Center", "Changelog"],
  },
  {
    title: "Company",
    links: ["About", "Careers", "Contact", "Privacy", "Terms"],
  },
];

export function SiteFooter() {
  return (
    <footer style={{ backgroundColor: "var(--periwinkle)" }}>
      <MarqueeBanner
        items={[
          "PathForge AI",
          "Visual Roadmaps",
          "Salary Insights",
          "AI Advisor",
          "Who's Hiring",
        ]}
      />
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid gap-10 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <div className="font-display uppercase text-2xl text-ink mb-3">PathForge AI</div>
            <p className="text-sm text-ink/80 mb-5 max-w-xs">
              Playful AI career guidance — discover the path that fits who you are.
            </p>
            <div className="flex gap-2">
              {["𝕏", "in", "▶", "✦"].map((s) => (
                <a
                  key={s}
                  href="#"
                  aria-label={`Social ${s}`}
                  className="flex h-10 w-10 items-center justify-center rounded-full border-[2.5px] border-ink bg-yellow font-display text-ink shadow-[2px_3px_0_0_rgba(26,26,26,0.9)] transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ink/30"
                >
                  {s}
                </a>
              ))}
            </div>
          </div>

          {COLS.map((c) => (
            <div key={c.title}>
              <h3 className="font-display uppercase text-lg text-ink mb-4">{c.title}</h3>
              <ul className="space-y-2">
                {c.links.map((l) => (
                  <li key={l}>
                    <a
                      href="#"
                      className="text-sm text-ink/80 hover:text-ink hover:underline focus-visible:outline-none focus-visible:underline"
                    >
                      {l}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
      <div className="border-t-[2.5px] border-ink bg-ink py-5 text-center">
        <p className="font-sans text-sm text-cream">
          © 2025 PathForge AI. Built for students and career changers everywhere.
        </p>
      </div>
    </footer>
  );
}
