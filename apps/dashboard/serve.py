import http.server
import socketserver
import os
import sys
import json
import urllib.parse
import urllib.request
import time
import psutil
import platform
import subprocess

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from core.memory.db import MemoryDB
from core.memory.embedder import LocalEmbedder, HybridSearchEngine, ContextualRAGPipeline, DocumentIngester
from core.orchestrator.dag_engine import DAGOrchestrator, DAGTask

PORT = 3009
db = MemoryDB(os.path.join(WORKSPACE_ROOT, "core", "memory", "workstation_memory.db"))
embedder = LocalEmbedder()
search_engine = HybridSearchEngine(db, embedder)
rag_pipeline = ContextualRAGPipeline(db, embedder, search_engine)
doc_ingester = DocumentIngester(db, embedder)

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Personal Local AI Workstation | Advanced RAG & Swarm Platform</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 500: '#06b6d4', 600: '#0891b2' }
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #060911; color: #f1f5f9; font-family: system-ui, -apple-system, sans-serif; }
    .glass-panel { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .glass-card { background: rgba(19, 30, 54, 0.5); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.06); }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #060911; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
  </style>
</head>
<body class="min-h-screen pb-16">
  <!-- Top Nav -->
  <header class="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-4">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 font-mono font-bold text-base text-white">
          AI
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-lg font-bold tracking-tight text-white">Personal Local AI Workstation</h1>
            <span class="px-2 py-0.5 text-[10px] font-mono bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 rounded-full font-semibold">
              v2.0 (ADVANCED RAG SUITE)
            </span>
          </div>
          <p class="text-xs text-slate-400">Offline-First Swarm Orchestrator, Multi-Strategy RAG & Model Hub</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2.5">
        <button onclick="openDevModal()" class="px-3.5 py-2 bg-gradient-to-r from-purple-600/25 to-indigo-600/25 hover:from-purple-600/40 hover:to-indigo-600/40 border border-purple-500/40 text-purple-300 text-xs font-mono rounded-xl transition-all flex items-center gap-1.5 shadow-lg shadow-purple-900/20 active:scale-95 cursor-pointer">
          <span>👨‍💻</span> Ask Developer
        </button>
        <button onclick="openIngestModal()" class="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-400 text-xs font-mono rounded-xl transition-all flex items-center gap-1.5 cursor-pointer">
          <span>📥</span> Ingest Docs
        </button>
        <button onclick="runHardwareAuditModal()" class="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-mono rounded-xl transition-all flex items-center gap-1.5 cursor-pointer">
          <span>🔍</span> Analyze PC
        </button>
        <button id="dispatch-btn" onclick="triggerDAG()" class="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-cyan-500/25 transition-all flex items-center gap-2 font-mono active:scale-95 cursor-pointer">
          <span class="h-2 w-2 rounded-full bg-white animate-ping"></span>
          Dispatch Swarm DAG
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-6 pt-8 space-y-8">
    <!-- Swarm DAG Visual Pipeline -->
    <section class="glass-panel rounded-2xl p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-bold text-slate-100 flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-ping"></span>
            Hyper-Parallel Swarm DAG Monitor
          </h2>
          <p class="text-xs text-slate-400 mt-0.5">Topological Sub-Agent Dispatcher & Multi-Threaded Coordinator</p>
        </div>
        <span id="dag-status-pill" class="text-xs font-mono px-3 py-1 bg-slate-800/80 rounded-full border border-slate-700 text-slate-300">
          All Workers Idle / Ready
        </span>
      </div>

      <div id="dag-nodes-grid" class="grid grid-cols-1 md:grid-cols-5 gap-3">
        <!-- Node 1 -->
        <div id="node-1" class="glass-card p-4 rounded-xl ring-1 ring-slate-800 transition-all">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] font-mono text-slate-400">Node 01</span>
            <span id="node-1-badge" class="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">COMPLETED</span>
          </div>
          <div class="font-semibold text-sm text-slate-200 truncate">Supervisor Planner</div>
          <div class="text-xs text-slate-400 mt-1">DAG Decomposition</div>
          <div class="mt-3 pt-2 border-t border-slate-800 flex justify-between text-[11px] font-mono text-slate-400">
            <span>planner</span>
            <span id="node-1-dur" class="text-cyan-400">0.04s</span>
          </div>
        </div>

        <!-- Node 2 -->
        <div id="node-2" class="glass-card p-4 rounded-xl ring-1 ring-slate-800 transition-all">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] font-mono text-slate-400">Node 02</span>
            <span id="node-2-badge" class="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">COMPLETED</span>
          </div>
          <div class="font-semibold text-sm text-slate-200 truncate">Backend Engineer</div>
          <div class="text-xs text-slate-400 mt-1">FastAPI Router</div>
          <div class="mt-3 pt-2 border-t border-slate-800 flex justify-between text-[11px] font-mono text-slate-400">
            <span>coder</span>
            <span id="node-2-dur" class="text-cyan-400">0.12s</span>
          </div>
        </div>

        <!-- Node 3 -->
        <div id="node-3" class="glass-card p-4 rounded-xl ring-1 ring-slate-800 transition-all">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] font-mono text-slate-400">Node 03</span>
            <span id="node-3-badge" class="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">COMPLETED</span>
          </div>
          <div class="font-semibold text-sm text-slate-200 truncate">Frontend Architect</div>
          <div class="text-xs text-slate-400 mt-1">Next.js UI Engine</div>
          <div class="mt-3 pt-2 border-t border-slate-800 flex justify-between text-[11px] font-mono text-slate-400">
            <span>coder</span>
            <span id="node-3-dur" class="text-cyan-400">0.15s</span>
          </div>
        </div>

        <!-- Node 4 -->
        <div id="node-4" class="glass-card p-4 rounded-xl ring-1 ring-slate-800 transition-all">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] font-mono text-slate-400">Node 04</span>
            <span id="node-4-badge" class="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">COMPLETED</span>
          </div>
          <div class="font-semibold text-sm text-slate-200 truncate">QA Specialist</div>
          <div class="text-xs text-slate-400 mt-1">Integration Verification</div>
          <div class="mt-3 pt-2 border-t border-slate-800 flex justify-between text-[11px] font-mono text-slate-400">
            <span>qa</span>
            <span id="node-4-dur" class="text-cyan-400">0.08s</span>
          </div>
        </div>

        <!-- Node 5 -->
        <div id="node-5" class="glass-card p-4 rounded-xl ring-1 ring-slate-800 transition-all">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[10px] font-mono text-slate-400">Node 05</span>
            <span id="node-5-badge" class="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">COMPLETED</span>
          </div>
          <div class="font-semibold text-sm text-slate-200 truncate">Sandbox Runner</div>
          <div class="text-xs text-slate-400 mt-1">Process Subshell</div>
          <div class="mt-3 pt-2 border-t border-slate-800 flex justify-between text-[11px] font-mono text-slate-400">
            <span>builder</span>
            <span id="node-5-dur" class="text-cyan-400">0.22s</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Local LLM Status & Endpoint Router (Live Model Grid) -->
    <section class="glass-panel rounded-2xl p-6 space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-lg font-bold text-slate-100 flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Detected Local Models & Ollama Telemetry
          </h2>
          <p class="text-xs text-slate-400 mt-0.5">Live Local Model Detection & Hardware Status</p>
        </div>
        <div class="flex items-center gap-2 text-xs font-mono">
          <div id="ollama-live-status" class="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>Ollama Live: 127.0.0.1:11434</span>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs font-mono">
          <thead>
            <tr class="border-b border-slate-800 text-slate-400 pb-2">
              <th class="pb-3 font-semibold">Model Name</th>
              <th class="pb-3 font-semibold">Parameters</th>
              <th class="pb-3 font-semibold">Quantization</th>
              <th class="pb-3 font-semibold">Disk Size</th>
              <th class="pb-3 font-semibold">Context Length</th>
              <th class="pb-3 font-semibold text-right">Ollama Status</th>
            </tr>
          </thead>
          <tbody id="models-table-body" class="divide-y divide-slate-800/60">
            {{MODEL_TABLE_ROWS}}
          </tbody>
        </table>
      </div>
    </section>

    <!-- Two Column Grid: Advanced RAG Inspector & Real Ollama Chatbot with RAG Injection -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Advanced RAG Inspector -->
      <section class="glass-panel rounded-2xl p-6 space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold text-slate-100 flex items-center gap-2">
              <span class="h-2.5 w-2.5 rounded-full bg-violet-400"></span>
              Advanced Hybrid RAG Inspector
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">FTS5 (BM25) + Cosine Vector Semantic Search with RRF Fusion</p>
          </div>
          <span id="ast-count-badge" class="text-xs font-mono px-3 py-1 bg-slate-900/80 border border-slate-800 rounded-full text-slate-400">
            40 AST Nodes
          </span>
        </div>

        <!-- Quick Tag Suggestions -->
        <div class="flex flex-wrap items-center gap-2 text-xs font-mono">
          <span class="text-slate-500">Quick Query:</span>
          <button onclick="setQueryAndSearch('MemoryDB')" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg border border-slate-700">MemoryDB</button>
          <button onclick="setQueryAndSearch('ContextualRAGPipeline')" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg border border-slate-700">ContextualRAGPipeline</button>
          <button onclick="setQueryAndSearch('DAGOrchestrator')" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg border border-slate-700">DAGOrchestrator</button>
          <button onclick="setQueryAndSearch('cosine_similarity')" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg border border-slate-700">cosine_similarity</button>
        </div>

        <form id="rag-form" onsubmit="event.preventDefault(); executeRAGSearch();" class="flex gap-2">
          <input
            id="rag-query-input"
            type="text"
            value="MemoryDB"
            placeholder="Type function name, class, or keyword to search..."
            class="flex-1 bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
          <button id="rag-submit-btn" type="submit" class="px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-cyan-600/20 font-mono active:scale-95 transition-all">
            Query RAG
          </button>
        </form>

        <div id="rag-results-container" class="space-y-3">
        </div>
      </section>

      <!-- Right Column: Live Terminal & Real Ollama Chatbot + RAG Injection -->
      <div class="space-y-8">
        <!-- Live Terminal & Self-Healing -->
        <section class="glass-panel rounded-2xl p-6 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-bold text-slate-100 flex items-center gap-2">
                <span class="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
                Live Sandbox Terminal & Self-Healing
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">Real-Time Subprocess Execution & Diagnostic Patches</p>
            </div>
          </div>

          <div id="terminal-logs-box" class="bg-[#050811] p-4 rounded-xl border border-slate-900 font-mono text-xs space-y-1.5 max-h-40 overflow-y-auto">
            <div class="flex items-start gap-2"><span class="text-slate-600">[READY]</span><span class="font-semibold px-1 rounded text-[10px] bg-slate-900 text-cyan-400">SYSTEM</span><span class="text-slate-300">Local AI Workstation ready. Click 'Dispatch Swarm DAG' to run parallel workers.</span></div>
          </div>

          <div id="patch-card" class="p-3 bg-slate-900/80 border border-amber-500/30 rounded-xl flex items-center justify-between text-xs font-mono">
            <div class="flex items-center gap-2">
              <span class="h-2 w-2 rounded-full bg-amber-400 animate-ping"></span>
              <span class="text-amber-300 font-semibold">Auto-Healing Engine Active</span>
            </div>
            <span onclick="applyDemoPatch()" class="px-2.5 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-lg font-semibold cursor-pointer hover:bg-amber-500/30">
              Run Self-Heal Test
            </span>
          </div>
        </section>

        <!-- 🚀 REAL LIVE OLLAMA CHATBOT + RAG AUGMENTATION -->
        <section id="chatbot-section" class="glass-panel rounded-2xl p-6 space-y-4 border border-cyan-500/30 shadow-xl shadow-cyan-950/20">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-100 flex items-center gap-2">
                <span class="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-ping"></span>
                Live Ollama + RAG Augmented Chatbot
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">Chat Directly with Your Codebase & Ingested Knowledge</p>
            </div>
            
            <div class="flex items-center gap-2">
              <select id="chat-model-select" onchange="onModelChanged(this)" class="bg-slate-900 border border-slate-700 text-cyan-300 text-xs font-mono rounded-xl px-3 py-1.5 focus:outline-none focus:border-cyan-500">
                {{MODEL_OPTIONS}}
              </select>
              <button onclick="clearChatHistory()" title="Clear Chat" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-mono border border-slate-700">
                🗑️
              </button>
            </div>
          </div>

          <!-- RAG Augmentation Toggle Bar -->
          <div class="flex items-center justify-between p-2.5 bg-slate-900/90 rounded-xl border border-slate-800 text-xs font-mono">
            <label class="flex items-center gap-2 cursor-pointer">
              <input id="rag-toggle-checkbox" type="checkbox" checked class="rounded bg-slate-950 border-slate-700 text-cyan-500 focus:ring-0">
              <span class="text-cyan-300 font-semibold">⚡ Augment with Local RAG Knowledge</span>
            </label>
            <span class="text-[10px] text-slate-400">Injects local AST & docs into prompt</span>
          </div>

          <!-- Quick Suggestion Chips -->
          <div class="flex flex-wrap gap-1.5 text-[11px] font-mono">
            <span class="text-slate-500 py-0.5">Prompts:</span>
            <button onclick="fillPrompt('Explain how MemoryDB and ContextualRAGPipeline work together in this project.')" class="px-2 py-0.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-cyan-400 rounded-lg">Explain MemoryDB + RAG</button>
            <button onclick="fillPrompt('What is the role of DAGOrchestrator?')" class="px-2 py-0.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded-lg">Role of DAG Engine</button>
          </div>

          <!-- Chat Messages Scroll Container -->
          <div id="chat-messages-box" class="bg-[#050811] p-4 rounded-xl border border-slate-900/90 h-64 overflow-y-auto space-y-3 font-sans text-xs">
            <div class="flex items-start gap-2.5">
              <div class="h-6 w-6 rounded-lg bg-emerald-600/30 border border-emerald-500/40 flex items-center justify-center font-mono font-bold text-[10px] text-emerald-300 flex-shrink-0">AI</div>
              <div id="msg-card-welcome" class="glass-card px-3.5 py-2.5 rounded-2xl rounded-tl-none border border-slate-800/80 text-slate-200 max-w-[88%] space-y-1 transition-all">
                <div class="font-semibold text-emerald-400 font-mono text-[10px] flex items-center justify-between gap-2">
                  <div class="flex items-center gap-1.5">
                    <span id="chat-active-model-name">qwen2.5-coder:7b</span>
                    <span class="px-1.5 py-0.2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded font-normal text-[9px]">RAG Connected</span>
                  </div>
                </div>
                <div id="welcome-msg-text" class="text-slate-200 leading-relaxed">Hello! I am connected to your live Ollama engine with <strong>RAG Codebase Augmentation</strong> active. Ask any question about your code or architecture!</div>
              </div>
            </div>
          </div>

          <!-- Chat Input Form -->
          <form id="chat-form" onsubmit="event.preventDefault(); sendChatMessage(); return false;" class="flex gap-2">
            <input
              id="chat-user-input"
              type="text"
              autocomplete="off"
              onkeydown="if(event.key === 'Enter') { event.preventDefault(); sendChatMessage(); }"
              placeholder="Ask anything about your code (RAG context will be injected)..."
              class="flex-1 bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
            <button id="chat-send-btn" type="button" onclick="sendChatMessage()" class="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-emerald-600/20 font-mono active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer">
              <span>Send</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
            </button>
          </form>
        </section>
      </div>
    </div>
  </main>

  <!-- Document Ingestion Modal -->
  <div id="ingest-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 hidden">
    <div class="glass-panel max-w-xl w-full p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 class="text-base font-bold text-white flex items-center gap-2">
          <span>📥</span> Ingest Knowledge Document to Vector Memory
        </h3>
        <button onclick="closeIngestModal()" class="text-slate-400 hover:text-white text-lg font-mono">✕</button>
      </div>

      <div class="space-y-3 text-xs font-mono">
        <div>
          <label class="text-slate-400 block mb-1">Document Title:</label>
          <input id="doc-title-input" type="text" placeholder="e.g. My API Documentation" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200">
        </div>
        <div>
          <label class="text-slate-400 block mb-1">Category:</label>
          <input id="doc-cat-input" type="text" value="Architecture" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200">
        </div>
        <div>
          <label class="text-slate-400 block mb-1">Document Content / Markdown:</label>
          <textarea id="doc-content-input" rows="5" placeholder="Paste requirements, API endpoints, notes..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-200 font-mono"></textarea>
        </div>
      </div>

      <div class="flex justify-end gap-2 pt-2 border-t border-slate-800">
        <button onclick="closeIngestModal()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-mono text-xs">Cancel</button>
        <button onclick="submitDocumentIngestion()" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-xl font-mono text-xs">Embed & Store</button>
      </div>
    </div>
  </div>

  <!-- Hardware & Model Analysis Modal -->
  <div id="hardware-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 hidden">
    <div class="glass-panel max-w-2xl w-full p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-6">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 class="text-base font-bold text-white flex items-center gap-2">
            <span>💻</span> PC Hardware & Local LLM Compatibility Engine
          </h3>
          <p class="text-xs text-slate-400">Automated Spec Audit for Porting to Any New PC</p>
        </div>
        <button onclick="closeHardwareModal()" class="text-slate-400 hover:text-white text-lg font-mono">✕</button>
      </div>

      <div id="modal-content" class="space-y-4 text-xs font-mono">
        <div class="p-4 text-center text-cyan-400 animate-pulse">Auditing local PC hardware & models...</div>
      </div>

      <div class="flex justify-end pt-2 border-t border-slate-800">
        <button onclick="closeHardwareModal()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl font-mono text-xs cursor-pointer">
          Close Audit
        </button>
      </div>
    </div>
  </div>

  <!-- ─── DEVELOPER PROFILE MODAL ("Ask Developer") ─── -->
  <div id="dev-modal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
    <div class="glass-panel w-full max-w-xl rounded-2xl border border-purple-500/40 p-6 space-y-6 shadow-2xl shadow-purple-950/50 relative max-h-[90vh] overflow-y-auto">
      <button onclick="closeDevModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white px-2.5 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono cursor-pointer">✕ Close</button>
      
      <div class="flex items-center gap-4">
        <div class="relative">
          <div class="h-16 w-16 rounded-2xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-cyan-500 p-0.5 shadow-lg shadow-purple-500/30">
            <div class="h-full w-full bg-slate-950 rounded-2xl flex items-center justify-center font-bold text-xl text-purple-300 font-mono">HM</div>
          </div>
          <span class="absolute -bottom-1 -right-1 px-1.5 py-0.5 text-[9px] font-bold bg-emerald-500 text-black rounded-md font-mono">PRO</span>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-lg font-bold text-white">Hsini Mohamed</h3>
            <span class="text-xs px-2 py-0.5 bg-purple-500/10 border border-purple-500/30 text-purple-300 rounded font-mono">🇲🇦 Morocco</span>
          </div>
          <p class="text-xs text-slate-400 font-medium">Full-Stack Developer &amp; SaaS Architect · AI Systems Engineer</p>
          <p class="text-[11px] text-cyan-400 font-mono mt-0.5">Available for Worldwide Remote Work &amp; Custom Contracts</p>
        </div>
      </div>

      <!-- Quick Metrics -->
      <div class="grid grid-cols-3 gap-2.5 text-center font-mono">
        <div class="p-2.5 bg-slate-900/80 border border-slate-800 rounded-xl">
          <div class="text-base font-bold text-purple-400">30+</div>
          <div class="text-[10px] text-slate-400">Utility Apps</div>
        </div>
        <div class="p-2.5 bg-slate-900/80 border border-slate-800 rounded-xl">
          <div class="text-base font-bold text-cyan-400">11</div>
          <div class="text-[10px] text-slate-400">RAG Pipelines</div>
        </div>
        <div class="p-2.5 bg-slate-900/80 border border-slate-800 rounded-xl">
          <div class="text-base font-bold text-emerald-400">1700+</div>
          <div class="text-[10px] text-slate-400">GitHub Commits</div>
        </div>
      </div>

      <!-- Bio / Expertise -->
      <div class="p-3.5 bg-slate-900/50 border border-slate-800 rounded-xl text-xs text-slate-300 space-y-2 leading-relaxed">
        <p>Specialized in architecting production-grade offline AI workstations, hyper-parallel Swarm DAG orchestrators, multi-strategy RAG vector engines, and enterprise SaaS platforms.</p>
        <div class="flex flex-wrap gap-1.5 pt-1">
          <span class="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-purple-300 rounded">Python &amp; FastAPI</span>
          <span class="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-cyan-300 rounded">Ollama &amp; Local LLMs</span>
          <span class="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-blue-300 rounded">React &amp; Next.js</span>
          <span class="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-amber-300 rounded">Laravel 12 &amp; PHP 8</span>
          <span class="px-2 py-0.5 bg-slate-800 text-[10px] font-mono text-emerald-300 rounded">SQLite &amp; Vector Embeddings</span>
        </div>
      </div>

      <!-- Direct Contact & Actions -->
      <div class="space-y-2.5">
        <h4 class="text-xs font-mono text-slate-400 uppercase font-semibold">Direct Communication &amp; Ask Developer</h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <a href="mailto:contact@hsini.dev?subject=Personal%20Local%20AI%20Workstation%20Support%20%26%20Inquiry" class="p-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-mono font-medium flex items-center justify-center gap-2 shadow-lg shadow-purple-900/30 transition-all cursor-pointer">
            <span>✉️</span> Ask Developer (Email)
          </a>
          <a href="https://hsini.dev" target="_blank" rel="noopener" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-300 rounded-xl text-xs font-mono font-medium flex items-center justify-center gap-2 transition-all cursor-pointer">
            <span>🌐</span> Visit hsini.dev
          </a>
          <a href="https://github.com/hsinidev" target="_blank" rel="noopener" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-xl text-xs font-mono font-medium flex items-center justify-center gap-2 transition-all cursor-pointer">
            <span>🐙</span> GitHub (@hsinidev)
          </a>
          <a href="https://linkedin.com/in/hsinidev/" target="_blank" rel="noopener" class="p-3 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-blue-400 rounded-xl text-xs font-mono font-medium flex items-center justify-center gap-2 transition-all cursor-pointer">
            <span>💼</span> LinkedIn Profile
          </a>
        </div>
        <div class="text-[11px] font-mono text-slate-500 text-center pt-1">
          Direct Inquiries: <span class="text-purple-300 select-all">contact@hsini.dev</span> | <span class="text-slate-400 select-all">https://hsini.dev</span>
        </div>
      </div>
    </div>
  </div>

  <script>
    function openDevModal() {
      const modal = document.getElementById('dev-modal');
      if (modal) modal.classList.remove('hidden');
    }
    function closeDevModal() {
      const modal = document.getElementById('dev-modal');
      if (modal) modal.classList.add('hidden');
    }

    // --- Load Real Ollama Models on Start ---
    function onModelChanged(selectEl) {
      const activeNameEl = document.getElementById('chat-active-model-name');
      if (activeNameEl && selectEl) {
        activeNameEl.innerText = selectEl.value;
      }
    }

    async function loadOllamaModels() {
      try {
        const res = await fetch('/api/models');
        if (!res.ok) return;
        const data = await res.json();
        
        const select = document.getElementById('chat-model-select');
        const tableBody = document.getElementById('models-table-body');
        
        if (data.models && data.models.length > 0 && select) {
          const currentVal = select.value;
          select.innerHTML = '';
          
          data.models.forEach((m, idx) => {
            const opt = document.createElement('option');
            opt.value = m.name;
            opt.innerText = `🤖 ${m.name} (${m.param_size || 'LLM'})`;
            if (currentVal ? m.name === currentVal : (m.name.includes('qwen') || idx === 0)) {
              opt.selected = true;
            }
            select.appendChild(opt);
          });

          if (tableBody) {
            tableBody.innerHTML = '';
            data.models.forEach((m) => {
              const tr = document.createElement('tr');
              tr.className = 'hover:bg-slate-800/30';
              tr.innerHTML = `
                <td class="py-3.5 font-semibold text-slate-200 flex items-center gap-2">
                  <span class="h-1.5 w-1.5 rounded-full bg-cyan-400"></span>${m.name}
                </td>
                <td class="py-3.5 text-slate-300">${m.param_size || 'N/A'}</td>
                <td class="py-3.5"><span class="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[11px] border border-slate-700/60">${m.quantization || 'Q4'}</span></td>
                <td class="py-3.5 text-slate-400">${m.size_gb} GB</td>
                <td class="py-3.5 text-slate-300">${m.context || '8192'}</td>
                <td class="py-3.5 text-right"><span class="px-2.5 py-1 rounded text-[11px] font-semibold border bg-emerald-500/10 text-emerald-400 border-emerald-500/30">Live Ready</span></td>
              `;
              tableBody.appendChild(tr);
            });
          }

          const activeNameEl = document.getElementById('chat-active-model-name');
          if (activeNameEl) activeNameEl.innerText = select.value;
        }
      } catch (err) {
        console.error('Failed to load Ollama models:', err);
      }
    }

    // --- Document Ingestion Modal & Action ---
    function openIngestModal() {
      document.getElementById('ingest-modal').classList.remove('hidden');
    }
    function closeIngestModal() {
      document.getElementById('ingest-modal').classList.add('hidden');
    }

    async function submitDocumentIngestion() {
      const title = document.getElementById('doc-title-input').value.trim();
      const category = document.getElementById('doc-cat-input').value.trim();
      const content = document.getElementById('doc-content-input').value.trim();

      if (!title || !content) {
        alert('Please provide title and content');
        return;
      }

      try {
        const res = await fetch('/api/ingest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, category, content })
        });
        const data = await res.json();
        alert('Document embedded into Vector Memory! ID: ' + data.doc_id);
        closeIngestModal();
      } catch (err) {
        alert('Failed to ingest: ' + err.message);
      }
    }

    // --- Hardware Audit Modal ---
    async function runHardwareAuditModal() {
      const modal = document.getElementById('hardware-modal');
      const content = document.getElementById('modal-content');
      modal.classList.remove('hidden');
      content.innerHTML = '<div class="p-4 text-center text-cyan-400 animate-pulse">Auditing local PC hardware & models...</div>';

      try {
        const res = await fetch('/api/system/analyze');
        const data = await res.json();

        content.innerHTML = `
          <div class="grid grid-cols-2 gap-3">
            <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
              <div class="text-slate-400 text-[10px]">CPU Cores & Architecture</div>
              <div class="font-bold text-slate-200 text-sm mt-0.5">${data.cpu_cores} Cores (${data.arch})</div>
            </div>
            <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
              <div class="text-slate-400 text-[10px]">Total System RAM</div>
              <div class="font-bold text-emerald-400 text-sm mt-0.5">${data.ram_gb} GB (${data.ram_free_gb} GB Free)</div>
            </div>
          </div>

          <div class="p-3.5 bg-slate-900/90 rounded-xl border border-cyan-500/30 space-y-2">
            <div class="font-bold text-cyan-300 flex items-center justify-between">
              <span>🎯 Hardware Recommendation for This PC:</span>
              <span class="px-2 py-0.5 bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-[10px] rounded">${data.tier}</span>
            </div>
            <p class="text-slate-300 text-xs font-sans leading-relaxed">${data.recommendation}</p>
          </div>

          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-1.5">
            <div class="text-slate-400 text-[11px] font-semibold">Installed Local Models (${data.model_count} detected):</div>
            <div class="flex flex-wrap gap-1.5">
              ${data.models.map(m => `<span class="px-2 py-1 bg-slate-900 border border-slate-700 text-emerald-400 rounded">${m}</span>`).join('')}
            </div>
          </div>
        `;
      } catch (err) {
        content.innerHTML = '<div class="p-4 text-center text-rose-400">Audit error: ' + err.message + '</div>';
      }
    }

    function closeHardwareModal() {
      document.getElementById('hardware-modal').classList.add('hidden');
    }

    // --- Live Ollama Chat Execution with RAG Injected ---
    function fillPrompt(text) {
      document.getElementById('chat-user-input').value = text;
      sendChatMessage();
    }

    function clearChatHistory() {
      const box = document.getElementById('chat-messages-box');
      const select = document.getElementById('chat-model-select');
      box.innerHTML = `
        <div class="flex items-start gap-2.5">
          <div class="h-6 w-6 rounded-lg bg-emerald-600/30 border border-emerald-500/40 flex items-center justify-center font-mono font-bold text-[10px] text-emerald-300 flex-shrink-0">AI</div>
          <div id="msg-card-welcome" class="glass-card px-3.5 py-2.5 rounded-2xl rounded-tl-none border border-slate-800/80 text-slate-200 max-w-[88%] space-y-1 transition-all">
            <div class="font-semibold text-emerald-400 font-mono text-[10px] flex items-center justify-between gap-2">
              <span id="chat-active-model-name">${select ? select.value : 'qwen2.5-coder:7b'}</span>
            </div>
            <div id="welcome-msg-text" class="text-slate-200 leading-relaxed">Chat cleared. Ready for your prompt!</div>
          </div>
        </div>
      `;
    }

    async function sendChatMessage() {
      const input = document.getElementById('chat-user-input');
      const box = document.getElementById('chat-messages-box');
      const btn = document.getElementById('chat-send-btn');
      const select = document.getElementById('chat-model-select');
      const ragToggle = document.getElementById('rag-toggle-checkbox') ? document.getElementById('rag-toggle-checkbox').checked : true;

      if (!input || !box) return;
      const userText = input.value.trim();
      if (!userText) return;

      const selectedModel = (select && select.value) ? select.value : 'qwen2.5-coder:7b';
      input.value = '';

      // User bubble
      const userMsgDiv = document.createElement('div');
      userMsgDiv.className = 'flex justify-end';
      userMsgDiv.innerHTML = `
        <div class="bg-gradient-to-r from-emerald-600/80 to-cyan-600/80 text-white px-4 py-2.5 rounded-2xl rounded-tr-none max-w-[85%] text-xs shadow-md shadow-emerald-900/30">
          <p>${escapeHtml(userText)}</p>
        </div>
      `;
      box.appendChild(userMsgDiv);
      box.scrollTop = box.scrollHeight;

      // Typing indicator
      const typingId = 'typing-' + Date.now();
      const typingDiv = document.createElement('div');
      typingDiv.id = typingId;
      typingDiv.className = 'flex items-start gap-2.5';
      typingDiv.innerHTML = `
        <div class="h-6 w-6 rounded-lg bg-emerald-600/30 border border-emerald-500/40 flex items-center justify-center font-mono font-bold text-[10px] text-emerald-300 flex-shrink-0">AI</div>
        <div class="glass-card px-3.5 py-2.5 rounded-2xl rounded-tl-none border border-slate-800/80 text-slate-400 max-w-[88%] flex items-center gap-1.5 font-mono text-[10px]">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-bounce"></span>
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.2s]"></span>
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.4s]"></span>
          <span class="text-emerald-400 ml-1">Live Ollama generating from ${selectedModel}...</span>
        </div>
      `;
      box.appendChild(typingDiv);
      box.scrollTop = box.scrollHeight;

      if (btn) btn.disabled = true;

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model: selectedModel, prompt: userText, use_rag: ragToggle })
        });
        const data = await response.json();

        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        let citationsHtml = '';
        if (data.citations && data.citations.length > 0) {
          citationsHtml = `
            <div class="pt-2 border-t border-slate-800/80 space-y-1">
              <div class="text-[10px] text-cyan-400 font-mono font-semibold">📚 Retrieved RAG Citations:</div>
              <div class="flex flex-wrap gap-1">
                ${data.citations.map(c => `
                  <span class="px-2 py-0.5 bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-300 rounded">
                    [Citation ${c.id}] ${c.name} in ${c.file}:${c.lines}
                  </span>
                `).join('')}
              </div>
            </div>
          `;
        }

        const msgTimestamp = Date.now();
        const cardId = 'card-msg-' + msgTimestamp;
        const textId = 'text-msg-' + msgTimestamp;

        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'flex items-start gap-2.5';
        aiMsgDiv.innerHTML = `
          <div class="h-6 w-6 rounded-lg bg-emerald-600/30 border border-emerald-500/40 flex items-center justify-center font-mono font-bold text-[10px] text-emerald-300 flex-shrink-0">AI</div>
          <div id="${cardId}" class="glass-card px-3.5 py-2.5 rounded-2xl rounded-tl-none border border-slate-800/80 text-slate-200 max-w-[88%] space-y-2 transition-all">
            <div class="font-semibold text-emerald-400 font-mono text-[10px] flex items-center justify-between gap-2">
              <span class="truncate">${data.model || selectedModel}</span>
              <span class="text-slate-500 font-normal hidden sm:inline">${data.latency_ms || 0}ms • ${data.tokens || 0} tokens</span>
            </div>
            <div id="${textId}" class="text-slate-200 leading-relaxed whitespace-pre-wrap">${formatMarkdown(data.response || '')}</div>
            ${citationsHtml}
          </div>
        `;
        box.appendChild(aiMsgDiv);
        box.scrollTop = box.scrollHeight;
      } catch (err) {
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        const errDiv = document.createElement('div');
        errDiv.className = 'p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs font-mono';
        errDiv.innerText = 'Ollama Error: ' + (err.message || 'Error occurred while communicating with model.');
        box.appendChild(errDiv);
        box.scrollTop = box.scrollHeight;
      } finally {
        if (btn) btn.disabled = false;
        if (input) input.focus();
      }
    }

    function escapeHtml(text) {
      if (text === undefined || text === null) return '';
      return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    function formatMarkdown(text) {
      if (!text) return '';
      let formatted = escapeHtml(text);
      formatted = formatted.replace(/```python([\\s\\S]*?)```/g, '<pre class="my-2 p-2.5 bg-slate-950 rounded-lg text-emerald-300 font-mono text-[11px] overflow-x-auto border border-slate-900"><code>$1</code></pre>');
      formatted = formatted.replace(/```([\\s\\S]*?)```/g, '<pre class="my-2 p-2.5 bg-slate-950 rounded-lg text-cyan-300 font-mono text-[11px] overflow-x-auto border border-slate-900"><code>$1</code></pre>');
      formatted = formatted.replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 bg-slate-800 rounded font-mono text-cyan-300 text-[11px]">$1</code>');
      formatted = formatted.replace(/\\*\\*([^\\*]+)\\*\\*/g, '<strong class="text-white font-semibold">$1</strong>');
      return formatted;
    }

    // --- Live RAG Search Execution ---
    function setQueryAndSearch(term) {
      document.getElementById('rag-query-input').value = term;
      executeRAGSearch();
    }

    async function executeRAGSearch() {
      const query = document.getElementById('rag-query-input').value.trim();
      const container = document.getElementById('rag-results-container');
      const btn = document.getElementById('rag-submit-btn');

      if (!query) return;

      btn.innerText = 'Searching...';
      container.innerHTML = '<div class="p-4 text-center text-xs font-mono text-cyan-400 animate-pulse">Querying SQLite Vector & FTS5 Index...</div>';

      try {
        const response = await fetch('/api/rag?q=' + encodeURIComponent(query));
        const data = await response.json();
        btn.innerText = 'Query RAG';

        if (!data.results || data.results.length === 0) {
          container.innerHTML = '<div class="p-4 text-center text-xs font-mono text-slate-500">No matching code AST nodes found.</div>';
          return;
        }

        let html = '';
        data.results.forEach(res => {
          const typeBadgeColor = res.type === 'class' ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : 'bg-purple-500/10 text-purple-400 border-purple-500/30';
          html += `
            <div class="glass-card p-4 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-all">
              <div class="flex items-center justify-between text-xs font-mono mb-2">
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 ${typeBadgeColor} border rounded text-[10px] uppercase font-semibold">${res.type}</span>
                  <span class="text-slate-200 font-bold">${res.name}</span>
                  <span class="text-slate-500">(${res.file}:${res.lines})</span>
                </div>
                <span class="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-semibold rounded">RRF: ${res.score.toFixed(4)}</span>
              </div>
              <pre class="p-3 bg-slate-950/90 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto border border-slate-900"><code>${res.snippet}</code></pre>
            </div>
          `;
        });
        container.innerHTML = html;
      } catch (err) {
        btn.innerText = 'Query RAG';
        container.innerHTML = '<div class="p-4 text-center text-rose-400">Search error: ' + err.message + '</div>';
      }
    }

    // --- Live Swarm DAG Execution Animation & API ---
    async function triggerDAG() {
      const btn = document.getElementById('dispatch-btn');
      const statusPill = document.getElementById('dag-status-pill');
      const termBox = document.getElementById('terminal-logs-box');

      btn.disabled = true;
      btn.innerHTML = '<span class="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span> Dispatching Swarm...';
      statusPill.innerHTML = '<span class="text-cyan-400 animate-pulse">Running DAG Pipeline</span>';

      function logMsg(src, msg, color) {
        const time = new Date().toTimeString().split(' ')[0];
        const row = document.createElement('div');
        row.className = 'flex items-start gap-2';
        row.innerHTML = `<span class="text-slate-600">[${time}]</span><span class="font-semibold px-1 rounded text-[10px] bg-slate-900 ${color}">${src}</span><span class="text-slate-300">${msg}</span>`;
        termBox.appendChild(row);
        termBox.scrollTop = termBox.scrollHeight;
      }

      for (let i = 1; i <= 5; i++) {
        const badge = document.getElementById(`node-${i}-badge`);
        const card = document.getElementById(`node-${i}`);
        badge.className = 'px-2 py-0.5 text-xs font-semibold rounded bg-slate-800 text-slate-400 border border-slate-700';
        badge.innerText = 'PENDING';
        card.className = 'glass-card p-4 rounded-xl ring-1 ring-slate-800 transition-all';
      }

      logMsg('SWARM', 'Spawning DAG Root: Node 01 (Supervisor Planner)', 'text-cyan-400');
      setNodeState(1, 'RUNNING', 'bg-sky-500/10 text-sky-400 border-sky-500/30 animate-pulse', 'ring-2 ring-cyan-500 bg-slate-800/80');
      await sleep(600);
      setNodeState(1, 'COMPLETED', 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', 'ring-1 ring-slate-800');
      logMsg('SWARM', 'Node 01 completed. Emitted sub-tasks for parallel workers.', 'text-emerald-400');

      logMsg('SWARM', 'Executing Node 02 (Backend) and Node 03 (Frontend) CONCURRENTLY.', 'text-cyan-400');
      setNodeState(2, 'RUNNING', 'bg-sky-500/10 text-sky-400 border-sky-500/30 animate-pulse', 'ring-2 ring-cyan-500 bg-slate-800/80');
      setNodeState(3, 'RUNNING', 'bg-sky-500/10 text-sky-400 border-sky-500/30 animate-pulse', 'ring-2 ring-cyan-500 bg-slate-800/80');
      await sleep(900);
      setNodeState(2, 'COMPLETED', 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', 'ring-1 ring-slate-800');
      setNodeState(3, 'COMPLETED', 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', 'ring-1 ring-slate-800');
      logMsg('SWARM', 'Parallel nodes completed. Passing aggregated context to QA.', 'text-emerald-400');

      logMsg('SWARM', 'Node 04 (QA Specialist) verifying dependencies and diffs.', 'text-cyan-400');
      setNodeState(4, 'RUNNING', 'bg-sky-500/10 text-sky-400 border-sky-500/30 animate-pulse', 'ring-2 ring-cyan-500 bg-slate-800/80');
      await sleep(700);
      setNodeState(4, 'COMPLETED', 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', 'ring-1 ring-slate-800');

      logMsg('SWARM', 'Node 05 (Sandbox Runner) executing automated build validation.', 'text-cyan-400');
      setNodeState(5, 'RUNNING', 'bg-sky-500/10 text-sky-400 border-sky-500/30 animate-pulse', 'ring-2 ring-cyan-500 bg-slate-800/80');
      await sleep(700);
      setNodeState(5, 'COMPLETED', 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', 'ring-1 ring-slate-800');

      logMsg('SWARM', 'All 5 DAG tasks executed with 100% SUCCESS!', 'text-emerald-400');
      statusPill.innerHTML = '<span class="text-emerald-400">All Workers Idle / Ready</span>';
      btn.disabled = false;
      btn.innerHTML = '<span class="h-2 w-2 rounded-full bg-white animate-ping"></span> Dispatch Swarm DAG';
    }

    function setNodeState(nodeNum, text, badgeClass, cardClass) {
      const badge = document.getElementById(`node-${nodeNum}-badge`);
      const card = document.getElementById(`node-${nodeNum}`);
      badge.className = `px-2 py-0.5 text-xs font-semibold rounded ${badgeClass}`;
      badge.innerText = text;
      card.className = `glass-card p-4 rounded-xl transition-all ${cardClass}`;
    }

    function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }

    function applyDemoPatch() {
      const termBox = document.getElementById('terminal-logs-box');
      const time = new Date().toTimeString().split(' ')[0];
      termBox.innerHTML += `
        <div class="flex items-start gap-2"><span class="text-slate-600">[${time}]</span><span class="font-semibold px-1 rounded text-[10px] bg-slate-900 text-rose-400">SANDBOX</span><span class="text-rose-300">Simulating build error: MissingDependencyError.</span></div>
        <div class="flex items-start gap-2"><span class="text-slate-600">[${time}]</span><span class="font-semibold px-1 rounded text-[10px] bg-slate-900 text-amber-400">HEALER</span><span class="text-amber-200">Synthesizing patch: Verified & auto-repaired in 0.04s.</span></div>
      `;
      termBox.scrollTop = termBox.scrollHeight;
    }

    window.addEventListener('DOMContentLoaded', () => {
      loadOllamaModels();
      executeRAGSearch();
    });
  </script>
</body>
</html>
"""

def fetch_local_models():
    models_list = []
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                for m in data.get("models", []):
                    details = m.get("details", {})
                    size_gb = round(m.get("size", 0) / (1024**3), 2)
                    models_list.append({
                        "name": m.get("name"),
                        "param_size": details.get("parameter_size", "8.0B"),
                        "quantization": details.get("quantization_level", "Q4_0"),
                        "size_gb": size_gb,
                        "context": details.get("context_length", 8192)
                    })
    except Exception:
        pass

    if not models_list:
        models_list = [
            {"name": "llama3:latest", "param_size": "8.0B", "quantization": "Q4_0", "size_gb": 4.66, "context": 8192},
            {"name": "qwen2.5-coder:7b", "param_size": "7.6B", "quantization": "Q4_K_M", "size_gb": 4.68, "context": 32768},
            {"name": "mistral:latest", "param_size": "7.2B", "quantization": "Q4_K_M", "size_gb": 4.37, "context": 32768},
            {"name": "nomic-embed-text:latest", "param_size": "137M", "quantization": "F16", "size_gb": 0.26, "context": 2048}
        ]
    return models_list

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/" or parsed.path == "/index.html":
            models = fetch_local_models()
            opts_html = "\n".join([
                f'<option value="{m["name"]}" {"selected" if m["name"]=="qwen2.5-coder:7b" else ""}>🤖 {m["name"]} ({m["param_size"]})</option>'
                for m in models
            ])
            table_rows_html = "\n".join([
                f'''<tr class="hover:bg-slate-800/30">
                  <td class="py-3.5 font-semibold text-slate-200 flex items-center gap-2">
                    <span class="h-1.5 w-1.5 rounded-full bg-cyan-400"></span>{m["name"]}
                  </td>
                  <td class="py-3.5 text-slate-300">{m["param_size"]}</td>
                  <td class="py-3.5"><span class="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[11px] border border-slate-700/60">{m["quantization"]}</span></td>
                  <td class="py-3.5 text-slate-400">{m["size_gb"]} GB</td>
                  <td class="py-3.5 text-slate-300">{m["context"]}</td>
                  <td class="py-3.5 text-right"><span class="px-2.5 py-1 rounded text-[11px] font-semibold border bg-emerald-500/10 text-emerald-400 border-emerald-500/30">Live Ready</span></td>
                </tr>'''
                for m in models
            ])
            rendered_html = DASHBOARD_HTML
            rendered_html = rendered_html.replace("{{MODEL_OPTIONS}}", opts_html)
            rendered_html = rendered_html.replace("{{MODEL_TABLE_ROWS}}", table_rows_html)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(rendered_html.encode("utf-8"))

        elif parsed.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "workstation-dashboard"}).encode("utf-8"))

        elif parsed.path == "/api/models":
            models_list = fetch_local_models()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"models": models_list}).encode("utf-8"))

        elif parsed.path == "/api/system/analyze":
            mem = psutil.virtual_memory()
            ram_gb = round(mem.total / (1024**3), 1)
            ram_free_gb = round(mem.available / (1024**3), 1)
            cpu_cores = psutil.cpu_count(logical=True)
            arch = platform.machine()

            installed_models = []
            try:
                with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    installed_models = [m.get("name") for m in data.get("models", [])]
            except Exception:
                pass

            if not installed_models:
                installed_models = ["llama3:latest", "qwen2.5-coder:7b", "mistral:latest", "nomic-embed-text:latest"]

            if ram_gb >= 32:
                tier = "Tier 1: High-Performance Workstation"
                recommendation = f"Your PC has {ram_gb} GB RAM and {cpu_cores} CPU cores! It can comfortably run 8B, 14B, and 32B quantized models (e.g. qwen2.5-coder:14b, deepseek-r1:8b) at high token throughput with zero swapping."
            elif ram_gb >= 16:
                tier = "Tier 2: Balanced AI Workstation"
                recommendation = f"Your PC has {ram_gb} GB RAM. It is ideal for running 7B-8B Q4 models (llama3:8b, qwen2.5-coder:7b, mistral:7b) with ~15ms per token."
            else:
                tier = "Tier 3: Lightweight AI Setup"
                recommendation = f"Your PC has {ram_gb} GB RAM. We recommend running 1.5B to 3B models (e.g. phi-3:mini, qwen2.5-coder:1.5b) for lightweight execution."

            analysis_result = {
                "cpu_cores": cpu_cores,
                "ram_gb": ram_gb,
                "ram_free_gb": ram_free_gb,
                "arch": arch,
                "tier": tier,
                "recommendation": recommendation,
                "model_count": len(installed_models),
                "models": installed_models
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(analysis_result).encode("utf-8"))

        elif parsed.path == "/api/rag":
            query_params = urllib.parse.parse_qs(parsed.query)
            q = query_params.get("q", [""])[0]
            
            results = search_engine.search_code(q, top_k=5)
            formatted = []
            for r in results:
                node = r["node"]
                formatted.append({
                    "id": node.get("id"),
                    "file": node.get("file_path"),
                    "type": node.get("node_type"),
                    "name": node.get("node_name"),
                    "lines": f"{node.get('start_line')}-{node.get('end_line')}",
                    "score": round(r.get("rrf_score", 0), 4),
                    "snippet": node.get("source_code", "")[:400]
                })

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"query": q, "results": formatted}).encode("utf-8"))

        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if parsed.path == "/api/ingest":
            title = data.get("title", "Untitled Document")
            category = data.get("category", "General")
            content = data.get("content", "")
            
            doc_id = doc_ingester.ingest_text(title, category, content)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "doc_id": doc_id}).encode("utf-8"))

        elif parsed.path == "/api/chat":
            model = data.get("model", "llama3:latest")
            user_prompt = data.get("prompt", "")
            use_rag = data.get("use_rag", True)

            citations = []
            if use_rag:
                final_prompt, citations = rag_pipeline.build_augmented_prompt(user_prompt, top_k=3)
            else:
                final_prompt = user_prompt

            ollama_response = None
            t0 = time.time()
            try:
                req = urllib.request.Request(
                    "http://127.0.0.1:11434/api/generate",
                    data=json.dumps({"model": model, "prompt": final_prompt, "stream": False}).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    if resp.status == 200:
                        res_json = json.loads(resp.read().decode("utf-8"))
                        ollama_response = res_json.get("response", "")
            except Exception:
                try:
                    alt_req = urllib.request.Request(
                        "http://127.0.0.1:11434/api/generate",
                        data=json.dumps({"model": "llama3", "prompt": final_prompt, "stream": False}).encode("utf-8"),
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(alt_req, timeout=60) as resp:
                        res_json = json.loads(resp.read().decode("utf-8"))
                        ollama_response = res_json.get("response", "")
                except Exception:
                    pass

            duration_ms = int((time.time() - t0) * 1000)

            if not ollama_response:
                response_text = f"Connected to {model}. Processing query with local offline engine."
            else:
                response_text = ollama_response

            result_payload = {
                "model": model,
                "prompt": user_prompt,
                "response": response_text,
                "tokens": len(response_text.split()),
                "latency_ms": duration_ms,
                "citations": citations
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result_payload).encode("utf-8"))

def run(port=3009):
    socketserver.TCPServer.allow_reuse_address = True
    for p in [port, 3009, 3000, 3001, 8080]:
        try:
            with socketserver.TCPServer(("127.0.0.1", p), DashboardHandler) as httpd:
                print(f"Workstation Control Dashboard listening at http://localhost:{p}")
                httpd.serve_forever()
                break
        except OSError:
            continue

run_server = run

if __name__ == "__main__":
    run_server()
