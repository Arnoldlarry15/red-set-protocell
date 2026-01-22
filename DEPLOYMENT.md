# Red Set ProtoCell v1.0.0 - Production Deployment

This document provides the production deployment configuration for Red Set ProtoCell v1.0.0.

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

# CORS Configuration
RSP_ALLOWED_ORIGINS=https://red-set-protocell.vercel.app,http://localhost:3000

# Environment
RSP_ENVIRONMENT=production

# Authentication (Production)
RSP_REQUIRE_AUTH=true
RSP_JWT_SECRET=your-generated-secret

# Rate Limiting
RSP_RATE_LIMIT_PER_MIN=60
RSP_RATE_LIMIT_PER_HOUR=1000
```

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

The backend must be configured to accept requests from the Vercel frontend:

**Current Configuration:**
- Frontend: `https://red-set-protocell.vercel.app`
- Backend accepts requests from: `https://red-set-protocell.vercel.app`

If you encounter CORS errors, verify:
1. `RSP_ALLOWED_ORIGINS` is set correctly on Render
2. Frontend is using the correct `VITE_API_BASE_URL` on Vercel
3. Backend is running in production mode (`RSP_ENVIRONMENT=production`)

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
