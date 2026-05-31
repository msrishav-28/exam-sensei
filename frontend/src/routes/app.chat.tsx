import { createFileRoute } from "@tanstack/react-router";
import { useMutation } from "@tanstack/react-query";
import { Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { PageBody, PageHeader } from "@/components/app/AppShell";
import { api, type ChatResponse } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export const Route = createFileRoute("/app/chat")({
  head: () => ({ meta: [{ title: "AI Mentor — ExamSensei" }] }),
  component: ChatPage,
});

type Turn =
  | { who: "you"; text: string }
  | { who: "sensei"; text: string; suggested?: string[] };

function ChatPage() {
  const { user } = useAuth();
  const userId = user?.id ?? "";

  const [turns, setTurns] = useState<Turn[]>([
    {
      who: "sensei",
      text:
        "Tell me what you're stuck on — a topic, an exam date, your weak spots. " +
        "I can pull your profile and the exam details to give you a real plan.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const endRef = useRef<HTMLDivElement>(null);

  const send = useMutation({
    mutationFn: (message: string) => api.chat(userId, message, sessionId),
    onSuccess: (data: ChatResponse) => {
      setSessionId(data.session_id);
      setTurns((t) => [
        ...t,
        { who: "sensei", text: data.response, suggested: data.suggested_actions },
      ]);
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Chat unavailable."),
  });

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns.length, send.isPending]);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || send.isPending || !userId) return;
    setTurns((t) => [...t, { who: "you", text }]);
    setInput("");
    send.mutate(text);
  }

  function suggest(s: string) {
    if (send.isPending) return;
    setTurns((t) => [...t, { who: "you", text: s }]);
    send.mutate(s);
  }

  return (
    <>
      <PageHeader
        number="08"
        eyebrow="Mentor console"
        title={
          <>
            Ask anything.<br />
            <em className="not-italic text-ember">Get a plan.</em>
          </>
        }
        subtitle="The mentor can read your profile, look up exam details, and build a study plan when you ask."
      />

      <PageBody>
        <div className="grid grid-cols-1 gap-px overflow-hidden rounded-2xl border border-ink/10 bg-ink/10">
          {/* Transcript */}
          <div className="flex h-[60vh] flex-col gap-5 overflow-y-auto bg-paper p-6 md:p-8">
            {turns.map((t, i) => (
              <Turn key={i} turn={t} onSuggest={suggest} />
            ))}
            {send.isPending ? (
              <div className="flex items-center gap-3 text-ink-soft">
                <span className="font-mono text-[10px] uppercase tracking-widest">Sensei</span>
                <span className="inline-flex items-center gap-1">
                  <Dot delay={0} /> <Dot delay={150} /> <Dot delay={300} />
                </span>
              </div>
            ) : null}
            <div ref={endRef} />
          </div>

          {/* Composer */}
          <form
            onSubmit={submit}
            className="flex items-end gap-3 bg-paper p-4 md:p-6"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit(e);
                }
              }}
              rows={1}
              placeholder="Ask anything about your syllabus, exam dates, or plan…"
              className="min-h-[44px] flex-1 resize-none rounded-xl border border-ink/15 bg-paper-2/40 px-4 py-3 text-[14px] text-ink placeholder:text-ink-soft focus:border-ember focus:outline-none"
            />
            <button
              type="submit"
              disabled={!input.trim() || send.isPending}
              className="inline-flex h-11 items-center gap-2 rounded-full bg-ink px-5 text-[12px] font-medium text-paper transition-colors hover:bg-ember disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
              Send
            </button>
          </form>
        </div>
      </PageBody>
    </>
  );
}

function Turn({ turn, onSuggest }: { turn: Turn; onSuggest: (s: string) => void }) {
  const isYou = turn.who === "you";
  return (
    <div className={isYou ? "flex flex-row-reverse" : "flex"}>
      <div className={"max-w-[80%] " + (isYou ? "text-right" : "text-left")}>
        <div className="font-mono text-[10px] uppercase tracking-widest text-ink-soft">
          {isYou ? "You" : "Sensei"}
        </div>
        <div
          className={
            "mt-2 inline-block rounded-2xl px-4 py-3 text-left text-[14px] leading-relaxed " +
            (isYou ? "bg-ink text-paper" : "border border-ink/10 bg-paper-2/40 text-ink")
          }
        >
          {turn.text.split("\n").map((line, i) => (
            <p key={i} className="not-first:mt-2">
              {line}
            </p>
          ))}
        </div>
        {!isYou && turn.suggested && turn.suggested.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {turn.suggested.map((s) => (
              <button
                key={s}
                onClick={() => onSuggest(s)}
                className="rounded-full border border-ink/15 bg-paper px-3 py-1.5 text-[11px] text-ink-dim hover:border-ink/40 hover:text-ink"
              >
                {s}
              </button>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function Dot({ delay }: { delay: number }) {
  return (
    <span
      className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-ink-soft"
      style={{ animationDelay: `${delay}ms` }}
    />
  );
}
