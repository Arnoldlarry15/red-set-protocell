# Red Set ProtoCell - Serverless API

This directory contains Vercel serverless functions for the Red Set ProtoCell backend.

## Architecture

Each Python file in this directory becomes a serverless endpoint:

- `/api/health.py` → `https://your-app.vercel.app/api/health`
- `/api/auth.py` → `https://your-app.vercel.app/api/auth`
- `/api/scan.py` → `https://your-app.vercel.app/api/scan`
- `/api/metrics.py` → `https://your-app.vercel.app/api/metrics`
- `/api/info.py` → `https://your-app.vercel.app/api/info`

## Function Structure

Each file exports a `handler` class that extends `BaseHTTPRequestHandler`:

```python
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        self.wfile.write(json.dumps({
            "status": "ok"
        }).encode())
```

## Available Endpoints

### GET /api/health
Health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "healthy",
  "service": "Red Set ProtoCell",
  "timestamp": "2024-01-19T03:23:34.531Z",
  "version": "1.0.0"
}
```

### GET /api/info
Returns API information and available endpoints.

**Response:**
```json
{
  "name": "Red Set ProtoCell API",
  "version": "1.0.0",
  "environment": "production",
  "endpoints": [...]
}
```

### GET /api/metrics
Returns operational metrics (integrates with external monitoring).

**Response:**
```json
{
  "timestamp": "2024-01-19T03:23:34.531Z",
  "requests_total": 0,
  "active_sessions": 0
}
```

### POST /api/auth
Handles user authentication and JWT token generation.

**Request:**
```json
{
  "username": "admin",
  "password": "changeme"
}
```

**Response:**
```json
{
  "success": true,
  "token": "jwt-token-here",
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

### POST /api/scan
Creates a new scan session (queued for processing in serverless mode).

**Request:**
```json
{
  "backend": "openai",
  "model": "gpt-3.5-turbo",
  "max_rounds": 100
}
```

**Response:**
```json
{
  "session_id": "scan-20240119-032334",
  "status": "queued",
  "message": "Session queued for processing"
}
```

## Environment Variables

Configure these in Vercel Dashboard → Settings → Environment Variables:

- `JWT_SECRET` - Secret key for JWT token signing (required, min 32 chars)
- `RSP_ENVIRONMENT` - Environment name (production/development)
- `RSP_REQUIRE_AUTH` - Enable authentication (true/false)
- `RSP_DEMO_PASSWORD` - Demo user password (change from default!)
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI backend)
- `ANTHROPIC_API_KEY` - Anthropic API key (if using Claude)

## Serverless Considerations

### Stateless Functions
Each function invocation is independent. No shared memory between requests.

### External State Storage
For persistent data, use:
- **Database**: PostgreSQL (Vercel Postgres), MongoDB, Supabase
- **Cache**: Redis (Upstash), Memcached
- **Queue**: AWS SQS, Google Pub/Sub, RabbitMQ

### Long-Running Tasks
For scans that take >10 seconds:
1. Queue the task (SQS, Pub/Sub)
2. Return immediately with `session_id`
3. Use webhooks or polling for status updates

### WebSocket Alternative
Since serverless functions can't maintain WebSocket connections:
- Use API Gateway WebSocket API (AWS)
- Use Pusher/Ably for real-time updates
- Use Server-Sent Events (SSE)
- Poll the status endpoint

## Development

### Local Testing
```bash
# Install Vercel CLI
npm i -g vercel

# Run locally
vercel dev
```

### Testing Individual Functions
```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Test auth endpoint
curl -X POST http://localhost:3000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'
```

## Deployment

### Automatic Deployment
Push to GitHub main branch triggers automatic deployment via Vercel.

### Manual Deployment
```bash
vercel --prod
```

## Security Notes

1. **Never hardcode secrets** - Use environment variables
2. **Never log sensitive data** - No API keys, passwords, or tokens in logs
3. **Validate all input** - Sanitize user input to prevent injection attacks
4. **Use HTTPS only** - Vercel provides automatic HTTPS
5. **Change default passwords** - Update `RSP_DEMO_PASSWORD` in production
6. **Rotate JWT secrets** - Change `JWT_SECRET` regularly

## Migration from FastAPI/Flask

This serverless architecture replaces the traditional FastAPI server (`backend/app/api_server.py`). Key differences:

| Traditional | Serverless |
|------------|-----------|
| Long-running server | Request → Response only |
| In-memory state | External database |
| WebSocket connections | API Gateway or polling |
| Background tasks | Message queues |
| Startup/shutdown hooks | Per-request initialization |

## Next Steps

To extend the API:
1. Add new `.py` file in `/api` directory
2. Implement `handler` class with HTTP methods
3. Deploy (automatic via Git push)
4. Update this README with new endpoint documentation

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Red Set ProtoCell Issues](https://github.com/Arnoldlarry15/red-set-protocell/issues)
