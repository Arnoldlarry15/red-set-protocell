"""
Monitoring and observability middleware for RSP API.

Implements:
- Structured logging
- Request/response logging
- Performance metrics
- Health checks
- Error tracking integration points
"""

import json
import logging
import sys
import time
import traceback
from datetime import datetime
from typing import Any, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class StructuredLogger:
    """
    Structured logging utility for production observability.

    Outputs JSON-formatted logs for easy parsing by log aggregation systems.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)

    def log(self, level: str, message: str, **kwargs):
        """Log a structured message with additional fields."""
        log_data = {"timestamp": datetime.utcnow().isoformat(), "level": level, "message": message, **kwargs}

        if level == "error":
            self.logger.error(json.dumps(log_data))
        elif level == "warning":
            self.logger.warning(json.dumps(log_data))
        elif level == "info":
            self.logger.info(json.dumps(log_data))
        elif level == "debug":
            self.logger.debug(json.dumps(log_data))


class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {  # type: ignore[assignment]
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",  # type: ignore[union-attr]
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_data)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests and responses with timing information.

    Essential for debugging and monitoring in production.
    """

    def __init__(self, app, log_body: bool = False):
        super().__init__(app)
        self.log_body = log_body
        self.structured_logger = StructuredLogger("rsp.api.requests")

    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()

        # Generate request ID
        request_id = request.headers.get("X-Request-ID", f"req_{int(start_time * 1000)}")

        # Log request
        request_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        self.structured_logger.log("info", "Request received", **request_data)

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            response_data = {
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }

            self.structured_logger.log("info", "Request completed", **response_data)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response

        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000

            error_data = {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": round(duration_ms, 2),
            }

            self.structured_logger.log("error", "Request failed", **error_data)

            # Re-raise to let FastAPI handle it
            raise


class MetricsCollector:
    """
    In-memory metrics collector for monitoring.

    Compatible with Prometheus scraping pattern.
    """

    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_endpoint": {},
            "total_duration_ms": 0,
            "errors_total": 0,
            "rate_limit_hits": 0,
        }

    def record_request(self, endpoint: str, status_code: int, duration_ms: float):
        """Record a completed request."""
        self.metrics["requests_total"] += 1
        self.metrics["total_duration_ms"] += duration_ms

        # By status code
        status_key = str(status_code)
        self.metrics["requests_by_status"][status_key] = self.metrics["requests_by_status"].get(status_key, 0) + 1

        # By endpoint
        self.metrics["requests_by_endpoint"][endpoint] = self.metrics["requests_by_endpoint"].get(endpoint, 0) + 1

        # Track errors
        if status_code >= 500:
            self.metrics["errors_total"] += 1

    def record_rate_limit(self):
        """Record a rate limit hit."""
        self.metrics["rate_limit_hits"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        metrics = self.metrics.copy()

        # Calculate derived metrics
        if metrics["requests_total"] > 0:
            metrics["average_duration_ms"] = metrics["total_duration_ms"] / metrics["requests_total"]
            metrics["error_rate"] = metrics["errors_total"] / metrics["requests_total"]
        else:
            metrics["average_duration_ms"] = 0
            metrics["error_rate"] = 0

        return metrics

    def reset(self):
        """Reset all metrics."""
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_endpoint": {},
            "total_duration_ms": 0,
            "errors_total": 0,
            "rate_limit_hits": 0,
        }


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""

    def __init__(self, app, collector: MetricsCollector):
        super().__init__(app)
        self.collector = collector

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        try:
            response = await call_next(request)

            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            self.collector.record_request(endpoint=request.url.path, status_code=response.status_code, duration_ms=duration_ms)

            return response

        except Exception:
            # Record error
            duration_ms = (time.time() - start_time) * 1000
            self.collector.record_request(endpoint=request.url.path, status_code=500, duration_ms=duration_ms)
            raise


class HealthCheck:
    """
    Health check utility for monitoring system status.

    Checks various system components and returns health status.
    """

    def __init__(self):
        self.checks = {}

    def add_check(self, name: str, check_fn):
        """Add a health check function."""
        self.checks[name] = check_fn

    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks and return results."""
        import inspect

        results = {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "checks": {}}

        for name, check_fn in self.checks.items():
            try:
                # Check if it's an async function
                if inspect.iscoroutinefunction(check_fn):
                    check_result = await check_fn()
                elif callable(check_fn):
                    check_result = check_fn()
                else:
                    # Not a function, use as-is (e.g., boolean value)
                    check_result = check_fn

                results["checks"][name] = {"status": "pass" if check_result else "fail", "details": check_result}  # type: ignore[index]

                if not check_result:
                    results["status"] = "degraded"

            except Exception as e:
                results["checks"][name] = {"status": "fail", "error": str(e)}  # type: ignore[index]
                results["status"] = "unhealthy"

        return results


# Global metrics collector instance
metrics_collector = MetricsCollector()
