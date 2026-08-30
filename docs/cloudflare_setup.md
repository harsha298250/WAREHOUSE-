# Production Cloudflare Deployment Setup

This document provides deployment guidelines for configuring Cloudflare as the production edge security layer for the Warehouse OS platform.

## Request Flow Architecture
```
User Browser  --->  Cloudflare Edge  --->  Web Server / Application Load Balancer
 (HTTPS TLS)           (TLS & WAF)              (FastAPI Backend / Frontend Static Files)
```

## Recommended Configurations

### 1. DNS & SSL/TLS Settings
- **SSL/TLS Mode**: Full (Strict).
- **Minimum TLS Version**: TLS 1.3 (Recommended for security).
- **HSTS (HTTP Strict Transport Security)**: Enabled with 1-year max age, subdomains, and preloading active.
- **Always Use HTTPS**: On (Forces automatic redirect of HTTP calls to HTTPS).

### 2. Web Application Firewall (WAF) & Rate Limiting
- **Rate Limiting**: Block clients triggering more than 100 requests per minute on API endpoints (e.g. `/api/*`). Bypass rules for `/static/*` assets to prevent false positives during dashboard loads.
- **OWASP Core Ruleset**: Enable standard SQL injection, Cross-Site Scripting (XSS), and Command Injection protection controls.
- **OAuth Redirects Protection**: Restrict access to `/auth/google/callback` to prevent auth replay attacks.

### 3. Cross-Origin Resource Sharing (CORS) & Origin Validation
- **Secure Cookies**: In production, FastAPI sessions are configured with `Secure`, `HttpOnly`, and `SameSite=Strict`.
- **CORS Configuration**: Restrict backend `CORS_ORIGINS` to the Cloudflare proxy domain. Avoid wildcards (`*`) in production.
- **Forwarded Headers**: FastAPI must trust `X-Forwarded-For` and `CF-Connecting-IP` headers to record real client IP addresses in the `AccessLog` database rather than the Cloudflare proxy IP.

### 4. Edge Caching & Static Content
- **Static Assets Cache**: Cache `.js`, `.css`, and `.svg` files at the edge for 7 days to enhance visual speed and responsiveness.
- **API Cache Bypass**: Bypass edge caching for all `/api/*` endpoints to guarantee real-time telemetry feeds. Configure Cloudflare page rule `Bypass Cache` for `/api/*`.
