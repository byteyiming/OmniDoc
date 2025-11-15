# Production Domain Configuration

## 🌐 Production Domain

**Main Domain:** `https://omnidoc.info/`

**API Subdomain:** `https://api.omnidoc.info/`

## 📋 Domain Configuration

### Frontend
- **Production URL:** `https://omnidoc.info`
- **WWW Redirect:** `https://www.omnidoc.info` → `https://omnidoc.info`

### Backend API
- **Production URL:** `https://api.omnidoc.info`
- **API Documentation:** `https://api.omnidoc.info/docs`
- **WebSocket:** `wss://api.omnidoc.info/ws/{project_id}`

## 🔧 Configuration Files

### Environment Variables

**Backend `.env`:**
```bash
ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info
ENVIRONMENT=prod
```

**Frontend `.env.local`:**
```bash
NEXT_PUBLIC_API_BASE=https://api.omnidoc.info
```

### Nginx Configuration

See [ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md) for complete Nginx configuration with these domains.

## 🔒 SSL/TLS

SSL certificates are managed via Let's Encrypt:
- Main domain: `omnidoc.info`
- WWW subdomain: `www.omnidoc.info`
- API subdomain: `api.omnidoc.info`

Auto-renewal is configured automatically.

## 📝 DNS Records

Ensure the following DNS records are configured:

```
A     omnidoc.info          → Server IP
A     www.omnidoc.info      → Server IP
A     api.omnidoc.info      → Server IP
```

Or use CNAME records if using a CDN/load balancer.

## 🔗 Related Documentation

- [Production Setup](PRODUCTION_SETUP.md)
- [Oracle Cloud Deployment](ORACLE_CLOUD_DEPLOYMENT.md)
- [Security Configuration](SECURITY.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)

