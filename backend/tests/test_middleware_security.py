"""
Tests for security middleware (RateLimitMiddleware, InputValidationMiddleware).
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.security import (
    InputValidationMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app(requests_per_minute: int = 10, requests_per_hour: int = 1000):
    """Create a minimal FastAPI app wrapped with security middleware."""
    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/data")
    async def data():
        return {"value": 42}

    @app.post("/submit")
    async def submit(payload: dict):
        return {"received": payload}

    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute, requests_per_hour=requests_per_hour)
    return app


def _make_validation_app():
    app = FastAPI()

    @app.post("/echo")
    async def echo():
        return {"ok": True}

    app.add_middleware(InputValidationMiddleware)
    return app


def _make_headers_app():
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"ok": True}

    app.add_middleware(SecurityHeadersMiddleware)
    return app


# ---------------------------------------------------------------------------
# SecurityHeadersMiddleware
# ---------------------------------------------------------------------------


class TestSecurityHeadersMiddleware:
    def test_security_headers_present(self):
        client = TestClient(_make_headers_app())
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Content-Security-Policy" in resp.headers
        assert "X-Frame-Options" in resp.headers
        assert "X-Content-Type-Options" in resp.headers
        assert "X-XSS-Protection" in resp.headers


# ---------------------------------------------------------------------------
# RateLimitMiddleware
# ---------------------------------------------------------------------------


class TestRateLimitMiddleware:
    def test_health_check_skips_rate_limiting(self):
        """Health check endpoint bypasses rate limit."""
        app = _make_app(requests_per_minute=1)
        client = TestClient(app)
        # Two requests to /health should both succeed even with limit=1
        assert client.get("/health").status_code == 200
        assert client.get("/health").status_code == 200

    def test_normal_request_passes(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/data")
        assert resp.status_code == 200

    def test_rate_limit_headers_present(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/data")
        assert "X-RateLimit-Limit-Minute" in resp.headers
        assert "X-RateLimit-Limit-Hour" in resp.headers
        assert "X-RateLimit-Remaining-Minute" in resp.headers

    def test_minute_rate_limit_exceeded(self):
        """After requests_per_minute requests the next one gets 429."""
        app = _make_app(requests_per_minute=3)
        client = TestClient(app)
        for _ in range(3):
            assert client.get("/data").status_code == 200
        resp = client.get("/data")
        assert resp.status_code == 429
        assert resp.json()["error"] == "Rate limit exceeded"

    def test_hour_rate_limit_exceeded(self):
        """After requests_per_hour requests the next one gets 429 (with minute limit much higher)."""
        app = _make_app(requests_per_minute=100, requests_per_hour=2)
        client = TestClient(app)
        for _ in range(2):
            assert client.get("/data").status_code == 200
        resp = client.get("/data")
        assert resp.status_code == 429

    def test_x_forwarded_for_header(self):
        """X-Forwarded-For is used as the client IP."""
        app = _make_app(requests_per_minute=3)
        client = TestClient(app)
        for _ in range(3):
            client.get("/data", headers={"X-Forwarded-For": "10.0.0.1"})
        resp = client.get("/data", headers={"X-Forwarded-For": "10.0.0.1"})
        assert resp.status_code == 429

    def test_x_real_ip_header(self):
        """X-Real-IP is used as the client IP when X-Forwarded-For is absent."""
        app = _make_app(requests_per_minute=3)
        client = TestClient(app)
        for _ in range(3):
            client.get("/data", headers={"X-Real-IP": "192.168.1.5"})
        resp = client.get("/data", headers={"X-Real-IP": "192.168.1.5"})
        assert resp.status_code == 429


# ---------------------------------------------------------------------------
# InputValidationMiddleware
# ---------------------------------------------------------------------------


class TestInputValidationMiddleware:
    def test_safe_payload_passes(self):
        client = TestClient(_make_validation_app())
        resp = client.post("/echo", json={"message": "hello world"})
        assert resp.status_code == 200

    def test_sql_injection_blocked(self):
        client = TestClient(_make_validation_app())
        resp = client.post(
            "/echo",
            content="UNION SELECT * FROM users",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        assert resp.json()["error"] == "Invalid request"

    def test_command_injection_blocked(self):
        client = TestClient(_make_validation_app())
        resp = client.post(
            "/echo",
            content="foo; rm -rf /",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400

    def test_get_request_not_validated(self):
        """GET requests skip body validation."""
        client = TestClient(_make_validation_app())
        resp = client.get("/echo")
        # endpoint doesn't exist but at least middleware doesn't block it
        assert resp.status_code in (200, 405, 404)
