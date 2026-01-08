"""
Red Set ProtoCell - Target Agent

Stateless execution wrapper for the LLM under test.

Role: Execute prompts against configured model backend
Constraints:
- No memory of prior rounds
- Fresh context window for each invocation
- No prompt/response persistence
"""

import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TargetBackend(ABC):
    """Abstract base class for Target backend implementations."""
    
    @abstractmethod
    def execute(self, prompt: str, **kwargs) -> str:
        """
        Execute a prompt against the backend.
        
        Args:
            prompt: The prompt to execute
            **kwargs: Backend-specific parameters
            
        Returns:
            Model response string
        """
        pass


class OpenAIBackend(TargetBackend):
    """OpenAI API backend - Real implementation."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo",
                 max_tokens: int = 1000, temperature: float = 0.7):
        """
        Initialize OpenAI backend.
        
        Args:
            api_key: OpenAI API key
            model_name: Model identifier
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
        """
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        
    def execute(self, prompt: str, **kwargs) -> str:
        """Execute prompt using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise


class AnthropicBackend(TargetBackend):
    """Anthropic API backend - Real implementation."""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022",
                 max_tokens: int = 1000, temperature: float = 0.7):
        """
        Initialize Anthropic backend.
        
        Args:
            api_key: Anthropic API key
            model_name: Model identifier
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
        """
        if not api_key:
            raise ValueError("Anthropic API key is required")
        
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize Anthropic client
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
        
    def execute(self, prompt: str, **kwargs) -> str:
        """Execute prompt using Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise


class Target:
    """
    The Target agent is a stateless execution wrapper for the LLM under test.
    
    Each invocation uses a fresh context window and does not persist data.
    """
    
    def __init__(self, backend: TargetBackend, fresh_context: bool = True):
        """
        Initialize Target agent.
        
        Args:
            backend: Backend implementation to use
            fresh_context: Always use fresh context (should be True)
        """
        self.backend = backend
        self.fresh_context = fresh_context
        self.execution_count = 0
        
    def execute(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a prompt against the configured backend.
        
        This is a stateless operation with no memory of prior executions.
        
        Args:
            prompt: The prompt to execute
            metadata: Optional metadata (not used by Target, for logging only)
            
        Returns:
            Raw model response string
        """
        if self.fresh_context:
            # Ensure fresh context (implementation would clear any session state)
            logger.debug("Using fresh context for execution")
        
        # Execute prompt
        try:
            response = self.backend.execute(prompt)
            self.execution_count += 1
            
            logger.info(f"Target execution #{self.execution_count} completed")
            
            return response
            
        except Exception as e:
            logger.error(f"Target execution failed: {e}")
            raise  # Re-raise the exception instead of returning error string
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_executions': self.execution_count,
            'backend_type': type(self.backend).__name__,
            'fresh_context': self.fresh_context
        }


def create_target(backend_type: str, **config) -> Target:
    """
    Factory function to create a Target agent with specified backend.
    
    Args:
        backend_type: Type of backend ('openai', 'anthropic')
        **config: Backend-specific configuration
        
    Returns:
        Configured Target instance
    """
    if backend_type.lower() == 'openai':
        backend = OpenAIBackend(
            api_key=config.get('api_key', ''),
            model_name=config.get('model_name', 'gpt-3.5-turbo'),
            max_tokens=config.get('max_tokens', 1000),
            temperature=config.get('temperature', 0.7)
        )
    elif backend_type.lower() == 'anthropic':
        backend = AnthropicBackend(
            api_key=config.get('api_key', ''),
            model_name=config.get('model_name', 'claude-3-5-sonnet-20241022'),
            max_tokens=config.get('max_tokens', 1000),
            temperature=config.get('temperature', 0.7)
        )
    else:
        raise ValueError(f"Unknown backend type: {backend_type}. Must be 'openai' or 'anthropic'")
    
    return Target(backend, fresh_context=config.get('fresh_context', True))

