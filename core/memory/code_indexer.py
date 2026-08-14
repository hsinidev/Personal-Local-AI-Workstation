import os
import ast
import re
import hashlib
from typing import List, Dict, Any
from core.memory.db import MemoryDB
from core.memory.embedder import LocalEmbedder

class CodeASTIndexer:
    """Workspace Code Scanner & AST Indexer for Python and JS/TS files."""

    def __init__(self, db: MemoryDB, embedder: LocalEmbedder):
        self.db = db
        self.embedder = embedder

    def index_workspace(self, root_dir: str, exclude_dirs: List[str] = None) -> Dict[str, Any]:
        if exclude_dirs is None:
            exclude_dirs = ["node_modules", ".git", ".next", "__pycache__", ".venv", "venv", "dist", "build"]

        indexed_files = 0
        total_nodes = 0
        file_stats = []

        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_dir)
                ext = os.path.splitext(filename)[1].lower()

                nodes = []
                if ext == ".py":
                    nodes = self._parse_python_ast(file_path, rel_path)
                elif ext in [".js", ".jsx", ".ts", ".tsx"]:
                    nodes = self._parse_jsts_ast(file_path, rel_path)

                if nodes:
                    indexed_files += 1
                    total_nodes += len(nodes)
                    file_stats.append({"file": rel_path, "nodes_count": len(nodes)})

                    for node in nodes:
                        # Combine metadata + source code for embedding text
                        embed_text = f"File: {node['file_path']}\nType: {node['node_type']}\nName: {node['node_name']}\nDocstring: {node['docstring']}\nCode:\n{node['source_code']}"
                        vec = self.embedder.generate_embedding(embed_text)

                        self.db.store_ast_node(
                            node_id=node["id"],
                            file_path=node["file_path"],
                            node_type=node["node_type"],
                            node_name=node["node_name"],
                            start_line=node["start_line"],
                            end_line=node["end_line"],
                            docstring=node["docstring"],
                            source_code=node["source_code"],
                            embedding=vec
                        )

        return {
            "indexed_files": indexed_files,
            "total_nodes": total_nodes,
            "file_stats": file_stats
        }

    def _parse_python_ast(self, abs_path: str, rel_path: str) -> List[Dict[str, Any]]:
        nodes = []
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                code = f.read()
            lines = code.splitlines()
            parsed = ast.parse(code, filename=abs_path)

            for item in ast.walk(parsed):
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    node_type = "class" if isinstance(item, ast.ClassDef) else ("async_function" if isinstance(item, ast.AsyncFunctionDef) else "function")
                    start_line = item.lineno
                    end_line = getattr(item, "end_lineno", start_line)
                    docstring = ast.get_docstring(item) or ""

                    # Extract source code lines
                    node_lines = lines[start_line - 1:end_line]
                    source_code = "\n".join(node_lines)

                    node_id = f"{rel_path}::{item.name}::{start_line}"
                    nodes.append({
                        "id": node_id,
                        "file_path": rel_path,
                        "node_type": node_type,
                        "node_name": item.name,
                        "start_line": start_line,
                        "end_line": end_line,
                        "docstring": docstring,
                        "source_code": source_code
                    })
        except Exception as e:
            pass
        return nodes

    def _parse_jsts_ast(self, abs_path: str, rel_path: str) -> List[Dict[str, Any]]:
        nodes = []
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                code = f.read()
            lines = code.splitlines()

            # Regex patterns for JS/TS function / class / component definitions
            pattern = re.compile(
                r'^(export\s+default\s+function|export\s+function|function|const|let|var)\s+([A-Za-z0-9_]+)\s*(=|\()',
                re.MULTILINE
            )

            for idx, line in enumerate(lines, 1):
                match = pattern.search(line)
                if match:
                    name = match.group(2)
                    if name in ["if", "for", "while", "switch", "catch"]:
                        continue

                    # Estimate end line by looking for closing brace or chunk of 25 lines
                    start_line = idx
                    end_line = min(idx + 25, len(lines))
                    source_code = "\n".join(lines[start_line - 1:end_line])

                    node_id = f"{rel_path}::{name}::{start_line}"
                    nodes.append({
                        "id": node_id,
                        "file_path": rel_path,
                        "node_type": "component" if name[0].isupper() else "function",
                        "node_name": name,
                        "start_line": start_line,
                        "end_line": end_line,
                        "docstring": "",
                        "source_code": source_code
                    })
        except Exception as e:
            pass
        return nodes


if __name__ == "__main__":
    db = MemoryDB()
    embedder = LocalEmbedder()
    indexer = CodeASTIndexer(db, embedder)
    result = indexer.index_workspace(".")
    print(f"Indexing Complete: {result['indexed_files']} files, {result['total_nodes']} nodes indexed.")
