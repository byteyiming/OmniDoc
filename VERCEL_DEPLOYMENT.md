# Vercel Frontend Deployment Guide

## Overview

This guide explains how to deploy the OmniDoc frontend to Vercel while keeping the backend on Oracle Cloud.

## Architecture

- **Frontend**: Deployed on Vercel (https://omnidoc.info)
- **Backend API**: Deployed on Railway (https://omnidoc-production.up.railway.app)
- **Database**: Neon (managed PostgreSQL)
- **Task Queue**: Upstash Redis

## Prerequisites

1. Vercel account (free tier is sufficient)
2. GitHub repository connected to Vercel
3. Backend API already deployed on Railway (see [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md))

## Deployment Steps

### 1. Connect Repository to Vercel

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Select the repository: `OmniDoc`

### 2. Configure Project Settings

**Framework Preset**: Next.js (auto-detected)

**Root Directory**: `frontend`

**Build Command**: `npm run build` (or `pnpm build` if using pnpm)

**Output Directory**: `.next`

**Install Command**: `npm install` (or `pnpm install`)

### 3. Environment Variables

Add these environment variables in Vercel:

**For Railway default domain:**
```
NEXT_PUBLIC_API_BASE=https://omnidoc-production.up.railway.app
```

**For custom domain (if configured):**
```
NEXT_PUBLIC_API_BASE=https://api.omnidoc.info
```

**How to add in Vercel:**
1. Go to your project → **Settings** → **Environment Variables**
2. Click **"Add New"**
3. Name: `NEXT_PUBLIC_API_BASE`
4. Value: Your Railway backend URL (see above)
5. Select environments: **Production**, **Preview**, **Development**
6. Click **"Save"**
7. **Redeploy** your application for changes to take effect

**Important**: 
- The `NEXT_PUBLIC_` prefix makes the variable available in the browser
- This tells the frontend where to connect to the backend API
- After adding variables, you must redeploy (Vercel won't auto-redeploy)

### 4. Deploy

1. Click "Deploy"
2. Vercel will automatically:
   - Install dependencies
   - Build the Next.js app
   - Deploy to production
   - Provide a preview URL

### 5. Configure Custom Domain

1. Go to Project Settings → Domains
2. Add your domain: `omnidoc.info`
3. Add www subdomain: `www.omnidoc.info`
4. Follow Vercel's DNS instructions:
   - Add CNAME record: `www` → `cname.vercel-dns.com`
   - Add A record: `@` → Vercel's IP addresses (provided by Vercel)

## Backend CORS Configuration

The backend on Railway needs to allow requests from Vercel. Update your Railway Variables:

1. Go to Railway → Your Backend Service → **Variables**
2. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info,https://*.vercel.app
   ```
3. Click **"Update Variables"**
4. Railway will automatically redeploy

This is already configured in `RAILWAY_VARIABLES.txt` - just make sure it's set correctly in Railway.

## Environment Variables Reference

### Required

- `NEXT_PUBLIC_API_BASE`: Backend API URL 
  - Railway default: `https://omnidoc-production.up.railway.app`
  - Custom domain: `https://api.omnidoc.info` (if configured)

### Optional

- `NEXT_PUBLIC_WS_URL`: WebSocket URL (defaults to `NEXT_PUBLIC_API_BASE`)

## Vercel Configuration File

You can also create a `vercel.json` in the `frontend` directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/$1"
    }
  ]
}
```

## Continuous Deployment

Vercel automatically deploys when you push to:
- `main` branch → Production
- Other branches → Preview deployments

Each preview gets a unique URL like: `omnidoc-git-feature-branch.vercel.app`

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Check `ALLOWED_ORIGINS` in backend `.env`
2. Ensure it includes your Vercel domain
3. Restart backend: `sudo systemctl restart omnidoc-backend`

### API Connection Issues

1. Verify `NEXT_PUBLIC_API_BASE` is set correctly in Vercel Environment Variables
2. Check backend is running: Railway → Your Service → **Metrics** or **Logs**
3. Test API directly: 
   ```bash
   curl https://omnidoc-production.up.railway.app/health
   ```
4. Make sure you **redeployed** after adding environment variables
5. Check browser console for CORS errors

### Build Failures

1. Check build logs in Vercel dashboard
2. Ensure all dependencies are in `package.json`
3. Verify Node.js version (Vercel auto-detects, but you can specify in `package.json`)

## Monitoring

- **Vercel Dashboard**: View deployments, logs, and analytics
- **Vercel CLI**: `vercel logs` for real-time logs
- **Backend Logs**: Railway → Your Service → **Logs** tab

## Cost

**Vercel Free Tier includes:**
- 100GB bandwidth/month
- Unlimited requests
- Automatic SSL
- Preview deployments
- Custom domains

This is more than enough for most projects!

## Next Steps

1. Deploy frontend to Vercel
2. Update backend CORS settings
3. Configure custom domain
4. Test end-to-end functionality

## Support

- Vercel Docs: https://vercel.com/docs
- Vercel Discord: https://vercel.com/discord
- OmniDoc Issues: GitHub Issues

