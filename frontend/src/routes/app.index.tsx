import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Flame, Sparkles, Target } from "lucide-react";

import { PageBody, PageHeader } from "@/components/app/AppShell";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export const Route = createFileRoute("/app/")({
  head: () => ({ meta: [{ title: "Dashboard — ExamSensei" }] }),
  component: Dashboard,
});

function Dashboard() {
  const { user } = useAuth();
  const enabled = Boolean(user?.id);
  const userId = user?.id ?? "";

  const me = useQuery({
    queryKey: ["me"],
    queryFn: api.getMe,
    enabled,
  });
  const recs = useQuery({
    queryKey: ["recommendations", userId],
    queryFn: () => api.getRecommendations(userId),
    enabled,
  });
  const game = useQuery({
    queryKey: ["gamification", userId],
    queryFn: () => api.getGamification(userId),
    enabled,
  });

  const displayName =
    me.data?.name?.trim() || me.data?.email.split("@")[0] || "aspirant";
  const careerPaths = me.data?.career_paths ?? [];
  const activeExams = me.data?.active_exams ?? [];
  const profileIncomplete = careerPaths.length === 0 || activeExams.length === 0;

  return (
    <>
      <PageHeader
        number="03"
        eyebrow="Today's atlas"
        title={
          <>
            Welcome back,<br />
            <em className="not-italic text-ember">{displayName}.</em>
          </>
        }
        subtitle="Your prioritized topics, recommendations, and streak — at a glance."
      />

      <PageBody>
        {/* Gamification strip */}
        <div className="grid grid-cols-1 gap-px overflow-hidden rounded-2xl border border-ink/10 bg-ink/10 sm:grid-cols-3">
          <Stat icon={Sparkles} label="Level" value={fmtInt(game.data?.level, "—")} loading={game.isLoading} />
          <Stat icon={Target} label="XP" value={fmtInt(game.data?.xp_points, "0")} loading={game.isLoading} />
          <Stat icon={Flame} label="Streak (days)" value={fmtInt(game.data?.streak_days, "0")} loading={game.isLoading} />
        </div>

        {/* Profile-completion nudge */}
        {me.data && profileIncomplete ? (
          <Link
            to="/app/profile"
            className="mt-8 block rounded-2xl border border-ember/40 bg-ember/5 p-6 transition-colors hover:bg-ember/10"
          >
            <div className="eyebrow text-ember">Finish your profile</div>
            <p className="mt-2 font-display text-xl text-ink">
              Pick your career paths + target exams to unlock real recommendations →
            </p>
          </Link>
        ) : null}

        <div className="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-3">
          {/* Recommendations */}
          <section className="lg:col-span-2">
            <SectionHeading caption="04" title="Recommendations" />
            {recs.isLoading ? (
              <p className="text-ink-dim">Composing your recommendations…</p>
            ) : recs.error ? (
              <p className="text-ink-dim">Couldn't load recommendations.</p>
            ) : recs.data && recs.data.recommendations.length === 0 ? (
              <p className="text-ink-dim">
                We need a little more from you first.{" "}
                <Link to="/app/profile" className="text-ember underline-offset-4 hover:underline">
                  Add your career paths and target exams →
                </Link>
              </p>
            ) : (
              <ul className="divide-y divide-ink/10 border-y border-ink/10">
                {recs.data?.recommendations.map((r, i) => (
                  <li key={`${r.type}-${i}`} className="py-5">
                    <div className="flex items-baseline justify-between gap-4">
                      <div className="font-display text-lg text-ink">{r.exam ?? r.type.replace(/_/g, " ")}</div>
                      <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                        {r.type.replace(/_/g, " ")}
                      </div>
                    </div>
                    <p className="mt-2 text-[14px] text-ink-dim">{r.reasoning}</p>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* Next actions */}
          <section>
            <SectionHeading caption="05" title="Next actions" />
            {recs.data?.next_actions?.length ? (
              <ul className="space-y-3">
                {recs.data.next_actions.map((a, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-ember" />
                    <span className="text-[14px] text-ink">{a}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-ink-dim">Set your profile to see your next moves.</p>
            )}
          </section>
        </div>
      </PageBody>
    </>
  );
}

function Stat({
  icon: Icon,
  label,
  value,
  loading,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  loading?: boolean;
}) {
  return (
    <div className="bg-paper px-6 py-7">
      <div className="flex items-center gap-2 text-ink-soft">
        <Icon className="h-4 w-4" />
        <span className="font-mono text-[10px] uppercase tracking-widest">{label}</span>
      </div>
      <div className="display mt-3 text-4xl text-ink">{loading ? "…" : value}</div>
    </div>
  );
}

function SectionHeading({ caption, title }: { caption: string; title: string }) {
  return (
    <div className="mb-6">
      <div className="eyebrow">№ {caption}</div>
      <h2 className="display mt-2 text-2xl text-ink">{title}</h2>
    </div>
  );
}

function fmtInt(n: number | undefined, fallback: string): string {
  return typeof n === "number" ? String(n) : fallback;
}
