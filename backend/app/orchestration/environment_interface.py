"""Environment interface layer for pluggable external system interaction.

Purpose:
- Provide a stable abstraction for Sniper-facing environment operations.
- Keep implementations pluggable for future systems (e.g., OpenClaw).

No external dependencies are required in this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class EnvironmentInterface(ABC):
    """Abstract base class for environment integrations.

    Implementations should provide deterministic behavior for:
    - executing an action,
    - reading current environment state,
    - resetting the environment.
    """

    @abstractmethod
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one action against the environment and return result payload."""

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Return current environment state snapshot."""

    @abstractmethod
    def reset_environment(self) -> Dict[str, Any]:
        """Reset environment to baseline state and return reset snapshot."""


@dataclass(slots=True)
class MockEnvironment(EnvironmentInterface):
    """In-memory example environment implementation.

    This mock is intentionally simple and dependency-free. It supports actions:
    - ``set``: set key/value
    - ``increment``: increment numeric key by value (default 1)
    - ``delete``: remove key
    """

    name: str = "mock_environment"
    initial_state: Dict[str, Any] = field(default_factory=dict)
    _state: Dict[str, Any] = field(default_factory=dict, init=False)
    _last_action_at: Optional[str] = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._state = dict(self.initial_state)

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = str(action.get("type", "")).strip().lower()
        key = action.get("key")
        value = action.get("value")

        if action_type == "set" and key is not None:
            self._state[str(key)] = value
            status = "ok"
        elif action_type == "increment" and key is not None:
            current = self._state.get(str(key), 0)
            increment_by = value if isinstance(value, (int, float)) else 1
            self._state[str(key)] = current + increment_by
            status = "ok"
        elif action_type == "delete" and key is not None:
            self._state.pop(str(key), None)
            status = "ok"
        else:
            status = "unsupported_action"

        self._last_action_at = datetime.now(timezone.utc).isoformat()

        return {
            "status": status,
            "action": action,
            "state": self.get_state(),
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "environment": self.name,
            "last_action_at": self._last_action_at,
            "data": dict(self._state),
        }

    def reset_environment(self) -> Dict[str, Any]:
        self._state = dict(self.initial_state)
        self._last_action_at = datetime.now(timezone.utc).isoformat()
        return self.get_state()


def get_example_mock_environment() -> MockEnvironment:
    """Return a pre-seeded mock environment for integration examples."""
    return MockEnvironment(initial_state={"step": 0, "status": "ready"})
