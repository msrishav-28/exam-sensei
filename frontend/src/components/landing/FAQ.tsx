import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const faqs = [
  {
    q: "Which exams does ExamSensei support?",
    a: "JEE Main & Advanced, NEET UG, BITSAT, CUET, GATE, UPSC Prelims, CAT, CLAT, NDA, and 38 more. The syllabus, paper history, and difficulty curves are tuned per exam.",
  },
  {
    q: "Is this another video-lecture platform?",
    a: "No. We don't sell lectures. ExamSensei is the mentor on top of the prep you're already doing — it decides what's next, drills your weak spots, and tracks your progress.",
  },
  {
    q: "Do I have to log every problem manually?",
    a: "Practically nothing. Solve inside the app or paste a screenshot of your scratch work; the mentor figures out what to update.",
  },
  {
    q: "Is the AI mentor accurate?",
    a: "Answers are cited from NCERT and the last decade of official papers. The model runs locally so your prompts never leave your device. If it doesn't know, it says so.",
  },
  {
    q: "How much does it cost?",
    a: "Free during the beta. Post-launch: one student-friendly subscription, with full access on scholarship for verified aspirants from underserved districts.",
  },
  {
    q: "I'm a parent. Why should my kid use this?",
    a: "Because hours studied is the wrong metric. ExamSensei replaces it with marks gained — and gives you (and your kid) a weekly report that's actually honest.",
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
