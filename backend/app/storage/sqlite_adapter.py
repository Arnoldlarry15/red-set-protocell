"""SQLite storage adapter implementation."""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator, Iterator

import aiosqlite

from app.storage.base import StorageAdapter


class SQLiteStorageAdapter(StorageAdapter):
    """SQLite adapter used by current StateManager implementation."""

    def __init__(self, database_path: str):
        self.database_path = database_path

    @property
    def backend_name(self) -> str:
        return "sqlite"

    def health_check_sync(self) -> None:
        conn = sqlite3.connect(self.database_path)
        try:
            conn.execute("SELECT 1")
        finally:
            conn.close()

    @contextmanager
    def transaction_sync(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.database_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @asynccontextmanager
    async def transaction_async(self) -> AsyncIterator[aiosqlite.Connection]:
        conn = await aiosqlite.connect(self.database_path)
        try:
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await conn.close()
