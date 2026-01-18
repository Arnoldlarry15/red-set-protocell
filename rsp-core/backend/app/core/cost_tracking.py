"""
Red Set ProtoCell - Cost Tracking Utilities

Provides token counting and cost estimation for different LLM providers.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage information for a single API call."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class CostEstimate:
    """Cost estimate for a single API call."""

    prompt_cost: float
    completion_cost: float
    total_cost: float
    token_usage: TokenUsage

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prompt_cost": self.prompt_cost,
            "completion_cost": self.completion_cost,
            "total_cost": self.total_cost,
            "token_usage": self.token_usage.to_dict(),
        }


# Pricing information (USD per 1K tokens) - Update as needed
# Source: Provider pricing pages (as of 2024)
PRICING_TABLE = {
    # OpenAI models
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    "gpt-4-turbo-preview": {"prompt": 0.01, "completion": 0.03},
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
    # Anthropic models
    "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
    "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
    "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
    "claude-2.1": {"prompt": 0.008, "completion": 0.024},
    "claude-2": {"prompt": 0.008, "completion": 0.024},
    "claude-instant-1.2": {"prompt": 0.0008, "completion": 0.0024},
    # Default fallback pricing (conservative estimate)
    "default": {"prompt": 0.01, "completion": 0.03},
}


class CostTracker:
    """
    Tracks token usage and cost across API calls.

    Supports OpenAI and Anthropic response formats.
    """

    def __init__(self):
        """Initialize cost tracker."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0

    def extract_token_usage_from_response(self, response: Any, backend_type: str) -> Optional[TokenUsage]:
        """
        Extract token usage from API response.

        Args:
            response: API response object (OpenAI or Anthropic)
            backend_type: Backend type ("openai" or "anthropic")

        Returns:
            TokenUsage object or None if extraction fails
        """
        try:
            if backend_type == "openai":
                # OpenAI response has .usage attribute
                if hasattr(response, "usage"):
                    usage = response.usage
                    return TokenUsage(
                        prompt_tokens=usage.prompt_tokens,
                        completion_tokens=usage.completion_tokens,
                        total_tokens=usage.total_tokens,
                    )

            elif backend_type == "anthropic":
                # Anthropic response has .usage attribute with different naming
                if hasattr(response, "usage"):
                    usage = response.usage
                    return TokenUsage(
                        prompt_tokens=usage.input_tokens,
                        completion_tokens=usage.output_tokens,
                        total_tokens=usage.input_tokens + usage.output_tokens,
                    )

        except Exception as e:
            logger.warning(f"Failed to extract token usage from {backend_type} response: {e}")
            return None

        return None

    def estimate_cost(self, token_usage: TokenUsage, model_name: str) -> CostEstimate:
        """
        Estimate cost for token usage.

        Args:
            token_usage: Token usage information
            model_name: Model name for pricing lookup

        Returns:
            CostEstimate object
        """
        # Normalize model name for pricing lookup
        model_key = model_name.lower()

        # Find pricing info
        pricing = None
        for key, value in PRICING_TABLE.items():
            if key in model_key:
                pricing = value
                break

        if pricing is None:
            logger.warning(f"No pricing found for model {model_name}, using default")
            pricing = PRICING_TABLE["default"]

        # Calculate costs (pricing is per 1K tokens)
        prompt_cost = (token_usage.prompt_tokens / 1000.0) * pricing["prompt"]
        completion_cost = (token_usage.completion_tokens / 1000.0) * pricing["completion"]
        total_cost = prompt_cost + completion_cost

        return CostEstimate(
            prompt_cost=prompt_cost, completion_cost=completion_cost, total_cost=total_cost, token_usage=token_usage
        )

    def track_call(self, response: Any, backend_type: str, model_name: str) -> Optional[CostEstimate]:
        """
        Track a single API call.

        Args:
            response: API response object
            backend_type: Backend type ("openai" or "anthropic")
            model_name: Model name

        Returns:
            CostEstimate or None if tracking failed
        """
        token_usage = self.extract_token_usage_from_response(response, backend_type)

        if token_usage is None:
            logger.warning("Could not extract token usage from response")
            return None

        cost_estimate = self.estimate_cost(token_usage, model_name)

        # Update totals
        self.total_prompt_tokens += token_usage.prompt_tokens
        self.total_completion_tokens += token_usage.completion_tokens
        self.total_cost += cost_estimate.total_cost
        self.call_count += 1

        # Safe logging with fallback for mock objects in tests
        try:
            logger.debug(f"API call tracked - Tokens: {token_usage.total_tokens}, " f"Cost: ${cost_estimate.total_cost:.6f}")
        except (TypeError, AttributeError):
            # Handle mock objects in tests gracefully
            logger.debug(f"API call tracked - Tokens: {token_usage.total_tokens}")

        return cost_estimate

    def get_totals(self) -> Dict[str, Any]:
        """
        Get total usage and cost statistics.

        Returns:
            Dictionary with total usage information
        """
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_cost": self.total_cost,
            "call_count": self.call_count,
            "average_cost_per_call": self.total_cost / max(1, self.call_count),
        }

    def reset(self):
        """Reset all tracking counters."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0


def estimate_tokens_from_text(text: str) -> int:
    """
    Rough estimation of token count from text.

    This is a fallback when actual token counts are not available.
    Uses the approximation: 1 token ≈ 4 characters for English text.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    # Rough approximation: ~4 chars per token for English
    return len(text) // 4


def estimate_cost_from_text(prompt: str, response: str, model_name: str) -> CostEstimate:
    """
    Estimate cost from text when actual usage is not available.

    Args:
        prompt: Input prompt text
        response: Model response text
        model_name: Model name for pricing

    Returns:
        CostEstimate based on text length approximation
    """
    prompt_tokens = estimate_tokens_from_text(prompt)
    completion_tokens = estimate_tokens_from_text(response)

    token_usage = TokenUsage(
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens
    )

    tracker = CostTracker()
    return tracker.estimate_cost(token_usage, model_name)
