import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

const text =
  "Most aspirants drown in syllabi. They read every chapter equally, mock every test the same way, and lose months to topics that won't matter. ExamSensei studies a decade of question papers, watches how you answer, and quietly tells you the next thing worth your hour.";

function Word({ word, i, total, progress }: { word: string; i: number; total: number; progress: any }) {
  const start = i / total;
  const end = start + 1 / total;
  const opacity = useTransform(progress, [start, end], [0.15, 1]);
  return (
    <motion.span style={{ opacity }} className="inline-block mr-[0.25em]">
      {word}
    </motion.span>
  );
}

export function Manifesto() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 0.9", "start 0.15"] });
  const words = text.split(" ");

  return (
    <section ref={ref} id="manifesto" className="relative bg-paper py-40 md:py-56">
      <div className="mx-auto max-w-[1400px] px-6 md:px-12">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 md:col-span-3">
            <div className="eyebrow">№ 02 / Thesis</div>
            <div className="mt-3 font-mono text-[11px] text-ink-soft">
              Why most prep<br/>fails the median<br/>aspirant.
            </div>
          </div>
          <div className="col-span-12 md:col-span-9">
            <p className="display text-[clamp(1.8rem,3.8vw,3.4rem)] leading-[1.05] text-ink">
              {words.map((w, i) => (
                <Word key={i} word={w} i={i} total={words.length} progress={scrollYProgress} />
              ))}
            </p>
            <div className="mt-12 flex items-center gap-6">
              <div className="h-px flex-1 bg-ink/15" />
              <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                Signed, the build team
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
