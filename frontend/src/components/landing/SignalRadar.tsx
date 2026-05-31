import { motion } from "framer-motion";

const steps = [
  {
    n: "I.",
    title: "It watches how you answer.",
    body: "Every solved problem, every skipped question, every second on a concept becomes signal. No spreadsheets to fill.",
  },
  {
    n: "II.",
    title: "It re-weights the syllabus.",
    body: "Topics where you wobble bubble up. Topics you've already mastered fall away. The plan rewrites itself nightly.",
  },
  {
    n: "III.",
    title: "It hands you tomorrow.",
    body: "You open the app and the next 90 minutes are already chosen: 2 concepts, 8 problems, 1 timed drill. That's it.",
  },
];

export function SignalRadar() {
  return (
    <section id="mentor" className="relative bg-paper py-32 md:py-44">
      <div className="mx-auto max-w-[1600px] px-6 md:px-12">
        <div className="mb-20 flex items-end justify-between">
          <div>
            <div className="eyebrow">№ 04 / Adaptive mentor</div>
            <h2 className="display mt-4 text-[clamp(2.2rem,4.6vw,4.2rem)] text-ink">
              A mentor that<br/>changes its mind <em className="not-italic text-ember">about you</em>.
            </h2>
          </div>
          <div className="hidden max-w-xs text-right text-[13px] text-ink-dim md:block">
            Static study plans assume you don't learn. Sensei updates yours nightly,
            using only what you actually did today.
          </div>
        </div>

        <div className="grid grid-cols-12 gap-px bg-ink/10">
          {steps.map((s, i) => (
            <motion.article
              key={s.n}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
              className="col-span-12 bg-paper p-8 md:col-span-4 md:p-12"
            >
              <div className="flex items-start justify-between">
                <span className="display text-4xl text-ember">{s.n}</span>
                <span className="eyebrow">Step {i + 1} of 3</span>
              </div>
              <h3 className="display mt-12 text-[clamp(1.5rem,2.2vw,2rem)] text-ink">{s.title}</h3>
              <p className="mt-5 text-[14px] leading-relaxed text-ink-dim">{s.body}</p>

              {/* mini visual per step */}
              <div className="mt-10 h-32 border border-ink/10 bg-paper-2 p-4">
                {i === 0 && <Pulse />}
                {i === 1 && <Reweight />}
                {i === 2 && <Plan />}
              </div>
            </motion.article>
          ))}
        </div>
      </div>
    </section>
  );
}

function Pulse() {
  return (
    <div className="flex h-full items-end gap-1.5">
      {[40, 65, 30, 80, 55, 90, 45, 70, 35, 60, 25, 75].map((h, i) => (
        <motion.div
          key={i}
          initial={{ height: 0 }}
          whileInView={{ height: `${h}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: i * 0.04 }}
          className="flex-1 bg-ink"
          style={{ opacity: h > 70 ? 1 : 0.4 }}
        />
      ))}
    </div>
  );
}

function Reweight() {
  return (
    <div className="flex h-full flex-col justify-between font-mono text-[10px] text-ink-dim">
      <div className="flex items-center justify-between"><span>ROT. MECH</span><span className="text-ember">▲ 0.18</span></div>
      <div className="flex items-center justify-between"><span>OPTICS</span><span className="text-ember">▲ 0.07</span></div>
      <div className="flex items-center justify-between"><span>VECTORS</span><span>— 0.00</span></div>
      <div className="flex items-center justify-between"><span>EQUIL.</span><span className="text-ink-soft">▼ 0.11</span></div>
      <div className="flex items-center justify-between"><span>PROB.</span><span className="text-ink-soft">▼ 0.22</span></div>
    </div>
  );
}

function Plan() {
  return (
    <div className="flex h-full flex-col justify-between text-[11px]">
      <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">Tomorrow · 90 min</div>
      <div className="space-y-1.5">
        <div className="flex items-center gap-2"><span className="h-1 w-1 rounded-full bg-ember" /> Concept · Friction on inclines</div>
        <div className="flex items-center gap-2"><span className="h-1 w-1 rounded-full bg-ink" /> 8 problems · mixed</div>
        <div className="flex items-center gap-2"><span className="h-1 w-1 rounded-full bg-ink" /> Timed drill · 12 min</div>
      </div>
    </div>
  );
}
