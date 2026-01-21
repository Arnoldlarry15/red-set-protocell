"""
Red Set ProtoCell - Main Serverless API Entrypoint

This file serves as the main entrypoint for Vercel serverless functions.
It wraps the FastAPI backend and exposes it for serverless deployment.

Note: The individual endpoint files (health.py, auth.py, etc.) are standalone 
serverless functions. This file provides an alternative approach using the 
full FastAPI application from the backend.

For production deployment:
- Individual serverless functions (health.py, auth.py, etc.) are recommended
  for simple endpoints due to lower cold start times
- This app.py can be used for more complex endpoints that require the full
  FastAPI application stack

Usage:
- Vercel will automatically detect this file when using @vercel/python
- The 'app' variable is exposed for Vercel's Python runtime
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path so we can import from app
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    # Import the FastAPI app from backend
    from app.api_server import app
    
    # Vercel looks for a variable named 'app' at the module level
    # This is already provided by the import above
    
except ImportError as e:
    # If backend dependencies are not available, create a minimal handler
    # This allows the api/ serverless functions to work independently
    from http.server import BaseHTTPRequestHandler
    import json
    
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            """Fallback handler when backend is not available"""
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "error": "Backend not available in serverless mode",
                "message": "Use individual API endpoints instead: /api/health, /api/auth, etc.",
                "available_endpoints": [
                    "GET /api/health",
                    "GET /api/info", 
                    "GET /api/metrics",
                    "POST /api/auth",
                    "POST /api/scan"
                ]
            }
            
            self.wfile.write(json.dumps(response).encode())
        
        def do_OPTIONS(self):
            """Handle CORS preflight"""
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()
    
    # Export the handler for Vercel
    app = handler
