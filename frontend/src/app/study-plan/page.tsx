'use client';

import { GlassCard } from "@/components/ui/GlassCard";
import { SpotlightButton } from "@/components/ui/SpotlightButton";
import { Calendar as CalendarIcon, CheckCircle, ChevronRight, Clock, Target } from "lucide-react";

const schedule = [
    {
        time: '09:00 AM',
        subject: 'Physics',
        topic: 'Rotational Motion',
        type: 'Concept',
        duration: '2h',
        status: 'upcoming'
    },
    {
        time: '11:30 AM',
        subject: 'Chemistry',
        topic: 'Chemical Bonding',
        type: 'Practice',
        duration: '1.5h',
        status: 'upcoming'
    },
    {
        time: '02:00 PM',
        subject: 'Mathematics',
        topic: 'Calculus - Limits',
        type: 'Revision',
        duration: '2h',
        status: 'upcoming'
    },
    {
        time: '05:00 PM',
        subject: 'Mock Test',
        topic: 'Full Syllabus Test #5',
        type: 'Test',
        duration: '3h',
        status: 'upcoming'
    }
];

export default function StudyPlanPage() {
    return (
        <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-display font-bold text-white">Study Plan</h1>
                    <p className="text-neutral-400">Your personalized schedule for today, May 26.</p>
                </div>
                <SpotlightButton>
                    <CalendarIcon className="mr-2 h-4 w-4" /> View Full Calendar
                </SpotlightButton>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    {schedule.map((item, index) => (
                        <GlassCard key={index} className="flex flex-col md:flex-row gap-6 relative overflow-hidden group">
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-primary to-transparent opacity-50" />

                            <div className="flex flex-col justify-center min-w-[100px]">
                                <span className="text-xl font-bold text-white">{item.time}</span>
                                <span className="text-sm text-neutral-500 flex items-center gap-1">
                                    <Clock className="h-3 w-3" /> {item.duration}
                                </span>
                            </div>

                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className={`px-2 py-1 rounded text-xs font-medium border ${item.subject === 'Physics' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                                            item.subject === 'Chemistry' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                                item.subject === 'Mathematics' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                                                    'bg-red-500/10 text-red-400 border-red-500/20'
                                        }`}>
                                        {item.subject}
                                    </span>
                                    <span className="px-2 py-1 rounded text-xs font-medium bg-white/5 text-neutral-400 border border-white/10">
                                        {item.type}
                                    </span>
                                </div>
                                <h3 className="text-lg font-bold text-white mb-1">{item.topic}</h3>
                                <p className="text-sm text-neutral-400">Chapter 5 • High Weightage</p>
                            </div>

                            <div className="flex items-center justify-end">
                                <button className="p-3 rounded-full bg-white/5 hover:bg-primary/20 hover:text-primary transition-all group-hover:scale-110">
                                    <ChevronRight className="h-5 w-5" />
                                </button>
                            </div>
                        </GlassCard>
                    ))}
                </div>

                <div className="space-y-6">
                    <GlassCard className="p-6 bg-gradient-to-br from-emerald-900/20 to-transparent border-emerald-500/20">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <Target className="h-5 w-5 text-emerald-500" /> Daily Goals
                        </h3>
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <CheckCircle className="h-5 w-5 text-emerald-500" />
                                <span className="text-neutral-300 line-through decoration-neutral-500">Review Physics Notes</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="h-5 w-5 rounded-full border-2 border-neutral-600" />
                                <span className="text-neutral-300">Solve 30 Chemistry MCQs</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="h-5 w-5 rounded-full border-2 border-neutral-600" />
                                <span className="text-neutral-300">Complete Math Assignment</span>
                            </div>
                        </div>
                    </GlassCard>

                    <GlassCard className="p-6">
                        <h3 className="text-xl font-bold text-white mb-4">Progress</h3>
                        <div className="relative pt-1">
                            <div className="flex mb-2 items-center justify-between">
                                <div>
                                    <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-emerald-600 bg-emerald-200">
                                        Task Completion
                                    </span>
                                </div>
                                <div className="text-right">
                                    <span className="text-xs font-semibold inline-block text-emerald-600">
                                        30%
                                    </span>
                                </div>
                            </div>
                            <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-emerald-200/20">
                                <div style={{ width: "30%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-emerald-500"></div>
                            </div>
                        </div>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}
