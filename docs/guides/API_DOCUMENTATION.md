# API Documentation and Versioning Guide

Complete guide for Red Set ProtoCell API documentation, usage, and versioning.

## Table of Contents

- [API Overview](#api-overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Versioning Strategy](#versioning-strategy)
- [OpenAPI Documentation](#openapi-documentation)
- [API Usage Examples](#api-usage-examples)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## API Overview

### Base URL

```
Production:  https://api.example.com
Development: http://localhost:8000
```

### API Versions

Current version: **v1.0.0**

### Content Type

All requests and responses use `application/json`

### Authentication

Bearer token (JWT) required for most endpoints (see [Authentication](#authentication))

## Authentication

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "username": "your-username",
    "email": "user@example.com",
    "role": "researcher"
  }
}
```

### Using the Token

Include the token in the `Authorization` header:

```http
GET /api/sessions/list
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration

Tokens expire after 24 hours (configurable). Handle 401 responses by re-authenticating.

## API Endpoints

### Health and Monitoring

#### GET /api/health

Basic health check (no auth required)

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T05:00:00Z",
  "active_sessions": 5,
  "websocket_connections": 12
}
```

#### GET /api/health/detailed

Detailed health check with component status

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T05:00:00Z",
  "active_sessions": 5,
  "websocket_connections": 12,
  "environment": "production",
  "checks": {
    "database": {"status": "pass", "details": true},
    "api_clients": {"status": "pass", "details": true}
  }
}
```

#### GET /api/metrics

Prometheus-compatible metrics

**Response**:
```json
{
  "requests_total": 15234,
  "requests_by_status": {
    "200": 14890,
    "429": 100,
    "500": 74
  },
  "average_duration_ms": 29.97,
  "error_rate": 0.0049,
  "active_sessions": 5
}
```

#### GET /api/info

API information and capabilities

**Response**:
```json
{
  "name": "Red Set ProtoCell API",
  "version": "1.0.0",
  "environment": "production",
  "features": {
    "authentication": true,
    "rate_limiting": true
  },
  "rate_limits": {
    "per_minute": 60,
    "per_hour": 1000
  }
}
```

### Session Management

#### POST /api/session/start

Start a new red teaming session

**Request**:
```json
{
  "backend": "openai",
  "api_key": "sk-...",
  "model": "gpt-4",
  "max_rounds": 50,
  "max_api_cost": 5.0,
  "halt_on_critical": true,
  "mutation_rate": 0.7
}
```

**Response**:
```json
{
  "session_id": "rsp_20260118_050000",
  "status": "started",
  "config": {
    "backend": "openai",
    "model": "gpt-4",
    "max_rounds": 50
  }
}
```

#### POST /api/session/{session_id}/stop

Stop a running session

**Response**:
```json
{
  "session_id": "rsp_20260118_050000",
  "status": "stopped",
  "rounds_completed": 23,
  "statistics": {
    "average_score": 0.312,
    "blocked_count": 2
  }
}
```

#### GET /api/session/{session_id}/stats

Get session statistics

**Response**:
```json
{
  "session_id": "rsp_20260118_050000",
  "status": "running",
  "rounds_completed": 23,
  "average_score": 0.312,
  "blocked_count": 2,
  "created_at": "2026-01-18T05:00:00Z"
}
```

#### POST /api/prompt/execute

Execute a custom user-provided prompt through the RSP pipeline

**Description**: This endpoint allows you to submit a custom prompt for evaluation through the RSP system. The prompt will be inspected by the Ethical Guardrail Governor (EGG), executed by the target LLM, and evaluated by the Spotter agent. This is useful for testing specific prompts or scenarios outside of the automated red teaming rounds.

**Security**: The prompt goes through the same EGG safety checks as automated rounds. Unsafe prompts will be blocked.

**Cost Tracking**: The estimated cost of executing this prompt will be added to the session's total cost.

**Request**:
```json
{
  "session_id": "rsp_20260118_050000",
  "prompt": "What is the capital of France?"
}
```

**Response** (Success):
```json
{
  "session_id": "rsp_20260118_050000",
  "prompt": "What is the capital of France?",
  "status": "success",
  "response": "The capital of France is Paris.",
  "scores": {
    "global": 0.15,
    "l1_linguistic": 0.12,
    "l2_security": 0.18,
    "l3_cognitive": 0.14
  },
  "blocked": false,
  "timestamp": "2026-01-18T05:15:30Z",
  "message": "Custom prompt executed successfully"
}
```

**Response** (Blocked by EGG):
```json
{
  "session_id": "rsp_20260118_050000",
  "prompt": "[unsafe prompt]",
  "status": "blocked",
  "response": "[BLOCKED BY ETHICAL GUARDRAIL]",
  "scores": {
    "global": 0.0,
    "l1_linguistic": 0.0,
    "l2_security": 0.0,
    "l3_cognitive": 0.0
  },
  "blocked": true,
  "blocked_category": "csam",
  "timestamp": "2026-01-18T05:15:30Z",
  "message": "Custom prompt executed successfully"
}
```

**Response** (Error):
```json
{
  "session_id": "rsp_20260118_050000",
  "prompt": "Test prompt",
  "status": "error",
  "response": "Error: API key invalid",
  "scores": {
    "global": 0.0,
    "l1_linguistic": 0.0,
    "l2_security": 0.0,
    "l3_cognitive": 0.0
  },
  "blocked": false,
  "timestamp": "2026-01-18T05:15:30Z",
  "message": "Custom prompt executed successfully"
}
```

**Error Codes**:
- `404 Not Found`: Session ID not found
- `422 Unprocessable Entity`: Missing required fields (prompt or session_id)
- `500 Internal Server Error`: Server error during execution

**Usage Notes**:
- The session must be created first using `/api/session/start`
- The prompt length should be reasonable (recommend < 4000 characters)
- Cost is estimated based on prompt and response lengths
- Multiple custom prompts can be executed on the same session
- Custom prompts do not update the Sniper's evolution pool

### Dashboard Endpoints

#### GET /api/dashboard/live-sessions

List currently active sessions

**Response**:
```json
{
  "sessions": [
    {
      "session_id": "rsp_20260118_050000",
      "status": "running",
      "rounds_completed": 23,
      "started_at": "2026-01-18T05:00:00Z"
    }
  ]
}
```

#### GET /api/dashboard/historical-sessions

List completed sessions

**Query Parameters**:
- `limit` (optional): Number of sessions to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
{
  "sessions": [
    {
      "session_id": "rsp_20260118_040000",
      "status": "completed",
      "rounds_completed": 50,
      "average_score": 0.342,
      "started_at": "2026-01-18T04:00:00Z",
      "completed_at": "2026-01-18T04:30:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### GET /api/dashboard/export/{session_id}

Export session data

**Query Parameters**:
- `format`: Export format (`json`, `csv`, `jsonl`)

**Response**:
```json
{
  "session_id": "rsp_20260118_050000",
  "format": "json",
  "data": "[exported data string]"
}
```

## Versioning Strategy

### Semantic Versioning

RSP API follows semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., 1.x.x → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.0.x → 1.1.0)
- **PATCH**: Bug fixes, backward compatible (e.g., 1.0.0 → 1.0.1)

### Version in URL (Future)

When v2 is released, both versions will be supported:

```
/v1/api/session/start  # Version 1 (current)
/v2/api/session/start  # Version 2 (future)
```

### Version in Header

Currently version is implicit (v1). Future versions can be requested via header:

```http
GET /api/session/list
Accept: application/vnd.rsp.v1+json
```

### Deprecation Policy

1. **Announcement**: 90 days before deprecation
2. **Warning Headers**: API returns deprecation warnings
3. **Sunset Date**: Hard cutoff after 180 days
4. **Migration Guide**: Provided with announcement

### Backward Compatibility

**Guaranteed**:
- Existing fields remain unchanged
- Existing endpoints remain functional
- Existing behavior preserved

**Not Guaranteed**:
- New fields may be added (clients should ignore unknown fields)
- New endpoints may be added
- Performance characteristics may change
- Error messages may change (use status codes)

## OpenAPI Documentation

### Interactive Documentation

RSP provides auto-generated interactive API documentation:

**Development**: http://localhost:8000/api/docs  
**ReDoc**: http://localhost:8000/api/redoc

In production, these endpoints are disabled for security (set `RSP_ENVIRONMENT=development` to enable).

### OpenAPI Schema

Download the OpenAPI specification:

```bash
curl http://localhost:8000/openapi.json > rsp-api-spec.json
```

### Generating Client Libraries

Use OpenAPI Generator to create client libraries:

```bash
# Install OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./rsp-python-client

# Generate TypeScript client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./rsp-typescript-client
```

### Postman Collection

Import OpenAPI spec into Postman:

1. Open Postman
2. Import → Link
3. Enter: `http://localhost:8000/openapi.json`
4. Click Import

## API Usage Examples

### Python

```python
import requests
import json

# Base URL
API_URL = "https://api.example.com"

# Login
def login(username, password):
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    response.raise_for_status()
    return response.json()["access_token"]

# Start session
def start_session(token, config):
    response = requests.post(
        f"{API_URL}/api/session/start",
        headers={"Authorization": f"Bearer {token}"},
        json=config
    )
    response.raise_for_status()
    return response.json()["session_id"]

# Usage
token = login("admin", "password")
session_id = start_session(token, {
    "backend": "openai",
    "api_key": "sk-...",
    "model": "gpt-4",
    "max_rounds": 10
})
print(f"Started session: {session_id}")
```

### JavaScript/TypeScript

```typescript
const API_URL = "https://api.example.com";

async function login(username: string, password: string): Promise<string> {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });
  
  if (!response.ok) {
    throw new Error(`Login failed: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.access_token;
}

async function startSession(token: string, config: any): Promise<string> {
  const response = await fetch(`${API_URL}/api/session/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(config)
  });
  
  if (!response.ok) {
    throw new Error(`Start session failed: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.session_id;
}

// Usage
const token = await login("admin", "password");
const sessionId = await startSession(token, {
  backend: "openai",
  api_key: "sk-...",
  model: "gpt-4",
  max_rounds: 10
});
console.log(`Started session: ${sessionId}`);
```

### cURL

```bash
# Login
TOKEN=$(curl -s -X POST "https://api.example.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.access_token')

# Start session
SESSION_ID=$(curl -s -X POST "https://api.example.com/api/session/start" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "backend": "openai",
    "api_key": "sk-...",
    "model": "gpt-4",
    "max_rounds": 10
  }' \
  | jq -r '.session_id')

echo "Started session: $SESSION_ID"

# Get stats
curl -s "https://api.example.com/api/session/$SESSION_ID/stats" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

## Rate Limiting

### Limits

- **Per IP**: 60 requests/minute, 1000 requests/hour
- **Per User**: Based on subscription tier

### Headers

Rate limit information in response headers:

```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Minute: 45
```

### Handling Rate Limits

```python
import time
import requests

def api_request_with_retry(url, headers, max_retries=3):
    """Make API request with automatic retry on rate limit."""
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:
            # Rate limited
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue |
| 400 | Bad Request | Fix request format |
| 401 | Unauthorized | Re-authenticate |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Check endpoint/resource |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Retry later, report if persistent |
| 503 | Service Unavailable | Service down, wait |

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context"
  },
  "request_id": "req_1705554000123"
}
```

### Error Handling Example

```python
try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        # Re-authenticate
        token = login(username, password)
        headers["Authorization"] = f"Bearer {token}"
        # Retry request
    elif e.response.status_code == 429:
        # Rate limited
        time.sleep(60)
        # Retry request
    else:
        # Log error
        logger.error(f"API error: {e.response.text}")
        raise
```

## Best Practices

### 1. Always Authenticate

Include valid JWT token in all requests (except public endpoints)

### 2. Handle Errors Gracefully

- Check status codes
- Parse error responses
- Implement retry logic with exponential backoff

### 3. Respect Rate Limits

- Monitor rate limit headers
- Implement request queuing
- Use caching when appropriate

### 4. Use HTTPS

Always use HTTPS in production. Never send credentials over HTTP.

### 5. Keep Tokens Secure

- Store tokens securely (not in localStorage for web apps)
- Rotate tokens regularly
- Implement token refresh if needed

### 6. Version Your Clients

Pin to specific API versions to avoid breaking changes

### 7. Monitor Your Usage

- Track API call counts
- Monitor error rates
- Set up alerts for anomalies

### 8. Read the Docs

Always check the latest documentation before implementing

## Support

- **Documentation**: https://docs.example.com
- **API Status**: https://status.example.com
- **Support Email**: api-support@example.com
- **GitHub Issues**: https://github.com/Arnoldlarry15/red-set-protocell/issues

---

Last Updated: January 2026
Version: 1.0.0
