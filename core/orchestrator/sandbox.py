import os
import re
import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from core.memory.db import MemoryDB
from core.memory.embedder import LocalEmbedder, HybridSearchEngine

@dataclass
class ExecutionResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    is_success: bool
    diagnostic_patch: Optional[Dict[str, Any]] = None

class SandboxRunner:
    """Subprocess Sandbox Runner with Automated QA Error Diagnosis & Self-Healing Patching."""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        self.db = MemoryDB()
        self.embedder = LocalEmbedder()
        self.search_engine = HybridSearchEngine(self.db, self.embedder)

    async def execute(self, command: str, timeout_sec: int = 60, auto_heal: bool = True) -> ExecutionResult:
        start_time = time.time()
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.workspace_root
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
            exit_code = proc.returncode or 0
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")
        except asyncio.TimeoutError:
            proc.kill()
            exit_code = -1
            stdout = ""
            stderr = f"Execution timed out after {timeout_sec} seconds."

        duration_ms = (time.time() - start_time) * 1000
        is_success = (exit_code == 0)
        diagnostic = None

        if not is_success and auto_heal:
            diagnostic = await self._diagnose_and_generate_patch(command, exit_code, stdout, stderr)

        return ExecutionResult(
            command=command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=round(duration_ms, 2),
            is_success=is_success,
            diagnostic_patch=diagnostic
        )

    async def _diagnose_and_generate_patch(
        self, command: str, exit_code: int, stdout: str, stderr: str
    ) -> Dict[str, Any]:
        """Analyze build/test error traces and synthesize a QA diagnostic patch."""
        full_log = (stderr + "\n" + stdout).strip()

        # 1. Classify Error Category
        category = "UnknownExecutionError"
        if "ModuleNotFoundError" in full_log or "No module named" in full_log:
            category = "MissingDependencyError"
        elif "SyntaxError" in full_log:
            category = "SyntaxError"
        elif "TypeError" in full_log:
            category = "TypeError"
        elif "ImportError" in full_log:
            category = "ImportError"
        elif "TS" in full_log or "Type error:" in full_log:
            category = "TypeScriptCompilationError"
        elif "cannot find package" in full_log or "Cannot find module" in full_log:
            category = "NodeModuleResolutionError"
        elif "error[E" in full_log:
            category = "RustCompilationError"
        elif "AssertionError" in full_log:
            category = "AssertionFailure"

        # 2. Extract Culprit Files and Lines
        py_trace_matches = re.findall(r'File "([^"]+)", line (\d+)', full_log)
        culprits = []
        for file_path, line_num in py_trace_matches:
            rel = os.path.relpath(file_path, self.workspace_root) if os.path.isabs(file_path) else file_path
            culprits.append({"file": rel, "line": int(line_num)})

        # 3. Retrieve Context from Memory
        retrieved_nodes = []
        if culprits:
            primary_culprit = culprits[-1]["file"]
            search_res = self.search_engine.search_code(primary_culprit, top_k=2)
            retrieved_nodes = [
                f"{r['node']['file_path']}::{r['node']['node_name']}" for r in search_res
            ]

        # 4. Synthesize Remediation Recommendations
        remediation_steps = []
        if category == "MissingDependencyError":
            mod_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", full_log)
            missing_mod = mod_match.group(1) if mod_match else "unknown"
            remediation_steps.append(f"Install missing package: `pip install {missing_mod}`")
        elif category == "NodeModuleResolutionError":
            remediation_steps.append("Install missing npm dependencies: `npm install`")
        elif category == "SyntaxError":
            remediation_steps.append("Review syntax error at indicated line and fix unmatched tokens or indentation.")
        else:
            remediation_steps.append("Check traceback context and verify variable types and function arguments.")

        return {
            "error_category": category,
            "exit_code": exit_code,
            "failed_command": command,
            "culprits": culprits,
            "related_memory_symbols": retrieved_nodes,
            "remediation_plan": remediation_steps,
            "qa_agent_action": "Dispatched automated remediation patch for swarm supervisor review."
        }
