'use client';

import { GlassCard } from "@/components/ui/GlassCard";
import { SpotlightButton } from "@/components/ui/SpotlightButton";
import { ArrowRight, Calendar, Search } from "lucide-react";
import Link from "next/link";

const exams = [
    {
        id: 'jee-adv-2025',
        name: 'JEE Advanced 2025',
        date: 'May 26, 2025',
        applicants: '1.5L+',
        tags: ['Engineering', 'National'],
        color: 'emerald'
    },
    {
        id: 'neet-ug-2025',
        name: 'NEET UG 2025',
        date: 'May 05, 2025',
        applicants: '20L+',
        tags: ['Medical', 'National'],
        color: 'blue'
    },
    {
        id: 'bitsat-2025',
        name: 'BITSAT 2025',
        date: 'June 2025',
        applicants: '3L+',
        tags: ['Engineering', 'University'],
        color: 'purple'
    }
];

export default function ExamsPage() {
    return (
        <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-display font-bold text-white">Explore Exams</h1>
                    <p className="text-neutral-400">Find and prepare for your target competitive exams.</p>
                </div>
                <div className="relative w-full md:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-500" />
                    <input
                        type="text"
                        placeholder="Search exams..."
                        className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-white placeholder:text-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {exams.map((exam) => (
                    <GlassCard key={exam.id} className="flex flex-col h-full">
                        <div className="flex justify-between items-start mb-4">
                            <div className={`w-12 h-12 rounded-xl bg-${exam.color}-500/20 flex items-center justify-center border border-${exam.color}-500/20`}>
                                <span className={`text-xl font-bold text-${exam.color}-500`}>{exam.name[0]}</span>
                            </div>
                            <span className="px-3 py-1 rounded-full bg-white/5 text-xs text-neutral-400 border border-white/10">
                                {exam.applicants} Applicants
                            </span>
                        </div>

                        <h3 className="text-xl font-bold text-white mb-2">{exam.name}</h3>

                        <div className="flex items-center gap-2 text-neutral-400 text-sm mb-6">
                            <Calendar className="h-4 w-4" />
                            {exam.date}
                        </div>

                        <div className="flex flex-wrap gap-2 mb-6">
                            {exam.tags.map(tag => (
                                <span key={tag} className="text-xs px-2 py-1 rounded bg-white/5 text-neutral-300">
                                    {tag}
                                </span>
                            ))}
                        </div>

                        <div className="mt-auto">
                            <Link href={`/exams/${exam.id}`}>
                                <SpotlightButton className="w-full">
                                    View Details <ArrowRight className="ml-2 h-4 w-4" />
                                </SpotlightButton>
                            </Link>
                        </div>
                    </GlassCard>
                ))}
            </div>
        </div>
    );
}
