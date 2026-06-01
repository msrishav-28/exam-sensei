import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const faqs = [
  {
    q: "Which exams does ExamSensei support?",
    a: "India's major competitive exams — JEE Main & Advanced, NEET UG, BITSAT, CUET, GATE, UPSC, CAT, SSC, IBPS, several state PSCs. We're starting with a focused set and adding more as we go; the planner is tuned per exam from public past papers.",
  },
  {
    q: "Is this another video-lecture platform?",
    a: "No. We don't sell lectures. ExamSensei is the mentor on top of the prep you're already doing — it decides what's next, drills your weak spots, and keeps your plan honest.",
  },
  {
    q: "How do I tell the mentor what I've done?",
    a: "Type. Tell it what you studied, what you bombed, which mock you took. It updates the plan and the priorities accordingly. We don't ask you to fill spreadsheets.",
  },
  {
    q: "Where does the AI run? Is my data private?",
    a: "Chat is powered by hosted LLM APIs (Gemini, Groq, OpenAI or Anthropic depending on configuration) — your messages go to the provider for that turn. We store your conversation history in your account so the next session has context; you can delete it from your profile any time.",
  },
  {
    q: "How much does it cost?",
    a: "Free while we're small. Once we hit real scale we'll add a paid tier; until then, the goal is to ship a tool that actually helps, not to charge you for it.",
  },
  {
    q: "Is this ready for me to bet my exam on?",
    a: "We're early. The planner, mentor, and exam calendar work; some things are still rough. Use it alongside your existing routine, not as a replacement for it — and tell us what's broken.",
  },
];

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="faq" className="relative bg-paper-2 py-32 md:py-44">
      <div className="mx-auto max-w-[1400px] px-6 md:px-12">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 md:col-span-4">
            <div className="eyebrow">№ 09 / Questions</div>
            <h2 className="display mt-4 text-[clamp(2.2rem,4.6vw,4.2rem)] text-ink">
              Things people<br/>actually ask.
            </h2>
            <p className="mt-6 max-w-sm text-[14px] text-ink-dim">
              Didn't find yours? Drop us a line at <span className="text-ink">hello@examsensei.in</span>.
            </p>
          </div>
          <div className="col-span-12 md:col-span-8">
            <ul className="divide-y divide-ink/15 border-y border-ink/15">
              {faqs.map((f, i) => {
                const isOpen = open === i;
                return (
                  <li key={i}>
                    <button
                      data-cursor="hover"
                      onClick={() => setOpen(isOpen ? null : i)}
                      className="group flex w-full items-center justify-between gap-6 py-6 text-left"
                    >
                      <span className="display text-[clamp(1.1rem,1.8vw,1.5rem)] text-ink">{f.q}</span>
                      <span
                        className="shrink-0 font-mono text-xl text-ember transition-transform"
                        style={{ transform: isOpen ? "rotate(45deg)" : "rotate(0)" }}
                      >
                        +
                      </span>
                    </button>
                    <AnimatePresence initial={false}>
                      {isOpen && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                          className="overflow-hidden"
                        >
                          <p className="max-w-2xl pb-7 pr-12 text-[15px] leading-relaxed text-ink-dim">
                            {f.a}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
