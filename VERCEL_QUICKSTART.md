# Quick Start: Deploy RSP UI to Vercel

Get your Red Set ProtoCell Web UI live in under 5 minutes!

## 🚀 Super Quick Deploy (No CLI Required)

### Step 1: Prepare Your Repository
Make sure your code is pushed to GitHub. ✅

### Step 2: Deploy to Vercel

1. **Click this button** or visit [vercel.com/new](https://vercel.com/new)

   [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Arnoldlarry15/red-set-protocell&project-name=rsp-ui&root-directory=rsp-ui)

2. **Sign in with GitHub**
   - Authorize Vercel to access your repositories

3. **Import the Repository**
   - Select `Arnoldlarry15/red-set-protocell`
   - Click "Import"

4. **Configure Project Settings**
   ```
   Framework Preset: Vite
   Root Directory: rsp-ui (IMPORTANT!)
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

5. **Click "Deploy"**
   - ☕ Wait 1-2 minutes for the build to complete
   - 🎉 Your app is live!

### Step 3: Access Your App

Once deployed, you'll get a URL like:
```
https://rsp-ui-xyz.vercel.app
```

Click on it to view your deployed Red Set ProtoCell dashboard!

## 🎯 What You Get

After deployment, your live app includes:

- ✅ **Authentication Page** - API key validation interface
- ✅ **Live Dashboard** - Real-time attack monitoring
- ✅ **Admin Panel** - Session management and analytics
- ✅ **Interactive UI** - Full glassmorphism design
- ✅ **Automatic HTTPS** - Secure by default
- ✅ **Global CDN** - Fast loading worldwide

## 📋 Configuration (Optional)

### Custom Domain

1. Go to your project in Vercel dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain (e.g., `rsp.yourdomain.com`)
4. Follow the DNS setup instructions

### Environment Variables

Currently not needed for frontend-only deployment. Add later if connecting to backend:

1. Go to "Settings" → "Environment Variables"
2. Add variables like `VITE_API_BASE_URL`
3. Redeploy to apply changes

## 🔄 Continuous Deployment

Vercel automatically deploys when you push to GitHub:

- **Main branch** → Production deployment
- **Feature branches** → Preview deployments
- **Pull requests** → Unique preview URLs

No configuration needed - it just works!

## 📱 Share Your Deployment

Your app is now live! Share it with:

```
🚀 Red Set ProtoCell Dashboard
🔗 https://your-project.vercel.app
🛡️ Autonomous AI Red Teaming System
```

## 🛠️ Troubleshooting

### Build Failed?
- Check that `rsp-ui` is set as the root directory
- Verify the build command is `npm run build`
- Check deployment logs in Vercel dashboard

### Blank Page?
- Check browser console for errors
- Verify assets are loading correctly
- Try a hard refresh (Ctrl+F5 or Cmd+Shift+R)

### Need Help?
- See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed guide
- Check [Vercel Documentation](https://vercel.com/docs)
- Open an issue on GitHub

## 🎓 Next Steps

1. **Test your deployment**
   - Try logging in with different backends
   - Test all dashboard features
   - Check mobile responsiveness

2. **Customize**
   - Add your logo (replace `/public/logo.png`)
   - Modify colors in CSS
   - Add custom domains

3. **Connect Backend** (optional)
   - Deploy FastAPI backend separately
   - Configure API endpoint
   - Enable real-time features

4. **Monitor**
   - Enable Vercel Analytics
   - Set up alerts
   - Monitor performance

## 💡 Pro Tips

- **Preview Deployments**: Every branch gets a preview URL
- **Rollbacks**: Easy rollback to previous deployments
- **Environment Branches**: Different configs for staging/production
- **Team Collaboration**: Invite team members in Vercel

---

**That's it!** Your Red Set ProtoCell Web UI is now live on Vercel! 🎉

For more details, see the complete [deployment guide](VERCEL_DEPLOYMENT.md).
