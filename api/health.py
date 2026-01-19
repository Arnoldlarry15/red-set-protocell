"""
Health Check Endpoint
Simple health check for monitoring and load balancers.
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timezone


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        response = {
            "status": "healthy",
            "service": "Red Set ProtoCell",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0"
        }

        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
