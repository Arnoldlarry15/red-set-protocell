# Vercel Deployment Guide

> **⚠️ ARCHIVED DOCUMENTATION - OUTDATED**
> 
> This guide references the **old FastAPI monolith architecture** and is kept for historical reference only.
> 
> **For current deployment:** See [`/docs/deployment/VERCEL_SERVERLESS_GUIDE.md`](/docs/deployment/VERCEL_SERVERLESS_GUIDE.md)
> 
> **Issues with this guide:**
> - Routes to `/backend/main.py` (FastAPI monolith) instead of `/api/*.py` (serverless functions)
> - Uses deprecated Vercel function pattern for FastAPI
> - Configuration shown here conflicts with current `/vercel.json` at repository root

---

## Repository Structure

The repository has been reorganized for Vercel deployment:

```
/
├── frontend/          ← React/Vite frontend (formerly rsp-ui)
├── backend/          ← FastAPI Python backend (formerly rsp-core/backend)
└── vercel.json       ← Vercel configuration
```

## Deployment Steps

### 1. Connect Repository to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your Git repository
4. Vercel will automatically detect the `vercel.json` configuration

### 2. Configure Environment Variables

In the Vercel Dashboard, go to **Project Settings → Environment Variables** and add:

#### Frontend Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_BASE_URL` | `/api` or `https://your-domain.vercel.app/api` | API endpoint URL. Use `/api` for relative path (recommended) or full URL with your Vercel domain |

**Recommended**: Use `/api` to take advantage of Vercel's routing and avoid CORS issues.

#### Backend Environment Variables (Optional - for production security)

| Variable | Value | Description |
|----------|-------|-------------|
| `RSP_ENVIRONMENT` | `production` | Enables production security validations |
| `RSP_ALLOWED_ORIGINS` | `https://your-domain.vercel.app` | CORS allowed origins (comma-separated) |
| `RSP_JWT_SECRET` | `your-secret-key-here` | JWT secret key (32+ characters) |
| `RSP_REQUIRE_AUTH` | `true` | Enable authentication |
| `RSP_DEMO_PASSWORD` | `your-secure-password` | Change from default |

**Important**: Replace `your-domain.vercel.app` with your actual Vercel deployment domain.

### 3. Deploy

Click "Deploy" - Vercel will:
1. Build the frontend using `npm run build` in the `frontend/` directory
2. Package the backend Python code as serverless functions
3. Set up routing:
   - `/api/*` → backend/main.py (FastAPI)
   - `/*` → frontend SPA (React)

## How It Works

### vercel.json Configuration

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/backend/main.py"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/backend/main.py"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "functions": {
    "backend/main.py": {
      "runtime": "python3.9"
    }
  }
}
```

- **buildCommand**: Builds the frontend React/Vite application
- **outputDirectory**: Where Vercel finds the built frontend files
- **rewrites**: Maps `/api/*` requests to the backend (for development preview)
- **routes**: 
  - API requests (`/api/*`) go to the FastAPI backend
  - Static files are served first (filesystem)
  - All other requests go to the SPA (for client-side routing)

### Backend Entry Point

The `backend/main.py` file exports the FastAPI app instance that Vercel needs:

```python
from app.api_server import app  # Vercel looks for 'app' variable
```

### Frontend API Configuration

The frontend uses `VITE_API_BASE_URL` environment variable to know where to make API requests:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

## Local Development

For local development, the structure is the same:

```bash
# Terminal 1: Start backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.api_server:app --reload

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

Or use the provided script:

```bash
./start-ui.sh
```

## Troubleshooting

### Frontend can't reach backend

1. Verify `VITE_API_BASE_URL` is set correctly in Vercel environment variables
2. Check that the value includes `/api` at the end (e.g., `https://your-domain.vercel.app/api`)
3. Rebuild and redeploy after changing environment variables

### CORS errors

1. Set `RSP_ALLOWED_ORIGINS` in Vercel environment variables to your Vercel domain
2. For development, you can set `RSP_ENVIRONMENT=development` to allow localhost origins

### Backend not responding

1. Check Vercel function logs in the dashboard
2. Verify `backend/main.py` exports an `app` variable
3. Ensure all Python dependencies are in `backend/requirements.txt`

## Production Security Checklist

- [ ] Set `RSP_ENVIRONMENT=production`
- [ ] Configure `RSP_ALLOWED_ORIGINS` with your domain
- [ ] Set a strong `RSP_JWT_SECRET` (32+ characters)
- [ ] Change `RSP_DEMO_PASSWORD` from default
- [ ] Set `RSP_REQUIRE_AUTH=true`
- [ ] Review and configure rate limits if needed

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/vercel/)
