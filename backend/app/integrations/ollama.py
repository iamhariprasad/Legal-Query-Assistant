"""Local Ollama integration."""

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class OllamaClient:
    """Async client for local Ollama generation."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = settings.ollama_base_url.rstrip("/")

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=2),
        reraise=True,
    )
    async def generate(self, prompt: str) -> str:
        """Generate a full response from Ollama."""
        payload = {"model": self.settings.ollama_model, "prompt": prompt, "stream": False}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                return str(data.get("response", "")).strip()
        except httpx.HTTPError as exc:
            logger.exception("Ollama generation failed", extra={"request_id": "-"})
            raise ExternalServiceError("Local Ollama generation failed") from exc

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream generated tokens from Ollama."""
        payload = {"model": self.settings.ollama_model, "prompt": prompt, "stream": True}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/generate", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        item: dict[str, Any] = json.loads(line)
                        token = item.get("response")
                        if token:
                            yield str(token)
        except httpx.HTTPError as exc:
            logger.exception("Ollama stream failed", extra={"request_id": "-"})
            raise ExternalServiceError("Local Ollama streaming failed") from exc

