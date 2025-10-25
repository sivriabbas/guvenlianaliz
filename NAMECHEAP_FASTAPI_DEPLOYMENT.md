# 🚀 NAMECHEAP DEPLOYMENT - FASTAPI STEP BY STEP

## 📋 ÖNEMLİ BİLGİLER
- **Domain:** xn--gvenlinaliz-dlb.com (güvenilanaliz.com)
- **Hosting:** Namecheap Stellar Plus Shared Hosting
- **Control Panel:** cPanel
- **Python Support:** ✅ Passenger WSGI

---

## 🎯 DEPLOYMENT ADIMLARI

### ADIM 1: MEVCUT PROJEYİ YEDEKLE VE KALDIR

#### 1.1 cPanel'e Giriş
```
URL: https://premium700.web-hosting.com:2083
Username: [Namecheap'ten al]
Password: [Namecheap'ten al]
```

#### 1.2 Mevcut Dosyaları Yedekle
1. cPanel → **File Manager**
2. `public_html` klasörüne git
3. Tüm dosyaları seç
4. Sağ tık → **Compress** → `backup_old_project.zip`
5. İndir ve güvenli yerde sakla

#### 1.3 Eski Projeyi Sil
1. `public_html` içindeki TÜM dosyaları seç
2. **Delete** (Sadece `.htaccess` ve `tmp/` klasörünü bırak - eğer varsa)
3. Silmeyi onayla

---

### ADIM 2: YENİ FASTAPI PROJESİNİ HAZIRLAA

#### 2.1 Gerekli Dosyaları Hazırla (Lokal)
Projenizde bu dosyalar olmalı:
```
yenianaliz_1_yedek/
├── simple_fastapi.py          # Ana uygulama
├── passenger_wsgi.py           # WSGI entry point
├── .htaccess                   # URL rewrite
├── requirements-namecheap.txt  # Bağımlılıklar
├── config.yaml                 # Konfigürasyon
├── .env.example                # Environment template
├── api_utils.py
├── analysis_logic.py
├── comprehensive_analysis.py
├── elo_utils.py
├── cache_manager.py
├── factor_weights.py
├── data_fetcher.py
├── ml_model_manager.py
├── ensemble_predictor.py
├── prediction_logger.py
├── api_security.py
├── request_validation.py
├── api_metrics.py
├── advanced_logging.py
├── models/                     # ML modeller
│   ├── lgb_v1.pkl
│   └── xgb_v1.pkl
├── static/                     # Static dosyalar
└── templates/                  # HTML templates
```

#### 2.2 .env Dosyası Oluştur
```bash
# Lokal'de .env dosyası oluştur (sunucuya yükleyeceğiz)
cp .env.example .env
```

`.env` içeriği:
```env
# API Keys
API_KEY=your_api_football_key_here

# Environment
ENVIRONMENT=production
DEBUG=False

# Database (cPanel'den alacaksın)
DB_HOST=localhost
DB_NAME=username_analiz_db
DB_USER=username_dbuser
DB_PASSWORD=strong_password_here
DB_PORT=3306

# Security
SECRET_KEY=generate_a_random_secret_key_here
ALLOWED_HOSTS=xn--gvenlinaliz-dlb.com,www.xn--gvenlinaliz-dlb.com

# Redis (Shared hosting'de olmayabilir - disable et)
REDIS_ENABLED=False
```

#### 2.3 Dosyaları Zip'le
```bash
# Windows PowerShell
Compress-Archive -Path * -DestinationPath fastapi_deploy.zip

# Veya manuel olarak tüm dosyaları seç ve sağ tık → Send to → Compressed folder
```

---

### ADIM 3: DOSYALARI SUNUCUYA YÜKLE

#### 3.1 cPanel File Manager ile Upload
1. cPanel → **File Manager**
2. `public_html` klasörüne git
3. **Upload** butonuna tıkla
4. `fastapi_deploy.zip` dosyasını seç
5. Upload tamamlanana kadar bekle

#### 3.2 Extract (Çıkart)
1. `fastapi_deploy.zip` dosyasına sağ tıkla
2. **Extract** seçeneğini seç
3. Extract path: `/public_html` olarak ayarla
4. **Extract Files** butonuna tıkla
5. Zip dosyasını sil (opsiyonel)

---

### ADIM 4: PYTHON SANAL ORTAM KURULUMU

#### 4.1 SSH ile Bağlan (Eğer SSH erişiminiz varsa)
```bash
ssh username@premium700.web-hosting.com
cd public_html
```

#### 4.2 Virtual Environment Oluştur
```bash
# Python version kontrol et
python3 --version

# Virtual environment oluştur
python3 -m venv venv

# Aktive et
source venv/bin/activate

# Pip güncellemeleri
pip install --upgrade pip setuptools wheel
```

#### 4.3 Bağımlılıkları Kur
```bash
# Minimal requirements (shared hosting için)
pip install -r requirements-namecheap.txt

# Veya full requirements (eğer kaynak yeterliyse)
# pip install -r requirements.txt

# Kurulum tamamlandığını kontrol et
pip list
```

**NOT:** SSH erişimi yoksa, cPanel'deki **Terminal** özelliğini kullanın!

---

### ADIM 5: DOSYA YETKİLERİNİ AYARLA

#### 5.1 File Manager'dan Yetki Ayarla
```
passenger_wsgi.py → 755 (rwxr-xr-x)
.htaccess        → 644 (rw-r--r--)
.env             → 600 (rw-------)
simple_fastapi.py → 644 (rw-r--r--)
```

Nasıl yapılır:
1. Dosyaya sağ tıkla
2. **Change Permissions**
3. Yukarıdaki değerleri gir

---

### ADIM 6: .HTACCESS'İ GÜNCELLE

`.htaccess` dosyasını aç ve `[USERNAME]` kısmını gerçek kullanıcı adınla değiştir:
```apache
PassengerAppRoot /home/GERÇEK_KULLANICI_ADI/public_html
PassengerPython /home/GERÇEK_KULLANICI_ADI/public_html/venv/bin/python3
```

Kullanıcı adını öğrenmek için:
- cPanel → sağ üst köşede gösterilir
- SSH: `whoami` komutu

---

### ADIM 7: VERITABANI OLUŞTUR

#### 7.1 MySQL Database Oluştur
1. cPanel → **MySQL® Databases**
2. **Create New Database**:
   - Database Name: `analiz_db` (otomatik prefix eklenecek: `username_analiz_db`)
   - **Create Database**

#### 7.2 Database User Oluştur
1. **Add New User**:
   - Username: `dbuser`
   - Password: **Güçlü bir şifre oluştur** (kaydet!)
   - **Create User**

#### 7.3 User'ı Database'e Ata
1. **Add User To Database** bölümüne git
2. User: `username_dbuser` seç
3. Database: `username_analiz_db` seç
4. **Add**
5. **ALL PRIVILEGES** seç
6. **Make Changes**

#### 7.4 .env Dosyasını Güncelle
```env
DB_HOST=localhost
DB_NAME=username_analiz_db
DB_USER=username_dbuser
DB_PASSWORD=az_önce_oluşturduğun_güçlü_şifre
DB_PORT=3306
```

---

### ADIM 8: PASSENGER'I YENİDEN BAŞLAT

#### 8.1 tmp Klasörü Oluştur
```bash
# SSH veya Terminal
cd ~/public_html
mkdir -p tmp
touch tmp/restart.txt
```

#### 8.2 File Manager ile
1. `public_html` klasöründe
2. **+ Folder** → `tmp`
3. `tmp` klasörüne gir
4. **+ File** → `restart.txt`

**NOT:** Her kod değişikliğinden sonra `tmp/restart.txt` dosyasına dokunarak Passenger'ı yeniden başlatabilirsiniz:
```bash
touch ~/public_html/tmp/restart.txt
```

---

### ADIM 9: TEST ET

#### 9.1 Website'i Aç
```
https://xn--gvenlinaliz-dlb.com
veya
https://güvenilanaliz.com
```

#### 9.2 API Docs Kontrol Et
```
https://xn--gvenlinaliz-dlb.com/docs
```

#### 9.3 Log Dosyalarını Kontrol Et
```bash
# SSH/Terminal
cd ~/public_html
cat logs/passenger_startup.log
cat logs/api.log
```

cPanel File Manager'dan da kontrol edebilirsiniz:
- `logs/passenger_startup.log`
- `logs/api_errors.log`

---

### ADIM 10: SORUN GİDERME

#### 10.1 "500 Internal Server Error" Alıyorsanız:
```bash
# Error log kontrol et
tail -f ~/logs/[domain]_error_log

# Passenger log kontrol et
cat ~/public_html/logs/passenger_startup.log

# Yetkileri kontrol et
ls -la ~/public_html/passenger_wsgi.py
```

#### 10.2 "Module not found" Hatası:
```bash
# Virtual environment'ı kontrol et
source ~/public_html/venv/bin/activate
pip list

# Eksik paketleri kur
pip install -r requirements-namecheap.txt
```

#### 10.3 Python Version Hatası:
```bash
# Python version kontrol
python3 --version

# .htaccess'te doğru Python path'i ayarlı mı kontrol et
cat ~/public_html/.htaccess
```

---

## 🔄 GÜNCELLEME NASIL YAPILIR?

1. **Lokal'de değişiklik yap**
2. **Değişen dosyaları sunucuya yükle** (File Manager veya FTP)
3. **Passenger'ı yeniden başlat:**
   ```bash
   touch ~/public_html/tmp/restart.txt
   ```

---

## 📊 PERFORMANS ÖNERİLERİ

### Shared Hosting İçin Optimizasyon:
1. **ML Modellerini minimize et** - Sadece gerekli modelleri yükle
2. **Cache kullan** - Disk cache aktif (Redis yerine)
3. **Memory limit** - Shared hosting'de genellikle 512MB-1GB
4. **Concurrent requests** - Sınırlı tutun
5. **Static files** - CDN kullanın (opsiyonel)

---

## ✅ CHECKLIST

- [ ] Eski proje yedeklendi
- [ ] Eski proje temizlendi
- [ ] Yeni dosyalar yüklendi
- [ ] Virtual environment kuruldu
- [ ] Requirements kuruldu
- [ ] .htaccess güncellendi
- [ ] Database oluşturuldu
- [ ] .env dosyası ayarlandı
- [ ] Dosya yetkileri ayarlandı
- [ ] tmp/restart.txt oluşturuldu
- [ ] Website test edildi
- [ ] API docs çalışıyor
- [ ] Logs kontrol edildi

---

## 🆘 DESTEK

Sorun yaşarsanız:
1. **Error logs** kontrol edin
2. **Passenger logs** inceleyin
3. **cPanel Support** ile iletişime geçin
4. Namecheap Live Chat kullanın

**Başarılar! 🚀**
