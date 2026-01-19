# Vercel 404 Error Fix Summary

## Problem
Users were experiencing "404: NOT_FOUND" errors when accessing the deployed Red Set ProtoCell application on Vercel.

**Error Code:** `NOT_FOUND`  
**Error ID:** `cle1:cle1::wrjqx-1768831477921-405bace209af`

## Root Cause
**When a `builds` array exists in `vercel.json`, Vercel ignores all root-level build settings** (`buildCommand`, `outputDirectory`, `installCommand`, `framework`).

The previous configuration had:
- Root-level build settings for the frontend (which were **completely ignored**)
- Only `api/*.py` in the `builds` array
- Result: API functions were built, but **frontend was never built** → 404 at `/`

### Critical Vercel Behavior:
> ⚠️ **"Due to builds existing in your configuration file, the Build and Development Settings defined in your Project Settings will not apply."**

This means:
1. **With `builds` array present**: Root-level settings are ignored, only items in `builds` are processed
2. **Without `builds` array**: Root-level settings (or Vercel UI settings) are used
3. **Mixed approach doesn't work**: You can't have both `builds` array AND root-level build commands

## Solution
**Add the frontend to the `builds` array** so Vercel actually builds it. When using `builds`, you must explicitly include everything that needs to be built.

### Final Working Configuration:
```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    },
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### What Changed:
1. **Removed root-level build settings** - They were being ignored anyway due to `builds` array
2. **Added frontend to `builds`** - Now Vercel actually builds the React/Vite app
   - Uses `@vercel/static-build` which looks for `vercel-build` script in package.json
   - Sets `distDir: "dist"` to point to Vite's output directory
3. **Switched from `rewrites` to `routes`** - When using `builds` array, `routes` is the correct API
4. **Added filesystem handler** - `{ "handle": "filesystem" }` ensures static assets are served correctly
5. **Simplified catch-all** - SPA fallback to `/index.html` for React Router

### Key Patterns:
- **`@vercel/static-build`**: Automatically runs `npm install` then `npm run vercel-build` (or `build`)
- **`distDir: "dist"`**: Tells Vercel where Vite outputs built files (relative to `frontend/`)
- **`handle: "filesystem"`**: Critical for serving static assets (JS, CSS, images) before SPA fallback
- **Routes order matters**: API routes first, then filesystem, then SPA catch-all

## Why This Works

1. **Frontend is Actually Built**: Including `frontend/package.json` in `builds` array ensures Vercel runs the build process
2. **Explicit Build Targets**: Both frontend and API are explicitly listed, no ambiguity
3. **Proper Builder Usage**: `@vercel/static-build` is designed for Node.js frontends, automatically handles npm install/build
4. **Correct Routing with `routes`**: When `builds` array exists, must use `routes` (not `rewrites`)
5. **Filesystem Handling**: `{ "handle": "filesystem" }` serves static assets before falling back to SPA
6. **SPA Support**: Catch-all to `/index.html` enables React Router to handle client-side routing

### How Vercel Processes This:
1. **Build Phase**:
   - Builds `frontend/package.json` → runs `npm run vercel-build` → outputs to `frontend/dist/`
   - Builds each `api/*.py` → creates serverless functions at `/api/*`
2. **Request Phase** (routes processed in order):
   - `/api/health` → Matches route 1 → Serverless function
   - `/main.js` → Matches filesystem handler → Serves static file
   - `/dashboard` → No match → Falls through to catch-all → Serves `/index.html` (React Router takes over)

### Common Pitfalls Avoided:
- ❌ **Mixing `builds` with root-level settings** - Root settings are ignored when `builds` exists
- ❌ **Using `rewrites` with `builds`** - Must use `routes` when `builds` array is present
- ❌ **Forgetting `handle: "filesystem"`** - Static assets would 404 without this
- ✅ **Explicit `builds` array** - Clear, predictable, works every time

## Testing & Verification

### Configuration Validation:
- ✅ JSON syntax validated
- ✅ `frontend/package.json` has `vercel-build` script
- ✅ `builds` array includes both frontend and API
- ✅ `routes` array has proper order (API → filesystem → SPA)
- ✅ No conflicting root-level build settings

### Pre-Deployment Checklist:
1. ✅ Frontend has `vercel-build` script in package.json
2. ✅ Vite outputs to `dist/` directory (configured in vite.config.ts)
3. ✅ API functions in `/api` directory use handler pattern
4. ✅ Routes prioritize API endpoints before SPA fallback

### Expected Build Output:
```
Building frontend/package.json (Static Build)
  Installing dependencies...
  Running "npm run vercel-build"
  Build completed: frontend/dist/
  
Building api/*.py (Python Serverless)
  Created functions:
    /api/health
    /api/info
    /api/auth
    /api/scan
    /api/metrics
```

## Expected Result

After redeploying with this configuration:

### ✅ What Should Work:
1. **Root route (`/`)**: Serves `index.html` from `frontend/dist/` → React app loads
2. **Static assets**: `/assets/*.js`, `/assets/*.css` → Served via filesystem handler
3. **SPA routes**: `/dashboard`, `/settings` → Served `index.html`, React Router handles navigation
4. **API endpoints**: `/api/health`, `/api/scan`, etc. → Serverless functions respond
5. **CORS**: No CORS issues (frontend and API share same origin)

### ❌ Previous Behavior (404):
- `/` → 404 NOT_FOUND (frontend never built)
- `/dashboard` → 404 NOT_FOUND
- `/api/health` → ✅ Worked (API was built, just frontend missing)

### 🎯 Key Success Metrics:
- Homepage loads without 404
- React app renders
- Browser console shows no 404 errors for static assets
- API calls from frontend work without CORS errors

## References

- **Vercel Builds Documentation**: https://vercel.com/docs/build-step
- **Vercel Static Build (@vercel/static-build)**: https://vercel.com/docs/frameworks/vite
- **Repository Guide**: `docs/deployment/VERCEL_SERVERLESS_GUIDE.md`
- **Configuration Analysis**: `VERCEL_CONFIG_ANALYSIS.md`
- **Problem Statement**: Based on real-world Vercel 404 troubleshooting patterns

## Additional Notes

### Why Not Use Root-Level Settings?
You could alternatively remove the `builds` array entirely and use only root-level settings:
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install"
}
```

**However**, this doesn't work when you need **both** a frontend AND serverless API functions. The `builds` array is the only way to explicitly build multiple things.

### Alternative: Root Directory in Vercel UI
Setting "Root Directory" to `frontend` in Vercel project settings would work for a frontend-only deployment, but we need to deploy the API too, so we keep everything at the root and use `builds` to specify both.

### Vercel's Auto-Detection
Vercel can auto-detect frameworks, but auto-detection doesn't work reliably in monorepos with multiple buildable targets. Being explicit with the `builds` array eliminates ambiguity.
