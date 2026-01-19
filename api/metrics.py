"""
Metrics Endpoint
Returns operational metrics for monitoring.
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timezone


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Return system metrics"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # In production, these would come from a metrics collector or database
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requests_total": 0,
            "requests_per_minute": 0,
            "active_sessions": 0,
            "errors_total": 0,
            "response_time_avg_ms": 0,
            "note": "In serverless mode, metrics should be collected in external monitoring (DataDog, CloudWatch, etc.)"
        }

        self.wfile.write(json.dumps(metrics).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
