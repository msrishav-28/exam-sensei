// Honest, capability-led copy — no fabricated testimonials, no invented metrics.
// Same marquee design as before; each card states a real product promise.
const quotes = [
  { q: "The mentor reads your profile before answering — no generic study advice.", a: "How the chat works" },
  { q: "Pick an exam and the planner orders topics by past-paper weightage, not gut feel.", a: "How the planner works" },
  { q: "Add multiple target exams and we flag date clashes before they bite you.", a: "How clash detection works" },
  { q: "Mark a topic as a weakness once and every future plan over-weights it.", a: "How prioritization works" },
  { q: "Calendar pulls the official notification dates we track for each exam.", a: "How the calendar works" },
  { q: "Streaks + XP exist to keep you opening the app — no rewards you can buy.", a: "How streaks work" },
];

// Capability statements — no fabricated numbers.
const stats = [
  { n: "Weightage", l: "Topics ranked by past-paper frequency" },
  { n: "Adaptive", l: "Plan re-prioritizes as you log progress" },
  { n: "24 / 7", l: "Mentor available whenever you study" },
  { n: "Streaks", l: "Daily cadence + simple gamification" },
];

export function ProofMarquee() {
  return (
    <section id="proof" className="relative overflow-hidden bg-paper py-32 md:py-44">
      <div className="mx-auto max-w-[1600px] px-6 md:px-12">
        <div className="mb-16 grid grid-cols-12 gap-6">
          <div className="col-span-12 md:col-span-5">
            <div className="eyebrow">№ 08 / The method</div>
            <h2 className="display mt-4 text-[clamp(2.2rem,4.6vw,4.2rem)] text-ink">
              Built for the<br/>ones who <em className="not-italic text-ember">show up.</em>
            </h2>
          </div>
          <div className="col-span-12 grid grid-cols-2 gap-px bg-ink/10 md:col-span-7 md:grid-cols-4">
            {stats.map((s) => (
              <div key={s.n} className="bg-paper p-5">
                <div className="display text-2xl text-ink md:text-3xl">{s.n}</div>
                <div className="mt-2 font-mono text-[10px] uppercase tracking-widest text-ink-soft">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* full-bleed marquee */}
      <div className="relative overflow-hidden border-y border-ink/15 py-10">
        <div className="flex w-max animate-marquee items-stretch gap-px bg-ink/10">
          {[...quotes, ...quotes].map((q, i) => (
            <figure
              key={i}
              className="flex w-[440px] shrink-0 items-start gap-5 whitespace-normal bg-paper px-8 py-2"
            >
              <span className="display shrink-0 text-5xl leading-none text-ember">“</span>
              <div className="min-w-0">
                <blockquote className="font-display text-[17px] leading-snug text-ink">
                  {q.q}
                </blockquote>
                <figcaption className="mt-3 font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                  {q.a}
                </figcaption>
              </div>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
