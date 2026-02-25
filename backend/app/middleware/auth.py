"""
Authentication and authorization middleware for RSP API.

Implements:
- JWT-based session management
- API key authentication
- Role-based access control (RBAC)
"""

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# JWT configuration
JWT_SECRET_KEY = os.getenv("RSP_JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("RSP_JWT_EXPIRATION_HOURS", "24"))

# Security warning for production
if not JWT_SECRET_KEY and os.getenv("RSP_ENVIRONMENT") == "production":
    logger.error(
        "CRITICAL: RSP_JWT_SECRET not set in production environment! "
        "Authentication will not work. Set RSP_JWT_SECRET environment variable."
    )
    JWT_SECRET_KEY = secrets.token_urlsafe(32)  # Temporary fallback
    logger.warning("Using temporary auto-generated JWT secret - NOT RECOMMENDED FOR PRODUCTION")
elif not JWT_SECRET_KEY:
    # Development mode: auto-generate
    JWT_SECRET_KEY = secrets.token_urlsafe(32)
    logger.info("Generated temporary JWT secret for development")

# Export for use in other modules
__all__ = [
    "TokenManager",
    "PasswordHasher",
    "RBACManager",
    "AuthenticationMiddleware",
    "APIKeyMiddleware",
    "JWT_EXPIRATION_HOURS",
]


class TokenManager:
    """Manage JWT tokens for session authentication."""

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Args:
            data: Payload data to encode
            expires_delta: Optional custom expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload dict or None if invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.PyJWTError as e:
            logger.warning(f"Token validation failed: {e}")
            return None


class PasswordHasher:
    """Secure password hashing utility."""

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """
        Hash a password with salt.

        In production, use bcrypt or argon2 instead.
        This is a simple implementation for demonstration.
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA256
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)  # 100k iterations

        return f"{salt}${key.hex()}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, key = hashed.split("$")
            expected = PasswordHasher.hash_password(password, salt)
            return expected == hashed
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


class RBACManager:
    """Role-based access control manager."""

    # Define role hierarchy (higher number = more permissions)
    ROLES = {
        "observer": 1,  # Read-only access
        "researcher": 2,  # Can run experiments
        "admin": 3,  # Full access
    }

    # Define endpoint permissions
    PERMISSIONS = {
        "observer": [
            "/api/sessions/list",
            "/api/sessions/stats",
            "/api/health",
            "/api/metrics",
        ],
        "researcher": [
            "/api/sessions/start",
            "/api/sessions/stop",
            "/api/custom-prompt",
            "/api/experiments/*",
        ],
        "admin": [
            "/api/users/*",
            "/api/config/*",
            "/api/admin/*",
        ],
    }

    @classmethod
    def has_permission(cls, role: str, endpoint: str) -> bool:
        """
        Check if a role has permission to access an endpoint.

        Args:
            role: User role
            endpoint: API endpoint path

        Returns:
            True if permission granted, False otherwise
        """
        # Admin has access to everything
        if role == "admin":
            return True

        # Get role level
        role_level = cls.ROLES.get(role, 0)

        # Check role-specific permissions
        for permitted_role, endpoints in cls.PERMISSIONS.items():
            permitted_level = cls.ROLES.get(permitted_role, 0)

            # If user's role level is >= required level
            if role_level >= permitted_level:
                for pattern in endpoints:
                    if pattern.endswith("/*"):
                        # Wildcard match
                        if endpoint.startswith(pattern[:-2]):
                            return True
                    elif endpoint == pattern or endpoint.startswith(pattern + "/"):
                        return True

        return False


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware using JWT tokens.

    Protects API endpoints requiring authentication.
    """

    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS = [
        "/",
        "/health",
        "/api/health",
        "/api/docs",
        "/api/openapi.json",
        "/api/login",
        "/api/auth/login",
        "/auth/validate-llm-key",  # allows API key validation without JWT
        "/docs",
        "/openapi.json",
        "/redoc",
    ]

    def __init__(self, app, require_auth: bool = True):
        super().__init__(app)
        self.require_auth = require_auth
        self.token_manager = TokenManager()

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if any(request.url.path.startswith(ep) for ep in self.PUBLIC_ENDPOINTS):
            return await call_next(request)

        # Skip auth if not required (development mode)
        if not self.require_auth:
            # Set default user for development
            request.state.user = {
                "username": "dev_user",
                "role": "admin",
                "email": "dev@example.com",
            }
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return self._unauthorized("Missing authorization header")

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return self._unauthorized("Invalid authentication scheme")
        except ValueError:
            return self._unauthorized("Invalid authorization header format")

        # Verify token
        payload = self.token_manager.verify_token(token)

        if not payload:
            return self._unauthorized("Invalid or expired token")

        # Attach user info to request
        request.state.user = {
            "username": payload.get("sub"),
            "role": payload.get("role"),
            "email": payload.get("email"),
        }

        # Check role-based permissions
        role = request.state.user.get("role", "observer")
        endpoint = request.url.path

        if not RBACManager.has_permission(role, endpoint):
            logger.warning(
                f"Permission denied: {request.state.user['username']} " f"(role={role}) attempted to access {endpoint}"
            )
            return self._forbidden("Insufficient permissions")

        return await call_next(request)

    def _unauthorized(self, message: str):
        """Return 401 Unauthorized response."""
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Unauthorized", "message": message},
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _forbidden(self, message: str):
        """Return 403 Forbidden response."""
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "Forbidden", "message": message},
        )


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Simple API key authentication middleware.

    Alternative to JWT for programmatic access.
    """

    def __init__(self, app, require_api_key: bool = False):
        super().__init__(app)
        self.require_api_key = require_api_key

        # Load API keys from environment
        # Format: RSP_API_KEYS=key1:role1,key2:role2
        api_keys_env = os.getenv("RSP_API_KEYS", "")
        self.api_keys: Dict[str, str] = {}

        if api_keys_env:
            for pair in api_keys_env.split(","):
                if ":" in pair:
                    key, role = pair.split(":", 1)
                    self.api_keys[key.strip()] = role.strip()

    async def dispatch(self, request: Request, call_next):
        # Skip if not required
        if not self.require_api_key:
            return await call_next(request)

        # Skip for public endpoints
        if any(request.url.path.startswith(ep) for ep in ["/health", "/docs", "/openapi.json"]):
            return await call_next(request)

        # Check for API key in header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "API key required"},
            )

        # Validate API key
        role = self.api_keys.get(api_key)

        if not role:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid API key"},
            )

        # Attach user info to request
        request.state.user = {
            "username": f"api_key_{api_key[:8]}",
            "role": role,
            "email": None,
        }

        return await call_next(request)
