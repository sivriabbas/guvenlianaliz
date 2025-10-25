# 🚀 NAMECHEAP SHARED HOSTING - HIZLI BAŞLANGIÇ

## ✅ Hazırlanan Dosyalar

1. **passenger_wsgi.py** - Passenger WSGI entry point
2. **.htaccess** - URL rewriting ve security
3. **.env.shared_hosting** - Environment template
4. **requirements-shared-hosting.txt** - Lightweight dependencies
5. **deploy-namecheap.sh** - Otomatik deployment script
6. **cron_daily_reset.py** - Günlük reset cron job
7. **cron_elo_update.py** - ELO update cron job

---

## 📋 Adım Adım Deployment

### 1️⃣ cPanel'e Giriş

```
URL: https://premium700.web-hosting.com:2083
veya Dashboard'dan "GO TO CPANEL" butonuna tıklayın
```

### 2️⃣ MySQL Database Oluştur

**cPanel → MySQL® Databases**

```sql
Database Name: xnggra_analiz_db
User Name: xnggra_dbuser
Password: [Güçlü şifre oluşturun ve kaydedin!]

✅ Create Database
✅ Create User  
✅ Add User to Database → ALL PRIVILEGES
```

**🔑 Credentials'ı kaydedin:**
```
DB_HOST=localhost
DB_NAME=xnggra_analiz_db
DB_USER=xnggra_dbuser
DB_PASSWORD=[sizin şifreniz]
```

### 3️⃣ Dosyaları Upload Et

**Seçenek A: cPanel File Manager (Kolay)**

1. Tüm dosyaları zip'le: `yenianaliz.zip`
2. cPanel → File Manager
3. `public_html` klasörüne git
4. Upload → `yenianaliz.zip`
5. Extract → Delete archive

**Seçenek B: FTP (FileZilla)**

```
Host: ftp.xn--gvenlinaliz-dlb.com
Username: [cPanel username]
Password: [cPanel password]
Port: 21
Remote path: /public_html
```

Tüm dosyaları yükle.

### 4️⃣ Environment Dosyasını Düzenle

**cPanel → File Manager → public_html/app**

1. `.env.shared_hosting` dosyasını `app/.env` olarak kopyala
2. `.env` dosyasını düzenle:

```env
# DATABASE - MySQL credentials'ı gir
DB_HOST=localhost
DB_NAME=xnggra_analiz_db
DB_USER=xnggra_dbuser
DB_PASSWORD=BURAYA_SİZİN_ŞİFRENİZ

# SECRET KEYS - Güvenli random keys oluştur
SECRET_KEY=BURAYA_RANDOM_32_KARAKTER_KEY
API_KEY=BURAYA_API_KEY_OLUŞTUR
```

**Random key oluşturmak için:**
```bash
# Yerel bilgisayarınızda PowerShell:
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

Kaydet ve kapat.

### 5️⃣ Terminal/SSH ile Deployment

**cPanel → Terminal** (veya SSH)

```bash
# 1. public_html'e git
cd ~/public_html

# 2. Deployment script'i çalıştırılabilir yap
chmod +x deploy-namecheap.sh

# 3. Deployment script'i çalıştır
./deploy-namecheap.sh
```

Script otomatik olarak:
- ✅ Virtual environment oluşturur
- ✅ Dependencies yükler
- ✅ Database'i initialize eder
- ✅ ELO ratings'i günceller
- ✅ Passenger'ı restart eder

**İşlem ~5-10 dakika sürer.**

### 6️⃣ Setup Python App (Alternatif - cPanel GUI)

Eğer script çalışmazsa manuel kurulum:

**cPanel → Setup Python App**

```
Python Version: 3.10 veya 3.11
Application Root: /home/[username]/public_html
Application URL: / (root)
Application Startup File: passenger_wsgi.py
Application Entry Point: application
```

**Create** → **Enter to the virtual environment:**

```bash
source /home/[username]/public_html/venv/bin/activate
pip install --upgrade pip
pip install -r requirements-shared-hosting.txt
```

### 7️⃣ Cron Jobs Ayarla

**cPanel → Cron Jobs**

**Daily Reset (Her gün saat 00:00):**
```
Minute: 0
Hour: 0
Day: *
Month: *
Weekday: *
Command: /home/[USERNAME]/public_html/venv/bin/python3 /home/[USERNAME]/public_html/app/cron_daily_reset.py >> /home/[USERNAME]/public_html/logs/cron_daily.log 2>&1
```

**ELO Update (Her 6 saatte):**
```
Minute: 0
Hour: */6
Day: *
Month: *
Weekday: *
Command: /home/[USERNAME]/public_html/venv/bin/python3 /home/[USERNAME]/public_html/app/cron_elo_update.py >> /home/[USERNAME]/public_html/logs/cron_elo.log 2>&1
```

**[USERNAME]** yerine kendi cPanel kullanıcı adınızı yazın!

### 8️⃣ Test ve Doğrulama

**Health Check:**
```bash
curl https://xn--gvenlinaliz-dlb.com/api/ml/health
```

Beklenen:
```json
{"status": "healthy", "database": "connected"}
```

**API Docs:**
```
https://xn--gvenlinaliz-dlb.com/docs
```

**Prediction Test:**
```bash
curl -X POST "https://xn--gvenlinaliz-dlb.com/api/ml/predict" \
  -H "Content-Type: application/json" \
  -d '{"team_home": "Galatasaray", "team_away": "Fenerbahçe"}'
```

---

## 🔧 Sorun Giderme

### ❌ 500 Internal Server Error

**Çözüm:**
```bash
# cPanel → Terminal
cd ~/public_html

# Logs kontrol
tail -f logs/application.log
tail -f ~/public_html/logs/error.log

# Passenger restart
touch tmp/restart.txt

# Permissions
chmod 755 passenger_wsgi.py
chmod -R 755 app/
```

### ❌ Database Connection Error

**Kontrol listesi:**
1. `.env` dosyasında credentials doğru mu?
2. Database user ALL PRIVILEGES var mı? (cPanel → MySQL)
3. `DB_HOST=localhost` olmalı (127.0.0.1 değil)

### ❌ Module Not Found

**Çözüm:**
```bash
cd ~/public_html
source venv/bin/activate
pip install --no-cache-dir -r requirements-shared-hosting.txt
touch tmp/restart.txt
```

### ❌ Permission Denied

**Çözüm:**
```bash
chmod 755 ~/public_html/passenger_wsgi.py
chmod -R 755 ~/public_html/app/
chmod 644 ~/public_html/.htaccess
touch ~/public_html/tmp/restart.txt
```

---

## 📊 Deployment Checklist

**Hazırlık:**
- [x] Dosyalar oluşturuldu
- [ ] MySQL database oluşturuldu
- [ ] Database user ve password kaydedildi
- [ ] Dosyalar upload edildi

**Konfigürasyon:**
- [ ] `.env` dosyası düzenlendi
- [ ] SECRET_KEY ve API_KEY oluşturuldu
- [ ] Database credentials girildi
- [ ] deploy-namecheap.sh çalıştırıldı

**Test:**
- [ ] Health check (/api/ml/health)
- [ ] API docs (/docs)
- [ ] Prediction endpoint test
- [ ] Cron jobs ayarlandı

**Canlı:**
- [ ] Domain erişilebilir
- [ ] SSL active (https)
- [ ] Error logs temiz
- [ ] Monitoring aktif

---

## 🎯 Sonraki Adımlar

1. **Şimdi yapın:** MySQL database oluştur (2 dakika)
2. **Sonra:** Dosyaları upload et (5 dakika)
3. **Ardından:** .env düzenle (2 dakika)
4. **Son:** deploy-namecheap.sh çalıştır (10 dakika)

**Toplam süre: ~20 dakika**

---

## 🆘 Yardım Lazım?

**Namecheap Live Chat:** 24/7  
**Knowledge Base:** https://www.namecheap.com/support/

**Sık Sorulan:**
- "Python app nasıl deploy edilir?" → Namecheap docs
- "SSH erişimi var mı?" → Shared hosting'de genelde var
- "Python 3.10 var mı?" → cPanel → Python Selector

---

**Hazır mısınız? Başlayalım! 🚀**

1. cPanel'e giriş yapın
2. MySQL database oluşturun
3. Bu dosyaları upload edin
4. .env düzenleyin
5. deploy-namecheap.sh çalıştırın

**20 dakika sonra siteniz canlıda!**
