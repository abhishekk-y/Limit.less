'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export default function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', content: 'Hello! I\'m your Limit.less guide. I can help you understand skill scores, plan career paths, draft applications, or explain any recommendation.\n\nI support English, Hindi, Punjabi, and Hinglish. How can I help?', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userMsg: Message = { role: 'user', content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    // Mock response (would call /copilot/chat API)
    setTimeout(() => {
      const botMsg: Message = {
        role: 'bot',
        content: getMockResponse(userMsg.content),
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMsg]);
      setIsLoading(false);
    }, 1200);
  };

  const suggestions = [
    'Why is my Python STS 91?',
    'What should I learn next?',
    'Am I eligible for SSC CGL?',
    'Draft a cover letter for Razorpay AI Engineer',
    'मेरा career path बताओ',
  ];

  return (
    <div className="page-enter flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-100 dark:bg-violet-500/10 flex items-center justify-center">
            <svg className="w-5 h-5 text-violet-600 dark:text-violet-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 8V4H8"/>
              <rect width="16" height="12" x="4" y="8" rx="2"/>
              <path d="M2 14h2"/>
              <path d="M20 14h2"/>
              <path d="M15 13v2"/>
              <path d="M9 13v2"/>
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Limit.less guide</h1>
            <p className="text-xs text-gray-500">Powered by Groq · llama-3.3-70b · Scores by deterministic algorithms</p>
          </div>
          <span className="ml-auto inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-violet-100 text-violet-600">DEMO</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 bg-gray-50/50 dark:bg-gray-900/50 rounded-2xl border border-gray-200 dark:border-gray-700">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm ${
              msg.role === 'user'
                ? 'bg-violet-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}>
              {msg.role === 'user' ? (
                'A'
              ) : (
                <svg className="w-4 h-4 text-gray-600 dark:text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 8V4H8"/>
                  <rect width="16" height="12" x="4" y="8" rx="2"/>
                  <path d="M2 14h2"/>
                  <path d="M20 14h2"/>
                  <path d="M15 13v2"/>
                  <path d="M9 13v2"/>
                </svg>
              )}
            </div>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-violet-600 text-white rounded-tr-sm'
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-sm shadow-sm'
            }`}>
              <div className="whitespace-pre-wrap">{msg.content}</div>
              <div className={`text-[10px] mt-1 ${msg.role === 'user' ? 'text-violet-200' : 'text-gray-400'}`}>
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-sm">
              <svg className="w-4 h-4 text-gray-600 dark:text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 8V4H8"/>
                <rect width="16" height="12" x="4" y="8" rx="2"/>
                <path d="M2 14h2"/>
                <path d="M20 14h2"/>
                <path d="M15 13v2"/>
                <path d="M9 13v2"/>
              </svg>
            </div>
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {suggestions.map(s => (
            <button key={s} onClick={() => setInput(s)}
              className="px-3 py-1.5 rounded-full text-xs bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-violet-300 hover:text-violet-600 transition-colors">
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form onSubmit={(e: React.FormEvent) => { e.preventDefault(); handleSend(); }} className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
          placeholder="Ask about skills, career paths, eligibility, or say 'mujhe guide karo'..."
          className="flex-1 px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none transition-all"
          aria-label="Chat input"
          disabled={isLoading}
        />
        <button type="submit" disabled={!input.trim() || isLoading}
          className="btn-primary !rounded-xl disabled:opacity-50 disabled:cursor-not-allowed" aria-label="Send message">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
        </button>
      </form>

      {/* Disclaimer */}
      <p className="text-[10px] text-gray-400 text-center mt-2">
        The copilot drafts and explains — all scores are computed by deterministic algorithms, never by LLM.
      </p>
    </div>
  );
}

function getMockResponse(input: string): string {
  const lower = input.toLowerCase();
  if (lower.includes('sts') || lower.includes('python') || lower.includes('score'))
    return 'Your Python STS is 91/100. Here\'s the breakdown:\n\n• Evidence (28/30): 3 GitHub repos with original commits\n• Recency (19/20): Active 2 weeks ago\n• Assessment (17/20): Scored 88% on Python assessment\n• Project Depth (14/15): 4 projects including FastAPI REST API\n• Professional (13/15): Internship experience\n\nLineage: STS = 0.30×E + 0.20×R + 0.20×A + 0.15×P + 0.15×X\nConfidence: High | Source: GitHub + Assessments + Projects';
  if (lower.includes('learn') || lower.includes('next') || lower.includes('gap'))
    return 'Based on your Career GPS, here\'s what to learn next:\n\n1. Docker (12h) → +18% opportunity gain\n2. AWS (20h) → +15% opportunity gain\n3. RAG Evaluation (8h) → +8% opportunity gain\n\nThese are computed by the SOE (Skill Opportunity Elasticity) formula:\nSOE = ΔOpportunity / LearningEffort\n\nWant me to create a 40-hour learning plan?';
  if (lower.includes('eligible') || lower.includes('ssc') || lower.includes('government'))
    return 'Eligibility Check: SSC CGL\n\n• Age: PASS (within 18-32 range)\n• Education: PASS (Bachelor\'s degree)\n• Documents: MISSING — Domicile certificate not in Vault\n\nOverall: CONDITIONAL — Upload domicile certificate to proceed.\n\nThis is computed by the rule-based Eligibility Engine, not by LLM.';
  if (lower.includes('cover') || lower.includes('draft') || lower.includes('letter'))
    return 'Here\'s a draft cover letter for Razorpay AI Engineer:\n\n"Dear Hiring Team,\n\nI\'m excited to apply for the AI Engineer role. With Python (STS: 91), ML (STS: 77), and FastAPI expertise, I bring production-ready skills. My recent projects include a containerized ML inference service...\n\nI\'d welcome the chance to discuss how my profile aligns with your needs."\n\nNote: Review and edit before sending. This draft is AI-generated.';
  if (lower.includes('career') || lower.includes('path') || lower.includes('बताओ') || lower.includes('guide'))
    return 'Career GPS — 3 paths to AI Engineer:\n\n1. Fastest (48h): Docker → AWS → RAG (62% → 84%)\n2. Cheapest (40h): Docker → CI/CD → Cloud basics (all free resources)\n3. Max Opportunity (52h): Docker → AWS → Kubernetes (unlocks 340 jobs)\n\nYour current readiness: 62%\nAfter plan: up to 84%\n\nComputed by prerequisite-aware knapsack optimization on 1,842 job postings.';
  return 'I understand your question. Let me check the relevant data...\n\nNote: Scores and metrics come from Limit.less workspace calculations. I can help explain them, plan next steps and draft applications, but please check important details yourself.\n\nCould you be more specific about what you\'d like to know?';
}

