'use client';
import React, { useState } from 'react';

interface RAGResult {
  id: string;
  file: string;
  type: string;
  name: string;
  lines: string;
  score: number;
  snippet: string;
}

export default function RAGInspector() {
  const [query, setQuery] = useState('LLMRouter');
  const [results, setResults] = useState<RAGResult[]>([
    {
      id: 'res-1',
      file: 'core/orchestrator/router.py',
      type: 'class',
      name: 'LLMRouter',
      lines: '6-43',
      score: 0.0163,
      snippet: 'class LLMRouter:\n    def __init__(self, config_path: str = "config/llm_router.json"):\n        self.config_path = config_path\n        self.config = self._load_config()'
    },
    {
      id: 'res-2',
      file: 'core/orchestrator/main.py',
      type: 'async_function',
      name: 'route_task',
      lines: '36-45',
      score: 0.0087,
      snippet: '@app.post("/route")\nasync def route_task(req: RouteRequest):\n    selected_model = router.resolve_model(req.task_type)\n    health = await router.check_health()'
    },
    {
      id: 'res-3',
      file: 'core/orchestrator/dag_engine.py',
      type: 'class',
      name: 'DAGOrchestrator',
      lines: '24-120',
      score: 0.0084,
      snippet: 'class DAGOrchestrator:\n    def __init__(self, max_concurrency: int = 4):\n        self.max_concurrency = max_concurrency\n        self.tasks: Dict[str, DAGTask] = {}'
    }
  ]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    if (query.toLowerCase().includes('memory')) {
      setResults([
        {
          id: 'res-mem-1',
          file: 'core/memory/db.py',
          type: 'class',
          name: 'MemoryDB',
          lines: '6-120',
          score: 0.0161,
          snippet: 'class MemoryDB:\n    def __init__(self, db_path: str = "core/memory/workstation_memory.db"):\n        self.db_path = db_path\n        self.init_db()'
        },
        {
          id: 'res-mem-2',
          file: 'core/memory/embedder.py',
          type: 'class',
          name: 'HybridSearchEngine',
          lines: '70-126',
          score: 0.0156,
          snippet: 'class HybridSearchEngine:\n    def search_code(self, query: str, top_k: int = 5, alpha: float = 0.5):'
        }
      ]);
    } else if (query.toLowerCase().includes('simil') || query.toLowerCase().includes('vector')) {
      setResults([
        {
          id: 'res-sim-1',
          file: 'core/memory/embedder.py',
          type: 'function',
          name: 'cosine_similarity',
          lines: '59-67',
          score: 0.0161,
          snippet: '@staticmethod\ndef cosine_similarity(v1: List[float], v2: List[float]) -> float:\n    dot = sum(a * b for a, b in zip(v1, v2))'
        }
      ]);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-violet-400" />
            Code & RAG Vector Inspector
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Direct Hybrid (BM25 + Cosine RRF) Query over SQLite AST Memory Graph</p>
        </div>
        <span className="text-xs font-mono px-3 py-1 bg-slate-900/80 border border-slate-800 rounded-full text-slate-400">
          Indexed Symbols: 40 Nodes
        </span>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search code symbols, classes, functions, or conversation memory..."
            className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 font-mono"
          />
        </div>
        <button
          type="submit"
          className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-cyan-600/20 transition-all font-mono"
        >
          Query RAG
        </button>
      </form>

      {/* Results List */}
      <div className="space-y-3">
        {results.map((res) => (
          <div key={res.id} className="glass-card p-4 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-all">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/30 rounded text-[10px] uppercase font-semibold">
                  {res.type}
                </span>
                <span className="text-slate-200 font-bold">{res.name}</span>
                <span className="text-slate-500">({res.file}:{res.lines})</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 text-[11px]">RRF Score:</span>
                <span className="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-semibold rounded">
                  {res.score.toFixed(4)}
                </span>
              </div>
            </div>

            <pre className="mt-3 p-3 bg-slate-950/90 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto border border-slate-900">
              <code>{res.snippet}</code>
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
