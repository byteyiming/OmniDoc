# Custom Domain Setup Guide

This guide explains how to configure custom domains for both frontend (Vercel) and backend (Railway).

## 🌐 Domain Architecture

- **Frontend**: `https://omnidoc.info` (Vercel)
- **Backend API**: `https://api.omnidoc.info` (Railway)

## 📋 Frontend Domain (Vercel)

### Step 1: Add Domain in Vercel

1. Go to your Vercel project → **Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain: `omnidoc.info`
4. Click **"Add"**
5. Vercel will show DNS configuration instructions

### Step 2: Configure DNS (Hostinger Example)

**For root domain (`omnidoc.info`):**

1. Log into Hostinger DNS management
2. Add DNS records as instructed by Vercel:

**Option A - A Record (Recommended):**
```
Type: A
Name: @
Value: 76.76.21.21 (Vercel's IP - check Vercel dashboard for current IP)
TTL: 3600
```

**Option B - CNAME (Alternative):**
```
Type: CNAME
Name: @
Value: cname.vercel-dns.com
TTL: 3600
```

**For www subdomain (`www.omnidoc.info`):**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
TTL: 3600
```

### Step 3: Wait for DNS Propagation

- DNS changes can take up to 24-48 hours
- Usually propagates within 1-2 hours
- Check status: https://dnschecker.org

### Step 4: SSL Certificate

Vercel automatically provisions SSL certificates via Let's Encrypt:
- Automatic
- Auto-renewal
- No action needed

### Step 5: Update Environment Variables

After domain is live, update Vercel environment variables:

```
NEXT_PUBLIC_API_BASE=https://api.omnidoc.info
```

Don't forget to **redeploy** after updating!

## 🔧 Backend Domain (Railway)

### Step 1: Add Custom Domain in Railway

1. Go to Railway → Your Backend Service → **Settings** → **Domains**
2. Click **"Custom Domain"**
3. Enter: `api.omnidoc.info`
4. Click **"Add"**
5. Railway will show DNS configuration

### Step 2: Configure DNS

**Add A Record for API subdomain:**

1. Log into Hostinger DNS management
2. Add record:

```
Type: A
Name: api
Value: [Railway's IP address - shown in Railway dashboard]
TTL: 3600
```

**OR use CNAME (if Railway provides):**

```
Type: CNAME
Name: api
Value: [Railway's CNAME - shown in Railway dashboard]
TTL: 3600
```

### Step 3: Wait for DNS Propagation

- Check DNS propagation: https://dnschecker.org
- Railway will automatically provision SSL certificate
- Status will show "Active" when ready

### Step 4: Update Backend CORS Settings

Update Railway Variables:

1. Go to Railway → Your Backend Service → **Variables**
2. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info,https://*.vercel.app
   ```
3. Click **"Update Variables"**

### Step 5: Update Frontend Environment Variable

In Vercel, update:

```
NEXT_PUBLIC_API_BASE=https://api.omnidoc.info
```

**Redeploy** frontend after updating!

## ✅ Verification

### Frontend
```bash
# Should return 200 OK
curl -I https://omnidoc.info

# Should redirect to HTTPS
curl -I http://omnidoc.info
```

### Backend
```bash
# Health check
curl https://api.omnidoc.info/health

# API docs
open https://api.omnidoc.info/docs
```

### CORS Test
Open browser console on `https://omnidoc.info` and check for CORS errors when calling the API.

## 🔍 Troubleshooting

### DNS Not Propagating

1. **Check DNS records are correct:**
   ```bash
   dig omnidoc.info
   dig api.omnidoc.info
   ```

2. **Clear DNS cache:**
   ```bash
   # macOS
   sudo dscacheutil -flushcache
   
   # Windows
   ipconfig /flushdns
   ```

3. **Wait longer** - DNS can take 24-48 hours

### SSL Certificate Issues

- **Vercel**: SSL is automatic - wait for domain verification
- **Railway**: SSL is automatic - check domain status in Railway dashboard

### CORS Errors

1. Check `ALLOWED_ORIGINS` in Railway includes your frontend domain
2. Make sure no trailing slash in `NEXT_PUBLIC_API_BASE`
3. Check browser console for exact error message

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_API_BASE` is set correctly in Vercel
2. **Redeploy frontend** after changing environment variables
3. Test backend directly: `curl https://api.omnidoc.info/health`

## 📝 Complete DNS Configuration Example

For Hostinger, your DNS records should look like:

```
Type    Name    Value                        TTL
A       @       76.76.21.21                  3600
CNAME   www     cname.vercel-dns.com         3600
A       api     [Railway IP]                 3600
```

## 🔗 Related Documentation

- [Vercel Deployment](VERCEL_DEPLOYMENT.md)
- [Railway Deployment](RAILWAY_DEPLOYMENT.md)
- [Production Domain](PRODUCTION_DOMAIN.md)

