"""
Vercel Entry Point for Red Set ProtoCell Backend

This file serves as the entry point for Vercel's Python runtime.
Vercel requires a top-level 'app' variable that contains the FastAPI application.

The actual FastAPI application with all middleware, routes, and configuration
is defined in app/api_server.py. This file simply imports and exposes it.
"""

from app.api_server import app

# Vercel looks for a variable named 'app' at the module level
# This is already provided by the import above

# The app includes:
# - CORS middleware (configured for production via environment variables)
# - Authentication and authorization
# - Rate limiting
# - Security headers
# - Request logging and metrics
# - All API routes and WebSocket endpoints

# For local development, you can still run:
# uvicorn backend.main:app --reload
# or
# uvicorn app.api_server:app --reload (from the backend directory)
