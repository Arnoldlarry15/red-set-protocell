"""PostgreSQL storage adapter scaffold for incremental integration."""

from __future__ import annotations

import asyncio
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Optional

from app.storage.base import StorageAdapter


class PostgresStorageAdapter(StorageAdapter):
    """Asyncpg-backed adapter scaffold (Phase 1)."""

    def __init__(self, postgres_dsn: str):
        if not postgres_dsn:
            raise ValueError("PostgreSQL DSN is required for postgres adapter")
        self.postgres_dsn = postgres_dsn
        self._pool = None

    @property
    def backend_name(self) -> str:
        return "postgres"

    async def _ensure_pool(self):
        if self._pool is not None:
            return self._pool

        try:
            import asyncpg
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("asyncpg is required for Postgres mode. Install dependencies including asyncpg.") from exc

        self._pool = await asyncpg.create_pool(self.postgres_dsn, min_size=1, max_size=5)
        return self._pool

    async def _health_check_async(self) -> None:
        pool = await self._ensure_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")

    def health_check_sync(self) -> None:
        asyncio.run(self._health_check_async())

    def transaction_sync(self) -> AbstractContextManager:
        raise NotImplementedError("Sync transaction path is not implemented for Postgres scaffold")

    def transaction_async(self) -> AbstractAsyncContextManager:
        raise NotImplementedError("Async transaction path will be enabled during Postgres cutover phase")
