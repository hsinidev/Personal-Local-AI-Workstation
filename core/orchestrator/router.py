import json
import os
import httpx
from typing import Dict, Any, List, Optional

class LLMRouter:
    """Swarm Routing engine for Local LLM endpoints and fallbacks."""
    
    def __init__(self, config_path: str = "config/llm_router.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"endpoints": {}, "model_routes": {}}

    async def check_health(self) -> Dict[str, Any]:
        """Check Ollama endpoint health status."""
        endpoint = self.config.get("endpoints", {}).get("ollama_local", {})
        tags_url = endpoint.get("base_url", "http://127.0.0.1:11434") + endpoint.get("tags_api_path", "/api/tags")
        
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(tags_url)
                if res.status_code == 200:
                    models = [m["name"] for m in res.json().get("models", [])]
                    return {"status": "online", "models": models, "url": tags_url}
        except Exception as e:
            return {
                "status": "offline",
                "error": str(e),
                "url": tags_url,
                "offline_message": self.config.get("offline_strategy", {}).get("mock_fallback_response")
            }
        return {"status": "offline", "url": tags_url}

    def resolve_model(self, task_type: str = "general") -> str:
        """Resolve primary model or fallback for specific task type."""
        routes = self.config.get("model_routes", {})
        route = routes.get(task_type, routes.get("general", {}))
        return route.get("primary", "llama3.1:latest")
