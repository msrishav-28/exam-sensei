import { motion } from "framer-motion";

export function EditorialSpread() {
  return (
    <section className="relative bg-paper-2 py-32 md:py-44">
      <div className="mx-auto max-w-[1600px] px-6 md:px-12">
        <div className="mb-16">
          <div className="eyebrow">№ 07 / The long game</div>
          <h2 className="display mt-4 max-w-3xl text-[clamp(2.2rem,4.6vw,4.2rem)] text-ink">
            Discipline, designed as a game you can <em className="not-italic text-ember">actually win.</em>
          </h2>
        </div>

        <div className="grid grid-cols-12 gap-px bg-ink/10">
          {/* Streak card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="col-span-12 bg-paper p-8 md:col-span-6 md:p-12"
          >
            <div className="flex items-baseline justify-between">
              <div className="eyebrow">Streak</div>
              <div className="display text-7xl text-ink">47</div>
            </div>
            <div className="mt-1 font-mono text-[10px] uppercase tracking-widest text-ink-soft">
              consecutive days
            </div>
            <div className="mt-10 grid gap-1" style={{ gridTemplateColumns: "repeat(14, minmax(0, 1fr))" }}>
              {Array.from({ length: 56 }).map((_, i) => {
                const lit = i % 8 !== 3 && i % 11 !== 5;
                const today = i === 55;
                return (
                  <div
                    key={i}
                    className="aspect-square"
                    style={{
                      background: today
                        ? "var(--color-ember)"
                        : lit
                          ? "var(--color-ink)"
                          : "color-mix(in oklab, var(--color-ink) 12%, transparent)",
                    }}
                  />
                );
              })}
            </div>
            <p className="mt-8 max-w-md text-[14px] leading-relaxed text-ink-dim">
              Show up 20 minutes. That counts. The streak isn't about hustle culture —
              it's a quiet contract with the version of you that wants this.
            </p>
          </motion.div>

          {/* XP & level */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="col-span-12 bg-paper p-8 md:col-span-6 md:p-12"
          >
            <div className="flex items-baseline justify-between">
              <div className="eyebrow">Mastery</div>
              <div className="display text-3xl text-ink">Lv. 14 <span className="text-ink-soft">/ 30</span></div>
            </div>
            <div className="mt-8 space-y-5">
              <Bar label="Physics" pct={72} />
              <Bar label="Maths" pct={58} />
              <Bar label="Chemistry" pct={81} accent />
              <Bar label="Mock test stamina" pct={44} />
            </div>
            <div className="mt-10 grid grid-cols-3 gap-4 text-[12px]">
              <Badge title="First century" sub="100 problems" />
              <Badge title="Night owl" sub="14-day midnight streak" />
              <Badge title="Comeback" sub="Bounced back from 28%" accent />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function Bar({ label, pct, accent }: { label: string; pct: number; accent?: boolean }) {
  return (
    <div>
      <div className="mb-2 flex items-baseline justify-between text-[12px]">
        <span className="text-ink">{label}</span>
        <span className="font-mono text-ink-soft">{pct}%</span>
      </div>
      <div className="h-1 w-full bg-ink/10">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${pct}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
          className="h-full"
          style={{ background: accent ? "var(--color-ember)" : "var(--color-ink)" }}
        />
      </div>
    </div>
  );
}

function Badge({ title, sub, accent }: { title: string; sub: string; accent?: boolean }) {
  return (
    <div className={`border p-3 ${accent ? "border-ember bg-ember/5" : "border-ink/15"}`}>
      <div className="font-display text-[13px] text-ink">{title}</div>
      <div className="mt-1 font-mono text-[9px] uppercase tracking-widest text-ink-soft">{sub}</div>
    </div>
  );
}
