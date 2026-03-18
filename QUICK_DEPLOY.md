# Quick Deployment Guide - Red Set ProtoCell

This guide provides step-by-step instructions for migration-ready deployment.

## Migration target (current phase)

- **Frontend**: Firebase Hosting on `redset.app`
- **Backend**: Cloud Run on `api.redset.app`
- **Secrets**: Secret Manager injected into Cloud Run env vars
- **Database**: keep current storage in this phase (Cloud SQL PostgreSQL is later)

## Domain plan

- `redset.app` → Firebase Hosting (frontend)
- `api.redset.app` → Cloud Run service (backend)

## Cloud Run environment model

### Secret Manager → Cloud Run (secrets)

| Env var | Secret Manager |
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

### Standard Cloud Run env vars (non-secret)

| Env var | Example value |
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

## Recommended quick path (Firebase + Cloud Run)

1. Build and deploy backend container to Cloud Run from `backend/Dockerfile`.
2. Configure Cloud Run env vars:
   - non-secrets via standard env vars
   - secrets via Secret Manager references
3. Map Cloud Run custom domain to `api.redset.app`.
4. Build and deploy frontend to Firebase Hosting (`frontend/dist`).
5. Configure frontend `VITE_API_BASE_URL=https://api.redset.app`.
6. Map Firebase Hosting custom domain to `redset.app`.
7. Validate:
   - `https://api.redset.app/health`
   - frontend can call backend without CORS errors

## Legacy Render/Vercel flow (kept during transition)

The sections below are legacy deployment instructions retained for rollback/transition safety.

## Prerequisites

- GitHub account
- Render account (free tier available at https://render.com)
- Vercel account (free tier available at https://vercel.com)
- OpenAI API key and/or Anthropic API key

## Option 1: One-Click Deployment (Legacy Render/Vercel)

### Step 1: Deploy Backend to Render

1. **Click the Deploy Button:**
   
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Arnoldlarry15/red-set-protocell)

2. **Connect Your Repository:**
   - Authorize Render to access your GitHub account
   - Select the `red-set-protocell` repository

3. **Configure Environment Variables:**
   
   Render will prompt you to set these required variables:
   
   - `OPENAI_API_KEY`: Your OpenAI API key (get it from https://platform.openai.com/api-keys)
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (get it from https://console.anthropic.com/)
   - `RSP_ALLOWED_ORIGINS`: Leave blank for now, we'll set this after deploying the frontend
   
   Optional variables (Render will auto-generate secure values):
   - `RSP_DEMO_PASSWORD`: Auto-generated secure password
   - `RSP_JWT_SECRET`: Auto-generated secure secret

4. **Deploy:**
   - Click "Apply" to start the deployment
   - Wait 5-10 minutes for the first deployment to complete
   - Note your backend URL: `https://red-set-protocell-api.onrender.com` (or your custom name)

### Step 2: Deploy Frontend to Vercel

1. **Go to Vercel Dashboard:**
   
   Visit https://vercel.com/new

2. **Import Repository:**
   - Click "Import Project"
   - Select "Import Git Repository"
   - Choose `Arnoldlarry15/red-set-protocell`
   - Authorize Vercel to access your repository

3. **Configure Project:**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. **Set Environment Variable:**
   
   In "Environment Variables" section, add:
   ```
   VITE_API_BASE_URL=https://red-set-protocell-api.onrender.com
   ```
   (Use your actual Render backend URL from Step 1)

5. **Deploy:**
   - Click "Deploy"
   - Wait 2-3 minutes for deployment to complete
   - Note your frontend URL: `https://red-set-protocell.vercel.app` (or your custom domain)

### Step 3: Update CORS Configuration

1. **Go back to Render Dashboard:**
   - Navigate to your `red-set-protocell-api` service
   - Click "Environment" in the left sidebar

2. **Set RSP_ALLOWED_ORIGINS:**
   ```
   RSP_ALLOWED_ORIGINS=https://red-set-protocell.vercel.app
   ```
   (Use your actual Vercel frontend URL from Step 2)

3. **Save Changes:**
   - Click "Save Changes"
   - Render will automatically restart your backend with the new configuration

### Step 4: Test Your Deployment

1. Visit your frontend URL (e.g., https://red-set-protocell.vercel.app)
2. The application should load without CORS errors
3. Try the health check: Visit `https://red-set-protocell-api.onrender.com/health`
4. You should see: `{"status": "healthy", "version": "1.0.0"}`

## Option 2: Manual Deployment

If you prefer manual control, follow these detailed steps:

### Backend Deployment (Render)

1. **Create New Web Service:**
   - Go to Render Dashboard → "New" → "Web Service"
   - Connect your GitHub repository
   - Select `Arnoldlarry15/red-set-protocell`

2. **Configure Service:**
   - **Name**: `red-set-protocell-api` (or your choice)
   - **Runtime**: Docker
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Plan**: Starter (or higher for production)

3. **Set Environment Variables:**
   
   **Required Variables:**
   ```bash
   RSP_ENVIRONMENT=production
   RSP_ALLOWED_ORIGINS=https://your-frontend.vercel.app  # Update after deploying frontend
   OPENAI_API_KEY=sk-your-openai-key
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
   RSP_DEMO_PASSWORD=your-secure-password  # Generate a strong password
   RSP_REQUIRE_AUTH=true
   RSP_JWT_SECRET=your-secure-jwt-secret  # Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   **Optional Variables (for advanced use):**
   ```bash
   SNIPER_ANTHROPIC_API_KEY=sk-ant-your-sniper-key
   SPOTTER_ANTHROPIC_API_KEY=sk-ant-your-spotter-key
   RSP_RATE_LIMIT_PER_MIN=60
   RSP_RATE_LIMIT_PER_HOUR=1000
   WORKERS=2
   WORKER_CONNECTIONS=1000
   PORT=8000
   ```

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Frontend Deployment (Vercel)

1. **Install Vercel CLI (Optional):**
   ```bash
   npm install -g vercel
   ```

2. **Deploy via Dashboard:**
   - Go to https://vercel.com/new
   - Import `Arnoldlarry15/red-set-protocell`
   - Set root directory: `frontend`
   - Framework: Vite
   - Environment Variable:
     ```
     VITE_API_BASE_URL=https://red-set-protocell-api.onrender.com
     ```
   - Click "Deploy"

3. **Or Deploy via CLI:**
   ```bash
   cd frontend
   vercel --prod
   ```
   - Follow the prompts
   - Set environment variable when asked

## Environment Variables Reference

### Backend (Render)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `RSP_ENVIRONMENT` | Yes | Environment mode | `production` |
| `RSP_ALLOWED_ORIGINS` | Yes | Trusted frontend URL (exact match, no wildcards) | `https://red-set-protocell.vercel.app` |
| `OPENAI_API_KEY` | Yes* | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key | `sk-ant-...` |
| `RSP_DEMO_PASSWORD` | Yes | Admin password for demo user | `strong-password-123` |
| `RSP_REQUIRE_AUTH` | Yes | Enable authentication | `true` |
| `RSP_JWT_SECRET` | Yes | JWT signing secret | Generated via `secrets.token_urlsafe(32)` |
| `SNIPER_ANTHROPIC_API_KEY` | No | Sniper agent API key | `sk-ant-...` |
| `SPOTTER_ANTHROPIC_API_KEY` | No | Spotter agent API key | `sk-ant-...` |
| `RSP_RATE_LIMIT_PER_MIN` | No | Rate limit per minute | `60` |
| `RSP_RATE_LIMIT_PER_HOUR` | No | Rate limit per hour | `1000` |
| `WORKERS` | No | Gunicorn worker count | `2` |
| `WORKER_CONNECTIONS` | No | Max connections per worker | `1000` |
| `PORT` | No | Server port | `8000` |

*At least one AI provider key (OpenAI or Anthropic) is required.

### Frontend (Vercel)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_BASE_URL` | Yes | Backend API URL | `https://red-set-protocell-api.onrender.com` |

## Troubleshooting

### CORS Errors

**Symptom:** Browser console shows CORS policy errors

**Solution:**
1. Verify `RSP_ALLOWED_ORIGINS` on Render matches your exact Vercel URL
2. No trailing slashes: ❌ `https://app.vercel.app/` ✅ `https://app.vercel.app`
3. No wildcards: ❌ `https://*.vercel.app` ✅ `https://red-set-protocell.vercel.app`
4. No commas: Use one exact URL only
5. Restart Render service after changing environment variables

### Backend Takes Long to Respond

**Symptom:** First request after inactivity takes 30-60 seconds

**Solution:**
- This is normal on Render's free tier (cold starts)
- Upgrade to paid tier for always-on instances
- Or implement a health check ping service

### Frontend Cannot Connect to Backend

**Symptom:** Network errors in browser console

**Solution:**
1. Check `VITE_API_BASE_URL` in Vercel environment variables
2. Verify backend is running: visit `https://your-backend.onrender.com/health`
3. Check Render logs for backend errors
4. Ensure `RSP_ALLOWED_ORIGINS` is set correctly

### Authentication Errors

**Symptom:** Login fails or JWT errors

**Solution:**
1. Verify `RSP_DEMO_PASSWORD` is set on Render
2. Check `RSP_JWT_SECRET` is set and not empty
3. Ensure `RSP_REQUIRE_AUTH=true` in production
4. Review Render logs for authentication errors

### Missing API Keys

**Symptom:** "API key not configured" errors

**Solution:**
1. Verify `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` are set
2. Check API keys are valid and have sufficient credits
3. Ensure no spaces or quotes around the key values
4. Restart Render service after adding keys

## Security Best Practices

1. **Never Commit Secrets:**
   - Never commit API keys, passwords, or secrets to git
   - Use environment variables for all sensitive data

2. **Use Strong Passwords:**
   - Generate `RSP_DEMO_PASSWORD` with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Generate `RSP_JWT_SECRET` with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

3. **Restrict CORS:**
   - Only set `RSP_ALLOWED_ORIGINS` to your production frontend
   - Never use wildcards like `*` or `https://*.vercel.app`

4. **Enable Rate Limiting:**
   - Keep `RSP_RATE_LIMIT_PER_MIN` and `RSP_RATE_LIMIT_PER_HOUR` enabled
   - Adjust based on your expected traffic

5. **Monitor Logs:**
   - Regularly check Render logs for suspicious activity
   - Set up monitoring alerts for your service

## Updating Your Deployment

### Backend Updates

Render automatically deploys when you push to the main branch:

```bash
git add .
git commit -m "Update backend"
git push origin main
```

Render will detect the change and redeploy automatically.

### Frontend Updates

Vercel automatically deploys when you push to the main branch:

```bash
git add .
git commit -m "Update frontend"
git push origin main
```

Vercel will detect the change and redeploy automatically.

### Manual Redeploy

**Render:**
- Go to Render Dashboard → Your Service → "Manual Deploy" → "Deploy latest commit"

**Vercel:**
- Go to Vercel Dashboard → Your Project → Deployments → "Redeploy"

## Cost Estimates

### Free Tier (Hobby/Personal Use)

- **Render Free Tier**: $0/month
  - 750 hours/month of compute
  - Spins down after 15 minutes of inactivity
  - Cold starts (30-60 seconds)

- **Vercel Free Tier**: $0/month
  - Unlimited deployments
  - 100 GB bandwidth/month
  - Serverless functions

**Total: $0/month** (Perfect for personal projects and demos)

### Paid Tier (Production Use)

> **Note**: Pricing may change. Check [Render Pricing](https://render.com/pricing) and [Vercel Pricing](https://vercel.com/pricing) for current rates.

- **Render Starter Plan**: ~$7/month (as of 2026)
  - Always-on instance
  - No cold starts
  - 0.5 GB RAM, shared CPU

- **Vercel Pro Plan**: ~$20/month (as of 2026)
  - 1 TB bandwidth/month
  - Advanced analytics
  - Custom domains

**Estimated Total: ~$27/month** (Recommended for production)

## Next Steps

- Review the [Full Deployment Documentation](DEPLOYMENT.md)
- Read the [Security Guidelines](SECURITY.md)
- Check the [Contributing Guide](CONTRIBUTING.md)
- Join our community discussions

## Support

- **Issues**: https://github.com/Arnoldlarry15/red-set-protocell/issues
- **Documentation**: See `docs/` directory
- **Repository**: https://github.com/Arnoldlarry15/red-set-protocell
