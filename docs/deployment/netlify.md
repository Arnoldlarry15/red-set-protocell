# Netlify Deployment Guide

## Overview

Red Set ProtoCell supports deployment on **Netlify** using serverless Python functions. This guide explains how to deploy the application to Netlify's platform.

Netlify provides:
- ✅ Static frontend hosting
- ✅ Serverless Python functions (AWS Lambda-based)
- ✅ Auto-scaling and pay-per-request pricing
- ✅ Clearer function boundaries than some alternatives
- ✅ Easier debugging with explicit function files

## Architecture

### The Netlify Mental Model

Netlify splits the world into two parts:

1. **Static Frontend**: Built with React + Vite, served from `frontend/dist`
2. **Serverless Functions**: Python functions in `netlify/functions/`

Each file in `netlify/functions/` becomes one endpoint. No Flask server, no background processes. Same constraints as Vercel, fewer abstractions.

### Repository Structure

```
/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── netlify/
│   └── functions/
│       ├── health.py
│       ├── auth.py
│       └── scan.py
│
├── netlify.toml
└── requirements.txt
```

This structure coexists with Vercel support. Nothing conflicts.

## Netlify Function Pattern

### Handler Format

Netlify expects Python functions with this signature:

```python
import json

def handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "status": "ok",
            "service": "Red Set ProtoCell"
        })
    }
```

Key points:
- Function named `handler(event, context)`
- Returns a dictionary response
- Body must be JSON serialized

### Event Object

The `event` object contains:
- `httpMethod`: GET, POST, OPTIONS, etc.
- `headers`: Request headers
- `body`: Raw request body (string)
- `queryStringParameters`: Query parameters

### Example: Health Check

```python
# netlify/functions/health.py
import json

def handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "status": "ok",
            "service": "Red Set ProtoCell"
        })
    }
```

### Example: POST Handler with CORS

```python
# netlify/functions/auth.py
import json

def handler(event, context):
    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }
    
    # Handle POST request
    if event.get("httpMethod") != "POST":
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }
    
    # Parse request body
    body = json.loads(event.get("body", "{}"))
    
    # Process request and return response
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"result": "success"})
    }
```

## API Paths

### Function URLs

Each file becomes an endpoint:

- **File**: `netlify/functions/health.py` → **URL**: `/.netlify/functions/health`
- **File**: `netlify/functions/auth.py` → **URL**: `/.netlify/functions/auth`
- **File**: `netlify/functions/scan.py` → **URL**: `/.netlify/functions/scan`

### API Compatibility Redirect

The `netlify.toml` includes a redirect rule for API compatibility:

```toml
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

This allows you to call:
```javascript
// Both work:
await fetch("/.netlify/functions/health");
await fetch("/api/health");  // Redirects to /.netlify/functions/health
```

This makes Vercel and Netlify share the same API shape. **That's developer empathy.**

## Configuration: netlify.toml

The `netlify.toml` file at the repository root configures the deployment:

```toml
[build]
  base = "/"
  publish = "frontend/dist"
  command = "cd frontend && npm install && npm run build"

[functions]
  directory = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### Configuration Explained

- `[build]`: Frontend build configuration
  - `base`: Repository root
  - `publish`: Output directory for static files
  - `command`: Build command for frontend
- `[functions]`: Serverless functions configuration
  - `directory`: Location of Python functions
- `[[redirects]]`: URL rewrite rules
  - Maps `/api/*` to `/.netlify/functions/*`

## Environment Variables

### Required Variables

Set these in **Netlify Dashboard → Site Settings → Environment Variables**:

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

### Accessing Environment Variables

In Python functions:

```python
import os

JWT_SECRET = os.environ.get("JWT_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
```

Identical to Vercel.

## Deployment Methods

### Method 1: Netlify Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done)

2. **Go to [Netlify Dashboard](https://app.netlify.com/)**

3. **Click "Add new site" → "Import an existing project"**

4. **Connect to GitHub and select your repository**
   - Repository: `Arnoldlarry15/red-set-protocell`

5. **Configure build settings** (should auto-detect from netlify.toml):
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`
   - Functions directory: `netlify/functions`

6. **Set environment variables**:
   - Go to Site Settings → Environment Variables
   - Add required variables (see above)

7. **Deploy!**
   - Click "Deploy site"
   - Your app will be live at `https://your-site.netlify.app`

### Method 2: Netlify CLI

Install and use the Netlify CLI for command-line deployment:

```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize Netlify for your project (from repository root)
netlify init

# Follow the prompts:
# - Framework: Vite
# - Build command: cd frontend && npm install && npm run build
# - Publish directory: frontend/dist
# - Functions folder: netlify/functions

# Deploy to production
netlify deploy --prod
```

### Method 3: Continuous Deployment

Netlify automatically deploys when you push to your connected Git branch:

```bash
# Make changes
git add .
git commit -m "Update application"
git push origin main

# Netlify automatically builds and deploys
```

## Frontend API Calls

From React components, call the API:

```javascript
// Using /.netlify/functions path
const res = await fetch("/.netlify/functions/health");
const data = await res.json();

// Or using /api path (via redirect)
const res = await fetch("/api/health");
const data = await res.json();
```

Both work identically due to the redirect rule.

## Verifying Deployment

After deployment, test your endpoints:

```bash
# Health check
curl https://your-site.netlify.app/api/health

# Authentication
curl -X POST https://your-site.netlify.app/api/auth \
  -H "Content-Type: application/json" \
  -d '{"password":"your-password"}'

# Scan endpoint
curl -X POST https://your-site.netlify.app/api/scan \
  -H "Content-Type: application/json" \
  -d '{"backend":"openai","rounds":10}'
```

## What Netlify Does Better Than Vercel

I'll be blunt:

✅ **Advantages:**
- No hidden routing state
- Clearer function boundaries
- Easier debugging
- Fewer "trust us" abstractions
- More explicit configuration

❌ **Disadvantages:**
- Cold starts slightly slower
- Python support is less glamorized
- Fewer edge features

For Red Set ProtoCell, **Netlify is a perfectly legitimate first-class home.**

## Troubleshooting

### Function Doesn't Work

1. **Check function logs**:
   - Netlify Dashboard → Functions → Select function → View logs

2. **Verify handler signature**:
   ```python
   def handler(event, context):  # Must be named "handler"
       return {"statusCode": 200, ...}
   ```

3. **Check Python dependencies**:
   - Ensure `requirements.txt` is at repository root
   - Test locally: `pip install -r requirements.txt`

### CORS Issues

Ensure all responses include CORS headers:

```python
"headers": {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json"
}
```

And handle OPTIONS requests:

```python
if event.get("httpMethod") == "OPTIONS":
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        },
        "body": ""
    }
```

### Build Fails

1. **Check build logs** in Netlify Dashboard
2. **Verify frontend builds locally**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
3. **Check netlify.toml syntax**

### Environment Variables Not Working

1. **Verify variables are set** in Site Settings → Environment Variables
2. **Redeploy** after adding variables (changes require rebuild)
3. **Check variable names** (case-sensitive)

## Comparison: Netlify vs Vercel

Both platforms support Red Set ProtoCell with identical functionality:

| Feature | Netlify | Vercel |
|---------|---------|--------|
| Static Hosting | ✅ | ✅ |
| Serverless Functions | ✅ (AWS Lambda) | ✅ (AWS Lambda) |
| Python Support | ✅ | ✅ |
| Auto-scaling | ✅ | ✅ |
| Free Tier | ✅ Generous | ✅ Generous |
| Environment Variables | ✅ | ✅ |
| Custom Domains | ✅ | ✅ |
| API Structure | `/.netlify/functions/*` | `/api/*` |
| Configuration | `netlify.toml` | `vercel.json` |
| Cold Starts | ~1-2s | ~0.5-1s |
| Debugging | Clearer | More abstracted |

**Choose based on your preference. Both work great.**

## Next Steps

After deployment:

1. **Test all endpoints** using curl or Postman
2. **Set up custom domain** (if desired)
3. **Configure monitoring** using Netlify's built-in analytics
4. **Enable automatic deployments** from your Git branch
5. **Review logs** regularly for errors

## Support

- **Netlify Docs**: https://docs.netlify.com/
- **Netlify Functions**: https://docs.netlify.com/functions/overview/
- **Netlify Community**: https://answers.netlify.com/

## No Vendor Lock-In

Red Set ProtoCell supports both Vercel and Netlify using the same codebase. Choose what works best for you, or use both! 🚀
