# ✅ NAMECHEAP DEPLOYMENT - KOMPLE CHECKLIST

## 📅 Deployment Tarihi: _____________

---

## 🎯 DEPLOYMENT SÜRECİ

### BÖLÜM 1: HAZIRLIK (Local) ✅

**Deployment Paketi:**
- [ ] `prepare-deployment.bat` çalıştırıldı
- [ ] `deploy_package/` klasörü oluşturuldu
- [ ] Tüm dosyalar kopyalandı (60+ dosya)
- [ ] Models klasörü dahil (4 dosya)
- [ ] Static klasörü dahil (4 dosya)
- [ ] Templates klasörü dahil (10 dosya)

**FileZilla Kurulum:**
- [ ] FileZilla indirildi
- [ ] FileZilla kuruldu
- [ ] Site Manager ayarlandı

**Bilgiler Toplandı:**
- [ ] cPanel username: _______________
- [ ] cPanel password: _______________
- [ ] FTP/SFTP host: premium700.web-hosting.com
- [ ] Domain: güvenilanaliz.com

---

### BÖLÜM 2: FILEZILLA BAĞLANTI ✅

**Site Manager Ayarları:**
- [ ] Protocol: SFTP seçildi
- [ ] Host: premium700.web-hosting.com
- [ ] Port: 22
- [ ] Username girildi
- [ ] Password girildi
- [ ] Default remote directory: /public_html
- [ ] Default local directory: deploy_package path

**Bağlantı Testi:**
- [ ] Connect butonuna tıklandı
- [ ] "Unknown host key" onaylandı
- [ ] Bağlantı başarılı
- [ ] Remote /public_html görünüyor

---

### BÖLÜM 3: YEDEKLEME ✅

**Eski Projeyi Yedekle:**
- [ ] Remote /public_html tümü seçildi
- [ ] Local yedek klasörü oluşturuldu
- [ ] Download başlatıldı
- [ ] Tüm dosyalar indirildi
- [ ] Yedek doğrulandı

**Kritik Dosyalar:**
- [ ] .env yedeklendi (varsa)
- [ ] config.yaml yedeklendi (varsa)
- [ ] Database dosyaları yedeklendi (varsa)

**Sunucuyu Temizle:**
- [ ] Remote /public_html tüm dosyalar seçildi
- [ ] Delete yapıldı (tmp/ hariç)
- [ ] Silme tamamlandı
- [ ] Dizin temiz

---

### BÖLÜM 4: YENİ PROJE UPLOAD ✅

**Dosya Transferi:**
- [ ] Local deploy_package açıldı
- [ ] Tüm dosyalar seçildi (Ctrl+A)
- [ ] Remote /public_html'e drag & drop
- [ ] Upload başladı
- [ ] Transfer tamamlandı
- [ ] Failed transfers kontrol edildi (0 olmalı)

**Klasör Kontrolü:**
- [ ] models/ klasörü yüklendi
- [ ] static/ klasörü yüklendi
- [ ] templates/ klasörü yüklendi
- [ ] Tüm .py dosyaları yüklendi

**Ek Klasörler Oluştur:**
- [ ] tmp/ klasörü oluşturuldu
- [ ] logs/ klasörü oluşturuldu
- [ ] tmp/restart.txt oluşturuldu

---

### BÖLÜM 5: DOSYA YETKİLERİ ✅

**Kritik Dosyalar:**
- [ ] passenger_wsgi.py → 755
- [ ] .htaccess → 644
- [ ] simple_fastapi.py → 644
- [ ] Diğer .py dosyaları → 644

**Klasörler:**
- [ ] models/ → 755
- [ ] static/ → 755
- [ ] templates/ → 755
- [ ] logs/ → 755
- [ ] tmp/ → 755

---

### BÖLÜM 6: DATABASE KURULUMU ✅

**cPanel → MySQL Databases:**
- [ ] cPanel'e giriş yapıldı
- [ ] MySQL Databases açıldı

**Create Database:**
- [ ] Database name: analiz_db
- [ ] Create Database tıklandı
- [ ] Full name kaydedildi: _____________analiz_db

**Create User:**
- [ ] Username: dbuser
- [ ] Password oluşturuldu (güçlü)
- [ ] Password kaydedildi: _______________
- [ ] Create User tıklandı
- [ ] Full username kaydedildi: _____________dbuser

**Add User to Database:**
- [ ] User seçildi
- [ ] Database seçildi
- [ ] Add tıklandı
- [ ] ALL PRIVILEGES seçildi
- [ ] Make Changes tıklandı

---

### BÖLÜM 7: .ENV DOSYASI ✅

**Dosya Oluşturma:**
- [ ] Local'de .env.example açıldı
- [ ] .env olarak kaydedildi
- [ ] Aşağıdaki bilgiler dolduruldu:

```
API_KEY: _______________
DB_HOST: localhost
DB_NAME: _______________analiz_db
DB_USER: _______________dbuser
DB_PASSWORD: _______________
DB_PORT: 3306
SECRET_KEY: _______________
ENVIRONMENT: production
DEBUG: False
REDIS_ENABLED: False
```

**Upload:**
- [ ] .env FileZilla ile yüklendi
- [ ] Remote'ta .env görünüyor
- [ ] File permissions → 600 ayarlandı

---

### BÖLÜM 8: .HTACCESS DÜZENLEME ✅

**Düzenleme:**
- [ ] Remote .htaccess'e sağ tık → View/Edit
- [ ] [USERNAME] bulundu

**Değiştir:**
- [ ] /home/[USERNAME]/ → /home/gerçek_username/
- [ ] Her iki satırda değiştirildi
- [ ] Kaydet (Ctrl+S)
- [ ] Upload to server → Yes

**Gerçek Username:** _______________

---

### BÖLÜM 9: SSH KURULUM ✅

**SSH Bağlantısı:**

**Seçenek A - cPanel Terminal:**
- [ ] cPanel → Terminal açıldı
- [ ] cd ~/public_html

**Seçenek B - PuTTY:**
- [ ] PuTTY açıldı
- [ ] Host: premium700.web-hosting.com
- [ ] Port: 22
- [ ] Login başarılı
- [ ] cd ~/public_html

**Setup Script:**
```bash
chmod +x server-setup.sh
./server-setup.sh
```

- [ ] Script çalıştırıldı
- [ ] Python version görüldü: _______________
- [ ] Virtual environment oluşturuldu
- [ ] Pip güncellendi
- [ ] Requirements kuruldu
- [ ] Klasörler oluşturuldu
- [ ] Yetkiler ayarlandı
- [ ] ✅ KURULUM TAMAMLANDI mesajı görüldü

**Kurulum Süresi:** _______________ dakika

---

### BÖLÜM 10: PASSENGER BAŞLATMA ✅

**Restart:**
```bash
touch ~/public_html/tmp/restart.txt
```

- [ ] Komut çalıştırıldı
- [ ] Hata yok

**İlk Başlatma (1-2 dakika bekle)**
- [ ] Beklendi

---

### BÖLÜM 11: TEST VE DOĞRULAMA ✅

**Website Test:**
- [ ] https://güvenilanaliz.com açıldı
- [ ] Ana sayfa yüklendi
- [ ] 500 error yok
- [ ] 404 error yok

**API Docs Test:**
- [ ] https://güvenilanaliz.com/docs açıldı
- [ ] Swagger UI görünüyor
- [ ] Endpoints listeleniyor

**Health Check:**
- [ ] https://güvenilanaliz.com/health çalışıyor
- [ ] Status: OK

**Additional Endpoints:**
- [ ] /cache-stats açılıyor
- [ ] /api/health çalışıyor

---

### BÖLÜM 12: LOG KONTROLÜ ✅

**SSH/Terminal:**
```bash
tail -20 ~/public_html/logs/passenger_startup.log
```
- [ ] Log dosyası var
- [ ] "FastAPI application started" görünüyor
- [ ] Import errors yok

```bash
tail -20 ~/public_html/logs/api.log
```
- [ ] Log dosyası var
- [ ] Request logları görünüyor

**cPanel Error Log:**
- [ ] cPanel → Metrics → Errors
- [ ] Son hatalar kontrol edildi
- [ ] Kritik hata yok

---

### BÖLÜM 13: PERFORMANS TESTİ ✅

**Hız Testi:**
- [ ] Ana sayfa yükleme: _____ saniye
- [ ] API response: _____ ms
- [ ] Docs yükleme: _____ saniye

**Database Bağlantı:**
- [ ] Database sorguları çalışıyor
- [ ] Connection error yok

**Static Files:**
- [ ] CSS yükleniyor
- [ ] JS çalışıyor
- [ ] Images görünüyor

---

## 🎯 SON KONTROL

### Temel İşlevsellik
- [ ] ✅ Website erişilebilir
- [ ] ✅ HTTPS çalışıyor
- [ ] ✅ API endpoints yanıt veriyor
- [ ] ✅ Database bağlantısı OK
- [ ] ✅ Logs yazılıyor
- [ ] ✅ Static files yükleniyor

### Güvenlik
- [ ] ✅ HTTPS zorunlu
- [ ] ✅ .env dosyası 600 yetkili
- [ ] ✅ Security headers aktif
- [ ] ✅ Directory listing kapalı

### Performans
- [ ] ✅ Sayfa yüklenme < 3 saniye
- [ ] ✅ API response < 500ms
- [ ] ✅ Gzip compression aktif
- [ ] ✅ Static file caching aktif

---

## 📊 DEPLOYMENT BİLGİLERİ

**Deployment Tarihi:** _______________
**Deployment Saati:** _______________
**Toplam Süre:** _____ dakika

**Deployment Eden:** _______________
**Versiyon:** 8.0.0 (Phase 8 Complete)

**Sorunlar (varsa):**
_________________________________________
_________________________________________
_________________________________________

**Notlar:**
_________________________________________
_________________________________________
_________________________________________

---

## 🔄 GÜNCEL TUTMA

**Düzenli Kontroller:**
- [ ] Her hafta logs kontrol et
- [ ] Her ay backup al
- [ ] Güvenlik güncellemelerini izle
- [ ] Performance metrics incele

**Güncelleme Prosedürü:**
1. Local'de değişiklik yap
2. FileZilla ile upload et
3. `touch ~/public_html/tmp/restart.txt`
4. Test et
5. Logs kontrol et

---

## ✅ DEPLOYMENT TAMAMLANDI!

**Proje Canlı:** https://güvenilanaliz.com

**Onay İmzası:** _______________
**Tarih:** _______________

---

## 🆘 DESTEK BİLGİLERİ

**Namecheap Support:**
- Live Chat: 24/7
- Email: support@namecheap.com
- Phone: +1.631.409.2992

**Dokümantasyon:**
- FILEZILLA_DEPLOYMENT.md
- FILEZILLA_SETUP.md
- NAMECHEAP_FASTAPI_DEPLOYMENT.md
- QUICKSTART_NAMECHEAP.md

**Backup Lokasyonu:**
C:\backup_namecheap\[tarih]\

---

**🎉 BAŞARILAR! DEPLOYMENT TAMAMLANDI! 🎉**
