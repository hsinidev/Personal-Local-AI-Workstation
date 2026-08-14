# Core Orchestrator Engine

FastAPI & Python IPC Bridge responsible for local Swarm Routing, model selection, health monitoring, and fallback routing across local LLM endpoints.

## Architecture
- `main.py`: FastAPI server exposing `/health` and `/route` endpoints.
- `router.py`: LLMRouter handling `config/llm_router.json` evaluation and fallback resolution.

## Quick Start
```bash
pip install -r requirements.txt
python -m core.orchestrator.main
```
