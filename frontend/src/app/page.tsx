import { BentoGrid, BentoGridItem } from "@/components/ui/BentoGrid";
import { GlassCard } from "@/components/ui/GlassCard";
import { SpotlightButton } from "@/components/ui/SpotlightButton";
import { ArrowRight, Brain, Calendar, Trophy, Users, Zap } from "lucide-react";

export default function Home() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-4 md:p-24 relative overflow-hidden">
            {/* Hero Section */}
            <section className="text-center max-w-4xl mx-auto mb-20 relative z-10">
                <div className="inline-flex items-center justify-center px-4 py-1.5 mb-8 text-sm font-medium text-primary bg-primary/10 rounded-full border border-primary/20 backdrop-blur-sm">
                    <span className="flex h-2 w-2 rounded-full bg-primary mr-2 animate-pulse"></span>
                    ExamSensei v2.0 is live
                </div>

                <h1 className="text-5xl md:text-7xl font-display font-bold tracking-tight text-white mb-6">
                    The dual nature for <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-300">developers</span>,
                    <br /> not the other way around.
                </h1>

                <p className="text-lg md:text-xl text-neutral-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                    Everything we learned from powering 20% of the internet, yours by default.
                    Master your competitive exams with AI-driven insights.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <SpotlightButton className="w-full sm:w-auto">
                        Get Started <ArrowRight className="ml-2 h-4 w-4" />
                    </SpotlightButton>
                    <button className="px-8 py-3 rounded-full text-sm font-medium text-neutral-300 hover:text-white transition-colors">
                        View Documentation
                    </button>
                </div>
            </section>

            {/* Bento Grid Showcase */}
            <section className="w-full max-w-7xl mx-auto relative z-10">
                <div className="mb-12 text-center">
                    <h2 className="text-3xl md:text-4xl font-display font-bold text-white mb-4">
                        Begin with the end in mind.
                    </h2>
                    <p className="text-neutral-400">
                        A complete ecosystem for your preparation journey.
                    </p>
                </div>

                <BentoGrid className="max-w-6xl mx-auto">
                    <BentoGridItem
                        title="AI Mentor"
                        description="Personalized guidance tailored to your learning pace and style."
                        header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800 border border-white/5" />}
                        icon={<Brain className="h-4 w-4 text-primary" />}
                        className="md:col-span-2"
                    />
                    <BentoGridItem
                        title="Real-time Analytics"
                        description="Track your progress with detailed performance metrics."
                        header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800 border border-white/5" />}
                        icon={<Zap className="h-4 w-4 text-yellow-500" />}
                        className="md:col-span-1"
                    />
                    <BentoGridItem
                        title="Community"
                        description="Connect with thousands of other aspirants."
                        header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800 border border-white/5" />}
                        icon={<Users className="h-4 w-4 text-blue-500" />}
                        className="md:col-span-1"
                    />
                    <BentoGridItem
                        title="Smart Schedule"
                        description="Adaptive study plans that evolve with you."
                        header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800 border border-white/5" />}
                        icon={<Calendar className="h-4 w-4 text-green-500" />}
                        className="md:col-span-2"
                    />
                </BentoGrid>
            </section>

            {/* Glass Card Feature */}
            <section className="mt-24 w-full max-w-5xl mx-auto">
                <GlassCard className="flex flex-col md:flex-row items-center justify-between gap-8 p-12 bg-gradient-to-r from-primary/10 to-transparent">
                    <div className="flex-1">
                        <h3 className="text-2xl font-bold text-white mb-4">Why developers choose ExamSensei?</h3>
                        <p className="text-neutral-400 mb-6">
                            Built for speed, reliability, and precision. Experience the future of exam preparation today.
                        </p>
                        <div className="flex gap-4">
                            <div className="flex flex-col">
                                <span className="text-3xl font-bold text-white">99%</span>
                                <span className="text-xs text-neutral-500 uppercase tracking-wider">Success Rate</span>
                            </div>
                            <div className="w-px h-12 bg-white/10"></div>
                            <div className="flex flex-col">
                                <span className="text-3xl font-bold text-white">50k+</span>
                                <span className="text-xs text-neutral-500 uppercase tracking-wider">Active Users</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex-1 flex justify-center">
                        <Trophy className="h-32 w-32 text-primary/20" />
                    </div>
                </GlassCard>
            </section>
        </div>
    );
}
