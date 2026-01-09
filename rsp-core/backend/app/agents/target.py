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

# Import requests for CustomHTTPBackend
try:
    import requests
except ImportError:
    requests = None


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


class LlamaCppBackend(TargetBackend):
    """Local GGUF model backend via llama-cpp-python."""
    
    def __init__(self, model_path: str, max_tokens: int = 1000, 
                 temperature: float = 0.7, n_ctx: int = 2048, n_gpu_layers: int = 0):
        """
        Initialize llama.cpp backend for local GGUF models.
        
        Args:
            model_path: Path to GGUF model file
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            n_ctx: Context window size
            n_gpu_layers: Number of layers to offload to GPU (0 = CPU only)
        """
        if not model_path:
            raise ValueError("Model path is required for LlamaCpp backend")
        
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        
        # Initialize llama.cpp
        try:
            from llama_cpp import Llama
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers
            )
        except ImportError:
            raise ImportError(
                "llama-cpp-python not installed. Install with: pip install llama-cpp-python"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load GGUF model from {model_path}: {e}")
    
    def execute(self, prompt: str, **kwargs) -> str:
        """Execute prompt using local GGUF model."""
        try:
            response = self.model(
                prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                echo=False
            )
            
            return response['choices'][0]['text']
            
        except Exception as e:
            logger.error(f"LlamaCpp execution failed: {e}")
            raise


class CustomHTTPBackend(TargetBackend):
    """Generic HTTP API backend for custom endpoints."""
    
    def __init__(self, api_url: str, api_key: Optional[str] = None,
                 max_tokens: int = 1000, temperature: float = 0.7,
                 request_format: str = "openai", headers: Optional[Dict[str, str]] = None):
        """
        Initialize custom HTTP backend.
        
        Args:
            api_url: Base URL of the API endpoint
            api_key: Optional API key
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            request_format: Request format ('openai', 'anthropic', or 'generic')
            headers: Additional HTTP headers
        """
        if not api_url:
            raise ValueError("API URL is required for CustomHTTP backend")
        
        self.api_url = api_url
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.request_format = request_format
        self.headers = headers or {}
        
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
        
        if requests is None:
            raise ImportError(
                "requests package not installed. Install with: pip install requests"
            )
    
    def execute(self, prompt: str, **kwargs) -> str:
        """Execute prompt using custom HTTP API."""
        try:
            # Build request based on format
            if self.request_format == "openai":
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            elif self.request_format == "anthropic":
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            else:
                # Generic format
                payload = {
                    "prompt": prompt,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response based on format
            if self.request_format == "openai":
                return data.get('choices', [{}])[0].get('message', {}).get('content', '')
            elif self.request_format == "anthropic":
                return data.get('content', [{}])[0].get('text', '')
            else:
                # Generic extraction
                return data.get('response', data.get('text', str(data)))
            
        except Exception as e:
            logger.error(f"Custom HTTP API call failed: {e}")
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
        backend_type: Type of backend ('openai', 'anthropic', 'llama_cpp', 'custom_http')
        **config: Backend-specific configuration
        
    Returns:
        Configured Target instance
    """
    backend_type_lower = backend_type.lower()
    
    if backend_type_lower == 'openai':
        backend = OpenAIBackend(
            api_key=config.get('api_key', ''),
            model_name=config.get('model_name', 'gpt-3.5-turbo'),
            max_tokens=config.get('max_tokens', 1000),
            temperature=config.get('temperature', 0.7)
        )
    elif backend_type_lower == 'anthropic':
        backend = AnthropicBackend(
            api_key=config.get('api_key', ''),
            model_name=config.get('model_name', 'claude-3-5-sonnet-20241022'),
            max_tokens=config.get('max_tokens', 1000),
            temperature=config.get('temperature', 0.7)
        )
    elif backend_type_lower == 'llama_cpp':
        backend = LlamaCppBackend(
            model_path=config.get('model_path', ''),
            max_tokens=config.get('max_tokens', 1000),
            temperature=config.get('temperature', 0.7),
            n_ctx=config.get('n_ctx', 2048),
            n_gpu_layers=config.get('n_gpu_layers', 0)
        )
    elif backend_type_lower == 'custom_http':
        backend = CustomHTTPBackend(
            api_url=config.get('api_url', ''),
            api_key=config.get('api_key'),
            max_tokens=config.get('max_tokens', 1000),
            temperature=config.get('temperature', 0.7),
            request_format=config.get('request_format', 'openai'),
            headers=config.get('headers')
        )
    else:
        raise ValueError(
            f"Unknown backend type: {backend_type}. "
            f"Must be 'openai', 'anthropic', 'llama_cpp', or 'custom_http'"
        )
    
    return Target(backend, fresh_context=config.get('fresh_context', True))

