import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { AuthLayout } from "@/components/auth/AuthLayout";
import { useAuth } from "@/lib/auth";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [{ title: "Log in — ExamSensei" }] }),
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const { signIn, session, configured } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Already signed in → straight into the app.
  useEffect(() => {
    if (session) navigate({ to: "/app" });
  }, [session, navigate]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!configured) {
      toast.error("Sign-in isn't configured. Set the VITE_SUPABASE_* env vars first.");
      return;
    }
    setSubmitting(true);
    try {
      await signIn(email, password);
      toast.success("Welcome back.");
      navigate({ to: "/app" });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Could not sign in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout
      number="02"
      eyebrow="Returning aspirant"
      title={
        <>
          Pick up where<br />
          you left off.
        </>
      }
      subtitle="Your atlas, mentor, and streaks are waiting."
      footer={
        <p className="text-[13px] text-ink-dim">
          New here?{" "}
          <Link to="/signup" className="text-ember underline-offset-4 hover:underline">
            Create your account
          </Link>
        </p>
      }
    >
      <form onSubmit={onSubmit} className="grid grid-cols-1 gap-5">
        <Field label="Email">
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

        <Field label="Password">
          <input
            type="password"
            required
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className={inputClass}
          />
        </Field>

        <button
          type="submit"
          disabled={submitting}
          className="mt-2 inline-flex items-center justify-center gap-2 rounded-full bg-ink px-6 py-3 text-[13px] font-medium text-paper transition-all hover:bg-ember disabled:opacity-60"
        >
          {submitting ? "Signing in…" : "Sign in →"}
        </button>
      </form>
    </AuthLayout>
  );
}

const inputClass =
  "w-full border-b border-ink/30 bg-transparent py-3 font-display text-lg text-ink placeholder:text-ink-soft/60 focus:border-ember focus:outline-none";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}
