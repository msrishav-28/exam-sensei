import { Link } from "@tanstack/react-router";
import type { ReactNode } from "react";

interface AuthLayoutProps {
  number: string;        // e.g. "01" / "02"
  eyebrow: string;       // section caption
  title: ReactNode;      // display headline (string or JSX)
  subtitle?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}

/**
 * Editorial frame matching the landing — paper background, grain overlay,
 * marginalia eyebrow, oversized display headline, ember accents.
 */
export function AuthLayout({ number, eyebrow, title, subtitle, children, footer }: AuthLayoutProps) {
  return (
    <div className="relative min-h-screen bg-paper text-ink">
      <div className="grain" aria-hidden />

      {/* Top marginalia */}
      <header className="absolute inset-x-0 top-0 z-10">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between px-6 py-5 md:px-12">
          <Link to="/" className="flex items-center gap-2.5">
            <svg width="22" height="22" viewBox="0 0 22 22" aria-hidden>
              <circle cx="11" cy="11" r="10" fill="none" stroke="currentColor" strokeWidth="1" />
              <circle cx="11" cy="11" r="3" fill="var(--color-ember)" />
              <path
                d="M11 1 L11 21 M1 11 L21 11"
                stroke="currentColor"
                strokeWidth="0.5"
                opacity="0.5"
              />
            </svg>
            <span className="font-display text-[15px] font-medium leading-none tracking-tight">
              ExamSensei
            </span>
          </Link>
          <div className="eyebrow">№ {number} / Access</div>
        </div>
      </header>

      <main className="relative z-10 mx-auto flex min-h-screen max-w-[1400px] items-center px-6 py-24 md:px-12">
        <div className="grid w-full grid-cols-1 gap-16 lg:grid-cols-12 lg:gap-12">
          {/* Editorial column — eyebrow + display headline */}
          <section className="lg:col-span-5">
            <div className="eyebrow">{eyebrow}</div>
            <div className="mt-3 h-px w-12 bg-ink/40" />
            <h1 className="display mt-8 text-[clamp(2.2rem,5vw,4.4rem)] text-ink">{title}</h1>
            {subtitle ? (
              <p className="mt-6 max-w-md text-[15px] leading-relaxed text-ink-dim">{subtitle}</p>
            ) : null}
          </section>

          {/* Form column */}
          <section className="lg:col-span-6 lg:col-start-7">
            <div className="rounded-2xl border border-ink/10 bg-paper-2/40 p-6 backdrop-blur-sm md:p-10">
              {children}
              {footer ? <div className="mt-8 border-t border-ink/10 pt-6">{footer}</div> : null}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
