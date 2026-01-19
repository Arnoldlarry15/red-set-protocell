"""
Scan Endpoint for Netlify
Handles red teaming scan sessions.
"""
import json


def handler(event, context):
    """Scan endpoint - starts a red teaming session"""
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
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
        
        # Extract parameters
        backend = body.get("backend", "openai")
        rounds = body.get("rounds", 10)
        model = body.get("model")
        
        # Mock response for demo
        # In production, this would trigger actual red teaming
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "sessionId": "rsp_demo_session",
                "status": "started",
                "backend": backend,
                "rounds": rounds,
                "model": model,
                "message": "Scan session started (demo mode)"
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
