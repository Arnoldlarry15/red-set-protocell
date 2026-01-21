# Vercel Serverless Deployment Guide

## Overview

Red Set ProtoCell has been restructured for Vercel's serverless architecture. This guide explains the new structure and how to deploy.

## New Repository Structure

```
/
├── frontend/           # React + Vite frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── api/               # Serverless Python functions (NEW)
│   ├── auth.py       # Authentication endpoint
│   ├── health.py     # Health check endpoint
│   ├── info.py       # API info endpoint
│   ├── metrics.py    # Metrics endpoint
│   ├── scan.py       # Scan session endpoint
│   └── README.md     # API documentation
│
├── backend/          # Legacy FastAPI server (kept for reference)
│   └── ...
│
├── vercel.json       # Vercel configuration
├── requirements.txt  # Python dependencies (root level)
└── .vercelignore     # Files to exclude from deployment
```

## Key Changes

### 1. Serverless API Functions (`/api`)

Each Python file in `/api` becomes a serverless endpoint:

- **File**: `/api/health.py` → **URL**: `https://your-app.vercel.app/api/health`
- **File**: `/api/auth.py` → **URL**: `https://your-app.vercel.app/api/auth`
- **File**: `/api/scan.py` → **URL**: `https://your-app.vercel.app/api/scan`

### 2. No Flask/FastAPI Server

- ❌ No `app = Flask(__name__)`
- ❌ No `gunicorn` or `uvicorn`
- ❌ No long-running server
- ✅ Request in, response out
- ✅ Stateless functions
- ✅ Auto-scaling

### 3. Handler Pattern

Each API file exports a `handler` class:

```python
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        response = {"status": "ok"}
        self.wfile.write(json.dumps(response).encode())
```

No decorators, no Flask lifecycle—just raw HTTP.

### 4. Minimal Dependencies

Root `requirements.txt` contains only what the API imports:

```
pydantic>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
```

Unused packages slow cold starts and invite deployment issues.

## Vercel Configuration

The `vercel.json` file wires frontend and backend together:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": { 
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/health",
      "dest": "/api/health.py"
    },
    {
      "src": "/api/info",
      "dest": "/api/info.py"
    },
    {
      "src": "/api/metrics",
      "dest": "/api/metrics.py"
    },
    {
      "src": "/api/auth",
      "dest": "/api/auth.py"
    },
    {
      "src": "/api/scan",
      "dest": "/api/scan.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

**Key Points:**
- **Builds section**: Explicitly tells Vercel to build Python functions and React frontend
- **Routes section**: Maps API endpoints to their serverless functions and frontend to static files
- **Explicit routing**: All API paths are explicitly routed for clarity and control
- **Static serving**: Frontend static files are served with proper routing

This configuration eliminates CORS hell—frontend and backend share the same origin.

## Frontend API Calls

From React, use relative paths:

```typescript
// Development (.env.local) - for local backend at http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000

// Production (Vercel) - leave empty to use relative paths
VITE_API_BASE_URL=
```

Then in your code:

```typescript
// Default to empty string for relative paths in production
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// This will call /api/health in production or http://localhost:8000/api/health in development
const response = await fetch(`${API_BASE_URL}/api/health`);
const data = await response.json();
```

Same origin. Clean. No CORS configuration needed.

## Environment Variables

### Required for Production

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET` | JWT signing secret | 32+ character random string |
| `RSP_ENVIRONMENT` | Environment name | `production` |
| `RSP_REQUIRE_AUTH` | Enable authentication | `true` |
| `RSP_DEMO_PASSWORD` | Demo user password | `secure-password-123` |

### Optional

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` |
| `RSP_ALLOWED_ORIGINS` | CORS origins (if needed) | `https://app.example.com` |

### Security Rules

- ❌ Never hardcode secrets
- ❌ Never log secrets
- ❌ Never commit secrets to Git
- ✅ Use environment variables
- ✅ Rotate secrets regularly
- ✅ Use strong, random values

## Deployment

### Method 1: Automatic (Recommended)

1. Push code to GitHub
2. Vercel auto-deploys on commit to `main`
3. Preview deployments for other branches
4. Done!

### Method 2: Vercel CLI

```bash
# Install CLI
npm i -g vercel

# Login
vercel login

# Deploy to production
vercel --prod
```

### Method 3: Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - Framework: Vite
   - Root Directory: `./frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Add environment variables
6. Click "Deploy"

## Architecture Notes

### Serverless = Stateless

Each function invocation is independent:

- ❌ No shared memory between requests
- ❌ No background threads
- ❌ No WebSocket connections (use API Gateway or polling)
- ✅ External database for state
- ✅ Message queues for long tasks
- ✅ Deterministic, testable functions

### Red Set Sniper/Spotter Architecture

Your architecture fits serverless perfectly:

- **Each scan** = one function call
- **Each audit** = deterministic output
- **Logs** = external (S3, Supabase, CloudWatch)
- **State** = database (PostgreSQL, MongoDB)
- **Long scans** = queue system (SQS, Pub/Sub)

You're building an immune system, not a pet server.

## What NOT To Do

- ❌ Do NOT deploy Flask as a server
- ❌ Do NOT use `gunicorn`
- ❌ Do NOT run background threads
- ❌ Do NOT store state in memory
- ❌ Do NOT log user input directly
- ❌ Do NOT use WebSockets (use alternatives)

Serverless is stateless. Embrace it.

## Migration Path

### Phase 1: Core Endpoints ✅ (Current)

- Health checks
- Authentication
- Basic scan endpoints
- Metrics
- Info

### Phase 2: Extended Functionality (Future)

- Full session management via database
- WebSocket alternative (polling/SSE)
- Async task processing via queues
- Integration with external storage

### Phase 3: Production Hardening (Future)

- Rate limiting (Vercel Edge Config)
- Advanced monitoring (DataDog, Sentry)
- Database integration (Vercel Postgres, Supabase)
- Queue system (AWS SQS, Google Pub/Sub)

## Testing

### Local Development

The frontend proxy still works for local development:

```bash
# Terminal 1: Start backend (legacy for now)
cd backend
python -m uvicorn app.api_server:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

The `vite.config.ts` proxies `/api` to `http://localhost:8000`.

### Production Testing

After deployment:

```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health

# Test authentication
curl -X POST https://your-app.vercel.app/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'
```

## Performance

Serverless is:
- ✅ Fast (edge deployment)
- ✅ Cheap (pay per request)
- ✅ Secure (isolated execution)
- ✅ Enterprise-legible
- ✅ Open-source friendly
- ✅ Scales automatically

Cold starts: ~200-500ms (acceptable for most use cases)

## Bottom Line

This setup gets you to **v1.0.0 in production** without rewriting your soul:

1. Clean architecture
2. Zero CORS issues
3. Auto-scaling
4. Cost-effective
5. Production-ready

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [API Documentation](/api/README.md)
- [Project Issues](https://github.com/Arnoldlarry15/red-set-protocell/issues)

---

**Red Set breathes. 🚀**
