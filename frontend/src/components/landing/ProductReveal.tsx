import { motion } from "framer-motion";
import { useState } from "react";

type Topic = { id: string; label: string; freq: number; subject: string; x: number; y: number };

const topics: Topic[] = [
  { id: "t1",  label: "Rotational Mechanics", subject: "Physics",  freq: 94, x: 18, y: 32 },
  { id: "t2",  label: "Electrostatics",       subject: "Physics",  freq: 88, x: 32, y: 18 },
  { id: "t3",  label: "Coordination Compounds", subject: "Chem",   freq: 86, x: 50, y: 28 },
  { id: "t4",  label: "Definite Integrals",   subject: "Maths",    freq: 92, x: 64, y: 16 },
  { id: "t5",  label: "Probability",          subject: "Maths",    freq: 78, x: 78, y: 36 },
  { id: "t6",  label: "Optics",               subject: "Physics",  freq: 71, x: 24, y: 56 },
  { id: "t7",  label: "Organic Mechanisms",   subject: "Chem",     freq: 89, x: 42, y: 64 },
  { id: "t8",  label: "Vectors & 3D",         subject: "Maths",    freq: 74, x: 60, y: 56 },
  { id: "t9",  label: "Thermodynamics",       subject: "Chem",     freq: 68, x: 78, y: 68 },
  { id: "t10", label: "Modern Physics",       subject: "Physics",  freq: 81, x: 88, y: 50 },
  { id: "t11", label: "Coordinate Geometry",  subject: "Maths",    freq: 64, x: 12, y: 78 },
  { id: "t12", label: "Equilibrium",          subject: "Chem",     freq: 58, x: 50, y: 84 },
];

const edges: [string, string][] = [
  ["t1","t6"], ["t2","t10"], ["t3","t7"], ["t4","t5"], ["t4","t8"],
  ["t5","t11"], ["t6","t10"], ["t7","t12"], ["t8","t11"], ["t9","t3"],
  ["t10","t2"], ["t1","t4"], ["t7","t9"], ["t8","t5"],
];

export function ProductReveal() {
  const [hover, setHover] = useState<string | null>(null);

  const get = (id: string) => topics.find(t => t.id === id)!;

  return (
    <section id="atlas" className="relative bg-paper-2 py-32 md:py-44">
      <div className="mx-auto max-w-[1600px] px-6 md:px-12">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 md:col-span-4">
            <div className="eyebrow">№ 03 / The Atlas</div>
            <h2 className="display mt-4 text-[clamp(2.2rem,4.6vw,4.2rem)] text-ink">
              Your syllabus,<br/>
              <span className="text-ember">weighted by reality.</span>
            </h2>
            <p className="mt-6 max-w-md text-[15px] leading-relaxed text-ink-dim">
              Every topic in your exam is plotted by how often it actually appears, how
              hard it scores, and how shaky you are on it. The Atlas tells you where
              the next hour of study earns the most marks.
            </p>
            <div className="mt-10 grid grid-cols-3 gap-4">
              <Stat n="10yr" l="of papers parsed" />
              <Stat n="12.4k" l="topics indexed" />
              <Stat n="3×" l="study efficiency" />
            </div>
          </div>

          <div className="col-span-12 md:col-span-8">
            <div className="relative aspect-[4/3] w-full overflow-hidden rounded-sm border border-ink/15 bg-paper">
              {/* paper grid */}
              <div
                aria-hidden
                className="pointer-events-none absolute inset-0 opacity-[0.08]"
                style={{
                  backgroundImage:
                    "linear-gradient(to right, #0d0d0d 1px, transparent 1px), linear-gradient(to bottom, #0d0d0d 1px, transparent 1px)",
                  backgroundSize: "40px 40px",
                }}
              />
              <div className="absolute left-4 top-4 z-10 font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                Atlas / Live Sample &nbsp;·&nbsp; JEE Advanced
              </div>
              <div className="absolute right-4 top-4 z-10 font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                Hover a node
              </div>

              <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
                {edges.map(([a, b], i) => {
                  const A = get(a), B = get(b);
                  const active = hover === a || hover === b;
                  return (
                    <line
                      key={i}
                      x1={A.x} y1={A.y} x2={B.x} y2={B.y}
                      stroke={active ? "var(--color-ember)" : "var(--color-ink)"}
                      strokeOpacity={active ? 0.9 : 0.25}
                      strokeWidth={active ? 0.3 : 0.15}
                      vectorEffect="non-scaling-stroke"
                    />
                  );
                })}
              </svg>

              {topics.map((t) => {
                const isHover = hover === t.id;
                const size = 6 + (t.freq / 100) * 18;
                return (
                  <button
                    key={t.id}
                    data-cursor="hover"
                    onMouseEnter={() => setHover(t.id)}
                    onMouseLeave={() => setHover(null)}
                    onFocus={() => setHover(t.id)}
                    onBlur={() => setHover(null)}
                    className="group absolute -translate-x-1/2 -translate-y-1/2 outline-none"
                    style={{ left: `${t.x}%`, top: `${t.y}%` }}
                    aria-label={`${t.label} — ${t.freq}% frequency`}
                  >
                    <span
                      className="block rounded-full transition-all duration-300"
                      style={{
                        width: size,
                        height: size,
                        background: t.freq > 80 ? "var(--color-ember)" : "var(--color-ink)",
                        boxShadow: isHover ? "0 0 0 8px color-mix(in oklab, var(--color-ember) 18%, transparent)" : "none",
                      }}
                    />
                    {isHover && (
                      <motion.div
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="absolute left-1/2 top-full mt-2 -translate-x-1/2 whitespace-nowrap rounded-sm border border-ink/20 bg-paper px-2.5 py-1.5 text-[11px] shadow-sm"
                      >
                        <div className="font-display font-medium text-ink">{t.label}</div>
                        <div className="font-mono text-[9px] uppercase tracking-widest text-ink-soft">
                          {t.subject} · {t.freq}% appears
                        </div>
                      </motion.div>
                    )}
                  </button>
                );
              })}

              {/* legend */}
              <div className="absolute bottom-4 left-4 right-4 z-10 flex items-center justify-between font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                <div className="flex items-center gap-3">
                  <span className="inline-flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-ember" /> High-yield
                  </span>
                  <span className="inline-flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-ink" /> Standard
                  </span>
                </div>
                <div>Size = exam frequency</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Stat({ n, l }: { n: string; l: string }) {
  return (
    <div>
      <div className="display text-2xl text-ink">{n}</div>
      <div className="mt-1 font-mono text-[10px] uppercase tracking-widest text-ink-soft">{l}</div>
    </div>
  );
}
