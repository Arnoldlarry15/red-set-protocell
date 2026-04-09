"""Real provider adapters built on existing target backend implementations."""

from __future__ import annotations

from app.agents.target import OpenAIBackend
from app.providers.base import Provider, ProviderResponse


class OpenAIProvider(Provider):
    """OpenAI-backed provider adapter."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.backend = OpenAIBackend(api_key=api_key, model_name=model_name)
        self.model_name = model_name

    async def generate(self, prompt: str) -> ProviderResponse:
        text = await self.backend.execute(prompt)
        return ProviderResponse(text=text, metadata={"source": "openai", "model": self.model_name})
