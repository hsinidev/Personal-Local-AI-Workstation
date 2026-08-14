'use client';
import React, { useState } from 'react';
import SwarmMonitor from '@/components/SwarmMonitor';
import LLMStatusMatrix from '@/components/LLMStatusMatrix';
import RAGInspector from '@/components/RAGInspector';
import TerminalLogs from '@/components/TerminalLogs';
import ChatbotWithVoice from '@/components/ChatbotWithVoice';

export default function WorkstationDashboard() {
  const [activeTab, setActiveTab] = useState<'all' | 'swarm' | 'models' | 'rag' | 'chat' | 'logs'>('all');
  const [triggerCount, setTriggerCount] = useState(0);
  const [isDevModalOpen, setIsDevModalOpen] = useState(false);

  return (
    <main className="min-h-screen bg-[#060911] text-slate-100 selection:bg-cyan-500 selection:text-white pb-16">
      {/* Top Navigation Header */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span className="font-mono font-bold text-base text-white">AI</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight text-white">Personal Local AI Workstation</h1>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 rounded-full font-semibold">
                  v2.0 (ADVANCED RAG SUITE)
                </span>
              </div>
              <p className="text-xs text-slate-400">Offline-First Swarm Orchestrator, Multi-Strategy RAG & Model Hub</p>
            </div>
          </div>

          {/* Top Control Badges & Quick Action */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => setIsDevModalOpen(true)}
              className="px-3.5 py-2 bg-gradient-to-r from-purple-600/25 to-indigo-600/25 hover:from-purple-600/40 hover:to-indigo-600/40 border border-purple-500/40 text-purple-300 text-xs font-mono rounded-xl transition-all flex items-center gap-1.5 shadow-lg shadow-purple-900/20 active:scale-95 cursor-pointer"
            >
              <span>👨‍💻</span> Ask Developer
            </button>

            <div className="hidden sm:flex items-center gap-2 text-xs font-mono px-3 py-1.5 bg-slate-900/90 border border-slate-800 rounded-xl">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-slate-400">Workstation Status:</span>
              <span className="text-emerald-300 font-semibold">Operational</span>
            </div>

            <button
              onClick={() => setTriggerCount(c => c + 1)}
              className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-cyan-500/25 transition-all flex items-center gap-2 font-mono"
            >
              <span className="h-2 w-2 rounded-full bg-white animate-ping" />
              Dispatch Swarm DAG {triggerCount > 0 && `(${triggerCount})`}
            </button>
          </div>
        </div>
      </header>

      {/* Developer Profile Modal */}
      {isDevModalOpen && (
        <div className="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-xl rounded-2xl border border-purple-500/40 p-6 space-y-6 shadow-2xl shadow-purple-950/50 relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setIsDevModalOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white px-2.5 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono cursor-pointer"
            >
              ✕ Close
            </button>
            
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-cyan-500 p-0.5 shadow-lg shadow-purple-500/30">
                  <div className="h-full w-full bg-slate-950 rounded-2xl flex items-center justify-center font-bold text-xl text-purple-300 font-mono">HM</div>
                </div>
                <span className="absolute -bottom-1 -right-1 px-1.5 py-0.5 text-[9px] font-bold bg-emerald-500 text-black rounded-md font-mono">PRO</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-white">Hsini Mohamed</h3>
                  <span className="text-xs px-2 py-0.5 bg-purple-500/10 border border-purple-500/30 text-purple-300 rounded font-mono">🇲🇦 Morocco</span>
                </div>
                <p className="text-xs text-slate-400 font-medium">Full-Stack Developer &amp; SaaS Architect · AI Systems Engineer</p>
                <p className="text-[11px] text-cyan-400 font-mono mt-0.5">Available for Worldwide Remote Work &amp; Custom Contracts</p>
              </div>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-3 gap-2.5 text-center font-mono">
              <div className="p-2.5 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-base font-bold text-purple-400">30+</div>
                <div className="text-[10px] text-slate-400">Utility Apps</div>
              </div>
              <div className="p-2.5 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-base font-bold text-cyan-400">11</div>
                <div className="text-[10px] text-slate-400">RAG Pipelines</div>
              </div>
              <div className="p-2.5 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-base font-bold text-emerald-400">1700+</div>
                <div className="text-[10px] text-slate-400">GitHub Commits</div>
              </div>
            </div>

            {/* Bio / Expertise */}
            <div className="p-3.5 bg-slate-900/50 border border-slate-800 rounded-xl text-xs text-slate-300 space-y-2 leading-relaxed">
              <p>Specialized in architecting production-grade offline AI workstations, hyper-parallel Swarm DAG orchestrators, multi-strategy RAG vector engines, and enterprise SaaS platforms.</p>
              <div className="flex flex-wrap gap-1.5 pt-1">
                <span className="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-purple-300 rounded">Python &amp; FastAPI</span>
                <span className="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-cyan-300 rounded">Ollama &amp; Local LLMs</span>
                <span className="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-blue-300 rounded">React &amp; Next.js</span>
                <span className="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-amber-300 rounded">Laravel 12 &amp; PHP 8</span>
                <span className="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-emerald-300 rounded">SQLite &amp; Vector Embeddings</span>
              </div>
            </div>

            {/* Direct Contact & Actions */}
            <div className="space-y-2.5">
              <h4 className="text-xs font-mono text-slate-400 uppercase font-semibold">Direct Communication &amp; Ask Developer</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <a href="mailto:contact@hsini.dev?subject=Personal%20Local%20AI%20Workstation%20Support%20%26%20Inquiry" className="p-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-mono font-medium flex items-center justify-center gap-2 shadow-lg shadow-purple-900/30 transition-all cursor-pointer">
                  <span>✉️</span> Ask Developer (Email)
                </a>
                <a href="https://hsini.dev" target="_blank" rel="noopener noreferrer" className="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-300 rounded-xl text-xs font-mono font-medium flex items-center justify-center gap-2 transition-all cursor-pointer">
                  <span>🌐</span> Visit hsini.dev
                </a>
                <a href="https://github.com/hsinidev" target="_blank" rel="noopener noreferrer" className="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-mono font-medium flex items-center justify-center gap-2 transition-all cursor-pointer">
                  <span>🐙</span> GitHub (@hsinidev)
                </a>
                <a href="https://linkedin.com/in/hsinidev/" target="_blank" rel="noopener noreferrer" className="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-xs font-mono font-medium flex items-center justify-center gap-2 transition-all cursor-pointer">
                  <span>💼</span> LinkedIn Profile
                </a>
              </div>
              <div className="text-[11px] font-mono text-slate-500 text-center pt-1">
                Direct Inquiries: <span className="text-purple-300 select-all">contact@hsini.dev</span> | <span className="text-slate-400 select-all">https://hsini.dev</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Body */}
      <div className="max-w-7xl mx-auto px-6 pt-8 space-y-8">
        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-800/80 text-xs font-mono">
          {[
            { id: 'all', label: 'Complete Overview' },
            { id: 'chat', label: '💬 Local LLM Chatbot' },
            { id: 'swarm', label: 'Swarm DAG Monitor' },
            { id: 'models', label: 'Local LLM Telemetry' },
            { id: 'rag', label: 'Vector Memory Inspector' },
            { id: 'logs', label: 'Sandbox Terminal & Logs' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 rounded-xl transition-all ${
                activeTab === tab.id
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700 font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dashboard Widgets */}
        {(activeTab === 'all' || activeTab === 'swarm') && (
          <section>
            <SwarmMonitor />
          </section>
        )}

        {(activeTab === 'all' || activeTab === 'models') && (
          <section>
            <LLMStatusMatrix />
          </section>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {(activeTab === 'all' || activeTab === 'rag') && (
            <section className={activeTab === 'rag' ? 'lg:col-span-2' : ''}>
              <RAGInspector />
            </section>
          )}

          {(activeTab === 'all' || activeTab === 'chat') && (
            <section className={activeTab === 'chat' ? 'lg:col-span-2' : ''}>
              <ChatbotWithVoice />
            </section>
          )}
        </div>

        {(activeTab === 'all' || activeTab === 'logs') && (
          <section>
            <TerminalLogs />
          </section>
        )}
      </div>
    </main>
  );
}
