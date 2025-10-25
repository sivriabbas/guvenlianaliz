# 🚀 NAMECHEAP FASTAPI DEPLOYMENT - ÖZET

## ✅ HAZIRLIK TAMAMLANDI!

Deployment paketi oluşturuldu: **`deploy_package/`** klasörü

---

## 📦 PAKET İÇERİĞİ

```
deploy_package/
├── simple_fastapi.py          # Ana FastAPI uygulaması
├── passenger_wsgi.py           # WSGI entry point
├── .htaccess                   # Apache config
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── config.yaml                 # App configuration
├── [40+ Python modülleri]      # Tüm API modülleri
├── models/                     # ML modeller (4 dosya)
├── static/                     # CSS, JS, images (4 dosya)
└── templates/                  # HTML templates (10 dosya)
```

**Toplam:** ~60 dosya, ~50MB

---

## 🎯 DEPLOYMENT ADIMLARI

### ADIM 1: ZIP OLUŞTUR
```
1. deploy_package\ klasörüne git
2. Tüm dosyaları seç (Ctrl+A)
3. Sağ tık → Send to → Compressed (zipped) folder
4. İsim: fastapi_deploy.zip
```

### ADIM 2: NAMECHEAP cPANEL
```
🌐 URL: https://premium700.web-hosting.com:2083
👤 Username: [Namecheap hesabından al]
🔑 Password: [Namecheap hesabından al]
```

### ADIM 3: ESKİ PROJEYİ TEMİZLE
```
cPanel → File Manager → public_html/

1. Tüm dosyaları seç
2. Compress → backup_$(date).zip
3. İndir ve güvenli yere kaydet
4. Tüm dosyaları sil
```

### ADIM 4: YENİ PROJEYİ YÜKLE
```
1. Upload → fastapi_deploy.zip seç
2. Bekle (upload tamamlansın)
3. fastapi_deploy.zip'e sağ tık → Extract
4. Extract Path: /home/[username]/public_html
5. Extract Files
```

### ADIM 5: VERITABANI
```
cPanel → MySQL® Databases

Database:
  Name: analiz_db
  
User:
  Username: dbuser
  Password: [GÜVENLİ ŞİFRE - KAYDET!]
  
Privileges: ALL PRIVILEGES
```

### ADIM 6: SUNUCU KURULUMU
```bash
# cPanel Terminal veya SSH
cd ~/public_html
chmod +x server-setup.sh
./server-setup.sh

# .env oluştur
cp .env.example .env
nano .env

# İçeriği doldur:
API_KEY=your_api_key
DB_NAME=[prefix]_analiz_db
DB_USER=[prefix]_dbuser
DB_PASSWORD=[database şifresi]
SECRET_KEY=random_secret_key
```

### ADIM 7: .HTACCESS GÜNCELLEe
```bash
nano .htaccess

# Değiştir:
[USERNAME] → gerçek_kullanıcı_adın

# Kullanıcı adı öğren:
whoami
```

### ADIM 8: BAŞLAT
```bash
touch ~/public_html/tmp/restart.txt
```

### ADIM 9: TEST
```
✅ https://güvenilanaliz.com
✅ https://güvenilanaliz.com/docs
✅ https://güvenilanaliz.com/health
```

---

## 📋 KONTROL LİSTESİ

- [ ] deploy_package ZIP'lendi
- [ ] cPanel'e giriş yapıldı
- [ ] Eski proje yedeklendi ve silindi
- [ ] Yeni proje yüklendi ve extract edildi
- [ ] Database oluşturuldu (analiz_db)
- [ ] Database user oluşturuldu (dbuser)
- [ ] server-setup.sh çalıştırıldı
- [ ] Virtual environment kuruldu
- [ ] Requirements kuruldu
- [ ] .env dosyası oluşturuldu ve dolduruldu
- [ ] .htaccess'te [USERNAME] değiştirildi
- [ ] tmp/restart.txt oluşturuldu
- [ ] Website açıldı
- [ ] /docs çalışıyor
- [ ] Loglar kontrol edildi

---

## 📝 ÖNEMLİ NOTLAR

### Database Bilgileri (Kaydet!)
```
Host: localhost
Database: [prefix]_analiz_db
User: [prefix]_dbuser
Password: ________________
Port: 3306
```

### cPanel Bilgileri
```
URL: https://premium700.web-hosting.com:2083
Username: ________________
Password: ________________
```

### Domain
```
Ana Domain: https://güvenilanaliz.com
Alternatif: https://xn--gvenlinaliz-dlb.com
```

---

## 🔧 SORUN GİDERME

### 500 Error
```bash
tail -20 ~/logs/[domain]_error_log
tail -20 ~/public_html/logs/passenger_startup.log
```

### Module Not Found
```bash
source ~/public_html/venv/bin/activate
pip install -r requirements.txt
```

### Permission Error
```bash
chmod 755 passenger_wsgi.py
chmod 644 .htaccess
chmod 600 .env
```

---

## 📚 DETAYLI DOKÜMANTASYON

- **Hızlı Başlangıç:** `QUICKSTART_NAMECHEAP.md`
- **Detaylı Adımlar:** `NAMECHEAP_FASTAPI_DEPLOYMENT.md`
- **Genel Bilgiler:** `NAMECHEAP_DEPLOYMENT.md`

---

## 🆘 DESTEK

**Namecheap Support:**
- 💬 Live Chat: 24/7
- 📧 Email: support@namecheap.com
- 📞 Tel: +1.631.409.2992

**Technical Issues:**
1. Error logs kontrol et
2. Passenger logs incele
3. cPanel support ile iletişime geç
4. Documentation'ı oku

---

## ✨ SON KONTROL

Başarılı deployment için:

```bash
# 1. Website açılıyor mu?
curl -I https://güvenilanaliz.com

# 2. API docs çalışıyor mu?
curl https://güvenilanaliz.com/docs

# 3. Health check OK mu?
curl https://güvenilanaliz.com/health

# 4. Logs temiz mi?
tail -10 ~/public_html/logs/api.log
```

---

## 🎉 BAŞARILI DEPLOYMENT!

Projeniz artık canlı:
- 🌐 **Website:** https://güvenilanaliz.com
- 📚 **API Docs:** https://güvenilanaliz.com/docs
- 🏥 **Health:** https://güvenilanaliz.com/health

**Tebrikler! 🚀**
