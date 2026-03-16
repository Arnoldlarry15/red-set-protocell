"""
Tests for lifecycle hooks module.
"""

import asyncio
import threading

import pytest

from app.lifecycle import background_tasks, background_tasks_lock, track_background_task


# ── track_background_task ─────────────────────────────────────────────────────


class TestTrackBackgroundTask:
    @pytest.mark.asyncio
    async def test_task_is_tracked_and_removed_on_completion(self):
        errors = []

        def log_exception_safely(msg, exc):
            errors.append((msg, exc))

        async def simple_coro():
            return "done"

        task = asyncio.create_task(simple_coro())
        track_background_task(task, "test_context", log_exception_safely)

        # Task is tracked immediately
        with background_tasks_lock:
            assert task in background_tasks

        # Wait for task to finish
        await task

        # Give the callback a chance to run
        await asyncio.sleep(0)

        with background_tasks_lock:
            assert task not in background_tasks

        assert errors == []

    @pytest.mark.asyncio
    async def test_task_returns_task_object(self):
        def log_exception_safely(msg, exc):
            pass

        async def simple_coro():
            return 42

        task = asyncio.create_task(simple_coro())
        returned = track_background_task(task, "ctx", log_exception_safely)
        assert returned is task
        await task

    @pytest.mark.asyncio
    async def test_cancelled_task_does_not_log(self):
        errors = []

        def log_exception_safely(msg, exc):
            errors.append((msg, exc))

        async def never_done():
            await asyncio.sleep(100)

        task = asyncio.create_task(never_done())
        track_background_task(task, "cancel_test", log_exception_safely)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        await asyncio.sleep(0)
        # Cancelled tasks should not be logged as errors
        assert errors == []

    @pytest.mark.asyncio
    async def test_multiple_tasks_tracked(self):
        def log_exception_safely(msg, exc):
            pass

        async def coro(n):
            return n

        tasks = [asyncio.create_task(coro(i)) for i in range(5)]
        for t in tasks:
            track_background_task(t, "multi", log_exception_safely)

        with background_tasks_lock:
            for t in tasks:
                assert t in background_tasks

        await asyncio.gather(*tasks)
        await asyncio.sleep(0)

        with background_tasks_lock:
            for t in tasks:
                assert t not in background_tasks


# ── bind_lifecycle_handlers ───────────────────────────────────────────────────


class TestBindLifecycleHandlers:
    @pytest.mark.asyncio
    async def test_startup_creates_sessions_dir(self, tmp_path, monkeypatch):
        """Test that startup creates the sessions directory."""
        import logging

        from fastapi import FastAPI

        from app.lifecycle import bind_lifecycle_handlers

        monkeypatch.chdir(tmp_path)

        app = FastAPI()

        class MockManager:
            active_connections = []

            def disconnect(self, ws):
                pass

        log_errors = []

        def log_exception_safely(msg, exc):
            log_errors.append((msg, exc))

        bind_lifecycle_handlers(
            app,
            MockManager(),
            {},
            logging.getLogger("test"),
            log_exception_safely,
        )

        # Trigger startup
        async with app.router.lifespan_context(app):
            sessions_dir = tmp_path / "sessions"
            assert sessions_dir.exists()

    @pytest.mark.asyncio
    async def test_shutdown_with_no_connections(self, tmp_path, monkeypatch):
        """Test clean shutdown with no active connections or sessions."""
        import logging

        from fastapi import FastAPI

        from app.lifecycle import bind_lifecycle_handlers

        monkeypatch.chdir(tmp_path)

        app = FastAPI()

        class MockManager:
            active_connections = []

            def disconnect(self, ws):
                pass

        log_errors = []

        def log_exception_safely(msg, exc):
            log_errors.append((msg, exc))

        bind_lifecycle_handlers(
            app,
            MockManager(),
            {},
            logging.getLogger("test"),
            log_exception_safely,
        )

        async with app.router.lifespan_context(app):
            pass  # startup + shutdown

        assert log_errors == []

    @pytest.mark.asyncio
    async def test_shutdown_closes_websockets(self, tmp_path, monkeypatch):
        """Test that shutdown closes active WebSocket connections."""
        import logging

        from fastapi import FastAPI

        from app.lifecycle import bind_lifecycle_handlers

        monkeypatch.chdir(tmp_path)

        app = FastAPI()

        close_calls = []

        class MockWebSocket:
            async def close(self, code=None, reason=None):
                close_calls.append({"code": code, "reason": reason})

        class MockManager:
            active_connections = [MockWebSocket()]

            def disconnect(self, ws):
                if ws in self.active_connections:
                    self.active_connections.remove(ws)

        bind_lifecycle_handlers(
            app,
            MockManager(),
            {},
            logging.getLogger("test"),
            lambda msg, exc: None,
        )

        async with app.router.lifespan_context(app):
            pass

        assert len(close_calls) == 1
        assert close_calls[0]["code"] == 1001

    @pytest.mark.asyncio
    async def test_shutdown_terminates_sessions(self, tmp_path, monkeypatch):
        """Test that shutdown terminates active orchestrator sessions."""
        import logging

        from fastapi import FastAPI

        from app.lifecycle import bind_lifecycle_handlers

        monkeypatch.chdir(tmp_path)

        app = FastAPI()

        terminate_calls = []

        class MockOrchestrator:
            def terminate_session(self):
                terminate_calls.append(True)

        class MockManager:
            active_connections = []

            def disconnect(self, ws):
                pass

        active_sessions = {"sess_1": {"orchestrator": MockOrchestrator()}}

        bind_lifecycle_handlers(
            app,
            MockManager(),
            active_sessions,
            logging.getLogger("test"),
            lambda msg, exc: None,
        )

        async with app.router.lifespan_context(app):
            pass

        assert len(terminate_calls) == 1

    @pytest.mark.asyncio
    async def test_shutdown_websocket_close_error(self, tmp_path, monkeypatch):
        """Test shutdown handles WebSocket close errors gracefully."""
        import logging

        from fastapi import FastAPI

        from app.lifecycle import bind_lifecycle_handlers

        monkeypatch.chdir(tmp_path)

        app = FastAPI()

        errors = []

        class FailingWebSocket:
            async def close(self, code=None, reason=None):
                raise RuntimeError("WebSocket already closed")

        class MockManager:
            active_connections = [FailingWebSocket()]

            def disconnect(self, ws):
                if ws in self.active_connections:
                    self.active_connections.remove(ws)

        def log_exception_safely(msg, exc):
            errors.append(msg)

        bind_lifecycle_handlers(
            app,
            MockManager(),
            {},
            logging.getLogger("test"),
            log_exception_safely,
        )

        async with app.router.lifespan_context(app):
            pass

        assert any("WebSocket" in e for e in errors)

    @pytest.mark.asyncio
    async def test_shutdown_orchestrator_error(self, tmp_path, monkeypatch):
        """Test shutdown handles orchestrator termination errors."""
        import logging

        from fastapi import FastAPI

        from app.lifecycle import bind_lifecycle_handlers

        monkeypatch.chdir(tmp_path)

        app = FastAPI()

        errors = []

        class FailingOrchestrator:
            def terminate_session(self):
                raise RuntimeError("Already terminated")

        class MockManager:
            active_connections = []

            def disconnect(self, ws):
                pass

        def log_exception_safely(msg, exc):
            errors.append(msg)

        active_sessions = {"sess_1": {"orchestrator": FailingOrchestrator()}}

        bind_lifecycle_handlers(
            app,
            MockManager(),
            active_sessions,
            logging.getLogger("test"),
            log_exception_safely,
        )

        async with app.router.lifespan_context(app):
            pass

        assert any("sess_1" in e for e in errors)

    @pytest.mark.asyncio
    async def test_shutdown_cancels_background_tasks(self, tmp_path, monkeypatch):
        """Test shutdown cancels tracked background tasks."""
        import logging

        from fastapi import FastAPI

        from app.lifecycle import background_tasks, background_tasks_lock, bind_lifecycle_handlers, track_background_task

        monkeypatch.chdir(tmp_path)

        app = FastAPI()

        class MockManager:
            active_connections = []

            def disconnect(self, ws):
                pass

        bind_lifecycle_handlers(
            app,
            MockManager(),
            {},
            logging.getLogger("test"),
            lambda msg, exc: None,
        )

        async with app.router.lifespan_context(app):
            # Create a long-running background task during the session
            async def long_running():
                await asyncio.sleep(100)

            task = asyncio.create_task(long_running())
            track_background_task(task, "test_shutdown", lambda msg, exc: None)

        # After shutdown, task should be cancelled and removed
        assert task.cancelled() or task.done()
        with background_tasks_lock:
            assert task not in background_tasks

        """Test that shutdown handles sessions without orchestrators."""
        import logging

        from fastapi import FastAPI

        from app.lifecycle import bind_lifecycle_handlers

        monkeypatch.chdir(tmp_path)

        app = FastAPI()

        class MockManager:
            active_connections = []

            def disconnect(self, ws):
                pass

        active_sessions = {"sess_no_orch": {"orchestrator": None}}

        bind_lifecycle_handlers(
            app,
            MockManager(),
            active_sessions,
            logging.getLogger("test"),
            lambda msg, exc: None,
        )

        # Should not raise
        async with app.router.lifespan_context(app):
            pass
