"""
Real Backend Integration Tests

These tests require actual API keys and will make real API calls.
DO NOT run these tests in CI/CD without proper API key management.

Set environment variables:
  export OPENAI_API_KEY="your-key"
  export ANTHROPIC_API_KEY="your-key"

Then run:
  pytest tests/test_real_backends.py -v -s
"""

import asyncio
import pytest
import os
from typing import Optional
from app.agents.target import OpenAIBackend, AnthropicBackend, create_target


def _is_valid_api_key(key: Optional[str]) -> bool:
    """
    Check if an API key appears to be valid (not a test/fake key).

    Returns False for:
    - Empty or None keys
    - Keys that start with 'sk-test-' (common test pattern)
    - Keys that contain obvious test markers like 'test', 'fake', 'demo', 'mock'
    - Keys that are too short (less than minimum required length)
    """
    MIN_API_KEY_LENGTH = 20

    if not key:
        return False

    key_lower = key.lower()

    # Check for test patterns
    if key.startswith('sk-test-'):
        return False

    # Check for test-related strings in the key
    test_markers = ['test', 'fake', 'demo', 'mock']
    if any(marker in key_lower for marker in test_markers):
        return False

    # Real API keys are typically longer than MIN_API_KEY_LENGTH characters
    if len(key) < MIN_API_KEY_LENGTH:
        return False

    return True


def test_openai_backend_requires_api_key():
    """Test that OpenAI backend requires API key."""
    with pytest.raises(ValueError, match="API key is required"):
        OpenAIBackend(api_key="")


def test_anthropic_backend_requires_api_key():
    """Test that Anthropic backend requires API key."""
    with pytest.raises(ValueError, match="API key is required"):
        AnthropicBackend(api_key="")


def test_create_target_requires_valid_backend():
    """Test that create_target rejects invalid backends."""
    with pytest.raises(ValueError, match="Unknown backend type"):
        create_target('invalid_backend', api_key="test")


def test_create_target_rejects_mock():
    """Test that mock backend is not supported."""
    with pytest.raises(ValueError, match="Unknown backend type"):
        create_target('mock')


@pytest.mark.skipif(
    os.environ.get('SKIP_REAL_API_TESTS', '').lower() == 'true'
    or not _is_valid_api_key(os.environ.get('OPENAI_API_KEY')),
    reason="Real API tests are skipped in CI or API key not set/invalid"
)
def test_openai_real_execution():
    """
    Test real OpenAI execution.

    WARNING: This makes a real API call and will incur costs.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    backend = OpenAIBackend(api_key=api_key, model_name="gpt-3.5-turbo")

    response = asyncio.get_event_loop().run_until_complete(
        backend.execute("Say 'test' in one word")
    )

    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.skipif(
    os.environ.get('SKIP_REAL_API_TESTS', '').lower() == 'true'
    or not _is_valid_api_key(os.environ.get('ANTHROPIC_API_KEY')),
    reason="Real API tests are skipped in CI or API key not set/invalid"
)
def test_anthropic_real_execution():
    """
    Test real Anthropic execution.

    WARNING: This makes a real API call and will incur costs.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    backend = AnthropicBackend(api_key=api_key)

    response = backend.execute("Say 'test' in one word")

    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.skipif(
    os.environ.get('SKIP_REAL_API_TESTS', '').lower() == 'true'
    or not _is_valid_api_key(os.environ.get('OPENAI_API_KEY')),
    reason="Real API tests are skipped in CI or API key not set/invalid"
)
def test_target_with_openai():
    """
    Test Target agent with real OpenAI backend.

    WARNING: This makes a real API call and will incur costs.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    target = create_target('openai', api_key=api_key, model_name="gpt-3.5-turbo")

    response = asyncio.get_event_loop().run_until_complete(
        target.execute("Say 'hello' in one word")
    )

    assert isinstance(response, str)
    assert len(response) > 0
    assert target.execution_count == 1


@pytest.mark.skipif(
    os.environ.get('SKIP_REAL_API_TESTS', '').lower() == 'true'
    or not _is_valid_api_key(os.environ.get('ANTHROPIC_API_KEY')),
    reason="Real API tests are skipped in CI or API key not set/invalid"
)
def test_target_with_anthropic():
    """
    Test Target agent with real Anthropic backend.

    WARNING: This makes a real API call and will incur costs.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    target = create_target('anthropic', api_key=api_key)

    response = asyncio.get_event_loop().run_until_complete(
        target.execute("Say 'hello' in one word")
    )

    assert isinstance(response, str)
    assert len(response) > 0
    assert target.execution_count == 1
