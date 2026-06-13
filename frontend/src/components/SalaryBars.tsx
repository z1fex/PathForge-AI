import { useEffect, useRef, useState } from "react";
import type { SalaryOverview } from "@/lib/api/pathforge";

const SAMPLE = [
  { name: "Google", value: 195, color: "var(--sky)" },
  { name: "Meta", value: 210, color: "var(--lavender)" },
  { name: "Amazon", value: 175, color: "var(--yellow)" },
  { name: "Microsoft", value: 180, color: "var(--pink)" },
  { name: "OpenAI", value: 240, color: "var(--periwinkle)" },
];

export function SalaryBars({ overview }: { overview?: SalaryOverview }) {
  const ref = useRef<HTMLDivElement>(null);
  const [shown, setShown] = useState(false);

  // When live salary data is present, show Entry/Mid/Senior bands; else the sample.
  const data = overview
    ? [
        { name: "Entry", value: Math.round((overview.entry?.max ?? 0) / 1000), color: "var(--sky)" },
        { name: "Mid", value: Math.round((overview.mid?.max ?? 0) / 1000), color: "var(--yellow)" },
        { name: "Senior", value: Math.round((overview.senior?.max ?? 0) / 1000), color: "var(--pink)" },
      ].filter((d) => d.value > 0)
    : SAMPLE;

  const heading = overview ? "Salary By Level" : "Salary by Company";
  const max = Math.max(1, ...data.map((d) => d.value)) * 1.1;

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && (setShown(true), io.disconnect())),
      { threshold: 0.3 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  if (!data.length) return null;

  return (
    <div
      ref={ref}
      className="border-[2.5px] border-ink rounded-2xl bg-white p-6 sm:p-8 shadow-[6px_8px_0_0_rgba(26,26,26,0.9)]"
      style={{ transform: "rotate(-0.5deg)" }}
    >
      <h3 className="font-display uppercase text-xl text-ink mb-6 text-center">{heading}</h3>
      <div className="space-y-4">
        {data.map((c, i) => (
          <div key={c.name} className="flex items-center gap-3 sm:gap-4">
            <div className="w-20 sm:w-24 font-display uppercase text-xs sm:text-sm text-ink">
              {c.name}
            </div>
            <div className="flex-1 h-7 sm:h-8 rounded-full border-[2px] border-ink bg-cream overflow-hidden">
              <div
                className="h-full border-r-[2px] border-ink transition-[width] duration-1000 ease-out"
                style={{
                  width: shown ? `${(c.value / max) * 100}%` : "0%",
                  backgroundColor: c.color,
                  transitionDelay: `${i * 120}ms`,
                }}
              />
            </div>
            <div className="w-16 sm:w-20 text-right font-display text-sm sm:text-base text-ink">
              ${c.value}K
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
