"""
Info Endpoint
Returns API information and configuration.
"""
from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Return API info"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        info = {
            "name": "Red Set ProtoCell API",
            "version": "1.0.0",
            "description": "Serverless API for RSP red teaming system",
            "environment": os.environ.get("RSP_ENVIRONMENT", "production"),
            "auth_required": os.environ.get("RSP_REQUIRE_AUTH", "true").lower() == "true",
            "features": {
                "authentication": True,
                "health_checks": True,
                "metrics": True,
                "scan_sessions": True
            },
            "endpoints": [
                "GET /api/health",
                "GET /api/info",
                "GET /api/metrics",
                "POST /api/auth",
                "POST /api/scan"
            ]
        }

        self.wfile.write(json.dumps(info).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
