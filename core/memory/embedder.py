import math
import json
import re
import hashlib
import uuid
import httpx
from typing import List, Dict, Any, Tuple, Optional
from core.memory.db import MemoryDB

class LocalEmbedder:
    """Local Embeddings Provider with Ollama & Deterministic TF-IDF Fallback."""

    def __init__(self, ollama_url: str = "http://127.0.0.1:11434", model: str = "nomic-embed-text", dimension: int = 768):
        self.ollama_url = ollama_url
        self.model = model
        self.dimension = dimension

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector. Tries Ollama endpoint first, falls back to TF-IDF vectorizer."""
        try:
            res = httpx.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=3.0
            )
            if res.status_code == 200:
                data = res.json()
                vec = data.get("embedding")
                if vec and isinstance(vec, list):
                    return vec
        except Exception:
            pass

        return self._generate_fallback_embedding(text)

    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Deterministic hash & TF-IDF term frequency embedding generator (768-dim normalized vector)."""
        vec = [0.0] * self.dimension
        words = re.findall(r'\w+', text.lower())
        if not words:
            return vec

        for word in words:
            h = hashlib.md5(word.encode('utf-8')).hexdigest()
            idx1 = int(h[:4], 16) % self.dimension
            idx2 = int(h[4:8], 16) % self.dimension
            val = (int(h[8:10], 16) / 255.0) * 2.0 - 1.0
            vec[idx1] += 1.0
            vec[idx2] += val

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

class HybridSearchEngine:
    """Hybrid Search Engine combining SQLite FTS5 (BM25) and Cosine Vector Similarity."""

    def __init__(self, db: MemoryDB, embedder: LocalEmbedder):
        self.db = db
        self.embedder = embedder

    def search_code(self, query: str, top_k: int = 5, k_rrf: int = 60) -> List[Dict[str, Any]]:
        # 1. FTS5 BM25 Ranking
        fts_hits = self.db.search_fts(query, top_k=20)
        fts_ranks = {hit["node_id"]: rank for rank, hit in enumerate(fts_hits, start=1)}

        # 2. Vector Cosine Similarity Ranking
        query_vec = self.embedder.generate_embedding(query)
        all_nodes = self.db.get_all_ast_embeddings()
        
        sim_scores = []
        for node in all_nodes:
            if node["embedding"]:
                sim = self.embedder.cosine_similarity(query_vec, node["embedding"])
                sim_scores.append((node, sim))

        sim_scores.sort(key=lambda x: x[1], reverse=True)
        vec_ranks = {item[0]["id"]: rank for rank, item in enumerate(sim_scores[:20], start=1)}

        # 3. Reciprocal Rank Fusion (RRF)
        node_map = {node["id"]: node for node in all_nodes}
        rrf_scores = {}
        all_ids = set(fts_ranks.keys()).union(set(vec_ranks.keys()))

        for nid in all_ids:
            score = 0.0
            if nid in fts_ranks:
                score += 1.0 / (k_rrf + fts_ranks[nid])
            if nid in vec_ranks:
                score += 1.0 / (k_rrf + vec_ranks[nid])
            rrf_scores[nid] = score

        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [{"node": node_map[nid], "rrf_score": score} for nid, score in sorted_results if nid in node_map]

    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search ingested knowledge documents via vector similarity."""
        query_vec = self.embedder.generate_embedding(query)
        docs = self.db.get_all_documents()
        scored = []
        for d in docs:
            if d["embedding"]:
                sim = self.embedder.cosine_similarity(query_vec, d["embedding"])
                scored.append({"doc": d, "score": sim})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

class ContextualRAGPipeline:
    """Advanced RAG Orchestrator that retrieves local context and augments LLM generation."""

    def __init__(self, db: MemoryDB, embedder: LocalEmbedder, search_engine: HybridSearchEngine):
        self.db = db
        self.embedder = embedder
        self.search_engine = search_engine

    def build_augmented_prompt(self, user_query: str, top_k: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
        """Retrieve matching code AST nodes and build a citation-backed system prompt."""
        results = self.search_engine.search_code(user_query, top_k=top_k)
        citations = []
        
        context_parts = []
        for idx, res in enumerate(results, 1):
            node = res["node"]
            citations.append({
                "id": idx,
                "file": node["file_path"],
                "name": node["node_name"],
                "type": node["node_type"],
                "lines": f"{node['start_line']}-{node['end_line']}",
                "score": res["rrf_score"]
            })
            context_parts.append(
                f"--- [Citation {idx}: {node['node_type'].upper()} {node['node_name']} in {node['file_path']}:{node['start_line']}-{node['end_line']}] ---\n"
                f"{node['source_code']}\n"
            )

        context_block = "\n".join(context_parts) if context_parts else "No direct codebase AST matches found."
        
        augmented_prompt = (
            f"You are the Personal Local AI Workstation Code Assistant.\n"
            f"Here is verified context retrieved from the user's local codebase:\n\n"
            f"{context_block}\n\n"
            f"User Question: {user_query}\n\n"
            f"Please answer the question accurately. If referencing the codebase, cite the relevant [Citation X]."
        )

        return augmented_prompt, citations

class DocumentIngester:
    """Ingests custom documents, markdown files, and API docs into SQLite Vector Memory."""

    def __init__(self, db: MemoryDB, embedder: LocalEmbedder):
        self.db = db
        self.embedder = embedder

    def ingest_text(self, title: str, category: str, content: str) -> str:
        doc_id = str(uuid.uuid4())[:8]
        embedding = self.embedder.generate_embedding(f"{title}\n{category}\n{content}")
        self.db.store_document(doc_id, title, category, content, embedding)
        return doc_id
