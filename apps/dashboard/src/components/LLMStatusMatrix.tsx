'use client';
import React from 'react';

export default function LLMStatusMatrix() {
  const models = [
    { name: "qwen2.5-coder:latest", task: "Coding / Agentic", size: "4.7 GB", quant: "Q4_K_M", status: "Fallback Ready", vram: "5.2 GB", latency: "14.2 ms" },
    { name: "llama3.1:latest", task: "General Chat / Reasoning", size: "4.9 GB", quant: "Q4_K_M", status: "Fallback Ready", vram: "5.4 GB", latency: "12.8 ms" },
    { name: "codestral:22b", task: "Complex Refactoring", size: "12.4 GB", quant: "Q4_0", status: "Cold Standby", vram: "13.1 GB", latency: "28.5 ms" },
    { name: "deepseek-r1:8b", task: "Deep Reasoning / Math", size: "4.9 GB", quant: "Q4_K_M", status: "Fallback Ready", vram: "5.3 GB", latency: "18.1 ms" },
    { name: "nomic-embed-text", task: "Local Vector Embeddings", size: "274 MB", quant: "F16", status: "Active (768-dim)", vram: "0.4 GB", latency: "3.1 ms" }
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
            Local LLM Status & Endpoint Router
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Live Local Inference Telemetry & Offline Fallback Matrices</p>
        </div>

        {/* Real-time Telemetry Badges */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="px-3 py-1.5 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center gap-2">
            <span className="text-slate-500">Latency:</span>
            <span className="text-emerald-400 font-semibold">14.2 ms/tok</span>
          </div>
          <div className="px-3 py-1.5 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center gap-2">
            <span className="text-slate-500">Throughput:</span>
            <span className="text-cyan-400 font-semibold">82.4 tok/s</span>
          </div>
          <div className="px-3 py-1.5 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center gap-2">
            <span className="text-slate-500">Ollama API:</span>
            <span className="text-amber-400 font-semibold">Offline (Fallback Mode)</span>
          </div>
        </div>
      </div>

      {/* Model Matrix Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 pb-2">
              <th className="pb-3 font-semibold">Model ID</th>
              <th className="pb-3 font-semibold">Primary Task Route</th>
              <th className="pb-3 font-semibold">Quantization</th>
              <th className="pb-3 font-semibold">VRAM / RAM</th>
              <th className="pb-3 font-semibold">Avg Latency</th>
              <th className="pb-3 font-semibold text-right">Routing Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {models.map((m) => (
              <tr key={m.name} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-3.5 font-semibold text-slate-200 flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
                  {m.name}
                </td>
                <td className="py-3.5 text-slate-300 font-sans">{m.task}</td>
                <td className="py-3.5">
                  <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[11px] border border-slate-700/60">
                    {m.quant}
                  </span>
                </td>
                <td className="py-3.5 text-slate-400">{m.vram}</td>
                <td className="py-3.5 text-slate-300">{m.latency}</td>
                <td className="py-3.5 text-right">
                  <span className={`px-2.5 py-1 rounded text-[11px] font-semibold border ${
                    m.status.includes('Active')
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : m.status.includes('Fallback')
                      ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {m.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
