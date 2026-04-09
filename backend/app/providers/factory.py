"""Provider factory with mode switch for mock/real execution."""

from __future__ import annotations

import os

from app.providers.base import Provider
from app.providers.mock import MockProvider
from app.providers.real import OpenAIProvider


def create_provider(mode: str | None = None, **kwargs) -> Provider:
    """Create provider by mode.

    Modes:
    - mock: deterministic local provider
    - real: OpenAI-backed provider (requires OPENAI_API_KEY)
    """
    provider_mode = (mode or os.getenv("PROVIDER_MODE", "mock")).strip().lower()

    if provider_mode == "mock":
        return MockProvider(static_text=kwargs.get("mock_text", "Mock response"))

    if provider_mode == "real":
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for PROVIDER_MODE=real")
        return OpenAIProvider(api_key=api_key, model_name=kwargs.get("model_name", "gpt-4o-mini"))

    raise ValueError(f"Unsupported PROVIDER_MODE: {provider_mode}")
