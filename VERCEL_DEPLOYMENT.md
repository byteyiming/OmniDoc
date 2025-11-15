# Vercel Frontend Deployment Guide

## Overview

This guide explains how to deploy the OmniDoc frontend to Vercel while keeping the backend on Oracle Cloud.

## Architecture

- **Frontend**: Deployed on Vercel (https://omnidoc.info)
- **Backend API**: Deployed on Oracle Cloud (https://api.omnidoc.info)
- **Database**: Neon (managed PostgreSQL)
- **Task Queue**: Redis on Oracle Cloud

## Prerequisites

1. Vercel account (free tier is sufficient)
2. GitHub repository connected to Vercel
3. Backend API already deployed on Oracle Cloud

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

```
NEXT_PUBLIC_API_BASE=https://api.omnidoc.info
```

**Important**: 
- The `NEXT_PUBLIC_` prefix makes the variable available in the browser
- This tells the frontend where to connect to the backend API

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

The backend on Oracle Cloud needs to allow requests from Vercel. Update your `.env` file on the server:

```bash
ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info,https://*.vercel.app
```

Or if you want to allow all Vercel preview deployments:

```bash
ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info,https://*.vercel.app,https://*.vercel-dns.com
```

After updating, restart the backend:

```bash
sudo systemctl restart omnidoc-backend
```

## Environment Variables Reference

### Required

- `NEXT_PUBLIC_API_BASE`: Backend API URL (e.g., `https://api.omnidoc.info`)

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

1. Verify `NEXT_PUBLIC_API_BASE` is set correctly in Vercel
2. Check backend is running: `sudo systemctl status omnidoc-backend`
3. Test API directly: `curl https://api.omnidoc.info/health`

### Build Failures

1. Check build logs in Vercel dashboard
2. Ensure all dependencies are in `package.json`
3. Verify Node.js version (Vercel auto-detects, but you can specify in `package.json`)

## Monitoring

- **Vercel Dashboard**: View deployments, logs, and analytics
- **Vercel CLI**: `vercel logs` for real-time logs
- **Backend Logs**: `sudo journalctl -u omnidoc-backend -f`

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

