"""
Red Set ProtoCell - Abstract Interfaces

This module defines abstract base classes for the core components of RSP,
establishing clear contracts for extensibility and testing.

Industry-grade practices:
- Abstract interfaces for dependency injection
- Clear separation of concerns
- Type safety through abstract methods
- Extensibility through polymorphism
"""

from app.interfaces.target import BaseTarget
from app.interfaces.mutation import BaseMutationStrategy
from app.interfaces.scoring import BaseScoringStrategy, ScoreResult

__all__ = ["BaseTarget", "BaseMutationStrategy", "BaseScoringStrategy", "ScoreResult"]
