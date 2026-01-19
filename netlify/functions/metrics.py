"""
Metrics Endpoint for Netlify
Returns operational metrics for monitoring.
"""
import json
from datetime import datetime, timezone


def handler(event, context):
    """Return system metrics"""
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
    
    # In production, these would come from a metrics collector or database
    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform": "Netlify",
        "requests_total": 0,
        "requests_per_minute": 0,
        "active_sessions": 0,
        "errors_total": 0,
        "response_time_avg_ms": 0,
        "note": "In serverless mode, metrics should be collected in external monitoring (DataDog, CloudWatch, Netlify Analytics, etc.)"
    }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(metrics)
    }
