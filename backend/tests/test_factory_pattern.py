"""
Tests for factory pattern implementation.
"""

import pytest

from app.agents.target import (
    AnthropicBackend,
    OpenAIBackend,
    OpenRouterBackend,
    Target,
    TargetBackend,
)
from app.factories import BackendFactory, TargetFactory, create_target


def test_backend_factory_registration():
    """Test that backends can be registered."""
    # Check that built-in backends are registered
    available = BackendFactory.list_available()

    assert "openai" in available
    assert "openrouter" in available
    assert "anthropic" in available
    assert "llama_cpp" in available
    assert "custom_http" in available


def test_backend_factory_create_openai():
    """Test creating OpenAI backend via factory."""
    backend = BackendFactory.create("openai", api_key="test-key", model_name="gpt-4")

    assert isinstance(backend, OpenAIBackend)
    assert backend.model_name == "gpt-4"

    info = backend.get_backend_info()
    assert info["backend_type"] == "openai"
    assert info["model_name"] == "gpt-4"


def test_backend_factory_create_anthropic():
    """Test creating Anthropic backend via factory."""
    backend = BackendFactory.create(
        "anthropic", api_key="test-key", model_name="claude-3-opus-20240229"
    )

    assert isinstance(backend, AnthropicBackend)
    assert backend.model_name == "claude-3-opus-20240229"

    info = backend.get_backend_info()
    assert info["backend_type"] == "anthropic"


def test_backend_factory_create_openrouter():
    """Test creating OpenRouter backend via factory."""
    backend = BackendFactory.create(
        "openrouter", api_key="test-key", model_name="anthropic/claude-3-opus"
    )

    assert isinstance(backend, OpenRouterBackend)
    assert backend.model_name == "anthropic/claude-3-opus"
    assert backend.base_url == "https://openrouter.ai/api/v1"

    info = backend.get_backend_info()
    assert info["backend_type"] == "openrouter"
    assert info["model_name"] == "anthropic/claude-3-opus"
    assert info["base_url"] == "https://openrouter.ai/api/v1"


def test_backend_factory_create_openrouter_custom_url():
    """Test creating OpenRouter backend with custom base URL."""
    custom_url = "https://custom.openrouter.ai/api/v1"
    backend = BackendFactory.create(
        "openrouter", api_key="test-key", model_name="openai/gpt-4", base_url=custom_url
    )

    assert isinstance(backend, OpenRouterBackend)
    assert backend.base_url == custom_url

    info = backend.get_backend_info()
    assert info["base_url"] == custom_url


def test_backend_factory_unknown_type():
    """Test that unknown backend type raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        BackendFactory.create("unknown_backend", api_key="test")

    assert "unknown_backend" in str(exc_info.value).lower()
    assert "available backends" in str(exc_info.value).lower()


def test_backend_factory_case_insensitive():
    """Test that backend type is case-insensitive."""
    backend1 = BackendFactory.create("OpenAI", api_key="test")
    backend2 = BackendFactory.create("OPENAI", api_key="test")
    backend3 = BackendFactory.create("openai", api_key="test")

    assert isinstance(backend1, OpenAIBackend)
    assert isinstance(backend2, OpenAIBackend)
    assert isinstance(backend3, OpenAIBackend)


def test_target_factory_create():
    """Test creating Target via TargetFactory."""
    target = TargetFactory.create(
        "openai", api_key="test-key", model_name="gpt-3.5-turbo"
    )

    assert isinstance(target, Target)
    assert isinstance(target.backend, OpenAIBackend)
    assert target.fresh_context is True


def test_target_factory_with_config():
    """Test TargetFactory with custom configuration."""
    target = TargetFactory.create(
        "anthropic",
        api_key="test-key",
        model_name="claude-3-5-sonnet-20241022",
        fresh_context=False,
        max_tokens=2000,
        temperature=0.9,
    )

    assert isinstance(target, Target)
    assert target.fresh_context is False
    assert target.backend.max_tokens == 2000
    assert target.backend.temperature == 0.9


def test_create_target_backward_compatibility():
    """Test that create_target function still works (backward compatibility)."""
    target = create_target("openai", api_key="test-key", model_name="gpt-4")

    assert isinstance(target, Target)
    assert isinstance(target.backend, OpenAIBackend)


def test_factory_pattern_eliminates_coupling():
    """Test that factory pattern eliminates if/else coupling."""
    # The factory should be able to create any registered backend
    # without needing to modify the factory code itself

    # Test that we can get available backends dynamically
    backends = BackendFactory.list_available()
    assert len(backends) >= 4

    # Test that each registered backend can be created
    for backend_type in backends:
        if backend_type == "llama_cpp":
            # Skip llama_cpp as it requires model_path
            continue

        try:
            backend = BackendFactory.create(
                backend_type,
                api_key="test",
                api_url="http://test.com" if backend_type == "custom_http" else None,
            )
            assert isinstance(backend, TargetBackend)
        except ImportError:
            # Skip if optional dependency not installed
            pass


def test_custom_backend_registration():
    """Test that custom backends can be registered."""

    # Create a mock custom backend
    class MockCustomBackend(TargetBackend):
        def __init__(self, api_key: str, **kwargs):
            super().__init__()
            self.api_key = api_key

        async def execute(self, prompt: str, **kwargs) -> str:
            return f"Mock: {prompt}"

        def get_backend_info(self):
            return {"backend_type": "mock_custom"}

    # Register it
    BackendFactory.register("mock_custom", MockCustomBackend)

    # Verify it's available
    assert "mock_custom" in BackendFactory.list_available()

    # Create instance via factory
    backend = BackendFactory.create("mock_custom", api_key="test")
    assert isinstance(backend, MockCustomBackend)

    # Clean up registration
    del BackendFactory._registry["mock_custom"]


def test_factory_dependency_injection():
    """Test that factory enables proper dependency injection."""
    # Factory allows us to inject different backend implementations
    # without the client code needing to know about specific backends

    def use_target(target: Target) -> str:
        """Example client code that uses Target via dependency injection."""
        stats = target.get_statistics()
        return stats["backend_type"]

    # Inject OpenAI backend
    target1 = TargetFactory.create("openai", api_key="test")
    backend_type1 = use_target(target1)
    assert "OpenAI" in backend_type1

    # Inject Anthropic backend
    target2 = TargetFactory.create("anthropic", api_key="test")
    backend_type2 = use_target(target2)
    assert "Anthropic" in backend_type2

    # Client code didn't change, only the injected dependency


def test_factory_pattern_extensibility():
    """Test that factory pattern makes system extensible."""
    # New backends can be added without modifying existing code

    class NewExperimentalBackend(TargetBackend):
        async def execute(self, prompt: str, **kwargs) -> str:
            return "experimental"

        def get_backend_info(self):
            return {"backend_type": "experimental"}

    # Register new backend
    BackendFactory.register("experimental", NewExperimentalBackend)

    # Old code continues to work
    assert "openai" in BackendFactory.list_available()

    # New backend is immediately available
    assert "experimental" in BackendFactory.list_available()

    # Clean up
    del BackendFactory._registry["experimental"]
