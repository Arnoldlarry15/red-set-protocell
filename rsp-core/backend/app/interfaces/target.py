"""
Red Set ProtoCell - Target Interface

Abstract base class for Target backend implementations.
Establishes the contract for all LLM backend integrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseTarget(ABC):
    """
    Abstract base class for Target backend implementations.

    All LLM backend integrations must implement this interface to ensure
    consistent behavior and enable dependency injection.

    Example:
        >>> class MyCustomBackend(BaseTarget):
        ...     async def execute(self, prompt: str, **kwargs) -> str:
        ...         # Implementation here
        ...         return response
        ...
        ...     def get_backend_info(self) -> Dict[str, Any]:
        ...         return {"backend": "custom", "model": "my-model"}
    """

    @abstractmethod
    async def execute(self, prompt: str, **kwargs) -> str:
        """
        Execute a prompt against the backend.

        This method must be implemented by all backends to execute
        prompts and return responses.

        Args:
            prompt: The prompt to execute
            **kwargs: Backend-specific parameters

        Returns:
            Model response string

        Raises:
            Exception: Backend-specific errors (network, API, etc.)
        """
        pass

    @abstractmethod
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about this backend.

        Returns:
            Dictionary containing backend metadata:
            - backend_type: str (e.g., "openai", "anthropic")
            - model_name: str (e.g., "gpt-4")
            - version: Optional[str]
            - capabilities: Optional[List[str]]
        """
        pass

    def validate_configuration(self) -> bool:
        """
        Validate that the backend is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        return True

    async def health_check(self) -> bool:
        """
        Check if the backend is accessible and responding.

        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            # Simple health check - attempt a minimal request
            await self.execute("test", max_tokens=1)
            return True
        except:
            return False
