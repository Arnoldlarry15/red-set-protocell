"""Deterministic mock provider for CI and integration testing."""

from __future__ import annotations

from typing import Any, Dict

from app.providers.base import Provider, ProviderResponse


class MockProvider(Provider):
    """Simple dependency-free provider returning deterministic responses."""

    def __init__(self, static_text: str = "Mock response", metadata: Dict[str, Any] | None = None):
        self.static_text = static_text
        self.metadata = dict(metadata or {})
        self.calls = 0

    async def generate(self, prompt: str) -> ProviderResponse:
        self.calls += 1
        return ProviderResponse(
            text=self.static_text,
            metadata={
                "source": "mock",
                "calls": self.calls,
                "prompt_length": len(prompt),
                **self.metadata,
            },
        )
