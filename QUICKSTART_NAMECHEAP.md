# ⚡ HIZLI BAŞLANGIÇ - NAMECHEAP FASTAPI DEPLOYMENT

## 🎯 5 ADIMDA DEPLOYMENT

### 1️⃣ LOKAL HAZIRLIK (5 dakika)

```bash
# Windows'ta deployment paketi oluştur
prepare-deployment.bat

# deploy_package\ klasörünü ZIP'le
# Sağ tık → Send to → Compressed folder
# Dosya adı: fastapi_deploy.zip
```

---

### 2️⃣ cPANEL'E YÜKLENİN (10 dakika)

#### A. Giriş
```
URL: https://premium700.web-hosting.com:2083
```

#### B. Eski Projeyi Temizle
1. File Manager → `public_html`
2. Tüm dosyaları seç → Sağ tık → **Compress** → `backup.zip`
3. `backup.zip`'i indir
4. Tüm dosyaları sil (sadece `tmp/` klasörünü bırak)

#### C. Yeni Projeyi Yükle
1. **Upload** → `fastapi_deploy.zip`
2. Sağ tık → **Extract** → `/public_html`
3. Zip dosyasını sil

---

### 3️⃣ VERITABANI KURULUMU (5 dakika)

#### cPanel → MySQL® Databases

```
1. Create Database:
   Name: analiz_db
   
2. Create User:
   Username: dbuser
   Password: [Güçlü şifre oluştur - KAYDET!]
   
3. Add User to Database:
   User: dbuser
   Database: analiz_db
   Privileges: ALL PRIVILEGES
```

**Database bilgilerini not al:**
```
Host: localhost
Database: [prefix]_analiz_db
User: [prefix]_dbuser
Password: [az önce oluşturduğun]
Port: 3306
```

---

### 4️⃣ SUNUCU KURULUMU (10 dakika)

#### A. Terminal Aç
cPanel → **Terminal** (veya SSH ile bağlan)

#### B. Setup Script Çalıştır
```bash
cd ~/public_html
chmod +x server-setup.sh
./server-setup.sh
```

#### C. .env Dosyası Oluştur
```bash
cp .env.example .env
nano .env  # veya File Manager'dan düzenle
```

`.env` içeriği:
```env
API_KEY=your_api_football_key_here
DB_HOST=localhost
DB_NAME=[prefix]_analiz_db
DB_USER=[prefix]_dbuser
DB_PASSWORD=[veritabanı şifresi]
DB_PORT=3306
SECRET_KEY=rastgele_uzun_bir_anahtar_buraya
ENVIRONMENT=production
DEBUG=False
REDIS_ENABLED=False
```

#### D. .htaccess Güncelle
```bash
nano .htaccess
# [USERNAME] kısımlarını gerçek kullanıcı adınla değiştir
# Kaydet: Ctrl+O, Enter, Ctrl+X
```

Kullanıcı adını öğren:
```bash
whoami
```

---

### 5️⃣ BAŞLAT VE TEST ET (2 dakika)

#### A. Passenger'ı Başlat
```bash
touch ~/public_html/tmp/restart.txt
```

#### B. Test Et
```
✅ Ana sayfa: https://güvenilanaliz.com
✅ API Docs: https://güvenilanaliz.com/docs
✅ Health: https://güvenilanaliz.com/health
```

#### C. Logları Kontrol Et
```bash
# Passenger startup log
tail -f ~/public_html/logs/passenger_startup.log

# API logs
tail -f ~/public_html/logs/api.log

# Error logs (cPanel'den)
# Home → Metrics → Errors
```

---

## 🔧 SORUN GİDERME

### "500 Internal Server Error"
```bash
# 1. Error log kontrol
tail -20 ~/logs/[domain]_error_log

# 2. Yetkileri kontrol
ls -la ~/public_html/passenger_wsgi.py
chmod 755 ~/public_html/passenger_wsgi.py

# 3. Python path kontrol
which python3
cat ~/public_html/.htaccess | grep PassengerPython
```

### "Module not found"
```bash
# Virtual environment kontrol
source ~/public_html/venv/bin/activate
pip list | grep fastapi

# Eksik paket kur
pip install fastapi uvicorn asgiref
```

### Database Bağlantı Hatası
```bash
# .env dosyasını kontrol
cat ~/public_html/.env | grep DB_

# Database varlığını test (cPanel → phpMyAdmin)
```

---

## 🔄 GÜNCELLEME

```bash
# 1. Değişen dosyayı yükle (File Manager veya FTP)

# 2. Passenger'ı yeniden başlat
touch ~/public_html/tmp/restart.txt

# 3. Test et
curl https://güvenilanaliz.com/docs

# 4. Logs kontrol
tail -f ~/public_html/logs/api.log
```

---

## ✅ BAŞARILI DEPLOYMENT KONTROLÜc

- [ ] Website açılıyor
- [ ] API docs (/docs) çalışıyor
- [ ] Health endpoint yanıt veriyor
- [ ] Database bağlantısı OK
- [ ] Static files yükleniyor
- [ ] Logs dosyası oluşuyor
- [ ] No 500 errors

---

## 📞 DESTEK

**Namecheap Support:**
- Live Chat: 24/7
- Email: support@namecheap.com
- Tel: +1.631.409.2992

**Deployment Docs:**
- `NAMECHEAP_FASTAPI_DEPLOYMENT.md` - Detaylı adımlar
- `NAMECHEAP_DEPLOYMENT.md` - Genel bilgiler

---

## 🎉 TAMAMLANDI!

Projeniz artık canlı: **https://güvenilanaliz.com**

**API Endpoints:**
- `/docs` - Swagger UI
- `/api/predict` - ML Prediction
- `/api/health` - System Health
- `/cache-stats` - Cache Statistics

**Başarılar! 🚀**
