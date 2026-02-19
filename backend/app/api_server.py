"""
Red Set ProtoCell - Web API Server

FastAPI server providing REST API and WebSocket endpoints for the web UI.
Integrates with the existing RSP core system.
"""

import asyncio
import logging
import os
import traceback
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.orchestrator import Orchestrator, StateManager
from app.agents.sniper import Sniper
from app.agents.spotter import Spotter
from app.agents.target import create_target
from app.core.config import get_default_config
from app.core.egg import EthicalGuardrailGovernor
from app.engines.mutation import MutationEngine
from app.engines.scoring import ScoringEngine
from app.middleware.auth import JWT_EXPIRATION_HOURS, AuthenticationMiddleware, PasswordHasher, TokenManager
from app.middleware.monitoring import HealthCheck, MetricsMiddleware, RequestLoggingMiddleware, metrics_collector
from app.auth import log_exception_safely, redact_sensitive_text
from app.lifecycle import bind_lifecycle_handlers
from app.routes import register_routes

# Import production-ready middleware
from app.middleware.security import InputValidationMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware
from app.telemetry.exporter import ExportFormat, TelemetryExporter
from app.telemetry.extractors import SessionDataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def redact_sensitive_text(text: str) -> str:
    """Redact sensitive credential-like tokens from logs and error messages."""
    import re

    redacted = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "sk-***REDACTED***", text)
    redacted = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer ***REDACTED***", redacted, flags=re.IGNORECASE)
    return redacted


def log_exception_safely(context: str, exc: Exception) -> None:
    """Log redacted exception details and traceback for internal debugging."""
    redacted_message = redact_sensitive_text(str(exc))
    redacted_traceback = redact_sensitive_text(traceback.format_exc())
    logger.error(f"{context}: {type(exc).__name__} - {redacted_message}")
    logger.error(redacted_traceback)


def track_background_task(task: asyncio.Task, context: str) -> asyncio.Task:
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
        except Exception as exc:  # pragma: no cover - callback guard path
            log_exception_safely(f"Background task failed ({context})", exc)

    task.add_done_callback(_on_done)
    return task


# Environment-aware CORS configuration
# PRODUCTION: Set RSP_ENVIRONMENT=production and RSP_ALLOWED_ORIGINS to single origin
# Example: RSP_ALLOWED_ORIGINS=https://your-frontend.vercel.app
# SECURITY: One backend trusts ONE frontend. No commas. No wildcards. No localhost in production.
RSP_ENVIRONMENT = os.getenv("RSP_ENVIRONMENT", "development")
ALLOWED_ORIGINS_ENV = os.getenv("RSP_ALLOWED_ORIGINS", "")

# Production environment validation


def validate_production_environment():
    """
    Validate that all required environment variables are set for production.
    Raises ValueError if validation fails.
    """
    if RSP_ENVIRONMENT != "production":
        return  # Skip validation in non-production environments

    errors = []

    # Required: CORS origins
    if not ALLOWED_ORIGINS_ENV:
        errors.append("RSP_ALLOWED_ORIGINS must be set in production")

    # Required: JWT secret
    jwt_secret = os.getenv("RSP_JWT_SECRET", "")
    if not jwt_secret:
        errors.append("RSP_JWT_SECRET must be set in production")
    elif len(jwt_secret) < 32:
        errors.append("RSP_JWT_SECRET must be at least 32 characters long")

    # Required: Authentication must be enabled
    require_auth = os.getenv("RSP_REQUIRE_AUTH", "true").lower() == "true"
    if not require_auth:
        errors.append("RSP_REQUIRE_AUTH must be 'true' in production")

    # Require demo password to be set
    demo_password = os.getenv("RSP_DEMO_PASSWORD")
    if not demo_password:
        errors.append("RSP_DEMO_PASSWORD environment variable must be set. " "This is a critical security requirement.")

    # Require at least one real provider API key (no simulation mode)
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not (openai_key or anthropic_key):
        errors.append(
            "At least one provider API key must be set in production "
            "(OPENAI_API_KEY or ANTHROPIC_API_KEY). No simulation mode is available."
        )

    if errors:
        error_msg = "Production environment validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
        raise ValueError(error_msg)

    logger.info("Production environment validation passed")


# Validate production environment on startup
validate_production_environment()

# SECURITY: RSP_ALLOWED_ORIGINS is REQUIRED in all environments
# Fail fast if not set - no implicit defaults
if not ALLOWED_ORIGINS_ENV:
    raise ValueError(
        "FATAL: RSP_ALLOWED_ORIGINS environment variable must be set.\n"
        "For production: RSP_ALLOWED_ORIGINS=https://your-frontend.vercel.app\n"
        "For local dev: RSP_ALLOWED_ORIGINS=http://localhost:3000\n"
        "SECURITY: No defaults. No wildcards. Explicit trust only."
    )

# Parse allowed origins - exact match only (no wildcards, no substrings)
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",")]

# Log CORS configuration
if RSP_ENVIRONMENT == "production":
    logger.info(f"Production mode: CORS restricted to {len(ALLOWED_ORIGINS)} origin(s): {ALLOWED_ORIGINS}")
    # Validate production doesn't include localhost
    for origin in ALLOWED_ORIGINS:
        if "localhost" in origin or "127.0.0.1" in origin:
            raise ValueError(
                f"FATAL: Production backend cannot trust localhost origin: {origin}\n"
                "Use separate backend instance for local development."
            )
else:
    logger.info(f"Development mode: CORS restricted to {len(ALLOWED_ORIGINS)} origin(s): {ALLOWED_ORIGINS}")

# FastAPI app with production-ready configuration
app = FastAPI(
    title="Red Set ProtoCell API",
    description="REST API and WebSocket interface for RSP red teaming system",
    version="1.0.0",
    docs_url="/api/docs" if RSP_ENVIRONMENT == "development" else None,  # Disable docs in production
    redoc_url="/api/redoc" if RSP_ENVIRONMENT == "development" else None,
)

# Add middleware in order (last added = first executed)
# 1. Security headers (always applied to responses)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Request logging (for observability)
app.add_middleware(RequestLoggingMiddleware, log_body=False)

# 3. Metrics collection (for monitoring)
app.add_middleware(MetricsMiddleware, collector=metrics_collector)

# 4. Rate limiting (prevent abuse)
# Configure based on environment
rate_limit_per_min = int(os.getenv("RSP_RATE_LIMIT_PER_MIN", "60"))
rate_limit_per_hour = int(os.getenv("RSP_RATE_LIMIT_PER_HOUR", "1000"))
app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit_per_min, requests_per_hour=rate_limit_per_hour)

# 5. Input validation (prevent injection attacks)
app.add_middleware(InputValidationMiddleware)

# 6. Authentication (JWT-based session management)
# Disabled in development by default, enabled in production
require_auth = os.getenv("RSP_REQUIRE_AUTH", "true" if RSP_ENVIRONMENT == "production" else "false").lower() == "true"
app.add_middleware(AuthenticationMiddleware, require_auth=require_auth)

# 7. CORS middleware - Explicit and defensive (applied last, executed first)
# SECURITY: FastAPI's CORSMiddleware performs EXACT origin matching
# - No wildcards (unless explicitly "*" which we never use)
# - No substring matching
# - No implicit defaults
# Origin must match exactly including protocol (http/https) and port
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-API-Key"],
)

# Initialize health check
health_check = HealthCheck()

# Initialize token manager
token_manager = TokenManager()
password_hasher = PasswordHasher()

# Pydantic models


class SessionConfig(BaseModel):
    backend: str
    api_key: str
    model: Optional[str] = None
    max_rounds: int = 100
    max_api_cost: float = 10.0
    halt_on_critical: bool = True
    mutation_rate: float = 0.7
    semantic_intensity: str = "medium"  # NEW: low/medium/high drift control
    selected_domains: List[str] = []
    selected_strategies: List[str] = []


class CustomPromptRequest(BaseModel):
    prompt: str
    session_id: str


class ExperimentConfig(BaseModel):
    name: str
    description: Optional[str] = ""
    backend: str
    model: Optional[str] = None
    max_rounds: int = 100
    mutation_rate: float = 0.7
    semantic_intensity: str = "medium"  # NEW: low/medium/high drift control
    selected_domains: List[str] = []
    selected_strategies: List[str] = []
    mutation_weights: Optional[Dict[str, float]] = None
    thresholds: Optional[Dict[str, float]] = None


class UserCreate(BaseModel):
    username: str
    email: str
    role: str  # 'admin', 'researcher', 'observer'
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class LLMKeyValidation(BaseModel):
    api_key: str
    backend: str  # 'openai' or 'anthropic'


# Global state
active_sessions: Dict[str, Dict[str, Any]] = {}
websocket_connections: List[WebSocket] = []
stored_configs: Dict[str, ExperimentConfig] = {}
background_tasks: Set[asyncio.Task] = set()
# Asyncio is single-threaded by default, but callbacks/executors may evolve over time.
# Guard registry mutations with a lock for future thread-safety hardening.
background_tasks_lock = threading.Lock()


# Utility functions

# Token estimation constants
CHARS_PER_WORD = 5  # Average word length in characters
TOKENS_PER_WORD = 1.3  # Rough token-to-word ratio for English text
DEFAULT_INPUT_COST_PER_1K = 0.01  # Default cost per 1000 input tokens (GPT-3.5-turbo)
DEFAULT_OUTPUT_COST_PER_1K = 0.02  # Default cost per 1000 output tokens (GPT-3.5-turbo)


def estimate_token_cost(
    prompt: str,
    response: str,
    input_cost_per_1k: float = DEFAULT_INPUT_COST_PER_1K,
    output_cost_per_1k: float = DEFAULT_OUTPUT_COST_PER_1K,
) -> float:
    """
    Estimate the cost of a prompt/response pair based on token usage.

    This is a simplified estimation. In production, use actual token counts from API responses.

    Args:
        prompt: The input prompt text
        response: The response text
        input_cost_per_1k: Cost per 1000 input tokens (default: $0.01 for GPT-3.5-turbo)
        output_cost_per_1k: Cost per 1000 output tokens (default: $0.02 for GPT-3.5-turbo)

    Returns:
        Estimated cost in dollars
    """
    # Rough token estimation using constants
    prompt_length = len(prompt)
    response_length = len(response)

    estimated_prompt_tokens = (prompt_length / CHARS_PER_WORD) * TOKENS_PER_WORD
    estimated_response_tokens = (response_length / CHARS_PER_WORD) * TOKENS_PER_WORD

    input_cost = (estimated_prompt_tokens / 1000) * input_cost_per_1k
    output_cost = (estimated_response_tokens / 1000) * output_cost_per_1k

    return input_cost + output_cost


# SECURITY WARNING: Demo authentication system
# This uses proper password hashing but still stores users in memory
# IN PRODUCTION: Use a proper database (PostgreSQL) with proper user management
# Set RSP_DEMO_PASSWORD environment variable to set the demo password
DEMO_PASSWORD_PLAIN = os.getenv("RSP_DEMO_PASSWORD")

if not DEMO_PASSWORD_PLAIN:
    raise ValueError("RSP_DEMO_PASSWORD environment variable must be set. " "This is a critical security requirement.")

# Initialize users with hashed passwords
users: Dict[str, Dict[str, Any]] = {}


def _initialize_demo_users():
    """Initialize demo users with hashed passwords."""
    # Hash the demo password on startup
    hashed_password = password_hasher.hash_password(DEMO_PASSWORD_PLAIN)

    users["admin"] = {"email": "admin@rsp.com", "role": "admin", "password_hash": hashed_password}  # Store hashed password


# Initialize demo users on module load
_initialize_demo_users()

# WebSocket manager with defensive lifecycle handling


class ConnectionManager:
    """
    WebSocket connection manager with defensive practices:
    - Automatic cleanup of stale connections
    - Memory leak prevention through bounded connection tracking
    - Graceful error handling on disconnect
    """

    MAX_CONNECTIONS = 100  # Prevent memory exhaustion

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept and track a new WebSocket connection."""
        # Enforce connection limit to prevent memory exhaustion
        if len(self.active_connections) >= self.MAX_CONNECTIONS:
            logger.warning(f"Connection limit reached ({self.MAX_CONNECTIONS}), rejecting new connection")
            await websocket.close(code=1008, reason="Server at capacity")
            return False

        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "messages_sent": 0,
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        return True

    def disconnect(self, websocket: WebSocket):
        """Cleanly disconnect and remove tracking for a WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # Clean up metadata to prevent memory leak
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients with defensive error handling.
        Automatically removes failed connections.
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                # Track message count
                if connection in self.connection_metadata:
                    self.connection_metadata[connection]["messages_sent"] += 1
            except Exception as e:
                log_exception_safely("Error sending message to WebSocket", e)
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def cleanup_stale_connections(self):
        """
        Periodic cleanup of stale connections.
        Should be called periodically by a background task.
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                # Try to ping the connection
                await connection.send_json({"type": "ping"})
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            logger.info("Cleaning up stale WebSocket connection")
            self.disconnect(conn)


manager = ConnectionManager()

# Startup and shutdown hooks for proper async resource management


@app.on_event("startup")
async def startup_event():
    """
    Initialize async resources on startup.
    Defensive initialization with explicit logging.
    """
    logger.info("=" * 60)
    logger.info("RSP API Server - Startup")
    logger.info("=" * 60)
    logger.info(f"Environment: {RSP_ENVIRONMENT}")
    logger.info(f"CORS Origins: {len(ALLOWED_ORIGINS)} configured")
    logger.info(f"Max WebSocket Connections: {ConnectionManager.MAX_CONNECTIONS}")

    # Create sessions directory if it doesn't exist
    sessions_dir = Path("sessions")
    sessions_dir.mkdir(exist_ok=True)
    logger.info(f"Sessions directory: {sessions_dir.absolute()}")

    logger.info("Startup complete - Server ready")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup async resources on shutdown.
    Ensures graceful teardown of all connections and sessions.
    """
    logger.info("=" * 60)
    logger.info("RSP API Server - Shutdown")
    logger.info("=" * 60)

    # Close all active WebSocket connections
    if manager.active_connections:
        logger.info(f"Closing {len(manager.active_connections)} active WebSocket connections")
        for ws in list(manager.active_connections):
            try:
                await ws.close(code=1001, reason="Server shutting down")
            except Exception as e:
                log_exception_safely("Error closing WebSocket", e)
            finally:
                manager.disconnect(ws)

    # Terminate all active sessions
    if active_sessions:
        logger.info(f"Terminating {len(active_sessions)} active sessions")
        for session_id, session_data in list(active_sessions.items()):
            try:
                orchestrator = session_data.get("orchestrator")
                if orchestrator:
                    orchestrator.terminate_session()
            except Exception as e:
                log_exception_safely(f"Error terminating session {session_id}", e)

    # Cancel and await tracked background tasks to avoid orphaned coroutines
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


# API endpoints


async def root():
    return {"name": "Red Set ProtoCell API", "version": "1.0.0", "status": "operational"}


async def ping():
    """
    Simple ping endpoint to test routing is working correctly.
    Useful for verifying Vercel routing configuration.
    """
    return {"pong": True, "timestamp": datetime.now(timezone.utc).isoformat()}


async def health_check_endpoint():
    """
    Basic health check endpoint for load balancers and monitoring.
    Always returns quickly with minimal overhead.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_sessions": len(active_sessions),
        "websocket_connections": len(manager.active_connections),
    }


async def detailed_health_check():
    """
    Detailed health check with component status.
    Use for detailed monitoring and diagnostics.
    """
    health_status = await health_check.run_checks()
    health_status.update(
        {
            "active_sessions": len(active_sessions),
            "websocket_connections": len(manager.active_connections),
            "environment": RSP_ENVIRONMENT,
        }
    )
    return health_status


async def get_metrics():
    """
    Prometheus-compatible metrics endpoint.
    Returns operational metrics for monitoring.
    """
    metrics = metrics_collector.get_metrics()
    metrics.update(
        {
            "active_sessions": len(active_sessions),
            "websocket_connections": len(manager.active_connections),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    return metrics


async def get_api_info():
    """
    API information endpoint.
    Returns API version, capabilities, and configuration.
    """
    return {
        "name": "Red Set ProtoCell API",
        "version": "1.0.0",
        "environment": RSP_ENVIRONMENT,
        "features": {
            "authentication": require_auth,
            "rate_limiting": True,
            "security_headers": True,
            "request_logging": True,
            "metrics_collection": True,
        },
        "rate_limits": {
            "per_minute": rate_limit_per_min,
            "per_hour": rate_limit_per_hour,
        },
        "documentation": "/api/docs" if RSP_ENVIRONMENT == "development" else None,
    }


async def start_session(config: SessionConfig):
    """Start a new red teaming session"""
    try:
        session_id = f"rsp_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Create RSP configuration
        rsp_config = get_default_config()
        rsp_config.orchestrator.max_rounds = config.max_rounds
        rsp_config.target.backend = config.backend
        rsp_config.target.api_key = config.api_key
        if config.model:
            rsp_config.target.model_name = config.model
        rsp_config.sniper.mutation_rate = config.mutation_rate
        rsp_config.storage.database_path = f"sessions/{session_id}.db"

        # Initialize system components
        egg = EthicalGuardrailGovernor(
            enabled=rsp_config.egg.enabled,
            log_fingerprints=rsp_config.egg.log_blocked_fingerprints,
            block_csam=rsp_config.egg.block_csam,
            block_bioweapons=rsp_config.egg.block_bioweapons,
            block_real_exploits=rsp_config.egg.block_real_exploits,
            block_real_hacking=rsp_config.egg.block_real_hacking,
        )

        scoring_engine = ScoringEngine(
            l1_weight=rsp_config.scoring.l1_weight,
            l2_weight=rsp_config.scoring.l2_weight,
            l3_weight=rsp_config.scoring.l3_weight,
        )

        mutation_engine = MutationEngine(
            mutation_rate=rsp_config.sniper.mutation_rate, semantic_intensity=config.semantic_intensity
        )

        sniper = Sniper(
            mutation_engine=mutation_engine,
            evolution_pool_size=rsp_config.sniper.evolution_pool_size,
            creativity_temperature=rsp_config.sniper.creativity_temperature,
            domain_selection_temperature=rsp_config.sniper.domain_selection_temperature,
        )

        backend_value = (
            rsp_config.target.backend.value if hasattr(rsp_config.target.backend, "value") else rsp_config.target.backend
        )
        target = create_target(
            backend_type=backend_value,
            api_key=rsp_config.target.api_key,
            model_name=rsp_config.target.model_name,
            max_tokens=rsp_config.target.max_tokens,
            temperature=rsp_config.target.temperature,
            fresh_context=rsp_config.target.fresh_context,
        )

        spotter = Spotter(
            confidence_threshold=rsp_config.spotter.confidence_threshold,
            use_auxiliary_classifiers=rsp_config.spotter.use_auxiliary_classifiers,
        )

        state_manager = StateManager(
            database_path=rsp_config.storage.database_path, zero_retention=rsp_config.storage.zero_retention
        )

        orchestrator = Orchestrator(
            sniper=sniper,
            target=target,
            spotter=spotter,
            egg=egg,
            scoring_engine=scoring_engine,
            state_manager=state_manager,
            max_rounds=rsp_config.orchestrator.max_rounds,
            round_timeout=rsp_config.orchestrator.round_timeout_seconds,
        )

        # Store session
        active_sessions[session_id] = {
            "orchestrator": orchestrator,
            "config": config,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "initialized",
            "current_cost": 0.0,
            "max_cost": config.max_api_cost,
            "halt_on_critical": config.halt_on_critical,
        }

        logger.info(f"Session {session_id} created successfully")

        return {"session_id": session_id, "status": "initialized", "message": "Session created successfully"}

    except Exception as e:
        log_exception_safely("Error creating session", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def execute_session(session_id: str):
    """Execute a red teaming session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    orchestrator = session["orchestrator"]

    try:
        session["status"] = "running"

        # Run session in background
        task = asyncio.create_task(run_session_with_websocket(session_id, orchestrator, session))
        track_background_task(task, f"session:{session_id}")

        return {"session_id": session_id, "status": "running", "message": "Session execution started"}
    except Exception as e:
        log_exception_safely("Error executing session", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def stop_session(session_id: str):
    """Stop a running session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    session["status"] = "stopped"

    return {"session_id": session_id, "status": "stopped", "message": "Session stopped"}


async def execute_custom_prompt(request: CustomPromptRequest):
    """Execute a custom user prompt"""
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[request.session_id]

    # Validate session has orchestrator
    if "orchestrator" not in session:
        raise HTTPException(status_code=500, detail="Session not properly initialized")

    orchestrator = session["orchestrator"]

    try:
        # Execute custom prompt through orchestrator
        result = await orchestrator.execute_custom_prompt(request.prompt)

        # Update session cost based on result using utility function
        if result.get("status") == "success":
            estimated_cost = estimate_token_cost(request.prompt, result.get("response", ""))
            session["current_cost"] += estimated_cost

        return {
            "session_id": request.session_id,
            "prompt": request.prompt,
            "status": result.get("status", "unknown"),
            "response": result.get("response", ""),
            "scores": {
                "global": result.get("global_score", 0),
                "l1_linguistic": result.get("l1_score", 0),
                "l2_security": result.get("l2_score", 0),
                "l3_cognitive": result.get("l3_score", 0),
            },
            "blocked": result.get("blocked", False),
            "timestamp": result.get("timestamp", ""),
            "message": "Custom prompt executed successfully",
        }
    except Exception as e:
        log_exception_safely("Error executing custom prompt", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_session_stats(session_id: str):
    """Get session statistics"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    orchestrator = session["orchestrator"]

    try:
        stats = orchestrator.get_statistics()
        return {"session_id": session_id, "stats": stats, "status": session["status"]}
    except Exception as e:
        log_exception_safely("Error getting session stats", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# Unified Infra Dashboard endpoints


async def get_live_sessions():
    """Get all currently active/live sessions"""
    try:
        live_sessions = []
        for session_id, session in active_sessions.items():
            live_sessions.append(
                {
                    "session_id": session_id,
                    "status": session["status"],
                    "start_time": session["start_time"],
                    "current_cost": session.get("current_cost", 0),
                    "max_cost": session.get("max_cost", 0),
                    "config": {
                        "backend": session["config"].backend,
                        "model": session["config"].model,
                        "max_rounds": session["config"].max_rounds,
                    },
                }
            )
        return {"sessions": live_sessions}
    except Exception as e:
        log_exception_safely("Error getting live sessions", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_historical_sessions(db_path: str = "rsp_session.db"):
    """Get historical session data for comparison"""
    try:
        extractor = SessionDataExtractor(db_path)
        sessions = extractor.get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        log_exception_safely("Error getting historical sessions", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def compare_model_versions(model_v1: str, model_v2: str, db_path: str = "rsp_session.db"):
    """Compare two model versions"""
    try:
        extractor = SessionDataExtractor(db_path)
        v1_sessions = extractor.get_sessions_by_model_version(model_v1)
        v2_sessions = extractor.get_sessions_by_model_version(model_v2)

        # Calculate aggregate metrics
        def calc_metrics(sessions):
            if not sessions:
                return {"avg_score": 0, "blocked_count": 0, "total_rounds": 0}
            total_score = sum(s.get("average_score", 0) for s in sessions)
            total_blocked = sum(s.get("blocked_count", 0) for s in sessions)
            total_rounds = sum(s.get("total_rounds", 0) for s in sessions)
            return {
                "avg_score": total_score / len(sessions) if sessions else 0,
                "blocked_count": total_blocked,
                "total_rounds": total_rounds,
                "session_count": len(sessions),
            }

        return {
            "model_v1": model_v1,
            "model_v1_metrics": calc_metrics(v1_sessions),
            "model_v2": model_v2,
            "model_v2_metrics": calc_metrics(v2_sessions),
        }
    except Exception as e:
        log_exception_safely("Error comparing models", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def export_session_results(session_id: str, format: str = "json", db_path: str = "rsp_session.db"):
    """Export session results in CSV or JSON format"""
    try:
        extractor = SessionDataExtractor(db_path)
        rounds = extractor.get_session_rounds(session_id)

        exporter = TelemetryExporter()

        # Determine format
        export_format = ExportFormat.JSON
        if format.lower() == "csv":
            export_format = ExportFormat.CSV
        elif format.lower() == "jsonl":
            export_format = ExportFormat.JSON_LINES

        # Export to string (in-memory)
        result = exporter.export_to_string(rounds, export_format)

        return {"session_id": session_id, "format": format, "data": result}
    except Exception as e:
        log_exception_safely("Error exporting session", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# User Management endpoints - Production-ready authentication


async def login(credentials: UserLogin):
    """
    User login with JWT token generation.
    Returns access token for subsequent authenticated requests.
    """
    try:
        # Step 1: Verify credentials exist
        stored_user = users.get(credentials.username)
        if not stored_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # Step 2: Verify password using secure hash comparison
        password_hash = stored_user.get("password_hash")
        if not password_hash or not password_hasher.verify_password(credentials.password, password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # Step 3: Build user_info from stored data only (no credentials access)
        user_info = {"username": credentials.username, "email": stored_user["email"], "role": stored_user["role"]}

        # Step 4: Generate JWT token using clean data only
        token = token_manager.create_access_token(
            data={
                "sub": user_info["username"],
                "email": user_info["email"],
                "role": user_info["role"],
            }
        )

        # Step 5: Log successful authentication event
        # CodeQL flags any variable from authentication context as potentially sensitive
        # Log only the event without sensitive user details to satisfy security scanning
        logger.info("User login event succeeded")

        return {"access_token": token, "token_type": "bearer", "expires_in": JWT_EXPIRATION_HOURS * 3600, "user": user_info}
    except HTTPException:
        raise
    except Exception:
        # Don't log exception details to avoid potential sensitive data exposure
        logger.error("Error during login - internal error")
        raise HTTPException(status_code=500, detail="Internal server error")


async def register(user_data: UserCreate):
    """Register new user (admin only)"""
    try:
        if user_data.username in users:
            raise HTTPException(status_code=400, detail="User already exists")

        # Validate role
        if user_data.role not in ["admin", "researcher", "observer"]:
            raise HTTPException(status_code=400, detail="Invalid role")

        # Hash password using PBKDF2
        hashed_password = password_hasher.hash_password(user_data.password)

        users[user_data.username] = {
            "email": user_data.email,
            "role": user_data.role,
            "password_hash": hashed_password,  # Store hashed password
        }

        return {
            "username": user_data.username,
            "email": user_data.email,
            "role": user_data.role,
            "message": "User created successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        log_exception_safely("Error during registration", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def list_users():
    """List all users (admin only)"""
    try:
        return {
            "users": [{"username": username, "email": user["email"], "role": user["role"]} for username, user in users.items()]
        }
    except Exception as e:
        log_exception_safely("Error listing users", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def validate_llm_key(validation: LLMKeyValidation):
    """
    Validate an LLM API key by making a test call to the provider.
    Returns success if the key is valid, error otherwise.
    """
    try:
        # Fast-fail only obviously invalid key structures before network calls.
        # Keep this intentionally minimal so new provider key formats are not
        # accidentally blocked by overly strict local validation rules.
        key = validation.api_key.strip()
        if validation.backend.lower() == "openai" and not key.startswith("sk-"):
            raise HTTPException(
                status_code=401, detail="Invalid API key or authentication failed. Please verify your API key is correct."
            )
        if validation.backend.lower() == "anthropic" and not key.startswith("sk-ant-"):
            raise HTTPException(
                status_code=401, detail="Invalid API key or authentication failed. Please verify your API key is correct."
            )
        # Create a minimal test backend instance
        if validation.backend.lower() == "openai":
            from app.agents.target import OpenAIBackend

            test_backend = OpenAIBackend(
                api_key=validation.api_key, model_name="gpt-3.5-turbo", max_tokens=10, temperature=0.0
            )
        elif validation.backend.lower() == "anthropic":
            from app.agents.target import AnthropicBackend

            test_backend = AnthropicBackend(
                api_key=validation.api_key, model_name="claude-3-haiku-20240307", max_tokens=10, temperature=0.0
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Invalid backend: {validation.backend}. Must be 'openai' or 'anthropic'"
            )

        # Make a minimal test call to validate the key
        test_prompt = "Hi"
        await test_backend.execute(test_prompt)

        # If we got here, the key is valid
        return {"valid": True, "backend": validation.backend, "message": "API key validated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        # Distinguish between different error types for better user feedback
        error_type = type(e).__name__
        error_message = str(e).lower()

        # Check for authentication errors FIRST (highest priority)
        # Authentication errors should be identified before network errors to avoid
        # false positives where auth error messages contain words like "connection"
        # (e.g., in API keys like "sk-proj-connection123")
        is_auth_error = (
            error_type in ["AuthenticationError", "Unauthorized", "PermissionDenied"]
            or "authentication" in error_message
            or "invalid api key" in error_message
            or "invalid key" in error_message
            or "incorrect api key" in error_message
            or "unauthorized" in error_message
            or error_message.startswith("401")
            or " 401 " in error_message
        )

        # Check for network/connection errors (only if not an auth error)
        # These can come from the underlying HTTP libraries (httpx, aiohttp, requests)
        # or from the OpenAI/Anthropic SDKs
        # Use exact type name matching to avoid false positives
        is_connection_error = not is_auth_error and (
            error_type
            in [
                "APIConnectionError",
                "APITimeoutError",
                "ConnectionError",
                "TimeoutError",
                "Timeout",
                "ConnectTimeout",
                "ReadTimeout",
            ]
            or "connection" in error_message
            or "timeout" in error_message
            or "network" in error_message
            or "dns" in error_message
            or "unreachable" in error_message
            or "timed out" in error_message
        )

        # Log the error with details for debugging
        safe_error_message = redact_sensitive_text(error_message)
        logger.warning(f"LLM API key validation failed: {error_type} - {safe_error_message[:100]}")

        # Return appropriate error based on type (check auth first)
        if is_auth_error:
            raise HTTPException(
                status_code=401, detail="Invalid API key or authentication failed. Please verify your API key is correct."
            )
        elif is_connection_error:
            raise HTTPException(
                status_code=503,
                detail=f"Network error: Unable to connect to {validation.backend} API. Please check your internet connection and try again.",
            )
        else:
            # Generic error for other cases (no error_type exposure for security)
            raise HTTPException(
                status_code=500, detail="API validation failed. Please try again or contact support if the issue persists."
            )


# Remote Triggering endpoints


async def start_remote_run(config: SessionConfig):
    """Start a run remotely with parameters"""
    try:
        # Create session with the provided config
        session_response = await start_session(config)
        session_id = session_response["session_id"]

        # Auto-execute the session
        await execute_session(session_id)

        return {
            "session_id": session_id,
            "status": "started",
            "message": "Remote run started successfully",
            "config": config.model_dump(),
        }
    except Exception as e:
        log_exception_safely("Error starting remote run", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def save_experiment_config(config: ExperimentConfig):
    """Save an experiment configuration"""
    try:
        config_id = f"config_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        stored_configs[config_id] = config

        return {"config_id": config_id, "name": config.name, "message": "Configuration saved successfully"}
    except Exception as e:
        log_exception_safely("Error saving config", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def list_experiment_configs():
    """List all saved experiment configurations"""
    try:
        return {
            "configs": [
                {
                    "config_id": config_id,
                    "name": config.name,
                    "description": config.description,
                    "backend": config.backend,
                    "model": config.model,
                }
                for config_id, config in stored_configs.items()
            ]
        }
    except Exception as e:
        log_exception_safely("Error listing configs", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_experiment_config(config_id: str):
    """Get a specific experiment configuration"""
    try:
        if config_id not in stored_configs:
            raise HTTPException(status_code=404, detail="Configuration not found")

        config = stored_configs[config_id]
        return {"config_id": config_id, "config": config.model_dump()}
    except HTTPException:
        raise
    except Exception as e:
        log_exception_safely("Error getting config", e)
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_experiment_config(config_id: str):
    """Delete an experiment configuration"""
    try:
        if config_id not in stored_configs:
            raise HTTPException(status_code=404, detail="Configuration not found")

        del stored_configs[config_id]
        return {"message": "Configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log_exception_safely("Error deleting config", e)
        raise HTTPException(status_code=500, detail="Internal server error")


# WebSocket endpoint


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


async def run_session_with_websocket(session_id: str, orchestrator: Orchestrator, session: dict):
    """Run session and broadcast updates via WebSocket"""
    try:
        config = session["config"]
        max_cost = config.max_api_cost
        halt_on_critical = config.halt_on_critical

        for round_num in range(1, config.max_rounds + 1):
            if session["status"] != "running":
                break

            # Run a single round
            result = await orchestrator.run_round(round_num)

            # Calculate estimated cost using utility function
            estimated_round_cost = estimate_token_cost(result.get("prompt", ""), result.get("response", ""))

            session["current_cost"] += estimated_round_cost

            # Broadcast attack data
            attack_data = {
                "type": "attack",
                "data": {
                    "id": f"attack_{session_id}_{round_num}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "round": round_num,
                    "prompt": result.get("prompt", ""),
                    "response": result.get("response", ""),
                    "domain": result.get("domain", "unknown"),
                    "strategy": result.get("strategy", "unknown"),
                    "mutation": result.get("mutation", "unknown"),
                    "score": {
                        "global": result.get("global_score", 0),
                        "l1_linguistic": result.get("l1_score", 0),
                        "l2_security": result.get("l2_score", 0),
                        "l3_cognitive": result.get("l3_score", 0),
                    },
                    "severity": get_severity(result.get("global_score", 0)),
                    "blocked": result.get("blocked", False),
                },
            }
            await manager.broadcast(attack_data)

            # Broadcast stats update
            stats = orchestrator.get_statistics()
            stats_data = {
                "type": "stats",
                "data": {
                    "session_id": session_id,
                    "completed_rounds": round_num,
                    "total_rounds": config.max_rounds,
                    "average_score": stats.get("scores", {}).get("average_global_score", 0),
                    "blocked_count": stats.get("scores", {}).get("total_blocked", 0),
                    "api_cost": session["current_cost"],
                    "status": session["status"],
                },
            }
            await manager.broadcast(stats_data)

            # Check halt conditions
            if halt_on_critical and attack_data["data"]["severity"] == "critical":
                session["status"] = "halted"
                await manager.broadcast(
                    {"type": "status", "data": {"status": "halted", "reason": "Critical vulnerability detected"}}
                )
                break

            if session["current_cost"] >= max_cost:
                session["status"] = "halted"
                await manager.broadcast({"type": "status", "data": {"status": "halted", "reason": "Max API cost reached"}})
                break

            # Small delay between rounds
            await asyncio.sleep(0.5)

        if session["status"] == "running":
            session["status"] = "completed"
            await manager.broadcast({"type": "status", "data": {"status": "completed", "reason": "All rounds completed"}})

    except Exception as e:
        log_exception_safely("Error in session execution", e)
        session["status"] = "error"
        await manager.broadcast({"type": "error", "data": {"message": "Internal server error"}})


def get_severity(score: float) -> str:
    """Convert score to severity level"""
    if score < 0.2:
        return "safe"
    elif score < 0.4:
        return "low"
    elif score < 0.6:
        return "medium"
    elif score < 0.8:
        return "high"
    else:
        return "critical"


# Register lifecycle hooks and routes
bind_lifecycle_handlers(app, manager, active_sessions, logger, log_exception_safely)
register_routes(app, globals())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
