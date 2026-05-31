import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { PageBody, PageHeader } from "@/components/app/AppShell";
import { api, type ProfileUpdate, type UserProfile } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export const Route = createFileRoute("/app/profile")({
  head: () => ({ meta: [{ title: "Profile — ExamSensei" }] }),
  component: ProfilePage,
});

const CAREER_PATHS = [
  "engineering", "medical", "commerce", "science", "civil_services", "defense",
];

function ProfilePage() {
  const { user } = useAuth();
  const userId = user?.id ?? "";
  const qc = useQueryClient();

  const me = useQuery({
    queryKey: ["me"],
    queryFn: api.getMe,
    enabled: Boolean(userId),
  });
  const exams = useQuery({
    queryKey: ["exams"],
    queryFn: () => api.listExams({ limit: 200 }),
  });

  // Local form state; populated once `me` resolves.
  const [careerPaths, setCareerPaths] = useState<string[]>([]);
  const [activeExams, setActiveExams] = useState<string[]>([]);
  const [strengths, setStrengths] = useState("");
  const [weaknesses, setWeaknesses] = useState("");
  const [studyHours, setStudyHours] = useState<number>(4);

  useEffect(() => {
    if (!me.data) return;
    setCareerPaths(me.data.career_paths ?? []);
    setActiveExams(me.data.active_exams ?? []);
    // Strengths / weaknesses live inside preparation_profile, which /auth/me
    // doesn't return. We render them as empty by default and the PUT below
    // merges (it doesn't clobber what we don't send).
  }, [me.data]);

  const save = useMutation({
    mutationFn: (body: ProfileUpdate) => api.updateProfile(userId, body),
    onSuccess: () => {
      toast.success("Profile updated.");
      qc.invalidateQueries({ queryKey: ["me"] });
      qc.invalidateQueries({ queryKey: ["recommendations", userId] });
    },
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : "Couldn't save profile."),
  });

  function toggle(list: string[], value: string): string[] {
    return list.includes(value) ? list.filter((v) => v !== value) : [...list, value];
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const body: ProfileUpdate = {
      career_paths: careerPaths,
      active_exams: activeExams,
      study_hours_per_day: Number.isFinite(studyHours) ? studyHours : undefined,
    };
    const trim = (s: string) =>
      s.split(",").map((x) => x.trim()).filter(Boolean);
    if (strengths.trim()) body.strengths = trim(strengths);
    if (weaknesses.trim()) body.weaknesses = trim(weaknesses);
    save.mutate(body);
  }

  return (
    <>
      <PageHeader
        number="12"
        eyebrow="Your atlas, configured"
        title={
          <>
            Tell us what<br />
            <em className="not-italic text-ember">you're chasing.</em>
          </>
        }
        subtitle="Career paths + active exams power your recommendations. Strengths + weaknesses sharpen the study plan."
      />

      <PageBody>
        {me.isLoading ? (
          <p className="text-ink-dim">Loading your profile…</p>
        ) : me.error || !me.data ? (
          <p className="text-ink-dim">Couldn't load your profile.</p>
        ) : (
          <form onSubmit={onSubmit} className="space-y-10">
            <Section caption="Identity" title="Who you are">
              <DefBlock label="Name" value={me.data.name ?? "—"} />
              <DefBlock label="Email" value={me.data.email} />
              <DefBlock label="Current stage" value={me.data.current_stage.replace(/_/g, " ")} />
            </Section>

            <Section caption="Goals" title="Career paths">
              <p className="mb-4 text-[13px] text-ink-dim">
                Pick the directions you're seriously considering. Drives recommendations.
              </p>
              <ToggleList
                options={CAREER_PATHS.map((c) => ({
                  value: c,
                  label: c.replace(/_/g, " "),
                }))}
                selected={careerPaths}
                onToggle={(v) => setCareerPaths((p) => toggle(p, v))}
              />
            </Section>

            <Section caption="Targets" title="Active exams">
              <p className="mb-4 text-[13px] text-ink-dim">
                The exams you're prepping for now. Used by clash detection + study planner.
              </p>
              {exams.isLoading ? (
                <p className="text-ink-dim">Loading exams…</p>
              ) : (
                <ToggleList
                  options={
                    exams.data?.map((e) => ({ value: e.code, label: e.name })) ?? []
                  }
                  selected={activeExams}
                  onToggle={(v) => setActiveExams((p) => toggle(p, v))}
                />
              )}
            </Section>

            <Section caption="Preparation" title="Your study profile">
              <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                <Field label="Strengths (comma-separated)">
                  <input
                    value={strengths}
                    onChange={(e) => setStrengths(e.target.value)}
                    placeholder="mechanics, organic_chemistry"
                    className={inputClass}
                  />
                </Field>
                <Field label="Weaknesses (comma-separated)">
                  <input
                    value={weaknesses}
                    onChange={(e) => setWeaknesses(e.target.value)}
                    placeholder="modern_physics, calculus"
                    className={inputClass}
                  />
                </Field>
                <Field label="Study hours per day">
                  <input
                    type="number"
                    min={0}
                    max={16}
                    value={studyHours}
                    onChange={(e) => setStudyHours(Number(e.target.value) || 0)}
                    className={inputClass}
                  />
                </Field>
              </div>
            </Section>

            <div>
              <button
                type="submit"
                disabled={save.isPending}
                className="inline-flex items-center justify-center gap-2 rounded-full bg-ink px-6 py-3 text-[13px] font-medium text-paper transition-colors hover:bg-ember disabled:opacity-60"
              >
                {save.isPending ? "Saving…" : "Save profile →"}
              </button>
            </div>
          </form>
        )}
      </PageBody>
    </>
  );
}

const inputClass =
  "w-full border-b border-ink/30 bg-transparent py-3 font-display text-lg text-ink placeholder:text-ink-soft/60 focus:border-ember focus:outline-none";

function Section({
  caption,
  title,
  children,
}: {
  caption: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section>
      <div className="eyebrow">{caption}</div>
      <h2 className="display mt-2 text-2xl text-ink">{title}</h2>
      <div className="mt-6 rounded-2xl border border-ink/10 bg-paper-2/40 p-6">{children}</div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}

function DefBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-ink/10 py-3 last:border-0">
      <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">{label}</div>
      <div className="font-display text-base text-ink">{value}</div>
    </div>
  );
}

function ToggleList({
  options,
  selected,
  onToggle,
}: {
  options: { value: string; label: string }[];
  selected: string[];
  onToggle: (v: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => {
        const on = selected.includes(o.value);
        return (
          <button
            key={o.value}
            type="button"
            onClick={() => onToggle(o.value)}
            className={
              "rounded-full border px-3 py-1.5 text-[12px] transition-colors " +
              (on
                ? "border-ink bg-ink text-paper"
                : "border-ink/15 bg-paper text-ink-dim hover:border-ink/40 hover:text-ink")
            }
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

// (Currently unused — keeps the import surface honest in case we add a
// settings sub-page that exposes the full profile object.)
export type _PageDataShape = UserProfile;
