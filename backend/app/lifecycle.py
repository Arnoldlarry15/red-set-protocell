"""Lifecycle hooks and background-task registry for API server."""

import asyncio
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Set

background_tasks: Set[asyncio.Task] = set()
# Single-process assumption: in multi-worker deployments, use distributed coordination.
background_tasks_lock = threading.Lock()


def track_background_task(
    task: asyncio.Task, context: str, log_exception_safely: Callable[[str, Exception], None]
) -> asyncio.Task:
    """Track background tasks and surface exceptions deterministically."""
    with background_tasks_lock:
        background_tasks.add(task)

    def _on_done(done_task: asyncio.Task) -> None:
        with background_tasks_lock:
            background_tasks.discard(done_task)
        if done_task.cancelled():
            return
        try:
            done_task.result()
        except Exception as exc:  # pragma: no cover
            log_exception_safely(f"Background task failed ({context})", exc)

    task.add_done_callback(_on_done)
    return task


def bind_lifecycle_handlers(app, manager, active_sessions: Dict[str, Dict[str, Any]], logger, log_exception_safely):
    """Bind startup/shutdown hooks to app."""

    @app.on_event("startup")
    async def startup_event():
        logger.info("=" * 60)
        logger.info("RSP API Server - Startup")
        logger.info("=" * 60)
        sessions_dir = Path("sessions")
        sessions_dir.mkdir(exist_ok=True)
        logger.info(f"Sessions directory: {sessions_dir.absolute()}")
        logger.info("Startup complete - Server ready")
        logger.info("=" * 60)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("=" * 60)
        logger.info("RSP API Server - Shutdown")
        logger.info("=" * 60)

        if manager.active_connections:
            logger.info(f"Closing {len(manager.active_connections)} active WebSocket connections")
            for ws in list(manager.active_connections):
                try:
                    await ws.close(code=1001, reason="Server shutting down")
                except Exception as e:
                    log_exception_safely("Error closing WebSocket", e)
                finally:
                    manager.disconnect(ws)

        if active_sessions:
            logger.info(f"Terminating {len(active_sessions)} active sessions")
            for session_id, session_data in list(active_sessions.items()):
                try:
                    orchestrator = session_data.get("orchestrator")
                    if orchestrator:
                        orchestrator.terminate_session()
                except Exception as e:
                    log_exception_safely(f"Error terminating session {session_id}", e)

        with background_tasks_lock:
            tasks_snapshot = list(background_tasks)

        if tasks_snapshot:
            logger.info(f"Cancelling {len(tasks_snapshot)} tracked background task(s)")
            for task in tasks_snapshot:
                task.cancel()
            await asyncio.gather(*tasks_snapshot, return_exceptions=True)
            with background_tasks_lock:
                for task in tasks_snapshot:
                    background_tasks.discard(task)

        logger.info("Shutdown complete")
        logger.info("=" * 60)
