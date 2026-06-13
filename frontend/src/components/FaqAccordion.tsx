import { useState } from "react";

const FAQS = [
  {
    q: "What is PathForge AI?",
    a: "PathForge AI is a playful career-guidance app that turns any job title into a personalized visual roadmap — skills, certifications, salary, and companies hiring.",
  },
  {
    q: "Is it free?",
    a: "Yes — core roadmaps, salary insights, and the AI advisor are free. Premium courses and 1:1 coaching are coming soon.",
  },
  {
    q: "How accurate is the salary data?",
    a: "Salary ranges blend public sources (Levels.fyi, Glassdoor, BLS) with company-reported bands, refreshed monthly.",
  },
  {
    q: "How does the RAG chatbot work?",
    a: "The advisor retrieves grounded context from our roadmap, jobs, and course datasets, then a language model synthesizes a tailored answer.",
  },
  {
    q: "What jobs are supported?",
    a: "Anything from software, data, and ML to design, product, and marketing. If you can name it, we can map it.",
  },
];

export function FaqAccordion() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <div className="mx-auto w-full max-w-[800px] space-y-4">
      {FAQS.map((f, i) => {
        const isOpen = open === i;
        return (
          <div
            key={f.q}
            className="overflow-hidden rounded-2xl border-[2.5px] border-ink bg-cream shadow-[5px_6px_0_0_rgba(26,26,26,0.9)] transition-transform hover:-translate-y-0.5"
          >
            <button
              type="button"
              onClick={() => setOpen(isOpen ? null : i)}
              aria-expanded={isOpen}
              className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left focus-visible:outline-none focus-visible:bg-yellow/40"
            >
              <span className="font-display uppercase text-base sm:text-lg text-ink">{f.q}</span>
              <span
                aria-hidden
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-[2px] border-ink bg-yellow font-display text-xl text-ink transition-transform duration-300 ${
                  isOpen ? "rotate-45" : "rotate-0"
                }`}
              >
                +
              </span>
            </button>
            <div
              className="grid transition-[grid-template-rows] duration-300 ease-out"
              style={{ gridTemplateRows: isOpen ? "1fr" : "0fr" }}
            >
              <div className="overflow-hidden">
                <p className="px-5 pb-5 text-sm sm:text-base text-ink/80">{f.a}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
