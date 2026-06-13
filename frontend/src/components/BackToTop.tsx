import { useEffect, useState } from "react";

export function BackToTop() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const onScroll = () => setShow(window.scrollY > 600);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <button
      type="button"
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      aria-label="Back to top"
      className={`fixed bottom-6 right-6 z-50 rounded-full border-[2.5px] border-ink bg-yellow px-5 py-3 font-display uppercase text-sm text-ink shadow-[4px_5px_0_0_rgba(26,26,26,0.9)] transition-all duration-300 hover:scale-110 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ink/30 ${
        show ? "opacity-100 translate-y-0" : "pointer-events-none opacity-0 translate-y-4"
      }`}
    >
      Back to Top ↑
    </button>
  );
}
