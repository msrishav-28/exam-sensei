import { Link } from "@tanstack/react-router";

export function Nav() {
  return (
    <header className="fixed inset-x-0 top-0 z-50">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between px-6 py-5 md:px-12">
        <Link to="/" className="flex items-center gap-2.5 text-ink">
          <svg width="22" height="22" viewBox="0 0 22 22" aria-hidden>
            <circle cx="11" cy="11" r="10" fill="none" stroke="currentColor" strokeWidth="1" />
            <circle cx="11" cy="11" r="3" fill="var(--color-ember)" />
            <path d="M11 1 L11 21 M1 11 L21 11" stroke="currentColor" strokeWidth="0.5" opacity="0.5" />
          </svg>
          <span className="font-display text-[15px] font-medium leading-none tracking-tight">ExamSensei</span>
          <span className="eyebrow ml-2 hidden md:inline">v.2026.1</span>
        </Link>
        <nav className="hidden items-center gap-9 text-[12px] text-ink/70 md:flex">
          <a href="#atlas" className="hover:text-ember transition-colors">The Atlas</a>
          <a href="#mentor" className="hover:text-ember transition-colors">Mentor</a>
          <a href="#calendar" className="hover:text-ember transition-colors">Calendar</a>
          <a href="#console" className="hover:text-ember transition-colors">Chat</a>
          <a href="#proof" className="hover:text-ember transition-colors">Aspirants</a>
        </nav>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="hidden text-[12px] text-ink-dim hover:text-ember md:inline"
          >
            Sign in
          </Link>
          <Link
            to="/signup"
            data-cursor="hover"
            className="group inline-flex items-center gap-2 rounded-full border border-ink/15 bg-paper px-4 py-2 text-[12px] font-medium text-ink transition-all hover:border-ink hover:bg-ink hover:text-paper"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-ember animate-ember" />
            Get early access
          </Link>
        </div>
      </div>
    </header>
  );
}
