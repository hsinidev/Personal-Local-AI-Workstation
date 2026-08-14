import os
import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from core.memory.db import MemoryDB
from core.memory.embedder import LocalEmbedder, HybridSearchEngine
from core.orchestrator.router import LLMRouter

class MCPBridge:
    """Dynamic MCP Tool Bridge for Workstation Swarm Sub-Agents."""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        self.db = MemoryDB()
        self.embedder = LocalEmbedder()
        self.search_engine = HybridSearchEngine(self.db, self.embedder)
        self.llm_router = LLMRouter()

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return available dynamic MCP tools and their parameter schemas."""
        return [
            {
                "name": "memory_search",
                "description": "Perform hybrid BM25 + Vector search over indexed code AST nodes and memory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query keywords or code snippet"},
                        "top_k": {"type": "integer", "default": 5}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "filesystem_read",
                "description": "Read file contents from workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {"type": "string", "description": "Relative path to file in workspace"}
                    },
                    "required": ["relative_path"]
                }
            },
            {
                "name": "filesystem_write",
                "description": "Write or overwrite file contents in workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {"type": "string", "description": "Relative path to file"},
                        "content": {"type": "string", "description": "Text content to write"}
                    },
                    "required": ["relative_path", "content"]
                }
            },
            {
                "name": "filesystem_list",
                "description": "List files and directories in a given path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {"type": "string", "default": "."}
                    }
                }
            },
            {
                "name": "terminal_execute",
                "description": "Execute a shell command in the local workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command line to execute"},
                        "timeout_sec": {"type": "integer", "default": 30}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "llm_route",
                "description": "Route a task prompt to the optimal local model.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "default": "coding"},
                        "prompt": {"type": "string"}
                    },
                    "required": ["prompt"]
                }
            }
        ]

    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch tool call dynamically to respective subsystem."""
        try:
            if tool_name == "memory_search":
                query = arguments.get("query", "")
                top_k = int(arguments.get("top_k", 5))
                results = self.search_engine.search_code(query, top_k=top_k)
                formatted = [
                    {
                        "score": r["rrf_score"],
                        "file": r["node"]["file_path"],
                        "node_type": r["node"]["node_type"],
                        "node_name": r["node"]["node_name"],
                        "source_preview": r["node"]["source_code"][:150] + "..."
                    }
                    for r in results
                ]
                return {"status": "success", "results": formatted}

            elif tool_name == "filesystem_read":
                rel_path = arguments.get("relative_path", "")
                target_path = os.path.abspath(os.path.join(self.workspace_root, rel_path))
                if not target_path.startswith(self.workspace_root):
                    return {"status": "error", "error": "Access denied outside workspace root"}
                if not os.path.exists(target_path):
                    return {"status": "error", "error": f"File not found: {rel_path}"}
                with open(target_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return {"status": "success", "content": content, "size_bytes": len(content)}

            elif tool_name == "filesystem_write":
                rel_path = arguments.get("relative_path", "")
                content = arguments.get("content", "")
                target_path = os.path.abspath(os.path.join(self.workspace_root, rel_path))
                if not target_path.startswith(self.workspace_root):
                    return {"status": "error", "error": "Access denied outside workspace root"}
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"status": "success", "file": rel_path, "written_bytes": len(content)}

            elif tool_name == "filesystem_list":
                rel_path = arguments.get("relative_path", ".")
                target_path = os.path.abspath(os.path.join(self.workspace_root, rel_path))
                if not target_path.startswith(self.workspace_root):
                    return {"status": "error", "error": "Access denied"}
                items = os.listdir(target_path)
                return {"status": "success", "path": rel_path, "entries": items}

            elif tool_name == "terminal_execute":
                cmd = arguments.get("command", "")
                timeout = int(arguments.get("timeout_sec", 30))
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=self.workspace_root
                )
                try:
                    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                    return {
                        "status": "success" if proc.returncode == 0 else "failed",
                        "exit_code": proc.returncode,
                        "stdout": stdout.decode("utf-8", errors="replace"),
                        "stderr": stderr.decode("utf-8", errors="replace")
                    }
                except asyncio.TimeoutError:
                    proc.kill()
                    return {"status": "error", "error": f"Command timed out after {timeout} seconds"}

            elif tool_name == "llm_route":
                task_type = arguments.get("task_type", "coding")
                prompt = arguments.get("prompt", "")
                model = self.llm_router.resolve_model(task_type)
                health = await self.llm_router.check_health()
                return {
                    "status": "success",
                    "task_type": task_type,
                    "target_model": model,
                    "endpoint_status": health.get("status")
                }

            else:
                return {"status": "error", "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}
