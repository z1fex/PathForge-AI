import { useEffect, useState } from "react";
import mascot from "@/assets/chatbot-mascot.png";
import { sendChat } from "@/lib/api/pathforge";

type Msg = { from: "ai" | "user"; text: string };

const INITIAL: Msg[] = [
  {
    from: "ai",
    text: "Hey! 👋 I'm your PathForge advisor. Ask me anything about your career path — skills, certs, salary, or who's hiring!",
  },
];

const SUGGESTIONS = [
  "Do I need a degree? 🎓",
  "What skills matter most? 🛠️",
  "How long until I'm job-ready? ⏳",
];

export function FloatingChatbot({ jobTitle }: { jobTitle?: string }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>(INITIAL);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const send = async (text: string) => {
    const t = text.trim();
    if (!t || busy) return;
    setMessages((m) => [...m, { from: "user", text: t }, { from: "ai", text: "…" }]);
    setDraft("");
    setBusy(true);
    try {
      const res = await sendChat(jobTitle || "professional", t);
      const answer = (res.answer || "").trim() || "I'm not sure about that one — try rephrasing?";
      setMessages((m) => {
        const c = [...m];
        c[c.length - 1] = { from: "ai", text: answer };
        return c;
      });
    } catch {
      setMessages((m) => {
        const c = [...m];
        c[c.length - 1] = {
          from: "ai",
          text: "Hmm, I couldn't reach the advisor right now. Make sure the backend is running, then try again. 🙏",
        };
        return c;
      });
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      {/* Backdrop */}
      {open && (
        <div
          aria-hidden
          onClick={() => setOpen(false)}
          className="fixed inset-0 z-[998] bg-ink/20"
        />
      )}

      {/* Floating button + tooltip */}
      {!open && (
        <div className="fixed bottom-6 right-6 z-[997] group">
          <span
            className="pointer-events-none absolute bottom-full right-0 mb-3 whitespace-nowrap rounded-full border-[2px] border-ink bg-cream px-3 py-1.5 font-sans text-[13px] text-ink opacity-0 shadow-[2px_3px_0_0_rgba(26,26,26,0.9)] transition-opacity duration-200 group-hover:opacity-100"
          >
            Chat with PathForge 🤖
          </span>
          <button
            type="button"
            aria-label="Open PathForge advisor"
            onClick={() => setOpen(true)}
            className="flex h-[84px] w-[84px] items-center justify-center rounded-full border-[2.5px] border-ink bg-white shadow-[4px_6px_0_0_rgba(26,26,26,0.9)] transition-transform duration-200 hover:scale-110 hover:shadow-[6px_10px_0_0_rgba(26,26,26,0.9)] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ink/30"
          >
            <img
              src={mascot}
              alt=""
              width={72}
              height={72}
              className="h-[72px] w-[72px] object-contain"
            />
          </button>
        </div>
      )}

      {/* Sidebar */}
      <aside
        role="dialog"
        aria-label="PathForge Advisor"
        aria-hidden={!open}
        className="fixed top-0 right-0 z-[999] flex h-full w-full max-w-[380px] flex-col border-l-[2.5px] border-ink bg-white shadow-[-8px_0_24px_rgba(26,26,26,0.15)] transition-transform duration-300 ease-out"
        style={{ transform: open ? "translateX(0)" : "translateX(100%)" }}
      >
        {/* Header */}
        <div
          className="flex items-center gap-3 border-b-[2.5px] border-ink px-4 py-3"
          style={{ backgroundColor: "var(--periwinkle)" }}
        >
          <img
            src={mascot}
            alt=""
            width={40}
            height={40}
            className="h-10 w-10 shrink-0 rounded-full border-[2px] border-ink bg-white object-contain"
          />
          <div className="min-w-0 flex-1">
            <div className="font-display uppercase text-base text-ink truncate">
              PathForge Advisor 🤖
            </div>
            <span className="inline-flex items-center gap-1.5 font-display uppercase text-[10px] text-ink/80">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-green-600 animate-pulse" />
              {jobTitle ? jobTitle : "Online"}
            </span>
          </div>
          <button
            type="button"
            aria-label="Close chat"
            onClick={() => setOpen(false)}
            className="shrink-0 rounded-full border-[2px] border-ink bg-white px-3 py-1.5 font-display text-sm text-ink transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ink/30"
          >
            ✕
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 space-y-3 overflow-y-auto bg-cream/40 p-4">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${m.from === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] whitespace-pre-wrap rounded-[18px] border-[2px] border-ink px-4 py-2.5 font-sans text-[16px] leading-snug text-ink shadow-[3px_4px_0_0_rgba(26,26,26,0.9)] ${
                  m.from === "user" ? "bg-yellow" : "bg-lavender"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
        </div>

        {/* Suggestions */}
        <div className="flex flex-wrap gap-2 border-t-[2.5px] border-ink bg-white px-4 py-3">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              disabled={busy}
              onClick={() => send(s)}
              className="rounded-full border-[2px] border-ink bg-cream px-3 py-1.5 font-display uppercase text-[11px] text-ink transition-transform hover:scale-105 disabled:opacity-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ink/30"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(draft);
          }}
          className="flex items-center gap-2 border-t-[2.5px] border-ink bg-white p-3"
        >
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 rounded-full border-[2px] border-ink bg-white px-4 py-2.5 font-sans text-sm text-ink placeholder:text-ink/50 focus:outline-none focus-visible:ring-4 focus-visible:ring-ink/20"
          />
          <button
            type="submit"
            disabled={busy}
            className="rounded-full border-[2.5px] border-ink bg-yellow px-4 py-2.5 font-display uppercase text-sm text-ink transition-transform hover:scale-105 disabled:opacity-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ink/30"
          >
            {busy ? "…" : "Send →"}
          </button>
        </form>
      </aside>
    </>
  );
}
