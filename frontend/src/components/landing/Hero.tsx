import { useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { AtlasScene } from "./ConstellationScene";

const exams = ["JEE", "NEET", "UPSC", "CAT", "GATE", "CLAT", "NDA"];

export function Hero() {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    setReduced(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);



  return (
    <section className="relative h-[100svh] w-full overflow-hidden bg-paper">
      {/* The Atlas — 3D ink graph */}
      <div className="absolute inset-0">
        <AtlasScene reduced={reduced} />
      </div>

      {/* Editorial grid overlay — faint */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(to right, #0d0d0d 1px, transparent 1px), linear-gradient(to bottom, #0d0d0d 1px, transparent 1px)",
          backgroundSize: "80px 80px",
        }}
      />

      {/* Top marginalia */}
      <div className="absolute left-6 top-28 z-10 md:left-12 md:top-32">
        <div className="eyebrow">№ 01 / The Atlas</div>
        <div className="mt-2 h-px w-12 bg-ink/40" />
      </div>
      <div className="absolute right-6 top-28 z-10 hidden text-right md:right-12 md:top-32 md:block">
        <div className="eyebrow">Indexed · {new Date().getFullYear()}</div>
        <div className="font-mono text-[10px] mt-2 text-ink-soft">India's major exams · syllabus-indexed</div>
      </div>

      {/* Centerpiece */}
      <div className="relative z-10 flex h-full flex-col items-center justify-center px-6 text-center animate-fade-in">
        <div className="eyebrow mb-8">For the aspirant who's done guessing</div>

        <h1 className="display text-balance text-[clamp(2.6rem,8.8vw,8.4rem)] text-ink">
          Master what the exam<br />
          <span className="relative inline-block">
            <span className="italic font-display font-normal">actually</span>
            <svg
              aria-hidden
              viewBox="0 0 220 14"
              className="absolute -bottom-2 left-0 h-3 w-full"
              preserveAspectRatio="none"
            >
              <path
                d="M2 9 Q 55 1 110 7 T 218 6"
                stroke="var(--color-ember)"
                strokeWidth="2.5"
                fill="none"
                strokeLinecap="round"
              />
            </svg>
          </span>{" "}
          asks.
        </h1>

        <p className="mt-8 max-w-xl text-balance text-[15px] leading-relaxed text-ink-dim md:text-[17px]">
          ExamSensei reads a decade of past papers, learns your weak spots, and walks
          you to result day &mdash; one prioritized topic at a time.
        </p>

        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
          <Link
            to="/signup"
            data-cursor="hover"
            className="group inline-flex items-center gap-3 rounded-full bg-ink px-6 py-3 text-[13px] font-medium text-paper transition-all hover:bg-ember"
          >
            Start your atlas
            <span className="transition-transform group-hover:translate-x-1">→</span>
          </Link>
          <a
            href="#atlas"
            data-cursor="hover"
            className="text-[13px] text-ink-dim underline-offset-4 hover:text-ink hover:underline"
          >
            See how it works
          </a>
        </div>

        <div className="mt-14 flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
          <span className="eyebrow">Built for</span>
          {exams.map((e) => (
            <span key={e} className="font-mono text-[11px] uppercase tracking-widest text-ink">
              {e}
            </span>
          ))}
        </div>
      </div>

      {/* Bottom scroll cue */}
      <div className="absolute inset-x-0 bottom-6 z-10 flex flex-col items-center gap-3">
        <div className="eyebrow text-[10px]">Scroll</div>
        <div className="h-8 w-px bg-gradient-to-b from-ink/50 to-transparent" />
      </div>
    </section>
  );
}
