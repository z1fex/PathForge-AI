import { useState } from "react";

type Msg = { from: "ai" | "user"; text: string };

const INITIAL: Msg[] = [
  { from: "ai", text: "Hey! I'm your PathForge advisor 🤖 — what role are you aiming for?" },
  { from: "user", text: "I want to be an MLE at Google." },
  {
    from: "ai",
    text:
      "Great pick! For ML Engineer at Google, focus on: Python + DSA, Statistics & probability, TensorFlow/PyTorch, system design, and a couple of end-to-end ML projects. Want me to break this into a 6-month plan?",
  },
];

const SUGGESTIONS = [
  "What certs do I need? 📜",
  "What's the salary? 💰",
  "Who's hiring? 🏢",
];

export function ChatbotCard() {
  const [messages, setMessages] = useState<Msg[]>(INITIAL);
  const [draft, setDraft] = useState("");
  const [ripple, setRipple] = useState(false);

  const send = (text: string) => {
    const t = text.trim();
    if (!t) return;
    setMessages((m) => [...m, { from: "user", text: t }]);
    setDraft("");
    setRipple(true);
    setTimeout(() => setRipple(false), 500);
    setTimeout(() => {
      setMessages((m) => [
        ...m,
        { from: "ai", text: "Good question! Here's what I'd suggest based on your goal…" },
      ]);
    }, 600);
  };

  return (
    <div
      className="mx-auto w-full max-w-[800px] overflow-hidden rounded-3xl border-[2.5px] border-ink bg-white shadow-[8px_10px_0_0_rgba(26,26,26,0.9)]"
      style={{ transform: "rotate(-0.5deg)" }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between border-b-[2.5px] border-ink px-5 py-4"
        style={{ backgroundColor: "var(--periwinkle)" }}
      >
        <div className="font-display uppercase text-lg text-ink">PathForge AI Advisor 🤖</div>
        <span className="flex items-center gap-2 rounded-full border-[2px] border-ink bg-mint px-3 py-1 font-display uppercase text-[11px] text-ink">
          <span className="inline-block h-2 w-2 rounded-full bg-green-600 animate-pulse" />
          Online
        </span>
      </div>

      {/* Chat */}
      <div className="max-h-[340px] space-y-3 overflow-y-auto bg-cream/40 p-5">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.from === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl border-[2px] border-ink px-4 py-2.5 text-sm text-ink shadow-[3px_4px_0_0_rgba(26,26,26,0.9)] ${
                m.from === "user" ? "bg-yellow rounded-tr-sm" : "bg-lavender rounded-tl-sm"
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
      </div>

      {/* Suggestions */}
      <div className="flex flex-wrap gap-2 border-t-[2.5px] border-ink bg-white px-5 py-3">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => send(s)}
            className="rounded-full border-[2px] border-ink bg-cream px-3 py-1.5 font-display uppercase text-[11px] text-ink transition-transform hover:scale-105 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ink/30"
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
        className="flex items-center gap-2 border-t-[2.5px] border-ink bg-white p-4"
      >
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Ask me anything about your career..."
          className="flex-1 rounded-full border-[2px] border-ink bg-white px-4 py-2.5 font-sans text-sm text-ink placeholder:text-ink/50 focus:outline-none focus-visible:ring-4 focus-visible:ring-ink/20"
        />
        <button
          type="submit"
          className="relative overflow-hidden rounded-full border-[2.5px] border-ink bg-yellow px-5 py-2.5 font-display uppercase text-sm text-ink transition-transform hover:scale-105 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ink/30"
        >
          Send →
          {ripple && (
            <span
              aria-hidden
              className="pointer-events-none absolute inset-0 rounded-full bg-ink/20 animate-ping"
            />
          )}
        </button>
      </form>
    </div>
  );
}
