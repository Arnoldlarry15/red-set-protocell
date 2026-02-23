"""Storage adapter factory."""

from __future__ import annotations

from app.storage.base import StorageAdapter
from app.storage.postgres_adapter import PostgresStorageAdapter
from app.storage.sqlite_adapter import SQLiteStorageAdapter


def create_storage_adapter(mode: str, database_path: str, postgres_dsn: str | None = None) -> StorageAdapter:
    normalized = (mode or "sqlite").strip().lower()
    if normalized == "postgres":
        return PostgresStorageAdapter(postgres_dsn or "")
    return SQLiteStorageAdapter(database_path)
