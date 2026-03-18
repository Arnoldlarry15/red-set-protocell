# Red Set ProtoCell v1.0.0 - Production Deployment

This document provides the production deployment configuration for Red Set ProtoCell v1.0.0.

## Migration target (current phase)

- **Frontend**: Firebase Hosting at `https://redset.app`
- **Backend**: Cloud Run at `https://api.redset.app`
- **Secrets**: Secret Manager injected into Cloud Run environment variables
- **Database**: Cloud SQL PostgreSQL is a later phase (not part of this migration step)

### Target architecture summary

| Layer | Platform | Domain |
|---|---|---|
| Frontend | Firebase Hosting | `redset.app` |
| Backend | Cloud Run | `api.redset.app` |
| Secrets | Secret Manager | injected into Cloud Run |
| Database | Future Cloud SQL PostgreSQL | later phase |

### Secret Manager mapping table

| Env var | Secret Manager secret |
|---|---|
| `OPENAI_API_KEY` | `rsp-openai-api-key` |
| `ANTHROPIC_API_KEY` | `rsp-anthropic-api-key` |
| `OPENROUTER_API_KEY` | `rsp-openrouter-api-key` |
| `SNIPER_ANTHROPIC_API_KEY` | `rsp-sniper-anthropic-api-key` |
| `SPOTTER_ANTHROPIC_API_KEY` | `rsp-spotter-anthropic-api-key` |
| `RSP_JWT_SECRET` | `rsp-jwt-secret` |
| `RSP_DEMO_PASSWORD` | `rsp-demo-password` |
| `RSP_API_KEYS` | `rsp-api-keys` |
| `RSP_POSTGRES_URI` | `rsp-postgres-uri` (future Cloud SQL phase) |

### Cloud Run non-secret env vars

| Env var | Example |
|---|---|
| `RSP_ENVIRONMENT` | `production` |
| `RSP_ALLOWED_ORIGINS` | `https://redset.app` |
| `RSP_REQUIRE_AUTH` | `true` |
| `RSP_JWT_EXPIRATION_HOURS` | `24` |
| `RSP_RATE_LIMIT_PER_MIN` | `60` |
| `RSP_RATE_LIMIT_PER_HOUR` | `1000` |
| `BACKEND_TYPE` | `openai` |
| `WORKERS` | `2` |
| `WORKER_CONNECTIONS` | `1000` |

### Legacy note

Render/Vercel references in this document are retained during migration as legacy rollback guidance.

> 🚀 **Quick Start:** For step-by-step deployment instructions, see [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

> 🔵 **One-Click Deploy:** Use `render.yaml` for automated Render deployment

## Live Deployments

### Frontend (Vercel)
- **URL**: https://red-set-protocell.vercel.app
- **Platform**: Vercel
- **Framework**: React + Vite
- **Auto-Deploy**: Enabled on push to main branch

### Backend (Render)
- **URL**: https://red-set-protocell.onrender.com
- **Platform**: Render
- **Framework**: FastAPI + Python 3.11
- **Container**: Docker-based deployment

## Quick Deployment Options

### Option 1: One-Click Deployment (Recommended)

Use the included `render.yaml` blueprint for automated Render deployment:

1. Click: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Arnoldlarry15/red-set-protocell)
2. Set your API keys in the Render Dashboard
3. Deploy frontend to Vercel (see [QUICK_DEPLOY.md](QUICK_DEPLOY.md))
4. Update `RSP_ALLOWED_ORIGINS` with your Vercel URL

### Option 2: Manual Deployment

Follow the detailed instructions in [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for manual deployment.

## Environment Configuration

### Frontend Environment Variables (Vercel)

Set these in Vercel Dashboard → Project Settings → Environment Variables:

```bash
VITE_API_BASE_URL=https://red-set-protocell.onrender.com
```

### Backend Environment Variables (Render)

Set these in Render Dashboard → Web Service → Environment:

```bash
# Required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
RSP_DEMO_PASSWORD=your-secure-password

# Agent-specific API Keys (optional, for independent agent operations)
SNIPER_ANTHROPIC_API_KEY=sk-ant-...
SPOTTER_ANTHROPIC_API_KEY=sk-ant-...

# CORS Configuration - PRODUCTION ONLY
# WARNING: Only trust the production frontend. No localhost. No wildcards.
RSP_ALLOWED_ORIGINS=https://red-set-protocell.vercel.app

# Environment
RSP_ENVIRONMENT=production

# Authentication (Production)
RSP_REQUIRE_AUTH=true
RSP_JWT_SECRET=your-generated-secret

# Rate Limiting
RSP_RATE_LIMIT_PER_MIN=60
RSP_RATE_LIMIT_PER_HOUR=1000
```

### Agent-Specific API Keys

Red Set ProtoCell v1.0.0+ supports independent API keys for the Sniper and Spotter agents:

- **SNIPER_ANTHROPIC_API_KEY**: Optional API key for Sniper agent operations
- **SPOTTER_ANTHROPIC_API_KEY**: Optional API key for Spotter agent operations

**Benefits of Separate API Keys:**

1. **Resource Isolation**: Each agent can have its own rate limits and quotas
2. **Cost Tracking**: Track API usage per agent for better cost attribution
3. **Fault Tolerance**: Issues with one agent's key won't affect others
4. **Security**: Principle of least privilege - each agent only has access to its own credentials
5. **Modularity**: Agents operate independently without shared resource contention

**When to Use:**
- Production deployments requiring high reliability
- Environments with strict cost tracking requirements
- Systems with separate API key quotas per service
- Architectures prioritizing agent independence

**Note:** If not set, agents will operate without making external API calls. This is suitable for most use cases where agents perform local computations only.

## Quick Start

### For End Users

1. Visit https://red-set-protocell.vercel.app
2. Enter your API keys (OpenAI or Anthropic)
3. Configure attack parameters
4. Start red teaming session

### For Developers

**Local Development:**
```bash
# Clone repository
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Run with Docker
docker compose up --build

# Or run separately:
# Backend:
cd backend && pip install -r requirements.txt && python main.py

# Frontend:
cd frontend && npm install && npm run dev
```

## Deployment Updates

### Updating Frontend (Vercel)

Vercel automatically deploys on push to main branch. To deploy manually:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Updating Backend (Render)

Render automatically deploys on push to main branch. To trigger manual deploy:

1. Go to Render Dashboard → Web Service
2. Click "Manual Deploy" → "Deploy latest commit"

## CORS Configuration

The backend must be configured to accept requests ONLY from its trusted frontend.

### Security Principle: One Backend, One UI, One Trust Relationship

**Production Backend (Render):**
- Trusts ONLY: `https://red-set-protocell.vercel.app`
- No localhost, no wildcards, no comma-separated list

**Local Development Backend (Your Machine):**
- Trusts ONLY: `http://localhost:3000` (or `http://localhost:5173` if using Vite)
- Never mix production and local in the same deployment

### Why This Matters

Mixing production and local dev origins in the same backend:
- Creates unnecessary attack surface
- Violates principle of least privilege
- Contradicts v1.0.0's scope-limited security model

CORS is part of your containment story - same philosophy as:
- Policy locking per run
- Deterministic execution
- Scope-limited attack surfaces

**Production Configuration on Render:**
```bash
RSP_ALLOWED_ORIGINS=https://red-set-protocell.vercel.app
```

**Local Development Configuration:**
```bash
# If frontend runs on port 3000
RSP_ALLOWED_ORIGINS=http://localhost:3000

# If using Vite on default port 5173
RSP_ALLOWED_ORIGINS=http://localhost:5173
```

### Troubleshooting CORS Errors

If you encounter CORS errors, verify:
1. `RSP_ALLOWED_ORIGINS` contains ONLY the appropriate origin (no commas in production)
2. Frontend is using the correct `VITE_API_BASE_URL` 
3. Backend is running in correct mode (`RSP_ENVIRONMENT=production` or `development`)
4. No typos in URLs (trailing slashes, http vs https, etc.)

## Monitoring

### Health Checks

- Backend Health: https://red-set-protocell.onrender.com/health
- Backend Metrics: https://red-set-protocell.onrender.com/metrics
- API Documentation: https://red-set-protocell.onrender.com/api/docs (development only)

### Logs

- **Vercel**: Dashboard → Project → Deployments → [Deployment] → Function Logs
- **Render**: Dashboard → Web Service → Logs

## Security Checklist

- [x] HTTPS enabled on both frontend and backend
- [x] CORS restricted to specific origins
- [x] JWT authentication enabled in production
- [x] API keys stored as environment variables (never in code)
- [x] Rate limiting enabled
- [x] Security headers middleware active
- [x] Input validation middleware active
- [ ] Set strong `RSP_DEMO_PASSWORD` on Render
- [ ] Generate secure `RSP_JWT_SECRET` on Render
- [ ] Provision at least one provider key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`)

## Troubleshooting

### Frontend cannot connect to backend

1. Check `VITE_API_BASE_URL` in Vercel environment variables
2. Verify backend is running: https://red-set-protocell.onrender.com/health
3. Check browser console for CORS errors

### CORS errors

1. Verify `RSP_ALLOWED_ORIGINS` includes `https://red-set-protocell.vercel.app`
2. Check backend logs on Render for CORS-related errors
3. Ensure backend is in production mode

### Backend is slow or timing out

Render free tier spins down after inactivity. First request may take 30-60 seconds to wake up the service.

## Support

- **Documentation**: See `docs/` directory
- **Issues**: https://github.com/Arnoldlarry15/red-set-protocell/issues
- **Repository**: https://github.com/Arnoldlarry15/red-set-protocell
