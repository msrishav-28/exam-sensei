'use client';

import { GlassCard } from "@/components/ui/GlassCard";
import { SpotlightButton } from "@/components/ui/SpotlightButton";
import { ArrowLeft, BookOpen, Calendar, CheckCircle, Clock } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function ExamDetailPage() {
    const params = useParams();
    const id = params?.id as string;

    return (
        <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8">
            <Link href="/exams" className="inline-flex items-center text-neutral-400 hover:text-white transition-colors mb-4">
                <ArrowLeft className="h-4 w-4 mr-2" /> Back to Exams
            </Link>

            <div className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-emerald-900/50 to-black border border-white/10 p-8 md:p-12">
                <div className="relative z-10">
                    <div className="inline-block px-4 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm font-medium mb-4 border border-emerald-500/20">
                        Engineering Entrance
                    </div>
                    <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-6">
                        JEE Advanced 2025
                    </h1>
                    <div className="flex flex-wrap gap-6 text-neutral-300 mb-8">
                        <div className="flex items-center gap-2">
                            <Calendar className="h-5 w-5 text-emerald-500" />
                            <span>May 26, 2025</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Clock className="h-5 w-5 text-emerald-500" />
                            <span>6 Hours (2 Papers)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <BookOpen className="h-5 w-5 text-emerald-500" />
                            <span>Physics, Chem, Maths</span>
                        </div>
                    </div>
                    <SpotlightButton className="w-full md:w-auto">
                        Start Preparation
                    </SpotlightButton>
                </div>

                {/* Decorative background elements */}
                <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2 space-y-8">
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">About the Exam</h2>
                        <p className="text-neutral-400 leading-relaxed">
                            The Joint Entrance Examination (Advanced) 2025 will be conducted by the seven Zonal Coordinating IITs under the guidance of the Joint Admission Board (JAB) 2025. The performance of a candidate in this examination will form the basis for admission to the Bachelor's, Integrated Master's and Dual Degree programs (entry at the 10+2 level) in all the IITs.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-bold text-white mb-4">Syllabus Highlights</h2>
                        <div className="space-y-4">
                            <GlassCard className="p-4 flex items-start gap-4">
                                <div className="p-2 rounded-lg bg-purple-500/20 text-purple-400"><BookOpen className="h-5 w-5" /></div>
                                <div>
                                    <h3 className="font-bold text-white">Physics</h3>
                                    <p className="text-sm text-neutral-400">Mechanics, Electrodynamics, Optics, Modern Physics</p>
                                </div>
                            </GlassCard>
                            <GlassCard className="p-4 flex items-start gap-4">
                                <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400"><BookOpen className="h-5 w-5" /></div>
                                <div>
                                    <h3 className="font-bold text-white">Chemistry</h3>
                                    <p className="text-sm text-neutral-400">Physical, Inorganic, Organic Chemistry</p>
                                </div>
                            </GlassCard>
                            <GlassCard className="p-4 flex items-start gap-4">
                                <div className="p-2 rounded-lg bg-orange-500/20 text-orange-400"><BookOpen className="h-5 w-5" /></div>
                                <div>
                                    <h3 className="font-bold text-white">Mathematics</h3>
                                    <p className="text-sm text-neutral-400">Calculus, Algebra, Coordinate Geometry, Vectors</p>
                                </div>
                            </GlassCard>
                        </div>
                    </section>
                </div>

                <div className="space-y-6">
                    <GlassCard className="p-6">
                        <h3 className="text-xl font-bold text-white mb-4">Eligibility</h3>
                        <ul className="space-y-3">
                            <li className="flex items-start gap-3 text-sm text-neutral-300">
                                <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0" />
                                <span>Top 2,50,000 in JEE Main 2025</span>
                            </li>
                            <li className="flex items-start gap-3 text-sm text-neutral-300">
                                <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0" />
                                <span>Born on or after Oct 1, 2000</span>
                            </li>
                            <li className="flex items-start gap-3 text-sm text-neutral-300">
                                <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0" />
                                <span>Class 12th Pass (2024 or 2025)</span>
                            </li>
                        </ul>
                    </GlassCard>

                    <GlassCard className="p-6">
                        <h3 className="text-xl font-bold text-white mb-4">Important Dates</h3>
                        <div className="space-y-4">
                            <div className="flex gap-4">
                                <div className="flex-col items-center justify-center w-12 text-center">
                                    <span className="block text-xs text-neutral-500 uppercase">Apr</span>
                                    <span className="block text-xl font-bold text-white">27</span>
                                </div>
                                <div>
                                    <h4 className="text-white font-medium">Registration Begins</h4>
                                    <p className="text-xs text-neutral-500">10:00 AM IST</p>
                                </div>
                            </div>
                            <div className="flex gap-4">
                                <div className="flex-col items-center justify-center w-12 text-center">
                                    <span className="block text-xs text-neutral-500 uppercase">May</span>
                                    <span className="block text-xl font-bold text-white">26</span>
                                </div>
                                <div>
                                    <h4 className="text-white font-medium">Exam Date</h4>
                                    <p className="text-xs text-neutral-500">Paper 1 & 2</p>
                                </div>
                            </div>
                        </div>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}
