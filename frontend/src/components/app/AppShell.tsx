import { Link, Outlet, useLocation, useNavigate } from "@tanstack/react-router";
import {
  Brain,
  Calendar,
  LayoutGrid,
  LogOut,
  MessageSquare,
  User as UserIcon,
} from "lucide-react";
import { useEffect, type ReactNode } from "react";

import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

const NAV = [
  { to: "/app", icon: LayoutGrid, label: "Dashboard", exact: true },
  { to: "/app/exams", icon: Calendar, label: "Exams" },
  { to: "/app/chat", icon: MessageSquare, label: "AI mentor" },
  { to: "/app/study-plan", icon: Brain, label: "Study plan" },
  { to: "/app/profile", icon: UserIcon, label: "Profile" },
] as const;

/**
 * Authenticated app frame. Client-side auth guard (the route's beforeLoad
 * can't read Supabase's localStorage during SSR), Paper & Ink sidebar +
 * topbar matching the landing's editorial language.
 */
export function AppShell() {
  const { session, loading, signOut, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!loading && !session) {
      navigate({ to: "/login" });
    }
  }, [loading, session, navigate]);

  if (loading || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-paper text-ink">
        <div className="text-center">
          <div className="eyebrow">Verifying session</div>
          <div className="mt-2 h-px w-12 bg-ink/20 mx-auto" />
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-paper text-ink">
      <div className="grain" aria-hidden />

      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-60 border-r border-ink/10 bg-paper-2/40 backdrop-blur-sm md:flex md:flex-col">
        <div className="flex h-16 items-center gap-2.5 border-b border-ink/10 px-6">
          <Link to="/" className="flex items-center gap-2.5">
            <svg width="20" height="20" viewBox="0 0 22 22" aria-hidden>
              <circle cx="11" cy="11" r="10" fill="none" stroke="currentColor" strokeWidth="1" />
              <circle cx="11" cy="11" r="3" fill="var(--color-ember)" />
            </svg>
            <span className="font-display text-[14px] font-medium tracking-tight">ExamSensei</span>
          </Link>
        </div>
        <nav className="flex-1 px-3 py-6">
          <ul className="space-y-1">
            {NAV.map((item) => {
              const active = item.exact
                ? location.pathname === item.to
                : location.pathname.startsWith(item.to);
              return (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    className={cn(
                      "group flex items-center gap-3 rounded-lg px-3 py-2 text-[13px] transition-colors",
                      active
                        ? "bg-ink text-paper"
                        : "text-ink-dim hover:bg-ink/5 hover:text-ink",
                    )}
                  >
                    <item.icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        <div className="border-t border-ink/10 px-3 py-4">
          <div className="px-3 py-2">
            <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
              Signed in
            </div>
            <div className="mt-1 truncate text-[13px] text-ink">{user?.email}</div>
          </div>
          <button
            onClick={() => signOut().then(() => navigate({ to: "/" }))}
            className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-[13px] text-ink-dim transition-colors hover:bg-ink/5 hover:text-ink"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Mobile top bar */}
      <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-ink/10 bg-paper/90 px-4 backdrop-blur-md md:hidden">
        <Link to="/" className="flex items-center gap-2 font-display text-[14px]">
          <svg width="18" height="18" viewBox="0 0 22 22" aria-hidden>
            <circle cx="11" cy="11" r="10" fill="none" stroke="currentColor" strokeWidth="1" />
            <circle cx="11" cy="11" r="3" fill="var(--color-ember)" />
          </svg>
          ExamSensei
        </Link>
        <button
          onClick={() => signOut().then(() => navigate({ to: "/" }))}
          className="text-[12px] text-ink-dim hover:text-ink"
        >
          Sign out
        </button>
      </header>
      {/* Mobile bottom nav */}
      <nav className="fixed inset-x-0 bottom-0 z-20 flex border-t border-ink/10 bg-paper/95 backdrop-blur-md md:hidden">
        {NAV.map((item) => {
          const active = item.exact
            ? location.pathname === item.to
            : location.pathname.startsWith(item.to);
          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                "flex flex-1 flex-col items-center gap-1 py-2 text-[10px]",
                active ? "text-ember" : "text-ink-dim",
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <main className="relative z-10 pb-20 md:ml-60 md:pb-0">
        <Outlet />
      </main>
    </div>
  );
}

// Page shell — title block used by every screen for visual consistency
export function PageHeader({
  number,
  eyebrow,
  title,
  subtitle,
  action,
}: {
  number: string;
  eyebrow: string;
  title: ReactNode;
  subtitle?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="mx-auto max-w-[1400px] px-6 pb-8 pt-10 md:px-12 md:pb-10 md:pt-16">
      <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="eyebrow">№ {number} / {eyebrow}</div>
          <div className="mt-2 h-px w-12 bg-ink/30" />
          <h1 className="display mt-6 text-[clamp(1.8rem,3.6vw,3.2rem)] text-ink">{title}</h1>
          {subtitle ? (
            <p className="mt-3 max-w-2xl text-[14px] text-ink-dim md:text-[15px]">{subtitle}</p>
          ) : null}
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
    </div>
  );
}

export function PageBody({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto max-w-[1400px] px-6 pb-16 md:px-12">{children}</div>
  );
}
