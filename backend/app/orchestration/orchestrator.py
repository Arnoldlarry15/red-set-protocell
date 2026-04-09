"""Top-level orchestration interfaces for modular experiment coordination.

This module defines a lightweight orchestrator contract that composes an
``AgentManager`` and ``ExperimentRunner``. It does not replace existing
``app.agents.orchestrator`` business logic and is intentionally scoped to
structure + interface definitions only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.orchestration.agent_manager import AgentManager
from app.orchestration.experiment_runner import ExperimentConfig, ExperimentRunner


@dataclass(slots=True)
class OrchestratorContext:
    """Container for orchestration dependencies.

    Attributes:
        agent_manager: Lifecycle coordinator for agent instances.
        experiment_runner: Iterative execution coordinator.
    """

    agent_manager: AgentManager
    experiment_runner: ExperimentRunner


class ModularOrchestrator(Protocol):
    """Interface for isolated orchestration lifecycle and experiment control."""

    def boot(self) -> None:
        """Initialize and start managed agents for orchestration readiness."""
        ...

    async def execute(self, config: ExperimentConfig):
        """Run an experiment using configured iterative execution semantics."""
        ...

    def shutdown(self) -> None:
        """Stop managed agents and release orchestration resources safely."""
        ...
