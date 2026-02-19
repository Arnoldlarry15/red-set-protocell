"""
Security middleware for Red Set ProtoCell API.

Implements production-ready security features:
- HTTP security headers (CSP, HSTS, X-Frame-Options, etc.)
- Rate limiting per IP address
- Request validation and sanitization
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all HTTP responses.

    Implements OWASP recommendations for secure web applications.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Content Security Policy (CSP) - Prevents XSS attacks
        # Adjust based on your specific needs
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )

        # HTTP Strict Transport Security (HSTS) - Force HTTPS
        # Only add in production with HTTPS enabled
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection (legacy, but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy - control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy - restrict browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse.

    Implements sliding window rate limiting per IP address.
    Essential for production deployment of compute-heavy AI endpoints.
    """

    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # In-memory rate limit tracking
        # For production, consider Redis or similar for distributed systems
        self.minute_buckets: Dict[str, list] = {}
        self.hour_buckets: Dict[str, list] = {}

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address, handling proxies."""
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP (some proxies use this)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        return request.client.host if request.client else "unknown"

    def _clean_old_requests(self, bucket: list, window_seconds: int):
        """Remove requests outside the time window."""
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        return [req_time for req_time in bucket if req_time > cutoff]

    def _check_rate_limit(self, ip: str) -> Tuple[bool, str]:
        """
        Check if request is within rate limits.

        Returns:
            (allowed, reason) tuple
        """
        now = datetime.now()

        # Initialize buckets for new IPs
        if ip not in self.minute_buckets:
            self.minute_buckets[ip] = []
        if ip not in self.hour_buckets:
            self.hour_buckets[ip] = []

        # Clean old requests
        self.minute_buckets[ip] = self._clean_old_requests(self.minute_buckets[ip], 60)
        self.hour_buckets[ip] = self._clean_old_requests(self.hour_buckets[ip], 3600)

        # Check minute limit
        if len(self.minute_buckets[ip]) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"

        # Check hour limit
        if len(self.hour_buckets[ip]) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

        # Add current request
        self.minute_buckets[ip].append(now)
        self.hour_buckets[ip].append(now)

        return True, ""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/", "/api/health"]:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit
        allowed, reason = self._check_rate_limit(client_ip)

        if not allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {reason}")
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "message": reason, "retry_after": 60},
                headers={"Retry-After": "60"},
            )

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)

        # Safely get remaining count
        remaining = self.requests_per_minute - len(self.minute_buckets.get(client_ip, []))
        response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, remaining))

        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Input validation middleware to prevent injection attacks.

    Validates and sanitizes all incoming requests.
    """

    # Dangerous patterns to block
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(--\s*$)",
        r"(;\s*DROP\s+)",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r"(\||\&\&|\;)\s*(ls|cat|rm|wget|curl|bash|sh)",
        r"(`.*`)",
        r"(\$\(.*\))",
    ]

    def _check_payload_safety(self, data: str) -> Tuple[bool, str]:
        """Check if payload contains dangerous patterns."""
        # Check SQL injection
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, data, re.IGNORECASE):
                return False, "Potential SQL injection detected"

        # Check command injection
        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, data, re.IGNORECASE):
                return False, "Potential command injection detected"

        return True, ""

    async def dispatch(self, request: Request, call_next):
        # Only validate POST/PUT requests with bodies
        if request.method in ["POST", "PUT", "PATCH"]:
            # Read body
            body = await request.body()
            body_str = body.decode("utf-8", errors="ignore")

            # Check for dangerous patterns
            safe, reason = self._check_payload_safety(body_str)
            if not safe:
                logger.warning(f"Dangerous payload detected: {reason}")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid request", "message": "Request contains potentially dangerous content"},
                )

            # Re-create request with original body
            # This is needed because we consumed the body above
            async def receive():
                return {"type": "http.request", "body": body}

            request._receive = receive

        return await call_next(request)
