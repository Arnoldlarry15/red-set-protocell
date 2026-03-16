"""
Tests for monitoring middleware module.
"""

import asyncio
import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.monitoring import (
    HealthCheck,
    JSONFormatter,
    MetricsCollector,
    MetricsMiddleware,
    RequestLoggingMiddleware,
    StructuredLogger,
)

# ── JSONFormatter ─────────────────────────────────────────────────────────────


class TestJSONFormatter:
    def test_format_basic(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Hello world",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["message"] == "Hello world"
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert "timestamp" in data

    def test_format_with_exception(self):
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"
        assert data["exception"]["message"] == "test error"


# ── StructuredLogger ──────────────────────────────────────────────────────────


class TestStructuredLogger:
    def test_log_info(self, caplog):
        sl = StructuredLogger("test.structured")
        # Just verify it doesn't raise
        sl.log("info", "Test info message", key="value")

    def test_log_error(self):
        sl = StructuredLogger("test.structured.error")
        sl.log("error", "Test error", detail="some_detail")

    def test_log_warning(self):
        sl = StructuredLogger("test.structured.warn")
        sl.log("warning", "Test warning")

    def test_log_debug(self):
        sl = StructuredLogger("test.structured.debug")
        sl.log("debug", "Test debug message")


# ── MetricsCollector ──────────────────────────────────────────────────────────


class TestMetricsCollector:
    def test_initial_state(self):
        collector = MetricsCollector()
        metrics = collector.get_metrics()
        assert metrics["requests_total"] == 0
        assert metrics["errors_total"] == 0
        assert metrics["average_duration_ms"] == 0
        assert metrics["error_rate"] == 0

    def test_record_request(self):
        collector = MetricsCollector()
        collector.record_request("/api/health", 200, 15.5)

        metrics = collector.get_metrics()
        assert metrics["requests_total"] == 1
        assert metrics["requests_by_status"]["200"] == 1
        assert metrics["requests_by_endpoint"]["/api/health"] == 1
        assert metrics["average_duration_ms"] == pytest.approx(15.5)

    def test_record_multiple_requests(self):
        collector = MetricsCollector()
        collector.record_request("/api/health", 200, 10.0)
        collector.record_request("/api/health", 200, 20.0)
        collector.record_request("/api/sessions", 201, 30.0)

        metrics = collector.get_metrics()
        assert metrics["requests_total"] == 3
        assert metrics["requests_by_status"]["200"] == 2
        assert metrics["requests_by_status"]["201"] == 1
        assert metrics["requests_by_endpoint"]["/api/health"] == 2
        assert metrics["average_duration_ms"] == pytest.approx(20.0)

    def test_record_server_error(self):
        collector = MetricsCollector()
        collector.record_request("/api/run", 500, 5.0)

        metrics = collector.get_metrics()
        assert metrics["errors_total"] == 1
        assert metrics["error_rate"] == pytest.approx(1.0)

    def test_record_rate_limit(self):
        collector = MetricsCollector()
        collector.record_rate_limit()
        collector.record_rate_limit()

        metrics = collector.get_metrics()
        assert metrics["rate_limit_hits"] == 2

    def test_reset(self):
        collector = MetricsCollector()
        collector.record_request("/api/health", 200, 10.0)
        collector.reset()

        metrics = collector.get_metrics()
        assert metrics["requests_total"] == 0
        assert metrics["errors_total"] == 0

    def test_error_rate_calculation(self):
        collector = MetricsCollector()
        collector.record_request("/api/health", 200, 10.0)
        collector.record_request("/api/run", 500, 5.0)
        collector.record_request("/api/run", 503, 5.0)

        metrics = collector.get_metrics()
        assert metrics["error_rate"] == pytest.approx(2 / 3)


# ── HealthCheck ───────────────────────────────────────────────────────────────


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_no_checks(self):
        hc = HealthCheck()
        result = await hc.run_checks()
        assert result["status"] == "healthy"
        assert result["checks"] == {}

    @pytest.mark.asyncio
    async def test_passing_sync_check(self):
        hc = HealthCheck()
        hc.add_check("db", lambda: True)
        result = await hc.run_checks()
        assert result["status"] == "healthy"
        assert result["checks"]["db"]["status"] == "pass"

    @pytest.mark.asyncio
    async def test_failing_sync_check(self):
        hc = HealthCheck()
        hc.add_check("db", lambda: False)
        result = await hc.run_checks()
        assert result["status"] == "degraded"
        assert result["checks"]["db"]["status"] == "fail"

    @pytest.mark.asyncio
    async def test_passing_async_check(self):
        async def async_check():
            return True

        hc = HealthCheck()
        hc.add_check("cache", async_check)
        result = await hc.run_checks()
        assert result["status"] == "healthy"
        assert result["checks"]["cache"]["status"] == "pass"

    @pytest.mark.asyncio
    async def test_failing_async_check(self):
        async def async_check():
            return False

        hc = HealthCheck()
        hc.add_check("cache", async_check)
        result = await hc.run_checks()
        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_check_raises_exception(self):
        def bad_check():
            raise RuntimeError("Connection refused")

        hc = HealthCheck()
        hc.add_check("service", bad_check)
        result = await hc.run_checks()
        assert result["status"] == "unhealthy"
        assert result["checks"]["service"]["status"] == "fail"
        assert "Connection refused" in result["checks"]["service"]["error"]

    @pytest.mark.asyncio
    async def test_non_callable_check(self):
        hc = HealthCheck()
        hc.add_check("static_true", True)
        hc.add_check("static_false", False)
        result = await hc.run_checks()
        assert result["checks"]["static_true"]["status"] == "pass"
        assert result["checks"]["static_false"]["status"] == "fail"
        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_mixed_checks(self):
        hc = HealthCheck()
        hc.add_check("passing", lambda: True)
        hc.add_check("failing", lambda: False)
        result = await hc.run_checks()
        assert result["status"] == "degraded"


# ── RequestLoggingMiddleware ──────────────────────────────────────────────────


class TestRequestLoggingMiddleware:
    def test_basic_request(self):
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/test")
        def test_endpoint():
            return {"ok": True}

        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

    def test_request_with_request_id_header(self):
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/test")
        def test_endpoint():
            return {"ok": True}

        client = TestClient(app)
        response = client.get("/test", headers={"X-Request-ID": "my-req-id"})
        assert response.headers["X-Request-ID"] == "my-req-id"

    def test_request_logs_exception(self):
        """RequestLoggingMiddleware logs and re-raises exceptions from endpoints."""
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/fail")
        def failing_endpoint():
            raise RuntimeError("Intentional error")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/fail")
        assert response.status_code == 500


# ── MetricsMiddleware ─────────────────────────────────────────────────────────


class TestMetricsMiddleware:
    def test_records_request_metrics(self):
        collector = MetricsCollector()
        app = FastAPI()
        app.add_middleware(MetricsMiddleware, collector=collector)

        @app.get("/api/health")
        def health():
            return {"status": "ok"}

        client = TestClient(app)
        client.get("/api/health")

        metrics = collector.get_metrics()
        assert metrics["requests_total"] == 1
        assert "200" in metrics["requests_by_status"]

    def test_records_multiple_requests(self):
        collector = MetricsCollector()
        app = FastAPI()
        app.add_middleware(MetricsMiddleware, collector=collector)

        @app.get("/api/test")
        def test_ep():
            return {}

        client = TestClient(app)
        for _ in range(3):
            client.get("/api/test")

        metrics = collector.get_metrics()
        assert metrics["requests_total"] == 3

    def test_records_exception_as_500(self):
        """MetricsMiddleware records a 500 status code when an endpoint raises."""
        collector = MetricsCollector()
        app = FastAPI()
        app.add_middleware(MetricsMiddleware, collector=collector)

        @app.get("/api/fail")
        def fail_ep():
            raise RuntimeError("Intentional error")

        client = TestClient(app, raise_server_exceptions=False)
        client.get("/api/fail")

        metrics = collector.get_metrics()
        assert "500" in metrics["requests_by_status"]
