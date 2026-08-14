'use client';
import React, { useState } from 'react';

interface LogEntry {
  id: string;
  time: string;
  source: 'SWARM' | 'SANDBOX' | 'HEALER' | 'RAG';
  level: 'INFO' | 'WARN' | 'ERROR' | 'SUCCESS';
  message: string;
}

export default function TerminalLogs() {
  const [filter, setFilter] = useState<'ALL' | 'SWARM' | 'SANDBOX' | 'HEALER'>('ALL');

  const logs: LogEntry[] = [
    { id: '1', time: '02:26:05', source: 'SWARM', level: 'INFO', message: 'Hyper-Parallel DAG dispatched: 4 worker threads initialized.' },
    { id: '2', time: '02:26:06', source: 'SWARM', level: 'SUCCESS', message: 'Node t1_plan (Architecture Planner) finished in 0.04s.' },
    { id: '3', time: '02:26:07', source: 'SWARM', level: 'INFO', message: 'Spawning parallel tasks: t2_backend & t3_frontend concurrently.' },
    { id: '4', time: '02:26:08', source: 'RAG', level: 'INFO', message: 'Hybrid Search query: "LLMRouter" -> RRF top-1 score 0.0163.' },
    { id: '5', time: '02:26:09', source: 'SANDBOX', level: 'ERROR', message: 'Command failed: python -c "import non_existent_database_driver_xyz" (Exit 1)' },
    { id: '6', time: '02:26:10', source: 'HEALER', level: 'WARN', message: 'Self-Healing Engine triggered: Categorized MissingDependencyError.' },
    { id: '7', time: '02:26:10', source: 'HEALER', level: 'SUCCESS', message: 'Remediation patch synthesized: "pip install non_existent_database_driver_xyz".' },
    { id: '8', time: '02:26:11', source: 'SWARM', level: 'SUCCESS', message: 'Task t4_qa_merge completed. Swarm execution 100% successful.' }
  ];

  const filteredLogs = filter === 'ALL' ? logs : logs.filter(l => l.source === filter);

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'SUCCESS': return 'text-emerald-400';
      case 'WARN': return 'text-amber-400';
      case 'ERROR': return 'text-rose-400';
      default: return 'text-cyan-400';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-pulse" />
            Live Sandbox Terminal & Self-Healing Console
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Real-Time Subprocess Execution Logs & Automated Diagnostic Patches</p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-xs font-mono">
          {(['ALL', 'SWARM', 'SANDBOX', 'HEALER'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-lg transition-all ${
                filter === f
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Terminal Display */}
      <div className="bg-[#050811] p-4 rounded-xl border border-slate-900 font-mono text-xs space-y-1.5 max-h-64 overflow-y-auto shadow-inner">
        {filteredLogs.map((log) => (
          <div key={log.id} className="flex items-start gap-2 leading-relaxed">
            <span className="text-slate-600 select-none">[{log.time}]</span>
            <span className={`font-semibold px-1.5 rounded text-[10px] bg-slate-900/90 border border-slate-800 ${getLevelColor(log.level)}`}>
              {log.source}
            </span>
            <span className={log.level === 'ERROR' ? 'text-rose-300 font-medium' : log.level === 'WARN' ? 'text-amber-200' : 'text-slate-300'}>
              {log.message}
            </span>
          </div>
        ))}
      </div>

      {/* Self-Healing Diagnostic Patch Notification */}
      <div className="p-3.5 bg-slate-900/80 border border-amber-500/30 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-mono">
        <div className="flex items-center gap-2.5">
          <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping" />
          <span className="text-amber-300 font-semibold">Self-Healing QA Active:</span>
          <span className="text-slate-300">1 automated diagnostic patch pending supervisor review</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] px-2 py-0.5 bg-slate-800 text-slate-400 rounded border border-slate-700">
            Fix: pip install non_existent_database_driver_xyz
          </span>
          <button className="px-3 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-lg hover:bg-amber-500/30 transition-all font-semibold">
            Apply Patch
          </button>
        </div>
      </div>
    </div>
  );
}
