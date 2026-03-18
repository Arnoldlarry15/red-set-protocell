# Production Deployment Guide

This guide covers deploying Red Set ProtoCell in production environments.

## Architecture

Red Set ProtoCell uses a **clean separation** between frontend and backend:

- **Migration target (current phase)**
  - **Frontend**: Firebase Hosting at `https://redset.app`
  - **Backend**: Cloud Run at `https://api.redset.app`
  - **Secrets**: Google Secret Manager, injected into Cloud Run environment variables
  - **Database**: keep current storage in this phase; Cloud SQL PostgreSQL is a later phase

### Target architecture summary (migration phase)

| Layer | Target platform | Domain | Notes |
|---|---|---|---|
| Frontend SPA | Firebase Hosting | `redset.app` | Static Vite build from `frontend/dist` |
| Backend API | Cloud Run | `api.redset.app` | Container from `backend/Dockerfile` |
| Secrets | Secret Manager | n/a | Inject into Cloud Run as env vars |
| Database | Future Cloud SQL PostgreSQL | n/a | Explicitly out of scope for current migration phase |

### Secret Manager mapping (Cloud Run)

| Secret (recommended name) | Env var in Cloud Run | Required now |
|---|---|---|
| `rsp-openai-api-key` | `OPENAI_API_KEY` | Optional (at least one provider key required) |
| `rsp-anthropic-api-key` | `ANTHROPIC_API_KEY` | Optional (at least one provider key required) |
| `rsp-openrouter-api-key` | `OPENROUTER_API_KEY` | Optional |
| `rsp-sniper-anthropic-api-key` | `SNIPER_ANTHROPIC_API_KEY` | Optional |
| `rsp-spotter-anthropic-api-key` | `SPOTTER_ANTHROPIC_API_KEY` | Optional |
| `rsp-jwt-secret` | `RSP_JWT_SECRET` | Required in production |
| `rsp-demo-password` | `RSP_DEMO_PASSWORD` | Required in production |
| `rsp-api-keys` | `RSP_API_KEYS` | Optional |
| `rsp-postgres-uri` | `RSP_POSTGRES_URI` | Future phase (Cloud SQL cutover) |
| `rsp-sentry-dsn` | `SENTRY_DSN` | Optional |
| `rsp-rollbar-token` | `ROLLBAR_TOKEN` | Optional |

### Cloud Run non-secret environment variables

| Env var | Recommended value | Notes |
|---|---|---|
| `RSP_ENVIRONMENT` | `production` | Enables production checks |
| `RSP_ALLOWED_ORIGINS` | `https://redset.app` | Exact frontend origin |
| `RSP_REQUIRE_AUTH` | `true` | Must remain true in production |
| `RSP_JWT_EXPIRATION_HOURS` | `24` | Policy setting |
| `RSP_RATE_LIMIT_PER_MIN` | `60` | Tune as needed |
| `RSP_RATE_LIMIT_PER_HOUR` | `1000` | Tune as needed |
| `BACKEND_TYPE` | `openai` / `anthropic` / `openrouter` | Match provider configuration |
| `WORKERS` | platform-dependent | Optional gunicorn tuning |
| `WORKER_CONNECTIONS` | `1000` | Optional gunicorn tuning |

### Domain plan

- Frontend primary domain: `redset.app`
- Backend API domain: `api.redset.app`
- CORS in backend should allow only `https://redset.app` for production.

### Legacy references

- Existing Render/Vercel docs and configs are retained during migration for rollback safety.
- Treat Render/Vercel instructions in this file as legacy transition references.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
- [Backend Deployment (Container Platforms)](#backend-deployment-container-platforms)
- [Security Checklist](#security-checklist)

> **Legacy notice:** Vercel/Render/Railway/Fly.io sections below are retained as legacy references during migration.

## Prerequisites

### Frontend
- GitHub account
- Vercel account (free tier available)

### Backend
- Docker or container platform account (Railway/Render/Fly.io)
- API keys from OpenAI and/or Anthropic

## Frontend Deployment (Vercel)

### One-Click Deploy

1. **Push to GitHub** (if not already done)
2. **Go to [Vercel Dashboard](https://vercel.com/)**
3. **Import Repository**
   - Click "Add New" → "Project"
   - Select `Arnoldlarry15/red-set-protocell`
4. **Configure** (should auto-detect from `vercel.json`)
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
   - Framework: Vite
5. **Set Environment Variables**
   - `VITE_API_BASE_URL`: Your backend URL (e.g., `https://red-set-protocell.onrender.com`)
6. **Deploy**

Your frontend will be live at `https://red-set-protocell.vercel.app` in minutes!

### Command Line (Alternative)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from repository root
vercel --prod

# Set environment variable
vercel env add VITE_API_BASE_URL
```

## Backend Deployment (Container Platforms)

The backend runs as a Docker container and can be deployed to any container platform.

### Option 1: Railway 🚂 (Recommended)

Railway provides the easiest container deployment with automatic HTTPS and domain.

1. **Sign in to [Railway](https://railway.app)**
2. **Create New Project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `Arnoldlarry15/red-set-protocell`
3. **Configure Service**
   - Root Directory: `backend`
   - Dockerfile Path: `backend/Dockerfile`
4. **Set Environment Variables** (in Railway Dashboard)
   ```
   OPENAI_API_KEY=<OPENAI_API_KEY>
   ANTHROPIC_API_KEY=<ANTHROPIC_API_KEY>
   RSP_DEMO_PASSWORD=your-secure-password
   RSP_ENVIRONMENT=production
   RSP_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
   
   **SECURITY NOTE**: Production backends should trust ONLY their production frontend.
   - ✅ CORRECT: `RSP_ALLOWED_ORIGINS=https://your-frontend.vercel.app`
   - ❌ WRONG: `RSP_ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000`
   
   Never mix production and local development origins in a production deployment.
   For local development, run a separate backend instance with `RSP_ALLOWED_ORIGINS=http://localhost:3000`
   
5. **Deploy**
   - Railway auto-deploys on git push
   - Your backend will be at `https://your-app.railway.app`

### Option 2: Render 🎨

Render offers free tier with automatic deployments.

1. **Sign in to [Render](https://render.com)**
2. **Create Web Service**
   - Dashboard → "New" → "Web Service"
   - Connect GitHub repository
3. **Configure Service**
   - Environment: Docker
   - Root Directory: `backend`
   - Dockerfile Path: `./Dockerfile`
4. **Set Environment Variables** (same as Railway)
5. **Deploy**
   - Your backend will be at `https://your-app.onrender.com`

### Option 3: Fly.io ✈️

Fly.io provides edge deployment worldwide.

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Navigate to backend
cd backend

# Launch (interactive setup)
fly launch

# Set secrets
fly secrets set OPENAI_API_KEY=<OPENAI_API_KEY>
fly secrets set ANTHROPIC_API_KEY=<ANTHROPIC_API_KEY>
fly secrets set RSP_DEMO_PASSWORD=your-password
fly secrets set RSP_ENVIRONMENT=production
fly secrets set RSP_ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Deploy
fly deploy
```

### Option 4: Self-Hosted (Docker)

Run on your own infrastructure:

```bash
cd backend

# Build image
docker build -t rsp-backend:latest .

# Run backend
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY="<OPENAI_API_KEY>" \
  -e ANTHROPIC_API_KEY="<ANTHROPIC_API_KEY>" \
  -e RSP_DEMO_PASSWORD="changeme" \
  -e RSP_ENVIRONMENT="production" \
  -e RSP_ALLOWED_ORIGINS="https://your-frontend.vercel.app" \
  --restart unless-stopped \
  rsp-backend:latest

# Backend available at http://localhost:8000
```

For production, add nginx reverse proxy with SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables Reference

### Frontend (Vercel)

```bash
# Required
VITE_API_BASE_URL=https://your-backend.railway.app
```

### Backend (Container Platforms)

```bash
# Required: At least one API key
OPENAI_API_KEY=<OPENAI_API_KEY>
ANTHROPIC_API_KEY=<ANTHROPIC_API_KEY>

# Required: Security
RSP_DEMO_PASSWORD=your-secure-password
RSP_ENVIRONMENT=production
RSP_ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Optional
RSP_MAX_ROUNDS=100
RSP_REQUIRE_AUTH=true
JWT_SECRET=your-random-32-char-string
RSP_RATE_LIMIT_PER_MIN=60
```

## Security Checklist

Before going to production:

### Frontend (Vercel)
- [ ] `VITE_API_BASE_URL` set to production backend URL
- [ ] Custom domain configured (optional)
- [ ] HTTPS enabled (automatic on Vercel)

### Backend (Container Platform)
- [ ] `RSP_ENVIRONMENT=production` set
- [ ] Strong `RSP_DEMO_PASSWORD` configured
- [ ] `RSP_ALLOWED_ORIGINS` includes only trusted domains
- [ ] API keys secured and not committed to git
- [ ] HTTPS enabled (automatic on Railway/Render/Fly.io)
- [ ] Rate limiting configured
- [ ] Authentication enabled if needed (`RSP_REQUIRE_AUTH=true`)
- [ ] Monitoring/logging enabled

### Post-Deployment Verification
- [ ] Frontend loads successfully
- [ ] Backend health check responds: `curl https://your-backend/api/health`
- [ ] Frontend can connect to backend
- [ ] WebSocket connection works
- [ ] CORS configured correctly
- [ ] API authentication working (if enabled)

## Troubleshooting

### Frontend can't connect to backend
1. Verify `VITE_API_BASE_URL` is set correctly in Vercel
2. Check backend is running: visit `https://your-backend/api/health`
3. Verify CORS: `RSP_ALLOWED_ORIGINS` includes your Vercel domain

### Backend container failing
1. Check environment variables are set
2. Review container logs in platform dashboard
3. Test locally: `cd backend && docker build -t test . && docker run test`

### WebSocket connections failing
1. All recommended platforms support WebSocket by default
2. If self-hosting, ensure nginx configuration includes WebSocket upgrade headers (shown above)
3. Check firewall rules

## Support

For deployment issues:
- Check [GitHub Issues](https://github.com/Arnoldlarry15/red-set-protocell/issues)
- Review platform-specific docs: [Railway](https://docs.railway.app), [Render](https://render.com/docs), [Fly.io](https://fly.io/docs)
