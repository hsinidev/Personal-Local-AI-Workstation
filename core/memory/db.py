import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

class MemoryDB:
    """SQLite Storage & Hybrid Index Manager for Workstation Memory & Documents."""

    def __init__(self, db_path: str = "core/memory/workstation_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables using db_schema.sql and add documents table if missing."""
        schema_path = os.path.join(os.path.dirname(__file__), "db_schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                # Ensure documents tables exist
                conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                conn.commit()

    # --- Code AST Node Operations ---
    def store_ast_node(
        self,
        node_id: str,
        file_path: str,
        node_type: str,
        node_name: str,
        start_line: int,
        end_line: int,
        docstring: Optional[str],
        source_code: str,
        embedding: List[float]
    ) -> bool:
        embedding_json = json.dumps(embedding)
        with self.get_connection() as conn:
            conn.execute("DELETE FROM code_ast_fts WHERE node_id = ?", (node_id,))
            conn.execute(
                """
                INSERT OR REPLACE INTO code_ast_nodes 
                (id, file_path, node_type, node_name, start_line, end_line, docstring, source_code, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (node_id, file_path, node_type, node_name, start_line, end_line, docstring or "", source_code, embedding_json)
            )
            conn.execute(
                """
                INSERT INTO code_ast_fts (node_id, file_path, node_name, docstring, source_code)
                VALUES (?, ?, ?, ?, ?)
                """,
                (node_id, file_path, node_name, docstring or "", source_code)
            )
            conn.commit()
            return True

    def search_fts(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        clean_q = "".join([c if c.isalnum() else " " for c in query]).strip()
        if not clean_q:
            return []
        match_expr = " OR ".join([f"{w}*" for w in clean_q.split()])
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT node_id, rank
                FROM code_ast_fts
                WHERE code_ast_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (match_expr, top_k)
            )
            return [{"node_id": row["node_id"], "rank": row["rank"]} for row in cursor.fetchall()]

    def get_all_ast_embeddings(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, file_path, node_type, node_name, start_line, end_line, docstring, source_code, embedding
                FROM code_ast_nodes
                WHERE embedding IS NOT NULL
                """
            )
            results = []
            for row in cursor.fetchall():
                try:
                    emb = json.loads(row["embedding"])
                except Exception:
                    emb = []
                results.append({
                    "id": row["id"],
                    "file_path": row["file_path"],
                    "node_type": row["node_type"],
                    "node_name": row["node_name"],
                    "start_line": row["start_line"],
                    "end_line": row["end_line"],
                    "docstring": row["docstring"],
                    "source_code": row["source_code"],
                    "embedding": emb
                })
            return results

    # --- Document & Knowledge Ingestion ---
    def store_document(self, doc_id: str, title: str, category: str, content: str, embedding: List[float]) -> bool:
        embedding_json = json.dumps(embedding)
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_documents (id, title, category, content, embedding)
                VALUES (?, ?, ?, ?, ?)
                """,
                (doc_id, title, category, content, embedding_json)
            )
            conn.commit()
            return True

    def get_all_documents(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, category, content, embedding, created_at FROM knowledge_documents ORDER BY created_at DESC"
            )
            docs = []
            for row in cursor.fetchall():
                try:
                    emb = json.loads(row["embedding"]) if row["embedding"] else []
                except Exception:
                    emb = []
                docs.append({
                    "id": row["id"],
                    "title": row["title"],
                    "category": row["category"],
                    "content": row["content"],
                    "embedding": emb,
                    "created_at": row["created_at"]
                })
            return docs

    def log_conversation(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversation_logs (session_id, role, content, metadata)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, json.dumps(metadata or {}))
            )
            conn.commit()
