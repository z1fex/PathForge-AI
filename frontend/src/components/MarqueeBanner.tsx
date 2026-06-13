import { cn } from "@/lib/utils";

interface MarqueeBannerProps {
  items: string[];
  bgColor?: string;
  textColor?: string;
  className?: string;
}

export function MarqueeBanner({
  items,
  bgColor = "var(--ink)",
  textColor = "var(--yellow)",
  className,
}: MarqueeBannerProps) {
  const loop = [...items, ...items];

  return (
    <div
      className={cn(
        "w-full overflow-hidden border-y-[2.5px] border-ink",
        className,
      )}
      style={{
        backgroundColor: bgColor,
        color: textColor,
        height: 60,
      }}
    >
      <div className="flex h-full items-center whitespace-nowrap animate-marquee will-change-transform">
        {loop.map((item, i) => (
          <span
            key={i}
            className="font-display uppercase text-xl px-6 inline-flex items-center gap-6"
          >
            {item}
            <span aria-hidden="true">⭐</span>
          </span>
        ))}
      </div>
    </div>
  );
}
