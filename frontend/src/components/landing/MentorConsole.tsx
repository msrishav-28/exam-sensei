import { useEffect, useState } from "react";

const script: { who: "you" | "sensei"; text: string; pause?: number }[] = [
  { who: "you",    text: "explain bernoulli like i'm tired", pause: 600 },
  { who: "sensei", text: "Fast fluid → low pressure. Slow fluid → high pressure. Energy is conserved along the streamline.", pause: 900 },
  { who: "you",    text: "give me one JEE-style problem on it", pause: 700 },
  { who: "sensei", text: "Water flows through a horizontal pipe. Section A: 8 cm², 3 m/s. Section B: 2 cm². Find v_B and the pressure drop. (ρ = 1000)", pause: 1200 },
  { who: "you",    text: "i keep messing the units", pause: 500 },
  { who: "sensei", text: "Noted. I've added a 5-min units drill to tomorrow. You're now 3 wins from a 7-day streak.", pause: 900 },
];

export function MentorConsole() {
  const [lines, setLines] = useState<typeof script>([]);
  const [typing, setTyping] = useState("");
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    if (idx >= script.length) return;
    const step = script[idx];
    let i = 0;
    setTyping("");
    const typer = setInterval(() => {
      i++;
      setTyping(step.text.slice(0, i));
      if (i >= step.text.length) {
        clearInterval(typer);
        setTimeout(() => {
          setLines((l) => [...l, step]);
          setTyping("");
          setIdx((x) => x + 1);
        }, step.pause ?? 500);
      }
    }, step.who === "sensei" ? 18 : 38);
    return () => clearInterval(typer);
  }, [idx]);

  // loop
  useEffect(() => {
    if (idx >= script.length) {
      const t = setTimeout(() => { setLines([]); setIdx(0); }, 3000);
      return () => clearTimeout(t);
    }
  }, [idx]);

  const current = idx < script.length ? script[idx] : null;

  return (
    <section id="console" className="relative bg-paper py-32 md:py-44">
      <div className="mx-auto max-w-[1600px] px-6 md:px-12">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 md:col-span-4">
            <div className="eyebrow">№ 06 / Mentor on call</div>
            <h2 className="display mt-4 text-[clamp(2.2rem,4.6vw,4.2rem)] text-ink">
              Ask anything.<br/>
              <em className="not-italic text-ember">In your words.</em>
            </h2>
            <p className="mt-6 max-w-md text-[15px] leading-relaxed text-ink-dim">
              A private LLM mentor that knows your syllabus, your weak spots, and your
              streak. Hinglish, English, broken sentences — it just answers, then
              quietly updates your plan.
            </p>
            <ul className="mt-8 space-y-3 text-[13px] text-ink-dim">
              <li className="flex items-start gap-3">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-ember" />
                Cited from NCERT + previous-year papers
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-ember" />
                Runs locally · your questions don't leave the device
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-ember" />
                Every chat refines your atlas
              </li>
            </ul>
          </div>

          <div className="col-span-12 md:col-span-8">
            <div className="overflow-hidden rounded-sm border border-ink/15 bg-ink text-paper shadow-[0_30px_60px_-30px_rgba(13,13,13,0.4)]">
              <div className="flex items-center justify-between border-b border-paper/10 px-5 py-3">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-ember" />
                  <span className="h-2.5 w-2.5 rounded-full bg-paper/30" />
                  <span className="h-2.5 w-2.5 rounded-full bg-paper/30" />
                </div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-paper/50">
                  sensei · session 1,438
                </div>
              </div>
              <div className="min-h-[420px] space-y-5 px-5 py-6 font-mono text-[13px] md:px-8 md:py-8">
                {lines.map((l, i) => <Line key={i} line={l} done />)}
                {current && (
                  <Line line={{ who: current.who, text: typing }} />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Line({ line, done }: { line: { who: "you" | "sensei"; text: string }; done?: boolean }) {
  const label = line.who === "you" ? "you" : "sensei";
  return (
    <div>
      <div className={`mb-1 text-[10px] uppercase tracking-widest ${line.who === "sensei" ? "text-ember" : "text-paper/50"}`}>
        ▸ {label}
      </div>
      <div className={`font-display text-[15px] leading-relaxed md:text-[17px] ${line.who === "sensei" ? "text-paper" : "text-paper/80"}`}>
        {line.text}
        {!done && <span className="caret-blink ml-0.5 inline-block h-[1em] w-[0.5ch] -mb-1 bg-ember align-middle" />}
      </div>
    </div>
  );
}
