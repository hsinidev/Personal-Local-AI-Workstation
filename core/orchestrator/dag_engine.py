import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class DAGTask:
    task_id: str
    name: str
    agent_role: str  # e.g. 'coder', 'qa', 'indexer', 'builder', 'orchestrator'
    dependencies: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class DAGOrchestrator:
    """Hyper-Parallel Task DAG Execution Engine for Multi-Agent Swarms."""

    def __init__(self, max_concurrency: int = 4):
        self.max_concurrency = max_concurrency
        self.tasks: Dict[str, DAGTask] = {}
        self.semaphore = asyncio.Semaphore(max_concurrency)

    def add_task(self, task: DAGTask):
        self.tasks[task.task_id] = task

    def add_tasks(self, tasks: List[DAGTask]):
        for t in tasks:
            self.add_task(t)

    def _validate_dag(self):
        """Check for cycles and missing dependencies."""
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Task '{task_id}' depends on non-existent task '{dep}'")

        visited = {}
        def has_cycle(node: str) -> bool:
            visited[node] = 1  # visiting
            for dep in self.tasks[node].dependencies:
                if visited.get(dep) == 1:
                    return True
                if visited.get(dep) == 0 and has_cycle(dep):
                    return True
            visited[node] = 2  # visited
            return False

        for node in self.tasks:
            visited[node] = 0
        for node in self.tasks:
            if visited[node] == 0 and has_cycle(node):
                raise ValueError("Cyclic dependency detected in DAG graph")

    async def execute_dag(
        self,
        task_handler: Optional[Callable[[DAGTask, Dict[str, Any]], Awaitable[Any]]] = None
    ) -> Dict[str, Any]:
        """Execute the DAG graph with parallel concurrency and topological dependency resolution."""
        self._validate_dag()
        start_time = time.time()
        running_futures: Dict[str, asyncio.Task] = {}
        results: Dict[str, Any] = {}

        if task_handler is None:
            task_handler = self._default_agent_handler

        while True:
            # 1. Identify tasks ready to run
            ready_tasks = []
            for t_id, t in self.tasks.items():
                if t.status == TaskStatus.PENDING:
                    deps_satisfied = all(
                        self.tasks[dep].status == TaskStatus.COMPLETED for dep in t.dependencies
                    )
                    any_dep_failed = any(
                        self.tasks[dep].status == TaskStatus.FAILED for dep in t.dependencies
                    )
                    if any_dep_failed:
                        t.status = TaskStatus.FAILED
                        t.error = "Upstream dependency failed"
                    elif deps_satisfied:
                        t.status = TaskStatus.READY
                        ready_tasks.append(t)

            # 2. Launch ready tasks concurrently
            for task in ready_tasks:
                task.status = TaskStatus.RUNNING
                task.start_time = time.time()
                # Aggregate upstream outputs
                upstream_context = {
                    dep: self.tasks[dep].result for dep in task.dependencies
                }
                
                coro = self._run_single_task(task, upstream_context, task_handler)
                running_futures[task.task_id] = asyncio.create_task(coro)

            # 3. If no tasks running and none ready, we are done
            if not running_futures:
                break

            # 4. Wait for at least one running task to complete
            done, _ = await asyncio.wait(
                running_futures.values(),
                return_when=asyncio.FIRST_COMPLETED
            )

            for completed_future in done:
                # Find corresponding task_id
                finished_id = None
                for t_id, f in list(running_futures.items()):
                    if f == completed_future:
                        finished_id = t_id
                        del running_futures[t_id]
                        break

        total_duration = time.time() - start_time
        summary = {
            "total_tasks": len(self.tasks),
            "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
            "total_duration_sec": round(total_duration, 4),
            "tasks": {
                t_id: {
                    "name": t.name,
                    "role": t.agent_role,
                    "status": t.status.value,
                    "duration_sec": round((t.end_time or 0) - (t.start_time or 0), 4) if t.start_time and t.end_time else 0,
                    "result": t.result,
                    "error": t.error
                }
                for t_id, t in self.tasks.items()
            }
        }
        return summary

    async def _run_single_task(
        self,
        task: DAGTask,
        upstream_context: Dict[str, Any],
        handler: Callable[[DAGTask, Dict[str, Any]], Awaitable[Any]]
    ):
        async with self.semaphore:
            try:
                res = await handler(task, upstream_context)
                task.result = res
                task.status = TaskStatus.COMPLETED
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
            finally:
                task.end_time = time.time()

    async def _default_agent_handler(self, task: DAGTask, upstream_context: Dict[str, Any]) -> Any:
        """Simulated sub-agent worker execution."""
        await asyncio.sleep(0.05)  # Simulated processing latency
        return {
            "executed_by": f"Agent[{task.agent_role}]",
            "task_name": task.name,
            "processed_payload": task.payload,
            "received_upstream_keys": list(upstream_context.keys())
        }
