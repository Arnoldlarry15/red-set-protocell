# Vercel Deployment Guide

## Overview

Red Set ProtoCell supports deployment on **Vercel** using serverless Python functions. This guide explains how to deploy the application to Vercel's platform.

For complete details, see [Vercel Serverless Guide](./VERCEL_SERVERLESS_GUIDE.md).

## Quick Deploy

### Method 1: Vercel Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done)

2. **Go to [Vercel Dashboard](https://vercel.com/)**

3. **Click "Add New..." → "Project"**

4. **Import your GitHub repository**
   - Repository: `Arnoldlarry15/red-set-protocell`

5. **Configure environment variables**:
   - Go to Project → Settings → Environment Variables
   - Add required variables (see below)

6. **Deploy!**
   - Click "Deploy"
   - Your app will be live at `https://your-project.vercel.app`

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production (from repository root)
vercel --prod
```

## Repository Structure

```
/
├── frontend/           # React + Vite frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── api/               # Serverless Python functions
│   ├── auth.py       # Authentication endpoint
│   ├── health.py     # Health check endpoint
│   ├── info.py       # API info endpoint
│   ├── metrics.py    # Metrics endpoint
│   └── scan.py       # Scan session endpoint
│
├── vercel.json       # Vercel configuration
└── requirements.txt  # Python dependencies
```

## Vercel Handler Pattern

Vercel Python functions use a `handler` class pattern:

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

## Environment Variables

### Required Variables

Set these in **Vercel Dashboard → Project → Settings → Environment Variables**:

```bash
JWT_SECRET=your-random-32-plus-character-secret
RSP_DEMO_PASSWORD=your-secure-password
RSP_ENVIRONMENT=production
```

### Optional Variables

For actual red teaming functionality:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ADMIN_TOKEN=your-admin-token
```

## API Endpoints

Each Python file becomes an endpoint:

- `api/health.py` → `https://your-app.vercel.app/api/health`
- `api/auth.py` → `https://your-app.vercel.app/api/auth`
- `api/scan.py` → `https://your-app.vercel.app/api/scan`

## Frontend API Calls

From React components:

```javascript
// Simple relative path
const res = await fetch("/api/health");
const data = await res.json();
```

No CORS issues since frontend and backend share the same origin.

## Configuration: vercel.json

The `vercel.json` file configures the deployment:

```json
{
  "framework": "vite",
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/$1"
    }
  ]
}
```

**How it works:**
- **Framework mode**: Uses Vercel's native Vite support for optimal builds
- **Auto-detection**: Vercel automatically detects and deploys Python functions in `/api`
- **SPA routing**: Vercel automatically serves `/index.html` for all non-API routes
- **API routing**: Only `/api/*` paths need explicit routing to serverless functions

## Verifying Deployment

After deployment, test your endpoints:

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Authentication
curl -X POST https://your-project.vercel.app/api/auth \
  -H "Content-Type: application/json" \
  -d '{"password":"your-password"}'
```

## What Vercel Does Well

✅ **Advantages:**
- Faster cold starts (~0.5-1s)
- Seamless GitHub integration
- Excellent DX and documentation
- Advanced edge features
- Preview deployments for branches

## Troubleshooting

### Function Doesn't Work

1. **Check function logs**:
   - Vercel Dashboard → Deployments → Select deployment → Functions tab

2. **Verify handler class**:
   ```python
   class handler(BaseHTTPRequestHandler):  # Must be a class named "handler"
   ```

3. **Check Python dependencies**:
   - Ensure `requirements.txt` is at repository root

### CORS Issues

Vercel functions should include CORS headers:

```python
self.send_header("Access-Control-Allow-Origin", "*")
```

### Build Fails

1. Check build logs in Vercel Dashboard
2. Verify frontend builds locally:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

## Comparison: Vercel vs Netlify

Both platforms support Red Set ProtoCell with identical functionality:

| Feature | Vercel | Netlify |
|---------|--------|---------|
| Cold Starts | ~0.5-1s | ~1-2s |
| API Structure | `/api/*` | `/.netlify/functions/*` |
| Configuration | `vercel.json` | `netlify.toml` |
| Debugging | More abstracted | Clearer |
| Edge Features | More | Fewer |

**Choose based on your preference. Both work great.**

## Additional Resources

- **Complete Guide**: [Vercel Serverless Guide](./VERCEL_SERVERLESS_GUIDE.md)
- **Vercel Docs**: https://vercel.com/docs
- **Vercel Functions**: https://vercel.com/docs/functions

## No Vendor Lock-In

Red Set ProtoCell supports both Vercel and Netlify using the same codebase. Choose what works best for you! 🚀
