import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { z } from "zod";

import { AuthLayout } from "@/components/auth/AuthLayout";
import { useAuth } from "@/lib/auth";

const searchSchema = z.object({
  email: z.string().optional(),
  exam: z.string().optional(),
});

export const Route = createFileRoute("/signup")({
  head: () => ({ meta: [{ title: "Create your account — ExamSensei" }] }),
  validateSearch: (search) => searchSchema.parse(search),
  component: SignupPage,
});

const EDUCATION_LEVELS = [
  { value: "class_11", label: "Class 11" },
  { value: "class_12", label: "Class 12" },
  { value: "class_12_completed", label: "Class 12 completed" },
  { value: "undergraduate", label: "Undergraduate" },
  { value: "postgraduate", label: "Postgraduate" },
  { value: "working_professional", label: "Working professional" },
];

const STATES = [
  "Andhra Pradesh", "Assam", "Bihar", "Delhi", "Gujarat", "Haryana",
  "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Odisha",
  "Punjab", "Rajasthan", "Tamil Nadu", "Telangana", "Uttar Pradesh",
  "West Bengal", "Other",
];

const CATEGORIES = [
  { value: "general", label: "General" },
  { value: "obc", label: "OBC" },
  { value: "sc", label: "SC" },
  { value: "st", label: "ST" },
  { value: "ews", label: "EWS" },
];

const BUDGETS = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

// Map the landing CTA's exam shorthand → seed exam code (best-effort).
const EXAM_HINTS: Record<string, string> = {
  JEE: "jee_main_2025",
  NEET: "neet_2025",
  UPSC: "upsc_cse_2025",
  CAT: "cat_2025",
  GATE: "gate_2025",
  CUET: "cuet_ug_2025",
  CLAT: "clat_2025",
  NDA: "upsc_nda_2025",
};

function SignupPage() {
  const navigate = useNavigate();
  const { signUp, session, configured } = useAuth();
  const { email: presetEmail, exam: presetExam } = Route.useSearch();

  const [name, setName] = useState("");
  const [email, setEmail] = useState(presetEmail ?? "");
  const [password, setPassword] = useState("");
  const [educationLevel, setEducationLevel] = useState("class_12");
  const [state, setState] = useState("Tamil Nadu");
  const [category, setCategory] = useState("general");
  const [budget, setBudget] = useState("medium");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState<null | "in" | "confirm">(null);

  const examLabel = useMemo(
    () => (presetExam && EXAM_HINTS[presetExam.toUpperCase()] ? presetExam.toUpperCase() : null),
    [presetExam],
  );

  // Already signed in → skip to the app.
  useEffect(() => {
    if (session) navigate({ to: "/app" });
  }, [session, navigate]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!configured) {
      toast.error("Sign-up isn't configured. Set the VITE_SUPABASE_* env vars first.");
      return;
    }
    if (password.length < 8) {
      toast.error("Pick a password of at least 8 characters.");
      return;
    }
    setSubmitting(true);
    try {
      const { needsEmailConfirmation } = await signUp({
        email, password, name, education_level: educationLevel, state, category, budget,
      });
      if (needsEmailConfirmation) {
        setDone("confirm");
        toast.success("Check your email to confirm your account.");
      } else {
        setDone("in");
        toast.success("Welcome to ExamSensei.");
        navigate({ to: "/app" });
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Could not create account.");
    } finally {
      setSubmitting(false);
    }
  }

  if (done === "confirm") {
    return (
      <AuthLayout
        number="01"
        eyebrow="One more step"
        title={<>Check your inbox.</>}
        subtitle="We sent a confirmation link to your email. Open it and you'll be in."
        footer={
          <p className="text-[13px] text-ink-dim">
            Wrong email?{" "}
            <button
              className="text-ember underline-offset-4 hover:underline"
              onClick={() => setDone(null)}
            >
              Try again
            </button>
          </p>
        }
      >
        <p className="text-[14px] text-ink-dim">
          The link is valid for 24 hours. Once you've clicked it, head back here and sign in.
        </p>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      number="01"
      eyebrow={examLabel ? `For ${examLabel} aspirants` : "For aspirants"}
      title={
        <>
          Start your<br />
          <em className="not-italic text-ember">atlas.</em>
        </>
      }
      subtitle="A two-minute setup. Your plan, mentor, and calendar follow from this."
      footer={
        <p className="text-[13px] text-ink-dim">
          Already have an account?{" "}
          <Link to="/login" className="text-ember underline-offset-4 hover:underline">
            Sign in
          </Link>
        </p>
      }
    >
      <form onSubmit={onSubmit} className="grid grid-cols-1 gap-5 md:grid-cols-2">
        <Field label="Full name" wide>
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
            className={inputClass}
          />
        </Field>

        <Field label="Email" wide>
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className={inputClass}
          />
        </Field>

        <Field label="Password" wide>
          <input
            type="password"
            required
            minLength={8}
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
            className={inputClass}
          />
        </Field>

        <Field label="Education">
          <select
            value={educationLevel}
            onChange={(e) => setEducationLevel(e.target.value)}
            className={selectClass}
          >
            {EDUCATION_LEVELS.map((o) => (
              <option key={o.value} value={o.value} className="text-ink">{o.label}</option>
            ))}
          </select>
        </Field>

        <Field label="State">
          <select
            value={state}
            onChange={(e) => setState(e.target.value)}
            className={selectClass}
          >
            {STATES.map((s) => (
              <option key={s} value={s} className="text-ink">{s}</option>
            ))}
          </select>
        </Field>

        <Field label="Category">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className={selectClass}
          >
            {CATEGORIES.map((o) => (
              <option key={o.value} value={o.value} className="text-ink">{o.label}</option>
            ))}
          </select>
        </Field>

        <Field label="Budget">
          <select
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            className={selectClass}
          >
            {BUDGETS.map((o) => (
              <option key={o.value} value={o.value} className="text-ink">{o.label}</option>
            ))}
          </select>
        </Field>

        <div className="md:col-span-2">
          <button
            type="submit"
            disabled={submitting}
            className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-full bg-ink px-6 py-3 text-[13px] font-medium text-paper transition-all hover:bg-ember disabled:opacity-60 md:w-auto"
          >
            {submitting ? "Creating account…" : "Create my atlas →"}
          </button>
        </div>
      </form>
    </AuthLayout>
  );
}

const inputClass =
  "w-full border-b border-ink/30 bg-transparent py-3 font-display text-lg text-ink placeholder:text-ink-soft/60 focus:border-ember focus:outline-none";
const selectClass =
  "w-full appearance-none border-b border-ink/30 bg-transparent py-3 font-display text-lg text-ink focus:border-ember focus:outline-none";

function Field({
  label,
  wide,
  children,
}: {
  label: string;
  wide?: boolean;
  children: React.ReactNode;
}) {
  return (
    <label className={wide ? "block md:col-span-2" : "block"}>
      <span className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}
