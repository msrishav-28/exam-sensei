import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { z } from "zod";

import { PageBody, PageHeader } from "@/components/app/AppShell";
import { api, type StudyPlan } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const searchSchema = z.object({ exam: z.string().optional() });

export const Route = createFileRoute("/app/study-plan")({
  head: () => ({ meta: [{ title: "Study plan — ExamSensei" }] }),
  validateSearch: (s) => searchSchema.parse(s),
  component: StudyPlanPage,
});

function StudyPlanPage() {
  const { user } = useAuth();
  const userId = user?.id ?? "";
  const { exam: presetExam } = Route.useSearch();

  const exams = useQuery({
    queryKey: ["exams"],
    queryFn: () => api.listExams({ limit: 200 }),
  });

  const [examCode, setExamCode] = useState<string>(presetExam ?? "");
  const [days, setDays] = useState<number>(90);

  // Default to the first exam once loaded, unless a preset is set.
  useEffect(() => {
    if (!examCode && exams.data && exams.data.length > 0) {
      setExamCode(exams.data[0].code);
    }
  }, [examCode, exams.data]);

  const generate = useMutation({
    mutationFn: () => api.generateStudyPlan(userId, examCode, days),
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : "Couldn't generate plan."),
  });

  const plan = generate.data;

  return (
    <>
      <PageHeader
        number="09"
        eyebrow="Atlas builder"
        title={
          <>
            Build your<br />
            <em className="not-italic text-ember">study plan.</em>
          </>
        }
        subtitle="Pick an exam, tell us how many days you have. We'll prioritize topics by weightage and your weak spots."
      />

      <PageBody>
        <div className="grid grid-cols-1 gap-4 rounded-2xl border border-ink/10 bg-paper-2/40 p-6 md:grid-cols-12 md:items-end md:gap-6">
          <label className="md:col-span-6">
            <span className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
              Exam
            </span>
            <select
              value={examCode}
              onChange={(e) => setExamCode(e.target.value)}
              className="mt-1 w-full appearance-none border-b border-ink/30 bg-transparent py-3 font-display text-lg text-ink focus:border-ember focus:outline-none"
            >
              {!exams.data?.length ? <option value="">Loading…</option> : null}
              {exams.data?.map((e) => (
                <option key={e.code} value={e.code} className="text-ink">
                  {e.name}
                </option>
              ))}
            </select>
          </label>

          <label className="md:col-span-3">
            <span className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
              Days available
            </span>
            <input
              type="number"
              min={7}
              max={365}
              value={days}
              onChange={(e) => setDays(Math.max(1, Number(e.target.value) || 0))}
              className="mt-1 w-full border-b border-ink/30 bg-transparent py-3 font-display text-lg text-ink focus:border-ember focus:outline-none"
            />
          </label>

          <div className="md:col-span-3">
            <button
              onClick={() => examCode && generate.mutate()}
              disabled={!examCode || generate.isPending || !userId}
              className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-ink px-6 py-3 text-[13px] font-medium text-paper transition-colors hover:bg-ember disabled:opacity-60"
            >
              {generate.isPending ? "Building…" : "Generate plan →"}
            </button>
          </div>
        </div>

        {plan ? <PlanView plan={plan} /> : null}
      </PageBody>
    </>
  );
}

function PlanView({ plan }: { plan: StudyPlan }) {
  if (plan.error) {
    return <p className="mt-10 text-ink-dim">{plan.error}</p>;
  }
  return (
    <div className="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-3">
      <section className="lg:col-span-2">
        <SectionHeading caption="10" title="Prioritized topics" />
        {plan.prioritized_topics.length === 0 ? (
          <p className="text-ink-dim">No topics indexed yet for this exam.</p>
        ) : (
          <ul className="divide-y divide-ink/10 border-y border-ink/10">
            {plan.prioritized_topics.map((t, i) => (
              <li key={`${t.name}-${i}`} className="grid grid-cols-12 items-baseline gap-3 py-4">
                <div className="col-span-1 font-mono text-[11px] text-ink-soft">
                  {String(i + 1).padStart(2, "0")}
                </div>
                <div className="col-span-7">
                  <div className="font-display text-lg text-ink">
                    {t.name.replace(/_/g, " ")}
                  </div>
                  <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                    {t.subject} · {t.difficulty}
                  </div>
                </div>
                <div className="col-span-2 text-right text-[13px] text-ink">
                  ~{t.estimated_days}d
                </div>
                <div className="col-span-2 text-right">
                  <span className="rounded-full bg-ember/10 px-2.5 py-1 font-mono text-[10px] uppercase tracking-widest text-ember">
                    {t.weightage}% weight
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <aside>
        <SectionHeading caption="11" title="Weekly cadence" />
        <div className="rounded-2xl border border-ink/10 bg-paper-2/40 p-2">
          {Object.entries(plan.weekly_plan).slice(0, 6).map(([week, items]) => (
            <details key={week} className="group border-b border-ink/10 last:border-0">
              <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-[13px] text-ink">
                <span className="font-mono text-[11px] uppercase tracking-widest text-ink-soft">
                  {week.replace(/_/g, " ")}
                </span>
                <span className="text-ink-dim group-open:rotate-90 transition-transform">→</span>
              </summary>
              <ul className="space-y-1 px-4 pb-3 text-[12px] text-ink-dim">
                {items.map((it, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-ember" />
                    <span>
                      <span className="text-ink">{it.topic.replace(/_/g, " ")}</span> ·{" "}
                      {it.estimated_hours}h · {it.difficulty}
                    </span>
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </div>
        <p className="mt-4 font-mono text-[10px] uppercase tracking-widest text-ink-soft">
          Success probability ·{" "}
          <span className="text-ember">
            {Math.round((plan.success_probability ?? 0) * 100)}%
          </span>
        </p>
      </aside>
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
