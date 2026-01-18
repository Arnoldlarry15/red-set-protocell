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

import pytest
import os
from app.agents.target import OpenAIBackend, AnthropicBackend, create_target


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
    not os.environ.get('OPENAI_API_KEY'),
    reason="OPENAI_API_KEY environment variable not set"
)
def test_openai_real_execution():
    """
    Test real OpenAI execution.

    WARNING: This makes a real API call and will incur costs.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    backend = OpenAIBackend(api_key=api_key, model_name="gpt-3.5-turbo")

    response = backend.execute("Say 'test' in one word")

    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.skipif(
    not os.environ.get('ANTHROPIC_API_KEY'),
    reason="ANTHROPIC_API_KEY environment variable not set"
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
    not os.environ.get('OPENAI_API_KEY'),
    reason="OPENAI_API_KEY environment variable not set"
)
def test_target_with_openai():
    """
    Test Target agent with real OpenAI backend.

    WARNING: This makes a real API call and will incur costs.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    target = create_target('openai', api_key=api_key, model_name="gpt-3.5-turbo")

    response = target.execute("Say 'hello' in one word")

    assert isinstance(response, str)
    assert len(response) > 0
    assert target.execution_count == 1


@pytest.mark.skipif(
    not os.environ.get('ANTHROPIC_API_KEY'),
    reason="ANTHROPIC_API_KEY environment variable not set"
)
def test_target_with_anthropic():
    """
    Test Target agent with real Anthropic backend.

    WARNING: This makes a real API call and will incur costs.
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    target = create_target('anthropic', api_key=api_key)

    response = target.execute("Say 'hello' in one word")

    assert isinstance(response, str)
    assert len(response) > 0
    assert target.execution_count == 1
