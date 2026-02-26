"""
Red Set ProtoCell - New Target Backend Template

Template for adding a new LLM backend to the Target agent.

⚠️ CRITICAL SECURITY WARNING ⚠️
================================================================
This backend will execute adversarial prompts against live LLM APIs!

Before implementing:
1. ✅ Do you have authorization to test this LLM?
2. ✅ Have you reviewed the LLM provider's terms of service?
3. ✅ Is this backend for defensive research only?
4. ✅ Will you handle API keys securely?
5. ✅ Can you ensure no production system impact?

NEVER:
- Execute against production systems without authorization
- Store API keys in code or logs
- Introduce side effects beyond LLM API calls
- Persist conversation context between rounds
- Use this for offensive purposes

ALWAYS:
- Inherit from TargetBackend abstract class
- Implement proper error handling
- Maintain stateless operation
- Return string responses only
- Respect fresh_context requirement
- Document API-specific quirks
================================================================
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TargetBackend(ABC):
    """
    Abstract base class for all Target backends.

    All LLM backend implementations must inherit from this class and
    implement the execute() method.
    """

    def __init__(self):
        """Initialize backend."""
        self._statistics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_tokens": 0,
        }

    @abstractmethod
    def execute(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a prompt on the target LLM.

        Args:
            prompt: The prompt to execute
            metadata: Optional metadata (round number, domain, etc.)

        Returns:
            LLM response as string

        Raises:
            RuntimeError: If execution fails
        """
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Return execution statistics."""
        return self._statistics.copy()


class NewBackend(TargetBackend):
    """
    Target backend for [LLM Provider Name] API.

    This backend integrates with [Provider]'s API to execute prompts
    on their LLM models.

    Requirements:
        - API key from [Provider]
        - Python package: [package-name]
        - Network access to [Provider] API endpoint

    Configuration:
        - api_key: API authentication key
        - model_name: Specific model identifier
        - max_tokens: Maximum response length
        - temperature: Sampling temperature (0.0-1.0)
        - fresh_context: Always use fresh context (required=True)

    Examples:
        >>> backend = NewBackend(
        ...     api_key="your-api-key",
        ...     model_name="model-id",
        ...     max_tokens=1000
        ... )
        >>> response = backend.execute("What is 2+2?")
        >>> print(response)
        '4'
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "default-model",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        fresh_context: bool = True,
    ):
        """
        Initialize the new backend.

        Args:
            api_key: API authentication key
            model_name: Model identifier for this provider
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            fresh_context: Use fresh context per round (must be True)

        Raises:
            ValueError: If configuration is invalid
            ImportError: If required package is not installed
        """
        super().__init__()

        # Validate inputs
        if not api_key:
            raise ValueError("api_key is required")

        if not fresh_context:
            raise ValueError("fresh_context must be True for RSP compliance")

        if not 0.0 <= temperature <= 1.0:
            raise ValueError(f"temperature must be in [0.0, 1.0], got {temperature}")

        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be > 0, got {max_tokens}")

        # Store configuration
        self.api_key = api_key  # NOTE: Never log this!
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.fresh_context = fresh_context

        # Initialize API client
        try:
            # TODO: Import and initialize your API client here
            # Example:
            # from new_provider import Client
            # self.client = Client(api_key=api_key)
            pass
        except ImportError as e:
            raise ImportError(
                f"Required package not installed. "
                f"Install with: pip install [package-name]"
            ) from e

        logger.info(
            f"NewBackend initialized (model={model_name}, "
            f"max_tokens={max_tokens}, temperature={temperature})"
        )
        # NOTE: Never log API keys!

    def execute(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a prompt on the [Provider] LLM.

        Args:
            prompt: The adversarial prompt to execute
            metadata: Optional metadata (not used by backend, for logging only)

        Returns:
            LLM response as string

        Raises:
            RuntimeError: If API call fails
            ValueError: If prompt is empty

        Examples:
            >>> backend = NewBackend(api_key="key", model_name="model")
            >>> response = backend.execute("Hello!")
            >>> isinstance(response, str)
            True
        """
        # Validate prompt
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")

        # Log execution attempt (but not API keys or sensitive data!)
        logger.debug(
            f"Executing prompt on {self.model_name} "
            f"(length={len(prompt)}, round={metadata.get('round', 'N/A') if metadata else 'N/A'})"
        )

        try:
            # TODO: Implement API call to your LLM provider
            # Example structure:
            """
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract text from response
            response_text = response.choices[0].message.content

            # Update statistics
            self._statistics['total_tokens'] += response.usage.total_tokens
            """

            # Placeholder implementation
            response_text = f"[NewBackend] Response to: {prompt[:50]}..."

            # Update statistics
            self._statistics["total_executions"] += 1
            self._statistics["successful_executions"] += 1

            # Validate response
            if not isinstance(response_text, str):
                raise RuntimeError("API returned non-string response")

            logger.debug(f"Execution successful (response_length={len(response_text)})")

            return response_text

        except Exception as e:
            # Update failure statistics
            self._statistics["total_executions"] += 1
            self._statistics["failed_executions"] += 1

            # Log error (but not sensitive details!)
            logger.error(f"NewBackend execution failed: {type(e).__name__}")

            # Re-raise as RuntimeError
            raise RuntimeError(f"LLM execution failed: {e}") from e


# TODO: Register your backend in app/agents/target.py
# Add to the create_target() factory function:
"""
def create_target(backend_type: str, config: TargetConfig):
    if backend_type == "new_backend":
        return NewBackend(
            api_key=config.api_key,
            model_name=config.model_name,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
    # ... existing backends ...
"""

# TODO: Add to ModelBackend enum in app/core/config.py:
"""
class ModelBackend(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    NEW_BACKEND = "new_backend"  # Add your backend here
    # ... existing backends ...
"""

# TODO: Write integration tests in tests/test_real_backends.py:
"""
import pytest
import os

@pytest.mark.skipif(
    not os.getenv("NEW_BACKEND_API_KEY"),
    reason="NEW_BACKEND_API_KEY not set"
)
@pytest.mark.asyncio
async def test_new_backend_integration():
    '''Test NewBackend with real API.'''
    backend = NewBackend(
        api_key=os.getenv("NEW_BACKEND_API_KEY"),
        model_name="default-model"
    )

    response = backend.execute("Hello, how are you?")

    assert isinstance(response, str)
    assert len(response) > 0

    stats = backend.get_statistics()
    assert stats['successful_executions'] == 1
"""

# TODO: Update documentation in README.md:
"""
Add example usage:
```bash
python -m app.main --backend new_backend --api-key $NEW_BACKEND_API_KEY --rounds 10
```
"""
