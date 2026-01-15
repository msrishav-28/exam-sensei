'use client';

import { BentoGrid, BentoGridItem } from "@/components/ui/BentoGrid";
import { GlassCard } from "@/components/ui/GlassCard";
import { Activity, BookOpen, Brain, Calendar, Target, Trophy } from "lucide-react";

export default function DashboardPage() {
    return (
        <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-display font-bold text-white">Dashboard</h1>
                    <p className="text-neutral-400">Welcome back, Aspirant. You're on a 5-day streak!</p>
                </div>
                <div className="flex gap-2">
                    <div className="px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium flex items-center gap-2">
                        <Trophy className="h-4 w-4" />
                        Level 5
                    </div>
                </div>
            </div>

            <BentoGrid>
                <BentoGridItem
                    title="Active Exams"
                    description="JEE Advanced 2025 • 145 Days Left"
                    header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-900/20 border border-emerald-500/20 flex items-center justify-center"><Target className="h-8 w-8 text-emerald-500" /></div>}
                    icon={<BookOpen className="h-4 w-4 text-neutral-500" />}
                    className="md:col-span-1"
                />
                <BentoGridItem
                    title="Recent Performance"
                    description="Mock Test #4: 85% Accuracy"
                    header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-900/20 border border-blue-500/20 flex items-center justify-center"><Activity className="h-8 w-8 text-blue-500" /></div>}
                    icon={<Activity className="h-4 w-4 text-neutral-500" />}
                    className="md:col-span-1"
                />
                <BentoGridItem
                    title="AI Recommendations"
                    description="Focus on 'Rotational Motion' in Physics today."
                    header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-900/20 border border-purple-500/20 flex items-center justify-center"><Brain className="h-8 w-8 text-purple-500" /></div>}
                    icon={<Brain className="h-4 w-4 text-neutral-500" />}
                    className="md:col-span-1"
                />
                <BentoGridItem
                    title="Study Schedule"
                    description="Next: Mock Test Analysis at 4:00 PM"
                    header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-orange-500/20 to-orange-900/20 border border-orange-500/20 flex items-center justify-center"><Calendar className="h-8 w-8 text-orange-500" /></div>}
                    icon={<Calendar className="h-4 w-4 text-neutral-500" />}
                    className="md:col-span-2"
                />
                <BentoGridItem
                    title="Community Challenge"
                    description="Solve 50 Physics problems this weekend."
                    header={<div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-pink-500/20 to-pink-900/20 border border-pink-500/20 flex items-center justify-center"><Trophy className="h-8 w-8 text-pink-500" /></div>}
                    icon={<Trophy className="h-4 w-4 text-neutral-500" />}
                    className="md:col-span-1"
                />
            </BentoGrid>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <GlassCard className="p-6">
                    <h3 className="text-xl font-bold text-white mb-4">Quick Actions</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <button className="p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors text-left">
                            <span className="block text-primary mb-2"><BookOpen /></span>
                            <span className="text-white font-medium">Take Mock Test</span>
                        </button>
                        <button className="p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors text-left">
                            <span className="block text-blue-500 mb-2"><Brain /></span>
                            <span className="text-white font-medium">Ask AI Mentor</span>
                        </button>
                    </div>
                </GlassCard>
                <GlassCard className="p-6">
                    <h3 className="text-xl font-bold text-white mb-4">Daily Progress</h3>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-neutral-400">Physics</span>
                                <span className="text-white">75%</span>
                            </div>
                            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 w-3/4" />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-neutral-400">Chemistry</span>
                                <span className="text-white">45%</span>
                            </div>
                            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500 w-[45%]" />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-neutral-400">Mathematics</span>
                                <span className="text-white">60%</span>
                            </div>
                            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-purple-500 w-3/5" />
                            </div>
                        </div>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
}
