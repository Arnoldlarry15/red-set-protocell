"""Tests for API server background task tracking and error handling."""

import asyncio
import logging
import os

import pytest

os.environ.setdefault("RSP_ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("RSP_DEMO_PASSWORD", "test_demo_password_not_real")
os.environ.setdefault("OPENAI_API_KEY", "sk-" + "test-key")

from app.api_server import background_tasks, track_background_task  # noqa: E402


def _fake_openai_key(suffix: str = "secret-value") -> str:
    return "sk-" + suffix


@pytest.mark.asyncio
async def test_track_background_task_cleans_up_completed_task():
    async def _ok():
        return "ok"

    task = asyncio.create_task(_ok())
    track_background_task(task, "unit-ok")
    await task
    await asyncio.sleep(0)  # allow done callback to run

    assert task not in background_tasks


@pytest.mark.asyncio
async def test_track_background_task_logs_exception_and_cleans_up(caplog):
    async def _boom():
        fake_key = _fake_openai_key()
        raise RuntimeError(f"boom {fake_key}")

    caplog.set_level(logging.ERROR)

    task = asyncio.create_task(_boom())
    track_background_task(task, "unit-fail")
    await asyncio.sleep(0.05)  # allow task to fail and callback to execute

    assert task not in background_tasks
    log_text = "\n".join(record.message for record in caplog.records)
    assert "Background task failed (unit-fail)" in log_text
    assert _fake_openai_key() not in log_text
    assert "sk-***REDACTED***" in log_text
