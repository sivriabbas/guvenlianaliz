# 🎯 cPANEL MANUEL DEPLOYMENT REHBERİ

## ✅ NEDEN cPANEL?

- ✅ **Daha kolay** - Tarayıcı üzerinden her şey
- ✅ **Daha güvenli** - SFTP ayarı gerekmez
- ✅ **Hızlı** - ZIP upload + extract
- ✅ **Hata riski düşük** - Görsel arayüz
- ✅ **Terminal entegre** - SSH için PuTTY gerekmez

---

## 📦 ADIM 1: DEPLOYMENT PAKETİ HAZIRLAMA

### 1.1 ZIP Oluştur

**Windows Gezgini:**
1. `C:\Users\Mustafa\yenianaliz_1_yedek\deploy_package\` klasörüne git
2. Klasörün **İÇİNDEKİ TÜM DOSYALARI** seç (Ctrl+A)
3. Sağ tık → **Sıkıştırılmış (zip) klasöre gönder**
4. Adı: `fastapi_project.zip`
5. Bekle (2-3 dakika, ~50MB olacak)

**✅ Kontrol:**
- ZIP boyutu: ~30-50 MB
- Dosya sayısı: 60+ dosya
- İçinde: models/, static/, templates/, .py dosyaları

---

## 🌐 ADIM 2: cPANEL GİRİŞ

### 2.1 cPanel'e Eriş

**URL:** https://premium700.web-hosting.com:2083

**Giriş Bilgileri:**
- **Username:** [Namecheap cPanel username]
- **Password:** [Namecheap cPanel password]

**Not:** Bilgileri Namecheap dashboard'dan alabilirsin:
1. namecheap.com → Login
2. Dashboard → Hosting List
3. Manage → cPanel Login

---

## 🗂️ ADIM 3: MEVCUT PROJEYİ YEDEKLE

### 3.1 File Manager Aç

1. cPanel ana sayfada **File Manager** tıkla
2. Sol menüden **public_html** seç
3. Sağda tüm dosyalar görünecek

### 3.2 Yedek Klasörü Oluştur

1. Üst menüde **+ Folder** tıkla
2. Klasör adı: `backup_OLD_PROJECT`
3. Create tıkla

### 3.3 Mevcut Dosyaları Taşı

1. **public_html** içinde TÜMÜNÜ seç (Select All)
2. **SADECE** `backup_OLD_PROJECT` klasörünün seçimini kaldır (ctrl+click)
3. **SADECE** `tmp` klasörünün seçimini kaldır (varsa)
4. Üst menüde **Move** tıkla
5. Hedef: `/home/[username]/public_html/backup_OLD_PROJECT/`
6. Move File(s) tıkla

**✅ Kontrol:**
- public_html artık neredeyse boş olmalı
- Sadece `backup_OLD_PROJECT` ve `tmp` klasörleri kalmalı

---

## 📤 ADIM 4: YENİ PROJE UPLOAD

### 4.1 ZIP Upload

1. **public_html** içindesin (sol menüde seçili)
2. Üst menüde **Upload** butonuna tıkla
3. Yeni sekme açılacak
4. **Select File** veya dosyayı sürükle-bırak
5. `fastapi_project.zip` dosyasını seç
6. Upload başlayacak (2-5 dakika)
7. **100%** olunca sekmeyi kapat

**✅ Kontrol:**
- Upload tamamlandı mesajı
- Dosya boyutu görünüyor

### 4.2 ZIP Extract (Açma)

1. File Manager'a geri dön
2. `fastapi_project.zip` dosyasını bul
3. Dosyaya tıkla (seç)
4. Üst menüde **Extract** tıkla
5. Extract Path: `/home/[username]/public_html/`
6. Extract File(s) tıkla
7. Bekle (1-2 dakika)
8. Close tıkla

**✅ Kontrol:**
- Tüm klasörler görünmeli: models/, static/, templates/
- Tüm .py dosyaları görünmeli
- passenger_wsgi.py, .htaccess, requirements.txt olmalı

### 4.3 ZIP Sil (Opsiyonel)

1. `fastapi_project.zip` seç
2. **Delete** tıkla
3. Onayla

---

## 🔐 ADIM 5: DOSYA YETKİLERİ AYARLA

### 5.1 passenger_wsgi.py

1. `passenger_wsgi.py` dosyasına sağ tık
2. **Permissions** (veya **Change Permissions**)
3. **755** gir veya şunları işaretle:
   - ✅ User: Read, Write, Execute
   - ✅ Group: Read, Execute
   - ✅ World: Read, Execute
4. Change Permissions tıkla

### 5.2 .htaccess

1. `.htaccess` dosyasına sağ tık
2. Permissions
3. **644** gir veya:
   - ✅ User: Read, Write
   - ✅ Group: Read
   - ✅ World: Read
4. Change Permissions tıkla

### 5.3 Klasör Yetkileri

**models/, static/, templates/, logs/ klasörleri:**
1. Her klasöre sağ tık → Permissions
2. **755** ayarla
3. Change Permissions tıkla

---

## 🗄️ ADIM 6: MySQL DATABASE OLUŞTUR

### 6.1 cPanel → MySQL Databases

1. cPanel ana sayfaya dön (geri ok veya yeni sekme)
2. **Databases** bölümü altında **MySQL Databases** tıkla

### 6.2 Database Oluştur

**Create New Database:**
1. **New Database** alanına: `analiz_db`
2. **Create Database** tıkla
3. **Go Back** tıkla

**✅ Tam database adı:** `[cpanel_username]_analiz_db`
**Not:** Önünde otomatik eklenen prefix'i kaydet!

### 6.3 User Oluştur

**MySQL Users → Add New User:**
1. **Username:** `dbuser`
2. **Password:** [Güçlü şifre - Generate Password kullan]
3. **Şifreyi KAYDET!** (Notepad'e yapıştır)
4. **Create User** tıkla
5. **Go Back** tıkla

**✅ Tam username:** `[cpanel_username]_dbuser`

### 6.4 User'ı Database'e Ekle

**Add User To Database:**
1. **User:** `[cpanel_username]_dbuser` seç
2. **Database:** `[cpanel_username]_analiz_db` seç
3. **Add** tıkla

**Manage Privileges sayfası açılacak:**
1. **ALL PRIVILEGES** işaretle (en üstteki checkbox)
2. **Make Changes** tıkla
3. **Go Back** tıkla

**✅ Kontrol:**
- Current Databases listesinde database görünmeli
- Current Users listesinde user görünmeli
- Privileged Users'da user görünmeli

---

## ⚙️ ADIM 7: .ENV DOSYASI OLUŞTUR

### 7.1 Dosya Hazırla (Local)

1. `C:\Users\Mustafa\yenianaliz_1_yedek\.env.example` dosyasını aç
2. **Farklı Kaydet** → `.env` (uzantı .txt olmasın!)
3. Aşağıdaki bilgileri doldur:

```env
# API Keys
API_KEY=your_football_api_key_here
FOOTBALL_API_KEY=your_football_api_key_here

# Database Configuration
DB_HOST=localhost
DB_NAME=[cpanel_username]_analiz_db
DB_USER=[cpanel_username]_dbuser
DB_PASSWORD=[yukarıda oluşturduğun şifre]
DB_PORT=3306

# Application Settings
SECRET_KEY=[random 50 karakter string]
ENVIRONMENT=production
DEBUG=False

# Cache Settings
CACHE_TTL=3600
REDIS_ENABLED=False
REDIS_URL=

# ML Model Settings
MODEL_UPDATE_INTERVAL=86400
ENABLE_AUTO_RETRAIN=False

# API Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

**SECRET_KEY Oluştur (Python):**
```python
import secrets
print(secrets.token_urlsafe(50))
```

### 7.2 Upload .env

1. cPanel File Manager → **public_html**
2. **Upload** tıkla
3. `.env` dosyasını seç
4. Upload tamamlanınca sekmeyi kapat

### 7.3 .env Yetkilerini Ayarla

1. `.env` dosyasına sağ tık → Permissions
2. **600** gir (sadece owner okuyabilir)
3. Change Permissions tıkla

---

## 📝 ADIM 8: .HTACCESS DÜZENLE

### 8.1 Dosyayı Düzenle

1. File Manager'da **public_html** içinde
2. `.htaccess` dosyasına sağ tık
3. **Edit** tıkla (veya **Code Editor**)
4. Edit tıkla (yeni sekme açılacak)

### 8.2 [USERNAME] Değiştir

**Bul:**
```
/home/[USERNAME]/public_html
```

**Değiştir:**
```
/home/GERÇEK_CPANEL_USERNAME/public_html
```

**Not:** cPanel username'i şuradan bul:
- cPanel sağ üst köşede gösterilir
- Veya terminal'de `whoami` komutunu çalıştır

**Değiştirilecek 2 satır:**
```apache
PassengerAppRoot /home/GERÇEK_USERNAME/public_html
PassengerPython /home/GERÇEK_USERNAME/public_html/venv/bin/python3
```

### 8.3 Kaydet

1. **Save Changes** tıkla (üst sağda)
2. **Close** tıkla

---

## 🖥️ ADIM 9: TERMINAL İLE KURULUM

### 9.1 Terminal Aç

1. cPanel ana sayfaya dön
2. **Advanced** bölümü altında **Terminal** tıkla
3. Yeni pencerede terminal açılacak

### 9.2 Dizine Git

```bash
cd ~/public_html
pwd
```

**Çıktı:** `/home/[username]/public_html` görmelisin

### 9.3 Setup Script Çalıştır

```bash
chmod +x server-setup.sh
./server-setup.sh
```

**Script şunları yapacak:**
1. ✅ Python version kontrol
2. ✅ Virtual environment oluştur
3. ✅ Pip güncelle
4. ✅ Requirements kur (5-10 dakika)
5. ✅ Logs klasörü oluştur
6. ✅ Yetkiler ayarla

**⏳ BEKLEYİN:** 5-10 dakika sürebilir!

**✅ Başarı Mesajı:**
```
========================================
✅ KURULUM TAMAMLANDI!
========================================
```

### 9.4 Passenger Restart

```bash
mkdir -p tmp
touch tmp/restart.txt
```

**Not:** Hatalar log'da görünecek:
```bash
tail -20 logs/passenger_startup.log
```

---

## 🧪 ADIM 10: TEST VE DOĞRULAMA

### 10.1 Website Kontrolü

**Ana Sayfa:**
```
https://güvenilanaliz.com
```
veya
```
https://xn--gvenlinaliz-dlb.com
```

**Beklenen:** Sayfa yüklensin, 500 error olmasın

### 10.2 API Docs Kontrolü

```
https://güvenilanaliz.com/docs
```

**Beklenen:** 
- ✅ Swagger UI görünsün
- ✅ Tüm endpoints listelenmeli
- ✅ "Authorize" butonu olmalı

### 10.3 Health Check

```
https://güvenilanaliz.com/health
```

**Beklenen JSON:**
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "8.0.0"
}
```

### 10.4 Cache Stats

```
https://güvenilanaliz.com/cache-stats
```

**Beklenen:** Cache istatistikleri görünsün

---

## 📊 ADIM 11: LOG KONTROLÜ

### 11.1 Passenger Startup Log

**Terminal:**
```bash
cd ~/public_html
tail -30 logs/passenger_startup.log
```

**Bakılacaklar:**
- ✅ "FastAPI application started"
- ✅ "Loading models..."
- ❌ Import errors olmamalı
- ❌ Database connection errors olmamalı

### 11.2 API Log

```bash
tail -30 logs/api.log
```

**Bakılacaklar:**
- ✅ Request logları görünmeli
- ✅ Response kodları (200, 404, vs.)

### 11.3 cPanel Error Log

1. cPanel ana sayfa
2. **Metrics** → **Errors**
3. Son hataları kontrol et

**Beklenen:** Kritik hata olmamalı

---

## 🔧 SORUN GİDERME

### ❌ 500 Internal Server Error

**Kontrol Et:**
```bash
# Passenger log
tail -50 logs/passenger_startup.log

# .htaccess doğru mu?
cat .htaccess | grep PassengerAppRoot

# Yetkiler doğru mu?
ls -la passenger_wsgi.py
# Çıktı: -rwxr-xr-x olmalı (755)
```

**Çözüm:**
1. .htaccess'te [USERNAME] değiştirildi mi?
2. passenger_wsgi.py 755 yetkili mi?
3. Virtual environment kurulu mu? (`ls venv/`)

### ❌ ModuleNotFoundError

**Kontrol:**
```bash
source venv/bin/activate
pip list | grep fastapi
pip list | grep pandas
```

**Çözüm:**
```bash
pip install -r requirements.txt
touch tmp/restart.txt
```

### ❌ Database Connection Error

**Kontrol:**
```bash
cat .env | grep DB_
```

**Doğru olmalı:**
- DB_HOST=localhost
- DB_NAME=[prefix]_analiz_db
- DB_USER=[prefix]_dbuser
- DB_PASSWORD=correct_password

**Test:**
```bash
mysql -u [prefix]_dbuser -p
# Şifreyi gir
SHOW DATABASES;
# [prefix]_analiz_db görünmeli
```

### ❌ Sayfa Açılmıyor

**DNS Kontrol:**
```bash
ping güvenilanaliz.com
```

**Namecheap DNS Ayarları:**
1. Namecheap dashboard
2. Domain List → Manage
3. Advanced DNS
4. A Record → IP doğru mu?

**SSL Kontrol:**
- cPanel → SSL/TLS Status
- AutoSSL aktif mi?

---

## 📋 DEPLOYMENT SONRASI KONTROL LİSTESİ

### Temel İşlevsellik
- [ ] ✅ https://güvenilanaliz.com açılıyor
- [ ] ✅ https://güvenilanaliz.com/docs çalışıyor
- [ ] ✅ https://güvenilanaliz.com/health response veriyor
- [ ] ✅ API endpoints test edildi
- [ ] ✅ Database bağlantısı çalışıyor

### Güvenlik
- [ ] ✅ HTTPS zorunlu (HTTP redirect çalışıyor)
- [ ] ✅ .env dosyası 600 yetkili
- [ ] ✅ Directory listing kapalı
- [ ] ✅ Güvenlik headers aktif

### Logs
- [ ] ✅ passenger_startup.log yazılıyor
- [ ] ✅ api.log yazılıyor
- [ ] ✅ Error log'larda kritik hata yok

### Performans
- [ ] ✅ Ana sayfa < 3 saniye
- [ ] ✅ API response < 500ms
- [ ] ✅ Static files yükleniyor

---

## 🔄 GÜNCELLEME PROSEDÜRÜ

**Dosya Güncelleme:**
1. cPanel File Manager → public_html
2. Güncellenecek dosyaya sağ tık → Edit
3. Değişiklikleri yap
4. Save Changes
5. Terminal: `touch ~/public_html/tmp/restart.txt`
6. Test et

**Toplu Güncelleme:**
1. Yeni ZIP hazırla
2. Upload + Extract (üzerine yazar)
3. `touch tmp/restart.txt`
4. Test et

---

## 📞 DESTEK

**Namecheap Support:**
- **Live Chat:** https://www.namecheap.com/support/live-chat/
- **Email:** support@namecheap.com
- **Phone:** +1.631.409.2992

**Sık Sorulan Sorular:**
- Passenger Python app nasıl çalıştırılır?
- Virtual environment kurulumu
- Database oluşturma
- SSL sertifikası

---

## ✅ SON KONTROL

**Deployment Tamamlandı mı?**

1. [ ] Tüm dosyalar upload edildi
2. [ ] Database oluşturuldu
3. [ ] .env yapılandırıldı
4. [ ] .htaccess düzenlendi
5. [ ] Virtual environment kuruldu
6. [ ] Requirements kuruldu
7. [ ] Passenger restart yapıldı
8. [ ] Website açılıyor
9. [ ] API çalışıyor
10. [ ] Logs kontrol edildi

**🎉 BAŞARILAR! PROJE YAYINDA! 🎉**

---

## 📌 ÖNEMLİ BİLGİLER

**cPanel URL:** https://premium700.web-hosting.com:2083
**Domain:** https://güvenilanaliz.com
**API Docs:** https://güvenilanaliz.com/docs

**Database:**
- Name: [prefix]_analiz_db
- User: [prefix]_dbuser
- Host: localhost
- Port: 3306

**Project Path:** `/home/[username]/public_html/`
**Python:** `/home/[username]/public_html/venv/bin/python3`

**Restart Komutu:** `touch ~/public_html/tmp/restart.txt`

---

**Tarih:** 25 Ekim 2025
**Versiyon:** 8.0.0 (Phase 8 Complete)
