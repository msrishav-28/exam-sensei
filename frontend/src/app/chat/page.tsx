'use client';

import { GlassCard } from "@/components/ui/GlassCard";
import { SpotlightButton } from "@/components/ui/SpotlightButton";
import { Bot, Send, User } from "lucide-react";
import { useState, useRef, useEffect } from "react";

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: 'Hello! I am your AI Exam Mentor. How can I help you with your preparation today?',
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        // Simulate AI response
        setTimeout(() => {
            const aiMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "That's a great question about Rotational Motion. The key concept here is the conservation of angular momentum. Let's break it down step by step...",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMessage]);
            setIsTyping(false);
        }, 1500);
    };

    return (
        <div className="h-[calc(100vh-4rem)] p-4 md:p-8 max-w-5xl mx-auto flex flex-col">
            <div className="mb-6">
                <h1 className="text-3xl font-display font-bold text-white">AI Mentor</h1>
                <p className="text-neutral-400">Ask doubts, get study tips, and clear concepts instantly.</p>
            </div>

            <GlassCard className="flex-1 flex flex-col overflow-hidden relative">
                <div className="flex-1 overflow-y-auto p-4 space-y-6">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                        >
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'assistant' ? 'bg-primary/20 text-primary' : 'bg-blue-500/20 text-blue-500'
                                }`}>
                                {msg.role === 'assistant' ? <Bot className="h-5 w-5" /> : <User className="h-5 w-5" />}
                            </div>

                            <div className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'assistant'
                                    ? 'bg-white/5 border border-white/10 text-neutral-200'
                                    : 'bg-primary/20 border border-primary/20 text-white'
                                }`}>
                                <p className="leading-relaxed">{msg.content}</p>
                                <span className="text-xs text-neutral-500 mt-2 block">
                                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        </div>
                    ))}

                    {isTyping && (
                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center shrink-0">
                                <Bot className="h-5 w-5" />
                            </div>
                            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 flex items-center gap-2">
                                <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="p-4 border-t border-white/10 bg-black/20 backdrop-blur-md">
                    <form onSubmit={handleSend} className="flex gap-4">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask anything about your syllabus..."
                            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                        />
                        <SpotlightButton type="submit" className="!w-auto px-6">
                            <Send className="h-5 w-5" />
                        </SpotlightButton>
                    </form>
                </div>
            </GlassCard>
        </div>
    );
}
