# Custom Domain Setup Guide - Railway + Cloudflare

## 🌐 Domain: güvenlianaliz.com

### 1️⃣ Railway Configuration

1. **Railway Dashboard** → Your Project → **Settings** → **Domains**
2. **Add Custom Domain**:
   - Primary: `güvenlianaliz.com`
   - WWW: `www.güvenlianaliz.com`

### 2️⃣ Cloudflare DNS Setup

**A. DNS Records (Cloudflare Dashboard):**

```
Type: CNAME
Name: www
Target: web-production-fafbf.up.railway.app
Proxy Status: Proxied (🟠)
TTL: Auto

Type: CNAME
Name: @
Target: web-production-fafbf.up.railway.app  
Proxy Status: Proxied (🟠)
TTL: Auto
```

**B. SSL/TLS Settings:**
- **Encryption Mode:** Full (strict)
- **Always Use HTTPS:** On
- **Automatic HTTPS Rewrites:** On
- **Certificate Authority Authorization (CAA):** Allow (optional)

**C. Speed Optimizations:**
- **Auto Minify:** CSS, JS, HTML ✅
- **Brotli Compression:** On
- **Rocket Loader:** On (optional)

### 3️⃣ Cloudflare Page Rules (Optional)

```
Rule 1: http://*güvenlianaliz.com/*
Settings: Always Use HTTPS

Rule 2: www.güvenlianaliz.com/*  
Settings: Forwarding URL (301 redirect to https://güvenlianaliz.com/$1)
```

### 4️⃣ Verification Steps

1. **DNS Propagation Check:**
   - https://www.whatsmydns.net
   - Check for: güvenlianaliz.com
   
2. **SSL Certificate Check:**
   - https://www.ssllabs.com/ssltest/
   - Should show A+ rating

3. **Speed Test:**
   - https://gtmetrix.com
   - Test both versions

### 🎯 Expected Results

- ✅ `https://güvenlianaliz.com` → Railway App
- ✅ `https://www.güvenlianaliz.com` → Railway App  
- ✅ `http://güvenlianaliz.com` → Redirect to HTTPS
- ✅ SSL Certificate: Valid
- ✅ Speed: Enhanced by Cloudflare CDN

### ⏱️ Propagation Time

- **DNS Changes:** 5-30 minutes
- **SSL Certificate:** 10-60 minutes  
- **Full Propagation:** 24-48 hours (max)

### 🔧 Troubleshooting

**Issue: Domain not working**
- Check DNS propagation
- Verify CNAME targets
- Clear browser cache

**Issue: SSL errors**  
- Wait for certificate provisioning
- Check Cloudflare SSL mode
- Verify Railway domain status

**Issue: Redirect loops**
- Change Cloudflare SSL to "Full (strict)"
- Check page rules for conflicts

### 📊 Benefits

✅ **Professional URL:** güvenlianaliz.com
✅ **CDN Speed:** Cloudflare global network
✅ **DDoS Protection:** Automatic
✅ **SSL Certificate:** Free & Auto-renewed
✅ **Analytics:** Traffic insights
✅ **Caching:** Static content optimization

### 🎉 Final Test

Test these URLs after setup:
- https://güvenlianaliz.com
- https://www.güvenlianaliz.com
- http://güvenlianaliz.com (should redirect)

All should load your Güvenilir Analiz! ⚽