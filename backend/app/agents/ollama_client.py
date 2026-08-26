import httpx
from typing import Optional, Dict, Any
from app.config import settings


class OllamaClient:
    """
    Resilient client for interacting with local Ollama instance.
    Provides fast connection probing and instantaneous fallback if Ollama is unreachable.
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def is_available(self) -> bool:
        """Checks if local Ollama server is running and reachable."""
        try:
            async with httpx.AsyncClient(timeout=0.5) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Sends generation request to Ollama.
        Probes availability first (0.5s) to guarantee zero latency penalty when Ollama is offline.
        """
        if not await self.is_available():
            return None

        try:
            payload: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 300,
                },
            }
            if system_prompt:
                payload["system"] = system_prompt

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                return None
        except Exception:
            return None


ollama_client = OllamaClient()
