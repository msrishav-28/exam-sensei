import { createFileRoute } from "@tanstack/react-router";
import { Nav } from "@/components/landing/Nav";
import { Cursor } from "@/components/landing/Cursor";
import { Hero } from "@/components/landing/Hero";
import { Manifesto } from "@/components/landing/Manifesto";
import { ProductReveal } from "@/components/landing/ProductReveal";
import { SignalRadar } from "@/components/landing/SignalRadar";
import { Cryptex } from "@/components/landing/Cryptex";
import { MentorConsole } from "@/components/landing/MentorConsole";
import { EditorialSpread } from "@/components/landing/EditorialSpread";
import { ProofMarquee } from "@/components/landing/ProofMarquee";
import { FAQ } from "@/components/landing/FAQ";
import { FinalCTA, Footer } from "@/components/landing/FinalCTA";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "ExamSensei — The AI mentor for Indian competitive exams" },
      { name: "description", content: "Adaptive AI mentor for JEE, NEET, UPSC, CAT and India's major competitive exams. Prioritized syllabus, 24/7 chat, exam calendar, streaks." },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div className="relative bg-paper text-ink">
      <div className="grain" aria-hidden />
      <Cursor />
      <Nav />
      <main>
        <Hero />
        <Manifesto />
        <ProductReveal />
        <SignalRadar />
        <Cryptex />
        <MentorConsole />
        <EditorialSpread />
        <ProofMarquee />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}
