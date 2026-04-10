"""Real provider smoke tests with explicit gating and resilience controls."""

import asyncio
import os
from typing import Optional

import pytest

from app.agents.target import AnthropicBackend, OpenAIBackend, create_target


def _is_valid_api_key(key: Optional[str]) -> bool:
    """Return True when key appears usable for real provider calls."""
    min_len = 20
    if not key:
        return False
    key_lower = key.lower()
    if key.startswith("sk-test-"):
        return False
    if any(marker in key_lower for marker in ["test", "fake", "demo", "mock"]):
        return False
    return len(key) >= min_len


def _real_mode_enabled() -> bool:
    return os.environ.get("PROVIDER_MODE", "mock").lower() == "real" and os.environ.get("SKIP_REAL_API_TESTS", "").lower() != "true"


async def _call_with_retry(coro_factory, max_attempts: int = 3, base_delay: float = 1.0, timeout_seconds: float = 30.0):
    """Execute async provider call with retries and timeout."""
    last_error = None
    for attempt in range(max_attempts):
        try:
            return await asyncio.wait_for(coro_factory(), timeout=timeout_seconds)
        except Exception as exc:  # pragma: no cover - exercised only on provider/network issues
            last_error = exc
            if attempt < max_attempts - 1:
                await asyncio.sleep(base_delay * (2**attempt))
    raise last_error


def test_openai_backend_requires_api_key():
    with pytest.raises(ValueError, match="API key is required"):
        OpenAIBackend(api_key="")


def test_anthropic_backend_requires_api_key():
    with pytest.raises(ValueError, match="API key is required"):
        AnthropicBackend(api_key="")


def test_create_target_requires_valid_backend():
    with pytest.raises(ValueError, match="Unknown backend type"):
        create_target("invalid_backend", api_key="test")


@pytest.mark.skipif(
    not _real_mode_enabled() or not _is_valid_api_key(os.environ.get("OPENAI_API_KEY")),
    reason="Real provider smoke disabled or OPENAI_API_KEY unavailable",
)
def test_openai_real_execution():
    api_key = os.environ.get("OPENAI_API_KEY")
    backend = OpenAIBackend(api_key=api_key, model_name="gpt-3.5-turbo")

    response = asyncio.run(
        _call_with_retry(lambda: backend.execute("Say 'test' in one word"))
    )

    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.skipif(
    not _real_mode_enabled() or not _is_valid_api_key(os.environ.get("ANTHROPIC_API_KEY")),
    reason="Real provider smoke disabled or ANTHROPIC_API_KEY unavailable",
)
def test_anthropic_real_execution():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    backend = AnthropicBackend(api_key=api_key)

    response = asyncio.run(
        _call_with_retry(lambda: backend.execute("Say 'test' in one word"))
    )

    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.skipif(
    not _real_mode_enabled() or not _is_valid_api_key(os.environ.get("OPENAI_API_KEY")),
    reason="Real provider smoke disabled or OPENAI_API_KEY unavailable",
)
def test_target_with_openai():
    api_key = os.environ.get("OPENAI_API_KEY")
    target = create_target("openai", api_key=api_key, model_name="gpt-3.5-turbo")

    response = asyncio.run(
        _call_with_retry(lambda: target.execute("Say 'hello' in one word"))
    )

    assert isinstance(response, str)
    assert len(response) > 0
    assert target.execution_count == 1


@pytest.mark.skipif(
    not _real_mode_enabled() or not _is_valid_api_key(os.environ.get("ANTHROPIC_API_KEY")),
    reason="Real provider smoke disabled or ANTHROPIC_API_KEY unavailable",
)
def test_target_with_anthropic():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    target = create_target("anthropic", api_key=api_key)

    response = asyncio.run(
        _call_with_retry(lambda: target.execute("Say 'hello' in one word"))
    )

    assert isinstance(response, str)
    assert len(response) > 0
    assert target.execution_count == 1
