import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "@tanstack/react-router";

export function FinalCTA() {
  const btnRef = useRef<HTMLButtonElement>(null);
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [exam, setExam] = useState("JEE");

  const onMove = (e: React.MouseEvent) => {
    const btn = btnRef.current;
    if (!btn) return;
    const r = btn.getBoundingClientRect();
    const x = e.clientX - (r.left + r.width / 2);
    const y = e.clientY - (r.top + r.height / 2);
    btn.style.transform = `translate(${x * 0.22}px, ${y * 0.30}px)`;
  };
  const onLeave = () => { if (btnRef.current) btnRef.current.style.transform = ""; };

  // Real submit — routes into /signup with email + exam prefilled.
  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate({ to: "/signup", search: { email: email || undefined, exam } });
  };

  return (
    <section id="access" className="relative overflow-hidden bg-ink py-32 text-paper md:py-48">
      {/* ember corner wash */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(60% 50% at 100% 0%, color-mix(in oklab, var(--color-ember) 35%, transparent), transparent 60%)",
        }}
      />
      {/* faint grid */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage:
            "linear-gradient(to right, #f5f3ee 1px, transparent 1px), linear-gradient(to bottom, #f5f3ee 1px, transparent 1px)",
          backgroundSize: "80px 80px",
        }}
      />

      <div className="relative mx-auto max-w-[1400px] px-6 md:px-12">
        <div className="eyebrow" style={{ color: "color-mix(in oklab, var(--color-paper) 60%, transparent)" }}>
          № 10 / Begin
        </div>

        <motion.h2
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
          className="display mt-6 max-w-5xl text-[clamp(2.8rem,9vw,8.2rem)] text-paper"
        >
          The exam is a date.<br/>
          <em className="not-italic text-ember">Tomorrow is a choice.</em>
        </motion.h2>

        <p className="mt-10 max-w-xl text-[16px] leading-relaxed text-paper/70">
          Tell us which exam you're chasing. We'll create your atlas and pull together
          your first prioritized plan in a couple of minutes.
        </p>

        <form
          onSubmit={onSubmit}
          className="mt-14 grid w-full max-w-3xl grid-cols-12 gap-3"
        >
          <div className="col-span-12 sm:col-span-4">
            <label className="font-mono text-[10px] uppercase tracking-widest text-paper/50">Target exam</label>
            <select
              value={exam}
              onChange={(e) => setExam(e.target.value)}
              className="mt-2 w-full appearance-none border-b border-paper/30 bg-transparent py-3 font-display text-lg text-paper outline-none focus:border-ember"
            >
              {["JEE", "NEET", "UPSC", "CAT", "GATE", "CUET", "CLAT", "NDA"].map((e) => (
                <option key={e} value={e} className="text-ink">{e}</option>
              ))}
            </select>
          </div>
          <div className="col-span-12 sm:col-span-5">
            <label className="font-mono text-[10px] uppercase tracking-widest text-paper/50">Your email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@school.edu"
              className="mt-2 w-full border-b border-paper/30 bg-transparent py-3 font-display text-lg text-paper placeholder:text-paper/30 focus:border-ember focus:outline-none"
            />
          </div>
          <div className="col-span-12 flex items-end sm:col-span-3">
            <button
              ref={btnRef}
              onMouseMove={onMove}
              onMouseLeave={onLeave}
              data-cursor="hover"
              className="w-full rounded-full bg-ember px-6 py-3 text-[13px] font-medium text-ink transition-colors hover:bg-paper"
              style={{ transition: "transform 0.4s cubic-bezier(0.22,1,0.36,1), background-color 0.3s" }}
            >
              Continue →
            </button>
          </div>
        </form>

        <div className="mt-10 flex flex-wrap items-center gap-x-6 gap-y-2 font-mono text-[10px] uppercase tracking-widest text-paper/50">
          <span>No spam · No upsells</span>
          <span>·</span>
          <span>Free while we're small</span>
          <span>·</span>
          <span>Made in India</span>
        </div>
      </div>
    </section>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-ink/10 bg-paper">
      <div className="mx-auto flex max-w-[1600px] flex-col gap-10 px-6 py-14 md:flex-row md:items-end md:justify-between md:px-12">
        <div>
          <div className="flex items-center gap-2.5">
            <svg width="22" height="22" viewBox="0 0 22 22" aria-hidden>
              <circle cx="11" cy="11" r="10" fill="none" stroke="currentColor" strokeWidth="1" />
              <circle cx="11" cy="11" r="3" fill="var(--color-ember)" />
            </svg>
            <span className="font-display text-xl text-ink">ExamSensei</span>
          </div>
          <div className="eyebrow mt-3">© MMXXVI · Built for the long game</div>
        </div>
        <div className="grid grid-cols-2 gap-x-12 gap-y-2 text-[13px] text-ink-dim md:grid-cols-3">
          <a href="#atlas" className="hover:text-ember">The Atlas</a>
          <a href="#mentor" className="hover:text-ember">Mentor</a>
          <a href="#calendar" className="hover:text-ember">Exam Calendar</a>
          <a href="#console" className="hover:text-ember">AI Chat</a>
          <a href="#proof" className="hover:text-ember">Aspirants</a>
          <a href="#faq" className="hover:text-ember">FAQ</a>
        </div>
        <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
          Set in Space Grotesk & DM Sans<br/>
          Built quietly · Delhi → everywhere
        </div>
      </div>
    </footer>
  );
}
