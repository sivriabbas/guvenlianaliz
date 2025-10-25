# 🚀 Namecheap Shared Hosting Deployment Guide

## 📋 Mevcut Bilgiler

- **Domain:** xn--gvenlinaliz-dlb.com
- **Hosting Type:** Stellar Plus Shared Hosting
- **Server:** premium700.web-hosting.com (EU Datacenter)
- **IP Address:** 162.0.217.114
- **Control Panel:** cPanel (Installed)
- **Validity:** Oct 21, 2025 - Oct 21, 2026

---

## 🎯 Deployment Stratejisi

### Namecheap Shared Hosting Özellikleri:
- ✅ cPanel Access
- ✅ Python Support (via Passenger)
- ✅ MySQL Database
- ✅ SSH Access (potansiyel)
- ✅ FTP/SFTP
- ❌ Docker Support (shared hosting'de yok)
- ❌ Root Access (shared hosting)

**Strateji:** FastAPI uygulamasını Passenger WSGI ile deploy edeceğiz.

---

## 📝 Adım Adım Deployment

### Adım 1: cPanel'e Erişim

1. **cPanel'e Giriş:**
   ```
   URL: https://premium700.web-hosting.com:2083
   veya
   https://xn--gvenlinaliz-dlb.com/cpanel
   
   Username: xnğğra (veya Namecheap'ten alın)
   Password: [Namecheap hesabınızdan]
   ```

2. **Hosting Dashboard'dan "GO TO CPANEL" butonuna tıklayın**

---

### Adım 2: Python Version Kontrolü

1. cPanel'de **"Setup Python App"** veya **"Python Selector"** arayın
2. Desteklenen Python versiyonunu kontrol edin (3.8+ olmalı)
3. Python 3.10 veya 3.11 seçin

---

### Adım 3: MySQL Database Kurulumu

#### 3.1 Database Oluşturma
```sql
cPanel → MySQL® Databases

Database Name: xnğğra_analiz_db
Database User: xnğğra_dbuser
Password: [Güçlü bir şifre - kaydedin!]

Veritabanı Oluştur → User'ı veritabanına ata (ALL PRIVILEGES)
```

#### 3.2 Database Bağlantı Bilgileri (kaydedin):
```
DB_HOST=localhost
DB_NAME=xnğğra_analiz_db
DB_USER=xnğğra_dbuser
DB_PASSWORD=[şifreniz]
DB_PORT=3306
```

---

### Adım 4: Dosya Yapısı Hazırlığı

#### 4.1 Shared Hosting için dosya yapısı:
```
public_html/
├── .htaccess          # URL rewrite
├── passenger_wsgi.py  # WSGI entry point
├── tmp/              # Passenger restart
├── app/              # Ana uygulama
│   ├── app.py
│   ├── api_utils.py
│   ├── elo_utils.py
│   ├── analysis_logic.py
│   ├── requirements.txt
│   └── .env
└── venv/             # Virtual environment (kurulacak)
```

---

### Adım 5: Dosyaları Yükleme

#### Seçenek 1: cPanel File Manager (Kolay)
1. cPanel → **File Manager**
2. `public_html` klasörüne gidin
3. Tüm dosyaları zip'leyip upload edin
4. Extract işlemi yapın

#### Seçenek 2: FTP/SFTP (Profesyonel)
```
Host: ftp.xn--gvenlinaliz-dlb.com
Username: [cPanel username]
Password: [cPanel password]
Port: 21 (FTP) veya 22 (SFTP)
```

**FileZilla Ayarları:**
- Protocol: FTP veya SFTP
- Host: premium700.web-hosting.com
- Port: 21
- Folder: /public_html

---

### Adım 6: Passenger WSGI Konfigürasyonu

#### 6.1 passenger_wsgi.py Oluştur
```python
import sys
import os

# Virtual environment path
INTERP = os.path.join(os.environ['HOME'], 'public_html', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add app directory to path
sys.path.insert(0, os.path.join(os.environ['HOME'], 'public_html', 'app'))

# Import FastAPI app
from app import app as application
```

#### 6.2 .htaccess Oluştur
```apache
RewriteEngine On
RewriteBase /
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,PT,L]

# Security headers
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set X-XSS-Protection "1; mode=block"
```

---

### Adım 7: Virtual Environment Kurulumu

#### SSH Access varsa:
```bash
# SSH ile bağlan
ssh [username]@premium700.web-hosting.com

# Public_html'e git
cd public_html

# Virtual environment oluştur
python3 -m venv venv

# Activate
source venv/bin/activate

# Dependencies kur
pip install -r app/requirements.txt

# Passenger restart
mkdir -p tmp
touch tmp/restart.txt
```

#### SSH yoksa (cPanel Terminal):
```bash
# cPanel → Terminal
cd public_html
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
mkdir -p tmp && touch tmp/restart.txt
```

---

### Adım 8: Environment Variables (.env)

`public_html/app/.env` dosyası oluştur:

```env
# Application
APP_NAME=Güvenilir Analiz
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=2

# Security
SECRET_KEY=your-super-secret-key-change-this-min-32-chars
API_KEY=your-api-key-for-external-access-change-this
ALLOWED_HOSTS=["xn--gvenlinaliz-dlb.com", "www.xn--gvenlinaliz-dlb.com"]

# Database (MySQL)
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=xnğğra_analiz_db
DB_USER=xnğğra_dbuser
DB_PASSWORD=YOUR_DB_PASSWORD_HERE

# Redis (Shared hosting'de olmayabilir)
REDIS_ENABLED=False

# API Settings
API_V1_PREFIX=/api/v1
MAX_REQUESTS_PER_MINUTE=60

# ML Models
MODEL_UPDATE_INTERVAL=86400
ENABLE_AUTOML=True
ENABLE_DRIFT_DETECTION=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=application.log

# Monitoring (Opsiyonel)
SENTRY_DSN=
ENABLE_MONITORING=False

# CORS
CORS_ORIGINS=["https://xn--gvenlinaliz-dlb.com"]
```

---

### Adım 9: Setup Python App (cPanel)

1. cPanel → **Setup Python App**
2. **Create Application:**
   - Python version: 3.10 veya 3.11
   - Application root: `/public_html`
   - Application URL: `/` (root domain)
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`

3. **Environment Variables** ekle (cPanel arayüzünden)

4. **Click "Create"**

---

### Adım 10: Database Migration

```bash
# SSH/Terminal
cd public_html/app

# Python shell
python3 << EOF
from elo_utils import init_database
init_database()
print("Database initialized!")
EOF
```

---

### Adım 11: Test ve Doğrulama

#### 11.1 Health Check
```bash
curl https://xn--gvenlinaliz-dlb.com/api/ml/health
```

Beklenen sonuç:
```json
{
  "status": "healthy",
  "database": "connected",
  "models": "loaded"
}
```

#### 11.2 API Test
```bash
curl https://xn--gvenlinaliz-dlb.com/docs
```
FastAPI Swagger UI açılmalı.

#### 11.3 Prediction Test
```bash
curl -X POST "https://xn--gvenlinaliz-dlb.com/api/ml/predict" \
  -H "Content-Type: application/json" \
  -d '{"team_home": "Galatasaray", "team_away": "Fenerbahçe"}'
```

---

### Adım 12: Troubleshooting

#### Problem 1: 500 Internal Server Error
**Çözüm:**
```bash
# Error log kontrol
cPanel → Errors → Error Log

# Passenger restart
touch tmp/restart.txt

# Permissions kontrol
chmod 755 passenger_wsgi.py
chmod -R 755 app/
```

#### Problem 2: Module Not Found
**Çözüm:**
```bash
# Virtual env'i tekrar kur
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
touch tmp/restart.txt
```

#### Problem 3: Database Connection Error
**Çözüm:**
- MySQL database credentials kontrol
- cPanel → MySQL Databases → User privileges kontrol
- `.env` dosyasında DB_HOST=localhost olmalı
- Database user'ın ALL PRIVILEGES'i olmalı

#### Problem 4: Python Version Hatası
**Çözüm:**
```bash
# cPanel → Python Selector
# Python 3.10+ seçin
# Virtual environment yeniden oluşturun
```

---

## 🔧 Önemli Notlar

### Shared Hosting Kısıtlamaları:
1. **Docker yok** → Native Python kullanıyoruz
2. **Redis muhtemelen yok** → Cache disable ediyoruz
3. **Resource limits var** → Lightweight models kullanın
4. **No root access** → System packages kurulamaz

### Optimizasyonlar:
- ML modellerini lightweight tutun (XGBoost yerine LightGBM)
- Database connection pooling azaltın
- Background tasks için cron jobs kullanın (cPanel'den)
- Static files için CDN düşünün

---

## 📊 Deployment Checklist

### Ön Hazırlık:
- [ ] cPanel erişimi doğrula
- [ ] Python version kontrol (3.10+)
- [ ] SSH/Terminal access kontrol
- [ ] FTP credentials hazır

### Database:
- [ ] MySQL database oluştur
- [ ] Database user oluştur
- [ ] Privileges ata
- [ ] Connection test

### Dosyalar:
- [ ] Tüm dosyaları public_html'e upload
- [ ] passenger_wsgi.py oluştur
- [ ] .htaccess oluştur
- [ ] .env dosyası hazırla

### Environment:
- [ ] Virtual environment kur
- [ ] Dependencies yükle
- [ ] Environment variables set et
- [ ] Permissions ayarla (755)

### Test:
- [ ] Health check endpoint
- [ ] API docs erişimi
- [ ] Prediction endpoint
- [ ] Database connection
- [ ] Error logs kontrol

### Canlı:
- [ ] Domain'e erişim test
- [ ] SSL certificate (Let's Encrypt)
- [ ] Cron jobs ayarla (günlük reset)
- [ ] Monitoring aktif

---

## 🚀 Hızlı Başlangıç Komutları

```bash
# 1. SSH/Terminal Bağlantı
ssh [username]@premium700.web-hosting.com

# 2. Virtual Environment
cd public_html
python3 -m venv venv
source venv/bin/activate

# 3. Dependencies
pip install --upgrade pip
pip install -r app/requirements.txt

# 4. Database Init
cd app
python3 -c "from elo_utils import init_database; init_database()"

# 5. Restart
cd ..
mkdir -p tmp
touch tmp/restart.txt

# 6. Test
curl https://xn--gvenlinaliz-dlb.com/api/ml/health
```

---

## 📞 Yardım

### Namecheap Support:
- **Live Chat:** 24/7 available
- **Knowledge Base:** https://www.namecheap.com/support/knowledgebase/
- **Ticket:** Support dashboard

### Sorun mu yaşıyorsunuz?
1. Error logs kontrol edin (cPanel → Errors)
2. Passenger'ı restart edin (`touch tmp/restart.txt`)
3. Virtual environment'ı yeniden kurun
4. Database credentials'ı doğrulayın

---

**Oluşturulma:** 24 Ekim 2025  
**Version:** 1.0.0  
**Status:** Ready for Deployment
