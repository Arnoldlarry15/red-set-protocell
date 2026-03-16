"""
Tests for interfaces/target.py - BaseTarget abstract class.
"""

import pytest

from app.interfaces.target import BaseTarget


class ConcreteTarget(BaseTarget):
    """Concrete implementation for testing."""

    async def execute(self, prompt: str, **kwargs) -> str:
        if prompt == "test":
            return "test response"
        if prompt == "error":
            raise RuntimeError("Backend error")
        return f"response: {prompt}"

    def get_backend_info(self):
        return {"backend_type": "test", "model_name": "test-model"}


class FailingTarget(BaseTarget):
    """Target that always fails execute."""

    async def execute(self, prompt: str, **kwargs) -> str:
        raise ConnectionError("Cannot connect")

    def get_backend_info(self):
        return {"backend_type": "failing", "model_name": "none"}


class TestBaseTarget:
    def test_concrete_target_execute(self):
        target = ConcreteTarget()
        import asyncio

        result = asyncio.get_event_loop().run_until_complete(target.execute("hello"))
        assert result == "response: hello"

    def test_validate_configuration_default(self):
        """Default validate_configuration returns True."""
        target = ConcreteTarget()
        assert target.validate_configuration() is True

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """health_check returns True when execute("test") succeeds."""
        target = ConcreteTarget()
        result = await target.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """health_check returns False when execute raises an exception."""
        target = FailingTarget()
        result = await target.health_check()
        assert result is False

    def test_get_backend_info(self):
        target = ConcreteTarget()
        info = target.get_backend_info()
        assert info["backend_type"] == "test"
        assert info["model_name"] == "test-model"
