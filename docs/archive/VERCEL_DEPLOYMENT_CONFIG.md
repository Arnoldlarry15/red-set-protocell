# Vercel Deployment Configuration

## Overview

This document provides the complete configuration needed to deploy the RSP UI to Vercel successfully.

## Required Environment Variables

The following environment variables must be set in the Vercel dashboard under **Settings → Environment Variables**:

### VITE_API_BASE_URL

**Required**: Yes  
**Description**: The base URL for the RSP backend API  
**Example**: `https://your-backend-url.com` or `http://localhost:8000` for local testing  
**Format**: No trailing slash, no quotes

```
VITE_API_BASE_URL=https://your-backend-url.com
```

### Notes:
- This variable is used by the UI to make API calls to the backend
- For production: Set to your deployed backend URL
- For preview/development: Set to your staging backend or local backend URL
- Vite requires environment variables to be prefixed with `VITE_` to be exposed to the client

## Vercel Configuration (vercel.json)

The `vercel.json` file at the repository root has been simplified for optimal React SPA routing:

### 1. SPA Routing (Simplified)

```json
"rewrites": [
  {
    "source": "/(.*)",
    "destination": "/"
  }
]
```

**Key Changes:**
- Uses `"destination": "/"` instead of `"/index.html"` for better React Router compatibility
- This simpler approach routes everything to root, allowing React Router to handle client-side navigation
- Prevents blank page issues and 404 errors on route refreshes

### 2. Build Configuration

```json
"buildCommand": "cd rsp-ui && npm run build",
"outputDirectory": "rsp-ui/dist",
"installCommand": "cd rsp-ui && npm install",
"framework": "vite"
```

**Important Notes:**
- Only ONE `vercel.json` should exist (at repository root, NOT in `rsp-ui` directory)
- Previous cache control headers have been removed to prevent browser caching from hiding deployment updates
- Configuration is intentionally minimal to avoid conflicts and complexity

## Backend CORS Configuration

For the UI to successfully communicate with the backend, the backend must have CORS enabled:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-app.vercel.app",  # Production URL
        "http://localhost:5173",                # Local development
        "*"                                     # Allow all (dev only)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Important**: Replace `*` with specific origins in production for security.

## Deployment Checklist

Before deploying to Vercel:

- [ ] Set `VITE_API_BASE_URL` in Vercel environment variables
- [ ] Verify `vercel.json` is in repository root
- [ ] Test build locally: `cd rsp-ui && npm run build`
- [ ] Test preview locally: `cd rsp-ui && npm run preview`
- [ ] Ensure backend has CORS configured for frontend domain
- [ ] Verify backend API is accessible from Vercel
- [ ] Test all routes work (no 404s on page refresh)

## Local Testing

To test the production build locally:

```bash
cd rsp-ui
npm run build
npm run preview
```

This will serve the production build on `http://localhost:4173` (or similar).

## Troubleshooting

### Blank Page on Deployment

**Symptom**: UI shows blank page or nothing loads  
**Cause**: Client-side routing not properly configured for Vercel  
**Solution**: 
1. Verify `vercel.json` exists at repository root (not in `rsp-ui/`)
2. Ensure rewrite rule uses `"destination": "/"` (not `"/index.html"`)
3. Confirm only ONE `vercel.json` exists to avoid conflicts
4. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
5. Clear Vercel build cache and redeploy

### 404 Errors on Page Refresh

**Symptom**: Refreshing `/dashboard` or other routes gives 404 or blank page  
**Cause**: SPA rewrite rules not working or incorrectly configured  
**Solution**: 
1. Verify `vercel.json` has simplified rewrite: `"destination": "/"`
2. Ensure BrowserRouter (not HashRouter) is used in App.tsx
3. Check that there's only one `vercel.json` at repository root
4. Redeploy with build cache cleared

### API Calls Fail

**Symptom**: Network errors in browser console  
**Cause**: Missing `VITE_API_BASE_URL` or incorrect CORS  
**Solution**:
1. Set `VITE_API_BASE_URL` in Vercel environment variables
2. Configure backend CORS to allow frontend domain
3. Check Network tab in browser DevTools for specific errors

### Old Code Showing After Deploy

**Symptom**: Changes not visible after deployment  
**Cause**: Browser caching  
**Solution**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

## Production Readiness Features

The UI now includes:

### 1. LiveFeed Component
- ✅ Collapsible attack entries (show/hide details)
- ✅ Copy with redaction (PII, API keys, sensitive data)
- ✅ Metadata visible by default (prompt/response hidden)
- ✅ React.memo for performance optimization

### 2. MetricsPanel Component
- ✅ Tooltips explaining L1, L2, L3 metrics
- ✅ Colorblind-safe palette (distinct hues and patterns)
- ✅ Accessible color combinations
- ✅ React.memo for performance optimization

### 3. Dashboard Component
- ✅ React.memo on child components
- ✅ useCallback for event handlers
- ✅ Clear loading/error states
- ✅ Optimized render performance

### 4. AttackConfig Component
- ✅ Clear defaults
- ✅ Session-scoped controls only
- ⚠️ Confirmation dialogs for destructive actions (if implemented in future)

### 5. WebSocket Hook
- ✅ Production ready with reconnection logic
- ✅ Exponential backoff
- ✅ Memory leak prevention
- ✅ Connection state management

## Next Steps

After successful deployment:

1. Monitor browser console for errors
2. Test all routes and navigation
3. Verify API calls succeed
4. Test WebSocket connectivity (if backend supports it)
5. Validate performance with real data
6. Set up error monitoring (e.g., Sentry)

## Support

For issues or questions:
- Check Vercel deployment logs
- Review browser console for errors
- Verify environment variables are set correctly
- Ensure backend is accessible and CORS is configured
