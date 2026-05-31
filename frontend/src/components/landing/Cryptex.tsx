import { motion } from "framer-motion";

type Exam = { name: string; date: string; days: number; ring: number; angle: number; tone: "ink" | "ember" };

const exams: Exam[] = [
  { name: "JEE Main · S1",  date: "Jan 24",  days: 42,  ring: 0, angle: -20,  tone: "ember" },
  { name: "BITSAT",         date: "May 18",  days: 156, ring: 1, angle: 35,   tone: "ink" },
  { name: "JEE Advanced",   date: "May 25",  days: 163, ring: 1, angle: -65,  tone: "ember" },
  { name: "NEET UG",        date: "May 04",  days: 142, ring: 2, angle: 110,  tone: "ink" },
  { name: "CUET UG",        date: "May 13",  days: 151, ring: 2, angle: -120, tone: "ink" },
  { name: "UPSC Prelims",   date: "Jun 01",  days: 170, ring: 3, angle: 60,   tone: "ember" },
  { name: "GATE",           date: "Feb 08",  days: 57,  ring: 3, angle: -150, tone: "ink" },
];

export function Cryptex() {
  return (
    <section id="calendar" className="relative overflow-hidden bg-ink py-32 text-paper md:py-44">
      <div className="mx-auto max-w-[1600px] px-6 md:px-12">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 md:col-span-4">
            <div className="eyebrow" style={{ color: "color-mix(in oklab, var(--color-paper) 60%, transparent)" }}>
              № 05 / Exam Calendar
            </div>
            <h2 className="display mt-4 text-[clamp(2.2rem,4.6vw,4.2rem)] text-paper">
              Every deadline,<br/>in <em className="not-italic text-ember">one orbit.</em>
            </h2>
            <p className="mt-6 max-w-md text-[15px] leading-relaxed text-paper/70">
              Notifications, application windows, admit cards, exam dates, result days —
              all tracked, all surfaced before you miss them. You'll never refresh a
              government portal again.
            </p>
            <div className="mt-10 grid grid-cols-2 gap-y-4 text-[13px]">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-paper/50">Next up</div>
                <div className="mt-1 font-display text-paper">JEE Main · S1</div>
                <div className="text-ember">in 42 days</div>
              </div>
              <div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-paper/50">Tracked</div>
                <div className="mt-1 font-display text-paper">47 exams</div>
                <div className="text-paper/60">189 windows</div>
              </div>
            </div>
          </div>

          <div className="col-span-12 md:col-span-8">
            <div className="relative mx-auto aspect-square w-full max-w-[640px]">
              {/* concentric rings */}
              {[1, 2, 3, 4].map((r) => (
                <div
                  key={r}
                  className="absolute inset-0 rounded-full border border-paper/15"
                  style={{ inset: `${r * 8}%` }}
                />
              ))}
              {/* center marker */}
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                <div className="font-mono text-[10px] uppercase tracking-widest text-paper/50">Today</div>
                <div className="mt-1 display text-2xl text-paper">25.05</div>
              </div>

              {/* rotating exam group */}
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 90, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0"
              >
                {exams.map((e, i) => {
                  const radiusPct = 30 + e.ring * 7;
                  const rad = (e.angle * Math.PI) / 180;
                  const x = 50 + Math.cos(rad) * radiusPct;
                  const y = 50 + Math.sin(rad) * radiusPct;
                  return (
                    <motion.div
                      key={i}
                      animate={{ rotate: -360 }}
                      transition={{ duration: 90, repeat: Infinity, ease: "linear" }}
                      className="absolute"
                      style={{ left: `${x}%`, top: `${y}%`, transform: "translate(-50%, -50%)" }}
                    >
                      <div className="flex flex-col items-center gap-1.5">
                        <span
                          className="h-2 w-2 rounded-full"
                          style={{ background: e.tone === "ember" ? "var(--color-ember)" : "var(--color-paper)" }}
                        />
                        <div className="rounded-sm bg-paper/5 px-2 py-1 backdrop-blur-sm">
                          <div className="font-display text-[11px] leading-tight text-paper">{e.name}</div>
                          <div className="font-mono text-[9px] uppercase tracking-widest text-paper/60">
                            {e.date} · D-{e.days}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </motion.div>

              {/* sweep line */}
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0"
              >
                <div
                  className="absolute left-1/2 top-1/2 h-px origin-left"
                  style={{
                    width: "50%",
                    background: "linear-gradient(to right, var(--color-ember), transparent)",
                  }}
                />
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
