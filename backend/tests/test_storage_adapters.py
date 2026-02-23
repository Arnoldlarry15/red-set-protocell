import pytest
import sqlite3
import sys
import types
import asyncio

from app.agents.orchestrator import StateManager
from app.storage import create_storage_adapter
from app.storage.postgres_adapter import PostgresStorageAdapter
from app.storage.sqlite_adapter import SQLiteStorageAdapter


def test_create_storage_adapter_defaults_to_sqlite(tmp_path):
    db_path = str(tmp_path / "test.db")
    adapter = create_storage_adapter("", db_path)
    assert isinstance(adapter, SQLiteStorageAdapter)
    adapter.health_check_sync()


def test_create_storage_adapter_postgres_requires_dsn(tmp_path):
    db_path = str(tmp_path / "test.db")
    with pytest.raises(ValueError, match="PostgreSQL DSN is required"):
        create_storage_adapter("postgres", db_path)


def test_create_storage_adapter_postgres_returns_postgres_adapter(tmp_path):
    db_path = str(tmp_path / "test.db")
    adapter = create_storage_adapter("postgres", db_path, "postgresql://user:pass@localhost:5432/rsp")
    assert isinstance(adapter, PostgresStorageAdapter)
    assert adapter.backend_name == "postgres"


def test_postgres_adapter_transaction_methods_not_implemented():
    adapter = PostgresStorageAdapter("postgresql://user:pass@localhost:5432/rsp")
    with pytest.raises(NotImplementedError):
        adapter.transaction_sync()
    with pytest.raises(NotImplementedError):
        adapter.transaction_async()


def test_sqlite_adapter_sync_transaction_commit_and_rollback(tmp_path):
    db_path = str(tmp_path / "sqlite_sync.db")
    adapter = SQLiteStorageAdapter(db_path)

    with adapter.transaction_sync() as conn:
        conn.execute("CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)")
        conn.execute("INSERT INTO events (name) VALUES (?)", ("ok",))

    with sqlite3.connect(db_path) as verify_conn:
        count = verify_conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert count == 1

    with pytest.raises(RuntimeError):
        with adapter.transaction_sync() as conn:
            conn.execute("INSERT INTO events (name) VALUES (?)", ("rollback",))
            raise RuntimeError("force rollback")

    with sqlite3.connect(db_path) as verify_conn:
        count_after = verify_conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert count_after == 1


def test_sqlite_adapter_async_transaction_commit_and_rollback(tmp_path):
    db_path = str(tmp_path / "sqlite_async.db")
    adapter = SQLiteStorageAdapter(db_path)

    async def _run():
        async with adapter.transaction_async() as conn:
            await conn.execute("CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)")
            await conn.execute("INSERT INTO events (name) VALUES (?)", ("ok",))

        with sqlite3.connect(db_path) as verify_conn:
            count = verify_conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        assert count == 1

        with pytest.raises(RuntimeError):
            async with adapter.transaction_async() as conn:
                await conn.execute("INSERT INTO events (name) VALUES (?)", ("rollback",))
                raise RuntimeError("force rollback")

        with sqlite3.connect(db_path) as verify_conn:
            count_after = verify_conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        assert count_after == 1

    asyncio.run(_run())


def test_postgres_adapter_ensure_pool_uses_asyncpg_and_caches(monkeypatch):
    adapter = PostgresStorageAdapter("postgresql://user:pass@localhost:5432/rsp")
    created = {"count": 0}

    class _DummyConn:
        async def execute(self, _sql):
            return None

    class _AcquireCtx:
        async def __aenter__(self):
            return _DummyConn()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class _DummyPool:
        def acquire(self):
            return _AcquireCtx()

    async def _create_pool(_dsn, min_size=1, max_size=5):
        assert min_size == 1
        assert max_size == 5
        created["count"] += 1
        return _DummyPool()

    fake_asyncpg = types.SimpleNamespace(create_pool=_create_pool)
    monkeypatch.setitem(sys.modules, "asyncpg", fake_asyncpg)

    asyncio.run(adapter._health_check_async())
    asyncio.run(adapter._health_check_async())
    assert created["count"] == 1


def test_postgres_adapter_import_error_message(monkeypatch):
    adapter = PostgresStorageAdapter("postgresql://user:pass@localhost:5432/rsp")
    monkeypatch.delitem(sys.modules, "asyncpg", raising=False)

    original_import = __import__

    def _failing_import(name, *args, **kwargs):
        if name == "asyncpg":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _failing_import)

    with pytest.raises(RuntimeError, match="asyncpg is required for Postgres mode"):
        asyncio.run(adapter._ensure_pool())


def test_state_manager_rejects_postgres_mode_until_cutover(monkeypatch, tmp_path):
    db_path = str(tmp_path / "test.db")

    class DummyAdapter:
        backend_name = "postgres"

        def health_check_sync(self):
            return None

        def transaction_sync(self):
            raise NotImplementedError

        def transaction_async(self):
            raise NotImplementedError

    monkeypatch.setattr("app.agents.orchestrator.create_storage_adapter", lambda *args, **kwargs: DummyAdapter())

    with pytest.raises(RuntimeError, match="SQLite-specific"):
        StateManager(database_path=db_path, storage_mode="postgres")
