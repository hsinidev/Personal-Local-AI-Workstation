'use client';
import React, { useState } from 'react';

interface AgentNode {
  id: string;
  name: string;
  role: 'planner' | 'coder' | 'qa' | 'builder' | 'indexer';
  status: 'IDLE' | 'RUNNING' | 'COMPLETED' | 'HEALING';
  currentTask: string;
  duration: string;
  upstream: string[];
}

export default function SwarmMonitor() {
  const [nodes, setNodes] = useState<AgentNode[]>([
    { id: 'agent-1', name: 'Supervisor Planner', role: 'planner', status: 'COMPLETED', currentTask: 'Task DAG Decomposition', duration: '0.04s', upstream: [] },
    { id: 'agent-2', name: 'Backend Engineer', role: 'coder', status: 'COMPLETED', currentTask: 'FastAPI Router & Schema', duration: '0.12s', upstream: ['agent-1'] },
    { id: 'agent-3', name: 'Frontend Architect', role: 'coder', status: 'COMPLETED', currentTask: 'Next.js Workstation UI', duration: '0.15s', upstream: ['agent-1'] },
    { id: 'agent-4', name: 'QA Self-Healer', role: 'qa', status: 'HEALING', currentTask: 'Analyzing Stacktrace & Synthesizing Patch', duration: '0.08s', upstream: ['agent-2', 'agent-3'] },
    { id: 'agent-5', name: 'Sandbox Runner', role: 'builder', status: 'RUNNING', currentTask: 'Executing pytest & cargo check', duration: '0.22s', upstream: ['agent-4'] }
  ]);

  const [selectedNode, setSelectedNode] = useState<AgentNode | null>(nodes[3]);

  const getStatusBadge = (status: AgentNode['status']) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">COMPLETED</span>;
      case 'RUNNING':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-sky-500/10 text-sky-400 border border-sky-500/30 animate-pulse">RUNNING</span>;
      case 'HEALING':
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 animate-pulse">SELF-HEALING</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-slate-700/50 text-slate-400 border border-slate-700">IDLE</span>;
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-ping" />
            Hyper-Parallel Swarm DAG Monitor
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Topological Sub-Agent Dispatcher & Multi-Threaded Coordinator</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono px-3 py-1 bg-slate-800/80 rounded-full border border-slate-700 text-slate-300">
            Active Workers: 4 / 8 Max
          </span>
        </div>
      </div>

      {/* Visual DAG Pipeline */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative">
        {nodes.map((node, i) => (
          <div
            key={node.id}
            onClick={() => setSelectedNode(node)}
            className={`glass-card p-4 rounded-xl cursor-pointer transition-all duration-200 hover:scale-[1.02] ${
              selectedNode?.id === node.id ? 'ring-2 ring-cyan-500 bg-slate-800/80 shadow-lg shadow-cyan-500/10' : 'hover:border-slate-600'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Node 0{i + 1}</span>
              {getStatusBadge(node.status)}
            </div>
            <div className="font-semibold text-sm text-slate-200 truncate">{node.name}</div>
            <div className="text-xs text-slate-400 mt-1 line-clamp-2">{node.currentTask}</div>
            
            <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span>{node.role}</span>
              <span className="text-cyan-400">{node.duration}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Selected Node Details Drawer */}
      {selectedNode && (
        <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-cyan-400 font-semibold">{selectedNode.name} [{selectedNode.id}]</span>
            <span className="text-slate-400">Upstream Dependencies: {selectedNode.upstream.length > 0 ? selectedNode.upstream.join(', ') : 'None (Root Node)'}</span>
          </div>
          <div className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800/80 font-mono">
            <div><span className="text-slate-500">Operation:</span> {selectedNode.currentTask}</div>
            <div><span className="text-slate-500">Status:</span> {selectedNode.status}</div>
            {selectedNode.status === 'HEALING' && (
              <div className="mt-2 text-amber-300 bg-amber-950/40 p-2 rounded border border-amber-800/50">
                ⚠️ Stacktrace detected in sandbox runner. QA agent generated automatic patch recommendation for supervisor approval.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
