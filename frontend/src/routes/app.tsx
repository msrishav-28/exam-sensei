import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "@/components/app/AppShell";

// Layout route. The client-side auth guard + Outlet live in <AppShell />.
export const Route = createFileRoute("/app")({
  head: () => ({ meta: [{ title: "ExamSensei" }] }),
  component: AppShell,
});
