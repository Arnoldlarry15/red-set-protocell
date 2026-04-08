"""Experiment loop interfaces for isolated orchestration modules.

This module defines configuration and execution contracts for iterative
experiment runs. It intentionally avoids embedding domain-specific attack or
scoring behavior so existing Sniper/Spotter logic remains untouched.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Protocol


@dataclass(slots=True)
class ExperimentConfig:
    """Configuration envelope for orchestrator-driven iterative experiments.

    Attributes:
        experiment_id: Caller-provided experiment identifier.
        max_iterations: Upper bound for iterative execution loops.
        stop_on_error: Whether loop execution halts on first raised exception.
        tags: Optional labels for grouping/reporting experiments.
        parameters: Arbitrary configuration payload for future extensions.
    """

    experiment_id: str
    max_iterations: int = 100
    stop_on_error: bool = True
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IterationResult:
    """Structured result for one loop iteration."""

    iteration: int
    status: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class ExperimentRunner(Protocol):
    """Interface for running iterative orchestrator experiments.

    Implementations should run loops and emit iteration-level results while
    keeping business decisions delegated to existing agents/engines.
    """

    def configure(self, config: ExperimentConfig) -> None:
        """Store and validate experiment configuration for subsequent runs."""

    async def run(self) -> List[IterationResult]:
        """Execute iterative loop according to the active configuration."""

    async def run_iteration(self, iteration: int, context: Optional[Mapping[str, Any]] = None) -> IterationResult:
        """Execute exactly one iteration and return a typed result envelope."""

    def stop(self) -> None:
        """Request cooperative stop for an in-flight experiment run."""
