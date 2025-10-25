# 🚀 Phase 10: Production Deployment Guide

## 📋 İçindekiler

1. [Ön Hazırlık](#ön-hazırlık)
2. [Yerel Docker Deployment](#yerel-docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [CI/CD Setup](#cicd-setup)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Ön Hazırlık

### 1. Gereksinimler

**Yerel Geliştirme:**
- Docker Desktop (Windows/Mac) veya Docker Engine (Linux)
- Docker Compose v2.0+
- Git

**Cloud Deployment:**
- GitHub hesabı
- Cloud platform hesabı (Railway/Heroku/Render)
- Domain (opsiyonel)

### 2. Environment Configuration

```bash
# .env.example dosyasını kopyalayın
copy .env.example .env

# .env dosyasını düzenleyin
notepad .env
```

**Önemli değişkenler:**
```env
# Güvenlik
SECRET_KEY=your-strong-secret-key-here
API_KEY=your-api-sports-key

# Database
DATABASE_URL=postgresql://user:password@db:5432/analiz
POSTGRES_PASSWORD=strong-password-here

# Environment
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

---

## 🐳 Yerel Docker Deployment

### Adım 1: Build ve Start

```bash
# Otomatik deployment
docker-deploy.bat

# Manuel deployment
docker-compose up -d --build
```

### Adım 2: Health Check

```bash
# Container durumunu kontrol et
docker-compose ps

# API health check
curl http://localhost:8000/api/ml/health

# Logs
docker-compose logs -f app
```

### Adım 3: Test

```bash
# API dokümantasyonunu aç
start http://localhost:8000/docs

# Test suite çalıştır
python test_ml_api.py
```

### Yaygın Komutlar

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Shell
docker-compose exec app /bin/bash

# Database shell
docker-compose exec db psql -U user -d analiz
```

---

## ☁️ Cloud Deployment

### Option 1: Railway.app (Önerilen)

**Avantajlar:**
- Ücretsiz tier
- Otomatik HTTPS
- GitHub entegrasyonu
- PostgreSQL & Redis dahil

**Deployment Adımları:**

1. **Railway hesabı oluştur:** https://railway.app

2. **New Project → Deploy from GitHub:**
   ```
   Repository: yenianaliz
   Branch: main
   ```

3. **Environment variables ekle:**
   ```
   SECRET_KEY=your-secret
   API_KEY=your-api-key
   ENVIRONMENT=production
   ```

4. **Services ekle:**
   - PostgreSQL
   - Redis
   - App (main service)

5. **Deploy!**
   ```bash
   # Railway CLI ile (opsiyonel)
   npm install -g @railway/cli
   railway login
   railway up
   ```

---

### Option 2: Render.com

**Deployment Adımları:**

1. **Render hesabı oluştur:** https://render.com

2. **New Web Service:**
   ```
   Repository: yenianaliz
   Branch: main
   Runtime: Docker
   ```

3. **Build & Deploy Command:**
   ```dockerfile
   # Dockerfile kullan (otomatik detect eder)
   ```

4. **Environment variables:**
   ```
   Render Dashboard → Environment → Add variables
   ```

5. **Database ekle:**
   ```
   Dashboard → New PostgreSQL
   Dashboard → New Redis
   ```

---

### Option 3: Heroku

**Deployment Adımları:**

1. **Heroku CLI kur:**
   ```bash
   # Windows
   choco install heroku-cli
   
   # Veya: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login:**
   ```bash
   heroku login
   ```

3. **Create app:**
   ```bash
   heroku create guvenilir-analiz
   ```

4. **Add buildpacks:**
   ```bash
   heroku buildpacks:set heroku/python
   ```

5. **Add PostgreSQL & Redis:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   heroku addons:create heroku-redis:mini
   ```

6. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-secret
   heroku config:set API_KEY=your-api-key
   heroku config:set ENVIRONMENT=production
   ```

7. **Deploy:**
   ```bash
   git push heroku main
   ```

8. **Open:**
   ```bash
   heroku open
   heroku logs --tail
   ```

---

### Option 4: AWS/GCP/Azure

**AWS Elastic Beanstalk:**
```bash
# EB CLI
pip install awsebcli

# Initialize
eb init -p docker guvenilir-analiz

# Create environment
eb create production-env

# Deploy
eb deploy
```

**Google Cloud Run:**
```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT-ID/guvenilir-analiz

# Deploy
gcloud run deploy --image gcr.io/PROJECT-ID/guvenilir-analiz
```

---

## 🔄 CI/CD Setup

### GitHub Actions (Otomatik)

**Setup Adımları:**

1. **GitHub Secrets ekle:**
   ```
   Repository → Settings → Secrets → Actions
   
   Eklenecek secrets:
   - RAILWAY_TOKEN (Railway deployment için)
   - DEPLOY_TOKEN (diğer platformlar için)
   - SENTRY_DSN (monitoring için)
   ```

2. **Push to trigger:**
   ```bash
   git add .
   git commit -m "feat: production deployment"
   git push origin main
   ```

3. **Monitor:**
   ```
   GitHub → Actions → CI/CD Pipeline
   ```

**Workflow özellikleri:**
- ✅ Lint & code quality
- ✅ Unit tests
- ✅ Security scan
- ✅ Docker build & push
- ✅ Auto deploy to staging/production
- ✅ Health checks

---

## 📊 Monitoring

### 1. Application Monitoring (Sentry)

```bash
# Sentry hesabı: https://sentry.io

# .env'e ekle
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

**FastAPI entegrasyonu:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("SENTRY_ENVIRONMENT"),
    integrations=[FastApiIntegration()],
)
```

### 2. Logs

```bash
# Docker logs
docker-compose logs -f app

# Cloud platforms
railway logs
heroku logs --tail
```

### 3. Health Checks

```bash
# Manual check
curl https://your-app.com/api/ml/health

# Automated monitoring
# UptimeRobot: https://uptimerobot.com
# Pingdom: https://pingdom.com
```

---

## 🐛 Troubleshooting

### Container başlamıyor

```bash
# Check logs
docker-compose logs app

# Check config
docker-compose config

# Rebuild
docker-compose up -d --build --force-recreate
```

### Database connection hatası

```bash
# Check database
docker-compose exec db pg_isready

# Check connection string
echo $DATABASE_URL

# Restart database
docker-compose restart db
```

### Port conflict

```bash
# Check port usage
netstat -ano | findstr :8000

# Change port in .env
APP_PORT=8001
```

### Memory issues

```bash
# Check resource usage
docker stats

# Increase limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

---

## 📝 Deployment Checklist

### Pre-Deployment

- [ ] .env dosyası yapılandırıldı
- [ ] SECRET_KEY güçlü ve unique
- [ ] Database credentials güvenli
- [ ] API keys doğru
- [ ] Tests passing (`pytest`)
- [ ] Docker build başarılı

### Deployment

- [ ] Cloud platform seçildi
- [ ] Environment variables set edildi
- [ ] Database & Redis eklendi
- [ ] Domain yapılandırıldı (opsiyonel)
- [ ] SSL/HTTPS aktif
- [ ] Deployment başarılı

### Post-Deployment

- [ ] Health check passing
- [ ] API endpoints çalışıyor
- [ ] Logs monitör ediliyor
- [ ] Sentry/monitoring aktif
- [ ] Backup yapılandırıldı
- [ ] Documentation updated

---

## 🔐 Security Best Practices

1. **Environment Variables:**
   - Asla Git'e commit etmeyin
   - Cloud platform secrets kullanın
   - Rotate keys regularly

2. **Database:**
   - Güçlü passwords
   - SSL connections
   - Regular backups

3. **API Keys:**
   - Rate limiting aktif
   - API key rotation
   - Usage monitoring

4. **HTTPS:**
   - Always use HTTPS in production
   - SSL certificates (Let's Encrypt)
   - HSTS headers

---

## 📞 Support

**Deployment sorunları için:**

1. Logs kontrol et: `docker-compose logs`
2. Health endpoint: `/api/ml/health`
3. GitHub Issues
4. Cloud platform documentation

---

## 🎯 Next Steps

Deployment tamamlandıktan sonra:

1. ✅ Monitoring setup (Sentry)
2. ✅ Automated backups
3. ✅ Custom domain
4. ✅ CDN (Cloudflare)
5. ✅ Load testing
6. ✅ Performance optimization

---

**Last Updated:** 2025-10-24  
**Version:** 10.0.0  
**Status:** Production Ready ✅
