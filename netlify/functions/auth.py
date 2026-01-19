"""
Authentication Endpoint for Netlify
Handles user authentication and JWT token generation.
"""
import json
import os
import hmac
import hashlib
from datetime import datetime, timedelta, timezone


def handler(event, context):
    """Authentication endpoint"""
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }
    
    # Only allow POST
    if event.get("httpMethod") != "POST":
        return {
            "statusCode": 405,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Method not allowed"})
        }
    
    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        password = body.get("password")
        
        if not password:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "Password required"})
            }
        
        # Check password (use environment variable)
        # Demo password - in production, use database with bcrypt hashes
        expected_password = os.environ.get("RSP_DEMO_PASSWORD", "changeme")
        
        if password != expected_password:
            return {
                "statusCode": 401,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "Invalid password"})
            }
        
        # Generate simple token
        jwt_secret = os.environ.get("JWT_SECRET")
        
        # Fail fast if no JWT secret in production
        if not jwt_secret:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "JWT_SECRET environment variable must be set"})
            }
        expiry = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Simple HMAC-based token
        payload = f"rsp-user:{expiry.isoformat()}"
        token = hmac.new(
            jwt_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "token": token,
                "user": "rsp-user",
                "expiresAt": expiry.isoformat()
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }
