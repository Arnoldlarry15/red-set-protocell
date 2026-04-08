"""Agent lifecycle interfaces for isolated orchestration modules.

This module defines an ``AgentManager`` contract responsible for lifecycle
operations (register, initialize, start, stop, teardown) without embedding
business logic from existing Sniper/Spotter implementations.

Design goals:
- Keep lifecycle handling modular and testable.
- Avoid changes to existing ``app.agents.sniper`` and ``app.agents.spotter``.
- Provide typed interfaces for future concrete manager implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Protocol


class AgentState(str, Enum):
    """Lifecycle states for orchestrated agents."""

    REGISTERED = "registered"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass(slots=True)
class AgentDescriptor:
    """Metadata wrapper describing an agent managed by the orchestrator layer.

    Attributes:
        name: Stable agent name (e.g., ``sniper``, ``spotter``, ``target``).
        instance: Underlying concrete agent object.
        state: Current lifecycle state tracked by the manager.
        metadata: Optional manager-level metadata for diagnostics.
    """

    name: str
    instance: Any
    state: AgentState = AgentState.REGISTERED
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentManager(Protocol):
    """Interface for lifecycle operations across orchestrated agents.

    Concrete implementations should provide lifecycle transitions and retain a
    deterministic in-memory view of agent state. Implementations should not
    mutate Sniper/Spotter business logic; they only coordinate lifecycle steps.
    """

    def register(self, name: str, instance: Any, metadata: Optional[Mapping[str, Any]] = None) -> None:
        """Register an agent instance for lifecycle management."""

    def initialize_all(self) -> None:
        """Initialize all registered agents (non-business lifecycle step)."""

    def start_all(self) -> None:
        """Transition all initialized agents into running state."""

    def stop_all(self) -> None:
        """Stop all running agents gracefully."""

    def teardown_all(self) -> None:
        """Release all manager-held lifecycle resources for managed agents."""

    def get_snapshot(self) -> Dict[str, AgentDescriptor]:
        """Return a point-in-time view of tracked agents and states."""
