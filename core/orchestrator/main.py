from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from core.orchestrator.router import LLMRouter
from core.orchestrator.dag_engine import DAGOrchestrator, DAGTask, TaskStatus
from core.orchestrator.mcp_bridge import MCPBridge
from core.orchestrator.sandbox import SandboxRunner

app = FastAPI(
    title="Personal Local AI Workstation - Orchestrator Engine",
    description="Hyper-Parallel Swarm Routing, Task DAG Engine, MCP Bridge, and Self-Healing Sandbox",
    version="1.1.0"
)

router = LLMRouter()
mcp_bridge = MCPBridge()
sandbox = SandboxRunner()

# --- Request Models ---
class RouteRequest(BaseModel):
    task_type: str = "coding"
    prompt: str
    temperature: Optional[float] = None

class ToolInvokeRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}

class SandboxExecRequest(BaseModel):
    command: str
    timeout_sec: int = 30
    auto_heal: bool = True

class DAGTaskModel(BaseModel):
    task_id: str
    name: str
    agent_role: str
    dependencies: List[str] = []
    payload: Dict[str, Any] = {}

class DAGExecutionRequest(BaseModel):
    tasks: List[DAGTaskModel]
    max_concurrency: int = 4

# --- Endpoints ---
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Hyper-Parallel Swarm Orchestrator Engine",
        "version": "1.1.0"
    }

@app.get("/health")
async def health_check():
    ollama_status = await router.check_health()
    return {
        "orchestrator": "online",
        "ollama_endpoint": ollama_status
    }

@app.post("/route")
async def route_task(req: RouteRequest):
    selected_model = router.resolve_model(req.task_type)
    health = await router.check_health()
    return {
        "task_type": req.task_type,
        "selected_model": selected_model,
        "endpoint_status": health["status"],
        "prompt_received": req.prompt[:50] + "..." if len(req.prompt) > 50 else req.prompt
    }

@app.get("/tools/list")
async def list_tools():
    return {"tools": mcp_bridge.list_tools()}

@app.post("/tools/invoke")
async def invoke_tool(req: ToolInvokeRequest):
    res = await mcp_bridge.invoke_tool(req.tool_name, req.arguments)
    return res

@app.post("/sandbox/exec")
async def execute_in_sandbox(req: SandboxExecRequest):
    res = await sandbox.execute(req.command, timeout_sec=req.timeout_sec, auto_heal=req.auto_heal)
    return {
        "command": res.command,
        "exit_code": res.exit_code,
        "is_success": res.is_success,
        "duration_ms": res.duration_ms,
        "stdout": res.stdout,
        "stderr": res.stderr,
        "diagnostic_patch": res.diagnostic_patch
    }

@app.post("/swarm/dag/execute")
async def execute_dag(req: DAGExecutionRequest):
    orchestrator = DAGOrchestrator(max_concurrency=req.max_concurrency)
    for t in req.tasks:
        orchestrator.add_task(DAGTask(
            task_id=t.task_id,
            name=t.name,
            agent_role=t.agent_role,
            dependencies=t.dependencies,
            payload=t.payload
        ))
    result = await orchestrator.execute_dag()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
