import type { ReactNode, ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary";

interface PillButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  children: ReactNode;
}

export function PillButton({
  variant = "primary",
  className,
  children,
  ...props
}: PillButtonProps) {
  const base =
    "inline-flex items-center justify-center font-display uppercase tracking-wide " +
    "border-[2.5px] border-ink rounded-full px-9 py-3.5 text-base " +
    "transition-transform duration-200 ease-out " +
    "hover:scale-105 hover:[filter:drop-shadow(4px_6px_0_rgba(26,26,26,0.9))] " +
    "active:scale-100";

  const variants: Record<Variant, string> = {
    primary: "bg-yellow text-ink",
    secondary: "bg-cream text-ink",
  };

  return (
    <button className={cn(base, variants[variant], className)} {...props}>
      {children}
    </button>
  );
}
