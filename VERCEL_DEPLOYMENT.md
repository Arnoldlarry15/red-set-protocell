# Deploying RSP UI to Vercel

This guide walks you through deploying the Red Set ProtoCell Web UI to Vercel.

## Prerequisites

- A [Vercel account](https://vercel.com/signup) (free tier works!)
- [Vercel CLI](https://vercel.com/docs/cli) installed (optional, for command-line deployment)

## Deployment Methods

### Method 1: Deploy via Vercel Dashboard (Recommended)

This is the easiest method and doesn't require any command-line tools.

1. **Push your code to GitHub** (if not already done)
   
2. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
   - Sign in with your GitHub account
   
3. **Click "Add New..." → "Project"**

4. **Import your GitHub repository**
   - Select `Arnoldlarry15/red-set-protocell`
   - Click "Import"

5. **Configure the project**
   - **Framework Preset**: Select "Vite"
   - **Root Directory**: Click "Edit" and set to `rsp-ui`
   - **Build Command**: `npm run build` (should be auto-detected)
   - **Output Directory**: `dist` (should be auto-detected)
   - **Install Command**: `npm install` (should be auto-detected)

6. **Add Environment Variables** (if needed in the future)
   - You can add environment variables later in the project settings
   - For now, the app works without backend variables for frontend-only deployment

7. **Click "Deploy"**
   - Vercel will build and deploy your application
   - This typically takes 1-2 minutes

8. **Access your deployed app**
   - Once deployment completes, you'll get a URL like `https://your-project.vercel.app`
   - Click on the URL to view your deployed application

### Method 2: Deploy via Vercel CLI

If you prefer using the command line:

1. **Install Vercel CLI globally**
   ```bash
   npm install -g vercel
   ```

2. **Navigate to the rsp-ui directory**
   ```bash
   cd rsp-ui
   ```

3. **Login to Vercel**
   ```bash
   vercel login
   ```

4. **Deploy to Vercel**
   
   For production deployment:
   ```bash
   vercel --prod
   ```
   
   For preview deployment (testing):
   ```bash
   vercel
   ```

5. **Follow the prompts**
   - Set up and deploy: Y
   - Which scope: Select your account
   - Link to existing project: N (for first deployment)
   - Project name: Press Enter to accept default or enter custom name
   - Directory: Press Enter (it will use current directory)
   - Override settings: N (use vercel.json configuration)

6. **Access your deployed app**
   - The CLI will output the deployment URL
   - Example: `https://rsp-ui-xyz.vercel.app`

## Post-Deployment Configuration

### Custom Domain (Optional)

1. Go to your project in Vercel Dashboard
2. Navigate to "Settings" → "Domains"
3. Add your custom domain
4. Follow Vercel's instructions to configure DNS

### Environment Variables (For Backend Integration)

If you need to add environment variables later:

1. Go to your project in Vercel Dashboard
2. Navigate to "Settings" → "Environment Variables"
3. Add variables like:
   - `VITE_API_BASE_URL` - Backend API URL (if deploying backend separately)
   - Any other configuration variables

Note: In Vite, environment variables must be prefixed with `VITE_` to be exposed to the client.

## Backend API Deployment (Separate)

The UI currently uses mock data for demonstration. To connect to a real backend:

1. **Deploy the FastAPI backend** separately (e.g., on Railway, Render, or Fly.io)
2. **Update the API base URL** in the frontend code or via environment variables
3. **Redeploy the frontend** with the new backend URL

## Continuous Deployment

Vercel automatically sets up continuous deployment:

- **Main branch**: Commits to `main` branch trigger production deployments
- **Other branches**: Commits to other branches create preview deployments
- **Pull Requests**: Each PR gets its own preview URL for testing

## Vercel Configuration

The `vercel.json` file in the `rsp-ui` directory contains:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

Key features:
- **SPA Routing**: All routes redirect to `index.html` for client-side routing
- **Asset Caching**: Static assets are cached for 1 year
- **Framework Detection**: Vercel automatically detects Vite configuration

## Troubleshooting

### Build Fails

**Issue**: Build fails with TypeScript errors

**Solution**: Run `npm run build` locally first to catch errors:
```bash
cd rsp-ui
npm install
npm run build
```

### App Shows Blank Page

**Issue**: Deployed app shows a blank page

**Solution**: 
1. Check the browser console for errors
2. Verify the `vercel.json` rewrites are correct
3. Ensure `dist` folder was generated correctly

### Routing Not Working

**Issue**: Direct navigation to routes (e.g., `/dashboard`) returns 404

**Solution**: The `vercel.json` rewrites should handle this. If not:
1. Verify `vercel.json` exists in the `rsp-ui` directory
2. Check that rewrites are properly configured
3. Redeploy after making changes

### Assets Not Loading

**Issue**: Images or assets fail to load

**Solution**:
1. Ensure assets are in the `public` folder
2. Use root-relative paths (e.g., `/logo.png` not `./logo.png`)
3. Check the `dist` folder contains all assets after build

## Performance Optimization

For better performance:

1. **Enable Edge Caching**: Already configured in `vercel.json`
2. **Use Vercel Analytics**: Enable in project settings
3. **Optimize Images**: Use WebP format and appropriate sizes
4. **Code Splitting**: Vite handles this automatically

## Monitoring

Monitor your deployment:

1. **Vercel Dashboard**: View deployment logs and analytics
2. **Real-time Logs**: Use `vercel logs` CLI command
3. **Performance Metrics**: Enable Vercel Analytics in project settings

## Cost

- **Hobby (Free) Tier**: Suitable for personal projects and demos
  - 100 GB bandwidth per month
  - Unlimited deployments
  - Preview deployments for all branches

- **Pro Tier**: For production applications
  - 1 TB bandwidth per month
  - Advanced analytics
  - Custom deployment protection

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vite Documentation](https://vitejs.dev/)
- [Project Issues](https://github.com/Arnoldlarry15/red-set-protocell/issues)

## Next Steps

After deployment:

1. ✅ Test all routes and functionality
2. ✅ Set up custom domain (optional)
3. ✅ Configure backend API endpoint
4. ✅ Enable analytics and monitoring
5. ✅ Share your deployment URL!

---

**Deployment Status**: Ready to deploy! 🚀

Your Red Set ProtoCell Web UI is now configured for Vercel deployment.
