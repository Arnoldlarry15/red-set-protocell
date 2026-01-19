"""
Scan Session Endpoint
Handles scan session management (simplified for serverless).
Note: For long-running scans, use a queue system (SQS, Pub/Sub) in production.
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timezone


class handler(BaseHTTPRequestHandler):
    def _send_json_response(self, status_code, data):
        """Helper to send JSON response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        """Handle scan session creation"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            # Extract session config
            backend = data.get("backend", "openai")
            model = data.get("model", "gpt-3.5-turbo")
            max_rounds = data.get("max_rounds", 100)
            
            # For serverless, we don't run the session immediately
            # Instead, we'd typically queue it for processing
            session_id = f"scan-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            
            # In production, save to database and queue for processing
            session_info = {
                "session_id": session_id,
                "status": "queued",
                "backend": backend,
                "model": model,
                "max_rounds": max_rounds,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "message": "Session queued for processing. Use webhooks or polling for updates."
            }

            self._send_json_response(200, session_info)

        except json.JSONDecodeError:
            self._send_json_response(400, {
                "error": "Invalid JSON in request body"
            })
        except Exception as e:
            # Log error server-side (in production, use proper logging)
            # Don't expose internal error details to client
            self._send_json_response(500, {
                "error": "Failed to create session"
            })

    def do_GET(self):
        """Handle scan session status query"""
        try:
            # Extract session_id from path if present
            # In production, query from database
            self._send_json_response(200, {
                "message": "Scan session status endpoint",
                "note": "In serverless mode, use database or external state store for session tracking"
            })

        except Exception as e:
            # Log error server-side (in production, use proper logging)
            # Don't expose internal error details to client
            self._send_json_response(500, {
                "error": "Failed to query session"
            })

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()
