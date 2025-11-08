'use client';

import { useEffect, useState } from 'react';
import { useAuth, ProtectedRoute } from '@/contexts/AuthContext';
import { api, Exam, GamificationStatus } from '@/lib/api';
import Link from 'next/link';

export default function ModernDashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const { user, logout } = useAuth();
  const [exams, setExams] = useState<Exam[]>([]);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [gamification, setGamification] = useState<GamificationStatus | null>(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [loading, setLoading] = useState(true);
  const [chatLoading, setChatLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadDashboardData();
  }, [user]);

  const loadDashboardData = async () => {
    if (!user) return;

    try {
      const [examsData, recsData, gamData] = await Promise.all([
        api.getExams(),
        api.getRecommendations(user.id).catch(() => null),
        api.getGamificationStatus(user.id).catch(() => null),
      ]);

      setExams(examsData.slice(0, 3));
      setRecommendations(recsData);
      setGamification(gamData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim() || !user) return;

    setChatLoading(true);
    try {
      const response = await api.chat(user.id, chatMessage);
      setChatResponse(response.response);
      setChatMessage('');
    } catch (error) {
      console.error('Chat failed:', error);
      setChatResponse('Sorry, I encountered an error. Please try again.');
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="relative">
          <div className="w-20 h-20 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
          <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-t-purple-400 rounded-full animate-spin" style={{ animationDuration: '0.8s' }}></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-slate-900/50 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/50">
                <span className="text-2xl">🎓</span>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  ExamSensei
                </h1>
                <p className="text-sm text-gray-400">Welcome back, {user?.name}!</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link href="/profile">
                <button className="p-2 hover:bg-white/10 rounded-xl transition-colors">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </button>
              </Link>
              <button
                onClick={logout}
                className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-xl transition-colors border border-red-500/30"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { 
              label: 'Level', 
              value: gamification?.level || 1, 
              icon: '🏆', 
              gradient: 'from-yellow-500 to-orange-500',
              change: '+2 this week'
            },
            { 
              label: 'XP Points', 
              value: gamification?.xp_points || 0, 
              icon: '⭐', 
              gradient: 'from-purple-500 to-pink-500',
              change: '+150 today'
            },
            { 
              label: 'Streak', 
              value: `${gamification?.streak_days || 0} days`, 
              icon: '🔥', 
              gradient: 'from-red-500 to-orange-500',
              change: 'Keep it up!'
            },
            { 
              label: 'Exams', 
              value: exams.length, 
              icon: '📚', 
              gradient: 'from-blue-500 to-purple-500',
              change: '3 upcoming'
            }
          ].map((stat, index) => (
            <div
              key={index}
              className="group relative p-6 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 hover:border-white/20 transition-all hover:scale-105 cursor-pointer overflow-hidden"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-0 group-hover:opacity-10 transition-opacity`}></div>
              
              <div className="relative z-10">
                <div className="flex justify-between items-start mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-br ${stat.gradient} rounded-xl flex items-center justify-center text-2xl shadow-lg`}>
                    {stat.icon}
                  </div>
                  <span className="text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded-full">
                    {stat.change}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
                <p className="text-3xl font-bold">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex space-x-2 mb-6 bg-white/5 backdrop-blur-xl rounded-2xl p-2 border border-white/10">
          {['overview', 'exams', 'chat', 'analytics'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all ${
                activeTab === tab
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg shadow-purple-500/50'
                  : 'hover:bg-white/5'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upcoming Exams */}
            <div className="p-6 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Upcoming Exams</h2>
                <Link href="/exams" className="text-purple-400 hover:text-purple-300 text-sm font-semibold">
                  View All →
                </Link>
              </div>
              
              <div className="space-y-4">
                {exams.length > 0 ? (
                  exams.map((exam) => (
                    <div
                      key={exam.id}
                      className="group p-4 bg-white/5 hover:bg-white/10 rounded-xl border border-white/10 hover:border-purple-500/50 transition-all cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center font-bold shadow-lg">
                            {exam.name.substring(0, 2)}
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">{exam.name}</h3>
                            <p className="text-sm text-gray-400">{exam.body}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-purple-400 font-semibold">
                            {exam.important_dates?.exam_dates?.[0] || 'TBA'}
                          </p>
                          <p className="text-xs text-gray-400">Exam Date</p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <p className="text-4xl mb-4">📚</p>
                    <p>No exams found. Add some to get started!</p>
                  </div>
                )}
              </div>
            </div>

            {/* AI Recommendations */}
            <div className="p-6 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10">
              <h2 className="text-2xl font-bold mb-6">AI Recommendations</h2>
              
              {recommendations ? (
                <div className="space-y-3">
                  {recommendations.recommendations?.slice(0, 3).map((rec: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-4 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-xl border border-purple-500/20"
                    >
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center flex-shrink-0">
                          <span className="text-sm">🎯</span>
                        </div>
                        <div className="flex-1">
                          <p className="font-semibold mb-1">{rec.type}</p>
                          <p className="text-sm text-gray-400">{rec.reasoning}</p>
                          <div className="mt-2 flex items-center space-x-2">
                            <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                                style={{ width: `${rec.score * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-purple-400 font-semibold">
                              {(rec.score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-400">
                  <p className="text-4xl mb-4">🤖</p>
                  <p>Complete your profile to get AI recommendations</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - AI Chat */}
          <div className="lg:col-span-1">
            <div className="sticky top-6 p-6 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 h-[calc(100vh-8rem)]flex flex-col">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-xl">🤖</span>
                </div>
                <div>
                  <h2 className="text-xl font-bold">AI Mentor</h2>
                  <p className="text-xs text-gray-400">Ask me anything</p>
                </div>
              </div>

              {/* Chat Response */}
              {chatResponse && (
                <div className="mb-4 p-4 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-xl border border-purple-500/20">
                  <p className="text-sm leading-relaxed">{chatResponse}</p>
                </div>
              )}

              {/* Chat Form */}
              <form onSubmit={handleChat} className="mt-auto space-y-4">
                <textarea
                  rows={4}
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  placeholder="e.g., How should I prepare for JEE Main Physics?"
                  disabled={chatLoading}
                />
                <button
                  type="submit"
                  disabled={chatLoading || !chatMessage.trim()}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl font-semibold shadow-lg shadow-purple-500/50 hover:shadow-purple-500/70 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {chatLoading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Thinking...
                    </span>
                  ) : (
                    'Ask AI Mentor'
                  )}
                </button>
              </form>

              {/* Quick Actions */}
              <div className="mt-6 space-y-2">
                <p className="text-xs text-gray-400 font-semibold mb-3">QUICK ACTIONS</p>
                {['Generate Study Plan', 'View Analytics', 'Set Goals'].map((action, idx) => (
                  <button
                    key={idx}
                    className="w-full text-left px-4 py-2 bg-white/5 hover:bg-white/10 rounded-xl transition-colors text-sm"
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
