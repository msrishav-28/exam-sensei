import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Search } from "lucide-react";

import { PageBody, PageHeader } from "@/components/app/AppShell";
import { api, type Exam } from "@/lib/api";

export const Route = createFileRoute("/app/exams")({
  head: () => ({ meta: [{ title: "Exams — ExamSensei" }] }),
  component: ExamsPage,
});

function ExamsPage() {
  const [q, setQ] = useState("");
  const [type, setType] = useState<string | null>(null);

  const exams = useQuery({
    queryKey: ["exams"],
    queryFn: () => api.listExams({ limit: 200 }),
  });

  const types = useMemo(() => {
    const all = new Set<string>();
    exams.data?.forEach((e) => e.exam_type && all.add(e.exam_type));
    return Array.from(all).sort();
  }, [exams.data]);

  const filtered = useMemo<Exam[]>(() => {
    if (!exams.data) return [];
    const needle = q.trim().toLowerCase();
    return exams.data.filter((e) => {
      if (type && e.exam_type !== type) return false;
      if (!needle) return true;
      return (
        e.name.toLowerCase().includes(needle) ||
        e.code.toLowerCase().includes(needle) ||
        e.body?.toLowerCase().includes(needle)
      );
    });
  }, [exams.data, q, type]);

  return (
    <>
      <PageHeader
        number="06"
        eyebrow="The catalogue"
        title={
          <>
            Every exam,<br />
            <em className="not-italic text-ember">indexed.</em>
          </>
        }
        subtitle="Browse the exam bodies we track. Tap one for dates and a one-click study plan."
      />

      <PageBody>
        {/* Toolbar */}
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="relative w-full md:max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-soft" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search exams"
              className="w-full rounded-full border border-ink/15 bg-paper-2/40 py-2.5 pl-9 pr-4 text-[13px] text-ink placeholder:text-ink-soft focus:border-ember focus:outline-none"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <Chip active={type === null} onClick={() => setType(null)}>All</Chip>
            {types.map((t) => (
              <Chip key={t} active={type === t} onClick={() => setType(t)}>
                {t.replace(/_/g, " ")}
              </Chip>
            ))}
          </div>
        </div>

        {/* Results */}
        {exams.isLoading ? (
          <p className="text-ink-dim">Loading exams…</p>
        ) : exams.error ? (
          <p className="text-ink-dim">Couldn't load exams.</p>
        ) : filtered.length === 0 ? (
          <p className="text-ink-dim">No matches. Try a different filter.</p>
        ) : (
          <div className="grid grid-cols-1 gap-px overflow-hidden rounded-2xl border border-ink/10 bg-ink/10 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((exam) => (
              <Link
                key={exam.id}
                to="/app/exams/$id"
                params={{ id: String(exam.id) }}
                className="group flex flex-col gap-3 bg-paper p-6 transition-colors hover:bg-paper-2/60"
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                    {exam.body}
                  </span>
                  <span className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
                    {exam.exam_type?.replace(/_/g, " ")}
                  </span>
                </div>
                <div className="font-display text-xl text-ink">{exam.name}</div>
                <div className="mt-auto text-[12px] text-ink-dim group-hover:text-ember">
                  View details →
                </div>
              </Link>
            ))}
          </div>
        )}
      </PageBody>
    </>
  );
}

function Chip({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={
        "rounded-full border px-3 py-1.5 text-[11px] uppercase tracking-widest transition-colors " +
        (active
          ? "border-ink bg-ink text-paper"
          : "border-ink/15 bg-paper text-ink-dim hover:border-ink/40 hover:text-ink")
      }
    >
      {children}
    </button>
  );
}
