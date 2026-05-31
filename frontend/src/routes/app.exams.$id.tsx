import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Calendar } from "lucide-react";

import { PageBody, PageHeader } from "@/components/app/AppShell";
import { api } from "@/lib/api";

export const Route = createFileRoute("/app/exams/$id")({
  head: () => ({ meta: [{ title: "Exam — ExamSensei" }] }),
  component: ExamDetail,
});

function ExamDetail() {
  const { id } = Route.useParams();
  const examId = Number(id);
  const exam = useQuery({
    queryKey: ["exam", examId],
    queryFn: () => api.getExam(examId),
    enabled: Number.isFinite(examId),
  });

  const dates = (exam.data?.important_dates ?? {}) as Record<string, unknown>;
  const examDates = (dates.exam_dates as string[] | undefined) ?? [];

  return (
    <>
      <PageHeader
        number="07"
        eyebrow={exam.data?.body ?? "Exam"}
        title={exam.data?.name ?? "—"}
        subtitle={exam.data?.exam_type?.replace(/_/g, " ")}
        action={
          exam.data ? (
            <Link
              to="/app/study-plan"
              search={{ exam: exam.data.code }}
              className="inline-flex items-center gap-2 rounded-full bg-ink px-5 py-2.5 text-[12px] font-medium text-paper transition-colors hover:bg-ember"
            >
              Generate study plan →
            </Link>
          ) : null
        }
      />

      <PageBody>
        <Link
          to="/app/exams"
          className="mb-8 inline-flex items-center gap-2 text-[12px] text-ink-dim hover:text-ink"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to exams
        </Link>

        {exam.isLoading ? (
          <p className="text-ink-dim">Loading exam…</p>
        ) : exam.error || !exam.data ? (
          <p className="text-ink-dim">Couldn't find that exam.</p>
        ) : (
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-3">
            <section className="lg:col-span-2">
              <SectionHeading caption="Code" title={exam.data.code} />
              <div className="prose-sm max-w-none text-[14px] leading-relaxed text-ink-dim">
                Tap <em>Generate study plan</em> to get a prioritized topic list for the days
                you have available. Your mentor can answer questions about syllabus, weightage,
                and last year's paper.
              </div>
            </section>

            <aside className="space-y-8">
              <div>
                <SectionHeading caption="Important dates" title="Calendar" />
                {Object.keys(dates).length === 0 ? (
                  <p className="text-[14px] text-ink-dim">Dates will appear once we refresh this exam.</p>
                ) : (
                  <ul className="space-y-3">
                    {Object.entries(dates).map(([k, v]) => (
                      <li key={k} className="border-b border-ink/10 pb-3 last:border-0">
                        <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                          {k.replace(/_/g, " ")}
                        </div>
                        <div className="mt-1 flex items-start gap-2 text-[14px] text-ink">
                          <Calendar className="mt-0.5 h-3.5 w-3.5 text-ember" />
                          <span>{formatDateValue(v)}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
                {examDates.length > 1 ? (
                  <p className="mt-4 text-[12px] text-ink-soft">
                    {examDates.length} scheduled exam slots.
                  </p>
                ) : null}
              </div>
            </aside>
          </div>
        )}
      </PageBody>
    </>
  );
}

function SectionHeading({ caption, title }: { caption: string; title: string }) {
  return (
    <div className="mb-4">
      <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">{caption}</div>
      <h2 className="display mt-1 text-xl text-ink">{title}</h2>
    </div>
  );
}

function formatDateValue(v: unknown): string {
  if (Array.isArray(v)) return v.join(", ");
  if (typeof v === "string" || typeof v === "number") return String(v);
  return JSON.stringify(v);
}
