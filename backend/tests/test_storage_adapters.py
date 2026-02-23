import pytest

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


def test_postgres_adapter_transaction_methods_not_implemented():
    adapter = PostgresStorageAdapter("postgresql://user:pass@localhost:5432/rsp")
    with pytest.raises(NotImplementedError):
        adapter.transaction_sync()
    with pytest.raises(NotImplementedError):
        adapter.transaction_async()


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
