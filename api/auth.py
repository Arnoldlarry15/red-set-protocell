"""
Authentication Endpoint
Handles user login and JWT token generation.

SECURITY NOTE: This implementation uses a simplified HMAC-based token for demonstration.
For production use, replace with proper JWT using PyJWT library:
- Install: pip install PyJWT
- Use: jwt.encode(payload, secret, algorithm='HS256')
- Verify: jwt.decode(token, secret, algorithms=['HS256'])

This ensures:
- Standard JWT format
- Proper base64 encoding
- Token expiration validation
- Algorithm verification
- Protection against timing attacks
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import hmac
from datetime import datetime, timedelta, timezone

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


class handler(BaseHTTPRequestHandler):
    def _send_json_response(self, status_code, data):
        """Helper to send JSON response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _hash_password(self, password):
        """Hash password using bcrypt if available, otherwise fail"""
        if not BCRYPT_AVAILABLE:
            raise RuntimeError(
                "bcrypt library is required for secure password hashing. "
                "Install with: pip install bcrypt"
            )
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, password, stored_hash):
        """Verify password using bcrypt"""
        if not BCRYPT_AVAILABLE:
            raise RuntimeError(
                "bcrypt library is required for secure password hashing. "
                "Install with: pip install bcrypt"
            )
        try:
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        except Exception:
            return False

    def _generate_token(self, username, role):
        """Generate simple JWT-like token (use PyJWT in production)"""
        # This is a simplified version - use proper JWT in production
        jwt_secret = os.environ.get("JWT_SECRET")
        
        # Fail fast if no JWT secret in production
        if not jwt_secret:
            raise ValueError("JWT_SECRET environment variable must be set")
        
        payload = {
            "username": username,
            "role": role,
            "exp": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        }
        
        # Simple token for demo - use PyJWT for production
        import hashlib
        token_data = json.dumps(payload)
        signature = hmac.new(
            jwt_secret.encode(),
            token_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{token_data}.{signature}"

    def do_POST(self):
        """Handle login request"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                self._send_json_response(400, {
                    "error": "Username and password required"
                })
                return

            # Demo user - in production, use database
            # For demo purposes, we accept the password directly
            # In production, store bcrypt-hashed passwords in database
            demo_password = os.environ.get("RSP_DEMO_PASSWORD")
            
            if not demo_password:
                self._send_json_response(500, {
                    "error": "Server configuration error. RSP_DEMO_PASSWORD must be set."
                })
                return
            
            # Simple comparison for demo - in production use database with bcrypt hashes
            if username == "admin" and password == demo_password:
                token = self._generate_token(username, "admin")
                
                self._send_json_response(200, {
                    "success": True,
                    "token": token,
                    "user": {
                        "username": username,
                        "role": "admin",
                        "email": "admin@rsp.com"
                    }
                })
            else:
                self._send_json_response(401, {
                    "error": "Invalid credentials"
                })

        except ValueError as ve:
            # Configuration errors - these should be logged and monitored
            self._send_json_response(500, {
                "error": "Server configuration error. Please contact administrator."
            })
        except Exception as e:
            # Log error server-side (in production, use proper logging)
            # Don't expose internal error details to client
            self._send_json_response(500, {
                "error": "Internal server error"
            })

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()
