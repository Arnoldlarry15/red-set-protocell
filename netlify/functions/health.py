"""
Health Check Endpoint for Netlify
Simple health check for monitoring and load balancers.
"""
import json


def handler(event, context):
    """Health check endpoint"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "status": "ok",
            "service": "Red Set ProtoCell"
        })
    }
