"""
Red Set ProtoCell - Factory Pattern

Industry-grade factory implementations for creating components
without tight coupling to concrete implementations.
"""

from typing import Dict, Type, Any, Optional
from abc import ABC

from app.agents.target import (
    OpenAIBackend,
    AnthropicBackend,
    LlamaCppBackend,
    CustomHTTPBackend,
    TargetBackend,
    Target,
    PerturbationConfig
)


class BackendFactory(ABC):
    """
    Abstract factory for creating backend implementations.

    This eliminates coupling by using registry pattern instead of
    if/else chains for backend selection.
    """

    _registry: Dict[str, Type[TargetBackend]] = {}

    @classmethod
    def register(cls, backend_type: str, backend_class: Type[TargetBackend]):
        """
        Register a backend implementation.

        Args:
            backend_type: String identifier for the backend (e.g., "openai")
            backend_class: Backend class to register
        """
        cls._registry[backend_type.lower()] = backend_class

    @classmethod
    def create(cls, backend_type: str, **config) -> TargetBackend:
        """
        Create a backend instance using registry pattern.

        Args:
            backend_type: Type of backend to create
            **config: Backend-specific configuration

        Returns:
            Configured backend instance

        Raises:
            ValueError: If backend type is not registered
        """
        backend_type_lower = backend_type.lower()

        if backend_type_lower not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unknown backend type: {backend_type}. "
                f"Available backends: {available}"
            )

        backend_class = cls._registry[backend_type_lower]

        # Extract backend-specific config
        return cls._instantiate_backend(backend_class, config)

    @classmethod
    def _instantiate_backend(cls, backend_class: Type[TargetBackend], config: Dict[str, Any]) -> TargetBackend:
        """
        Instantiate a backend with appropriate configuration.

        Args:
            backend_class: The backend class to instantiate
            config: Configuration dictionary

        Returns:
            Configured backend instance
        """
        # Map common parameters based on backend type
        if backend_class == OpenAIBackend:
            return OpenAIBackend(
                api_key=config.get("api_key", ""),
                model_name=config.get("model_name", "gpt-3.5-turbo"),
                max_tokens=config.get("max_tokens", 1000),
                temperature=config.get("temperature", 0.7),
            )
        elif backend_class == AnthropicBackend:
            return AnthropicBackend(
                api_key=config.get("api_key", ""),
                model_name=config.get("model_name", "claude-3-5-sonnet-20241022"),
                max_tokens=config.get("max_tokens", 1000),
                temperature=config.get("temperature", 0.7),
            )
        elif backend_class == LlamaCppBackend:
            return LlamaCppBackend(
                model_path=config.get("model_path", ""),
                max_tokens=config.get("max_tokens", 1000),
                temperature=config.get("temperature", 0.7),
                n_ctx=config.get("n_ctx", 2048),
                n_gpu_layers=config.get("n_gpu_layers", 0),
            )
        elif backend_class == CustomHTTPBackend:
            return CustomHTTPBackend(
                api_url=config.get("api_url", ""),
                api_key=config.get("api_key"),
                max_tokens=config.get("max_tokens", 1000),
                temperature=config.get("temperature", 0.7),
                request_format=config.get("request_format", "openai"),
                headers=config.get("headers"),
            )
        else:
            # Generic instantiation for custom backends
            # Try to pass all config as kwargs
            return backend_class(**config)

    @classmethod
    def list_available(cls) -> list:
        """
        List all registered backend types.

        Returns:
            List of backend type strings
        """
        return list(cls._registry.keys())


# Register built-in backends
BackendFactory.register("openai", OpenAIBackend)
BackendFactory.register("anthropic", AnthropicBackend)
BackendFactory.register("llama_cpp", LlamaCppBackend)
BackendFactory.register("custom_http", CustomHTTPBackend)


class TargetFactory:
    """
    Factory for creating Target agents with proper dependency injection.
    """

    @staticmethod
    def create(
        backend_type: str,
        perturbation_config: Optional[PerturbationConfig] = None,
        **config
    ) -> Target:
        """
        Create a Target agent with specified backend.

        This uses the BackendFactory to eliminate coupling.

        Args:
            backend_type: Type of backend ('openai', 'anthropic', etc.)
            perturbation_config: Optional perturbation configuration
            **config: Backend-specific configuration

        Returns:
            Configured Target instance
        """
        # Use factory to create backend (eliminates if/else chain)
        backend = BackendFactory.create(backend_type, **config)

        # Create Target with dependency injection
        return Target(
            backend,
            fresh_context=config.get("fresh_context", True),
            perturbation_config=perturbation_config or config.get("perturbation_config"),
        )


# Convenience function for backward compatibility
def create_target(backend_type: str, **config) -> Target:
    """
    Factory function to create a Target agent (backward compatible).

    This now uses the factory pattern internally.

    Args:
        backend_type: Type of backend ('openai', 'anthropic', 'llama_cpp', 'custom_http')
        **config: Backend-specific configuration, including optional perturbation_config

    Returns:
        Configured Target instance
    """
    return TargetFactory.create(backend_type, **config)
