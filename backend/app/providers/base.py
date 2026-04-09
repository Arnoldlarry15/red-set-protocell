"""Provider abstraction layer for model generation.

This layer decouples orchestration/pipeline code from provider-specific SDKs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ProviderResponse:
    """Normalized provider response payload."""

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class Provider(ABC):
    """Base provider interface."""

    @abstractmethod
    async def generate(self, prompt: str) -> ProviderResponse:
        """Generate response for prompt."""
