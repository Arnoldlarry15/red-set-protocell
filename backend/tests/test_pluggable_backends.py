"""
Tests for pluggable backend support
"""

from unittest.mock import Mock, patch

import pytest

from app.agents.target import (
    AnthropicBackend,
    CustomHTTPBackend,
    LlamaCppBackend,
    OpenAIBackend,
    Target,
    create_target,
)

# Check if optional packages are available
try:
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI package not installed")
def test_create_target_openai():
    """Test creating OpenAI backend."""
    target = create_target("openai", api_key="test-key", model_name="gpt-3.5-turbo")
    assert isinstance(target, Target)
    assert isinstance(target.backend, OpenAIBackend)


@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="Anthropic package not installed")
def test_create_target_anthropic():
    """Test creating Anthropic backend."""
    target = create_target(
        "anthropic", api_key="test-key", model_name="claude-3-5-sonnet-20241022"
    )
    assert isinstance(target, Target)
    assert isinstance(target.backend, AnthropicBackend)


def test_create_target_llama_cpp():
    """Test creating llama.cpp backend (without actual library)."""
    with pytest.raises(ImportError):
        create_target("llama_cpp", model_path="/path/to/model.gguf")


def test_create_target_custom_http():
    """Test creating custom HTTP backend."""
    target = create_target(
        "custom_http",
        api_url="http://localhost:8000/v1/completions",
        api_key="test-key",
    )
    assert isinstance(target, Target)
    assert isinstance(target.backend, CustomHTTPBackend)


def test_create_target_invalid_backend():
    """Test error handling for invalid backend type."""
    with pytest.raises(ValueError, match="Unknown backend type"):
        create_target("invalid_backend")


def test_custom_http_backend_initialization():
    """Test CustomHTTPBackend initialization."""
    backend = CustomHTTPBackend(
        api_url="http://localhost:8000/api", api_key="test-key", request_format="openai"
    )

    assert backend.api_url == "http://localhost:8000/api"
    assert "Authorization" in backend.headers
    assert backend.request_format == "openai"


def test_custom_http_backend_no_api_key():
    """Test CustomHTTPBackend without API key."""
    backend = CustomHTTPBackend(api_url="http://localhost:8000/api")

    assert backend.api_url == "http://localhost:8000/api"
    assert "Authorization" not in backend.headers


@pytest.mark.asyncio
@patch("app.agents.target.requests")
async def test_custom_http_backend_execute_openai_format(mock_requests):
    """Test CustomHTTPBackend execution with OpenAI format."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    mock_requests.post.return_value = mock_response

    backend = CustomHTTPBackend(
        api_url="http://localhost:8000/api", request_format="openai"
    )

    result = await backend.execute("Test prompt")

    assert result == "Test response"
    mock_requests.post.assert_called_once()


@pytest.mark.asyncio
@patch("app.agents.target.requests")
async def test_custom_http_backend_execute_anthropic_format(mock_requests):
    """Test CustomHTTPBackend execution with Anthropic format."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "content": [{"text": "Test response from Anthropic"}]
    }
    mock_requests.post.return_value = mock_response

    backend = CustomHTTPBackend(
        api_url="http://localhost:8000/api", request_format="anthropic"
    )

    result = await backend.execute("Test prompt")

    assert result == "Test response from Anthropic"


@pytest.mark.asyncio
@patch("app.agents.target.requests")
async def test_custom_http_backend_execute_generic_format(mock_requests):
    """Test CustomHTTPBackend execution with generic format."""
    mock_response = Mock()
    mock_response.json.return_value = {"response": "Generic API response"}
    mock_requests.post.return_value = mock_response

    backend = CustomHTTPBackend(
        api_url="http://localhost:8000/api", request_format="generic"
    )

    result = await backend.execute("Test prompt")

    assert result == "Generic API response"


def test_llama_cpp_backend_requires_model_path():
    """Test that LlamaCppBackend requires model_path."""
    with pytest.raises(ValueError, match="Model path is required"):
        LlamaCppBackend(model_path="")


def test_custom_http_backend_requires_url():
    """Test that CustomHTTPBackend requires api_url."""
    with pytest.raises(ValueError, match="API URL is required"):
        CustomHTTPBackend(api_url="")
