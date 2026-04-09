"""Agent lifecycle manager for isolated orchestration modules.

This module provides:
1) Lightweight contracts for generic agent lifecycle management.
2) A concrete ``SniperLifecycleManager`` that can spawn and execute multiple
   Sniper-compatible agent instances without changing Sniper internals.

The implementation intentionally stays orchestration-focused:
- It tracks lifecycle/execution state.
- It runs configurable iteration loops per agent.
- It does not mutate or extend Sniper business logic.

Example:
    >>> from app.agents.sniper import Sniper
    >>> from app.orchestration.agent_manager import SniperLifecycleManager
    >>>
    >>> manager = SniperLifecycleManager(default_iterations=3)
    >>> manager.spawn_snipers(lambda: Sniper(mutation_engine=mutation_engine), count=2)
    >>> manager.initialize_all()
    >>> stats = await manager.run_all_agents()
    >>> print(stats["sniper_1"]["iterations_completed"])
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Mapping, Optional, Protocol, Tuple


class AgentState(str, Enum):
    """Lifecycle/execution states for orchestrated agents."""

    REGISTERED = "registered"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class SniperLike(Protocol):
    """Protocol for existing Sniper-compatible instances.

    The manager only depends on the public async ``generate_prompt`` method and
    does not require internal Sniper state access.
    """

    async def generate_prompt(self, prior_metadata: Optional[List[Dict[str, Any]]] = None) -> Tuple[str, Any]:
        """Generate one prompt candidate and its attack domain."""


@dataclass(slots=True)
class AgentDescriptor:
    """Metadata wrapper describing a managed agent.

    Attributes:
        name: Stable agent key.
        instance: Concrete agent object.
        state: Current lifecycle/execution state.
        metadata: Optional manager-level metadata.
    """

    name: str
    instance: Any
    state: AgentState = AgentState.REGISTERED
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentManager(Protocol):
    """Interface for lifecycle operations across orchestrated agents."""

    def register(self, name: str, instance: Any, metadata: Optional[Mapping[str, Any]] = None) -> None:
        """Register an agent instance for lifecycle management."""
        pass

    def initialize_all(self) -> None:
        """Initialize all registered agents (non-business lifecycle step)."""
        pass

    def start_all(self) -> None:
        """Transition all initialized agents into running state."""
        pass

    def stop_all(self) -> None:
        """Stop all running agents gracefully."""
        pass

    def teardown_all(self) -> None:
        """Release all manager-held lifecycle resources for managed agents."""
        pass

    def get_snapshot(self) -> Dict[str, AgentDescriptor]:
        """Return a point-in-time view of tracked agents and states."""
        pass


class SniperLifecycleManager:
    """Concrete lifecycle manager for multiple Sniper-compatible agents.

    Features:
    - Spawn multiple Sniper instances from a factory callback.
    - Track state transitions including active/completed/failed.
    - Execute configurable iteration loops per agent.
    """

    def __init__(self, default_iterations: int = 1):
        self.default_iterations = max(1, int(default_iterations))
        self._agents: Dict[str, AgentDescriptor] = {}
        self._execution_stats: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, instance: SniperLike, metadata: Optional[Mapping[str, Any]] = None) -> None:
        """Register a Sniper-compatible instance for managed execution."""
        self._agents[name] = AgentDescriptor(name=name, instance=instance, metadata=dict(metadata or {}))
        self._execution_stats[name] = {
            "iterations_requested": self._agents[name].metadata.get("iterations", self.default_iterations),
            "iterations_completed": 0,
            "last_prompt": None,
            "error": None,
        }

    def spawn_snipers(self, sniper_factory: Callable[[], SniperLike], count: int, name_prefix: str = "sniper") -> List[str]:
        """Spawn and register multiple sniper instances.

        Args:
            sniper_factory: Zero-argument callable returning a Sniper-like object.
            count: Number of sniper instances to create.
            name_prefix: Prefix for generated names.

        Returns:
            List of generated agent names.
        """
        names: List[str] = []
        for idx in range(1, max(0, count) + 1):
            name = f"{name_prefix}_{idx}"
            self.register(name=name, instance=sniper_factory())
            names.append(name)
        return names

    def initialize_all(self) -> None:
        """Initialize all registered agents."""
        for desc in self._agents.values():
            desc.state = AgentState.INITIALIZED

    def start_all(self) -> None:
        """Set all initialized agents to active execution state."""
        for desc in self._agents.values():
            if desc.state in (AgentState.INITIALIZED, AgentState.STOPPED):
                desc.state = AgentState.ACTIVE

    def stop_all(self) -> None:
        """Stop all running/active agents."""
        for desc in self._agents.values():
            if desc.state in (AgentState.RUNNING, AgentState.ACTIVE):
                desc.state = AgentState.STOPPED

    def teardown_all(self) -> None:
        """Clear all tracked agents and execution statistics."""
        self._agents.clear()
        self._execution_stats.clear()

    def get_snapshot(self) -> Dict[str, AgentDescriptor]:
        """Return current tracked descriptors by name."""
        return dict(self._agents)

    def set_iterations(self, name: str, iterations: int) -> None:
        """Configure iteration count for a specific agent."""
        if name not in self._agents:
            raise KeyError(f"Unknown agent: {name}")

        normalized = max(1, int(iterations))
        self._agents[name].metadata["iterations"] = normalized
        self._execution_stats[name]["iterations_requested"] = normalized

    async def run_agent(self, name: str, prior_metadata: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Run iterative prompt generation for one agent.

        The manager only invokes ``generate_prompt`` on the underlying agent.
        """
        if name not in self._agents:
            raise KeyError(f"Unknown agent: {name}")

        descriptor = self._agents[name]
        stats = self._execution_stats[name]
        iterations = int(descriptor.metadata.get("iterations", self.default_iterations))

        descriptor.state = AgentState.ACTIVE
        stats["iterations_requested"] = iterations

        try:
            for _ in range(iterations):
                prompt, _domain = await descriptor.instance.generate_prompt(prior_metadata=prior_metadata or [])
                stats["iterations_completed"] += 1
                stats["last_prompt"] = prompt

            descriptor.state = AgentState.COMPLETED
            return dict(stats)
        except Exception as exc:
            descriptor.state = AgentState.FAILED
            stats["error"] = str(exc)
            return dict(stats)

    async def run_all_agents(self, prior_metadata: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
        """Run all registered agents sequentially and return per-agent stats."""
        results: Dict[str, Dict[str, Any]] = {}
        for name in self._agents:
            results[name] = await self.run_agent(name=name, prior_metadata=prior_metadata)
        return results


def get_sniper_lifecycle_example_usage() -> str:
    """Return a compact example for external docs and quick-start snippets."""
    return (
        "manager = SniperLifecycleManager(default_iterations=2)\n"
        "manager.spawn_snipers(sniper_factory=create_sniper, count=3)\n"
        "manager.initialize_all()\n"
        "results = await manager.run_all_agents(prior_metadata=[])\n"
        "snapshot = manager.get_snapshot()\n"
    )
