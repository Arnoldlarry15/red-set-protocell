"""Storage adapter interfaces for StateManager persistence backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, AbstractContextManager


class StorageAdapter(ABC):
    """Narrow storage contract for persistence backends."""

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Human-readable backend identifier."""

    @abstractmethod
    def health_check_sync(self) -> None:
        """Validate connectivity/operability for sync code paths."""

    @abstractmethod
    def transaction_sync(self) -> AbstractContextManager:
        """Provide a sync transaction context manager."""

    @abstractmethod
    def transaction_async(self) -> AbstractAsyncContextManager:
        """Provide an async transaction context manager."""
