import { useEffect, useState } from "react";

export function Cursor() {
  const [pos, setPos] = useState({ x: -100, y: -100 });
  const [hover, setHover] = useState(false);
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    const isTouch = window.matchMedia("(pointer: coarse)").matches;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (isTouch || reduce) return;
    setEnabled(true);

    const move = (e: MouseEvent) => setPos({ x: e.clientX, y: e.clientY });
    const over = (e: MouseEvent) => {
      const t = e.target as HTMLElement;
      setHover(!!t.closest("a, button, [data-cursor='hover']"));
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseover", over);
    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseover", over);
    };
  }, []);

  if (!enabled) return null;
  return (
    <>
      <div
        aria-hidden
        className="pointer-events-none fixed z-[100] rounded-full transition-[width,height,opacity] duration-200 ease-out"
        style={{
          left: pos.x,
          top: pos.y,
          width: hover ? 38 : 8,
          height: hover ? 38 : 8,
          transform: "translate(-50%, -50%)",
          background: hover ? "transparent" : "var(--color-ember)",
          border: hover ? "1px solid var(--color-ember)" : "none",
          mixBlendMode: "difference",
        }}
      />
    </>
  );
}
