"""
Info Endpoint for Netlify
Returns API information and configuration.
"""
import json
import os


def handler(event, context):
    """Return API info"""
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }
    
    info = {
        "name": "Red Set ProtoCell API",
        "version": "1.0.0",
        "description": "Serverless API for RSP red teaming system",
        "platform": "Netlify",
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
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(info)
    }
