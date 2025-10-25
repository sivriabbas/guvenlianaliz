# 📋 ADIM 2: FILEZILLA İLE DOSYA YÜKLEME

## 🎯 Yapılacaklar
1. FileZilla kurulumu (eğer yoksa)
2. FTP bağlantı bilgilerini al
3. Dosyaları hazırla (zip veya direkt)
4. FileZilla'da bağlantı kur
5. Dosyaları public_html'e yükle

---

## 1️⃣ FileZilla Kurulumu

**FileZilla yüklü mü?**
- **Evet** → Devam edelim
- **Hayır** → İndir: https://filezilla-project.org/download.php?type=client
  - Windows için: FileZilla_3.x_win64-setup.exe
  - Ücretsiz (Client versiyonu)

---

## 2️⃣ FTP Bağlantı Bilgilerini Al

### cPanel'den FTP Bilgilerini Bulma:

**Yöntem A: cPanel → FTP Accounts**
1. cPanel ana sayfaya dön ("Return Home")
2. **"FTP Accounts"** bul ve tıkla
3. En üstte **"Configure FTP Client"** göreceksiniz
4. Bilgileri kopyalayın

**Yöntem B: Manuel Bilgiler**

```ini
# ==========================================
# FTP CONNECTION INFO
# ==========================================
Host: ftp.xn--gvenlinaliz-dlb.com
       veya
       premium700.web-hosting.com

Username: [cPanel username - ekran görüntüsünde görünecek]
Password: [cPanel şifreniz]
Port: 21 (FTP) veya 22 (SFTP)
```

**SFTP önerilir (daha güvenli)**

---

## 3️⃣ Dosyaları Hazırla

**Yerel bilgisayarınızda:**

### Hangi dosyaları yükleyeceğiz?

```
c:\Users\Mustafa\yenianaliz_1_yedek\

YÜKLENMESİ GEREKENLER:
✅ app/ (klasör - TÜM içeriği)
✅ assets/ (klasör)
✅ passenger_wsgi.py
✅ .htaccess
✅ .env.shared_hosting (sonra .env yapacağız)
✅ requirements-shared-hosting.txt
✅ deploy-namecheap.sh

YÜKLENMEYECEKLER:
❌ __pycache__/
❌ venv/ (sunucuda oluşturulacak)
❌ .git/
❌ *.pyc
❌ debug_log.txt
❌ *.json (user_usage.json vb)
❌ docs/ (opsiyonel)
```

**ÖNEMLİ:** Tüm dosyalar zaten hazır, sadece yükleyeceğiz!

---

## 4️⃣ FileZilla Bağlantısı Kurma

### FileZilla'yı Aç:

**Üst kısımda 4 alan göreceksiniz:**

```
Host: [____________________]
Username: [___________]
Password: [___________]
Port: [____]
```

### Bağlantı Bilgilerini Gir:

**SFTP (Önerilen - Güvenli):**
```
Host: sftp://premium700.web-hosting.com
Username: [cPanel username]
Password: [cPanel şifreniz]
Port: 22
```

**veya FTP (Alternatif):**
```
Host: ftp://ftp.xn--gvenlanaliz-dlb.com
Username: [cPanel username]
Password: [cPanel şifreniz]
Port: 21
```

### Bağlan:

**"Quickconnect"** butonuna tıklayın

**İlk bağlantıda:**
- "Unknown host key" uyarısı gelecek
- **"Always trust this host"** işaretleyin
- **"OK"** tıklayın

✅ **Bağlantı başarılı olunca:**
- Sol taraf: Yerel bilgisayarınız
- Sağ taraf: Sunucu (cPanel dosyaları)

---

## 5️⃣ Dosyaları Yükleme

### Adım A: public_html Klasörüne Git

**Sağ tarafta (Remote Site):**
```
/ (root)
  └─ public_html/  ← BURAYA GİDİN
```

**public_html** klasörüne çift tıklayın

### Adım B: Yerel Dosyalara Git

**Sol tarafta (Local Site):**
```
C:\Users\Mustafa\yenianaliz_1_yedek\
```

Bu klasöre gidin

### Adım C: Dosyaları Seç ve Yükle

**Sol tarafta şu dosyaları seçin (Ctrl tuşuyla çoklu seçim):**

```
☑ app (klasör)
☑ assets (klasör)
☑ passenger_wsgi.py
☑ .htaccess
☑ .env.shared_hosting
☑ requirements-shared-hosting.txt
☑ deploy-namecheap.sh
```

**Sağ tıklayın → "Upload"**

veya

**Sürükle-bırak:** Seçili dosyaları sağ tarafa sürükleyin

### Adım D: Transfer Bekleyin

**Alt kısımda (Queue/Transfer) göreceksiniz:**
- Hangi dosyalar yükleniyor
- Transfer hızı
- Kalan süre

**Upload süresi:** ~2-5 dakika (internet hızınıza bağlı)

---

## 6️⃣ Doğrulama

**Sağ tarafta (public_html) şunları görmeli:**

```
public_html/
├── app/
│   ├── app.py
│   ├── api_utils.py
│   ├── elo_utils.py
│   ├── cron_daily_reset.py
│   ├── cron_elo_update.py
│   └── ...
├── assets/
├── passenger_wsgi.py
├── .htaccess
├── .env.shared_hosting
├── requirements-shared-hosting.txt
└── deploy-namecheap.sh
```

✅ Tüm dosyalar görünüyorsa **BAŞARILI!**

---

## 7️⃣ İzinleri Kontrol Et (Önemli)

**Sağ tarafta (sunucuda):**

### passenger_wsgi.py izinleri:
1. **passenger_wsgi.py** sağ tıkla → **"File Permissions"**
2. **Numeric value: 755** olmalı
3. Checkboxlar: `rwxr-xr-x`
4. **OK** tıkla

### deploy-namecheap.sh izinleri:
1. **deploy-namecheap.sh** sağ tıkla → **"File Permissions"**
2. **Numeric value: 755** olmalı
3. **OK** tıkla

### app klasörü izinleri:
1. **app/** klasörü sağ tıkla → **"File Permissions"**
2. **Numeric value: 755** olmalı
3. **Recurse into subdirectories** işaretle
4. **OK** tıkla

---

## ✅ Dosya Yükleme Tamamlandı!

**Başardınız!** 🎉

---

## 🎯 Sonraki Adım: Environment Variables

Şimdi `.env` dosyasını düzenleyeceğiz:
- `.env.shared_hosting` → `app/.env` olarak kopyala
- Database credentials ekle
- Secret keys oluştur

**Hazırsanız devam edelim!** 🚀

---

## ❓ Sorun Yaşarsanız

### ❌ Bağlantı hatası (Connection refused)
**Çözüm:**
- SFTP yerine FTP deneyin (Port 21)
- Host: `ftp.xn--gvenlanaliz-dlb.com`

### ❌ Login hatası (530 Login incorrect)
**Çözüm:**
- cPanel username/password kontrol edin
- Namecheap dashboard'dan credentials'ı alın

### ❌ Permission denied (Upload hatası)
**Çözüm:**
- public_html klasörüne yazma izniniz olmalı
- cPanel → File Manager'dan izinleri kontrol edin

---

**Upload tamamlandı mı? "Yükleme bitti" yazın, devam edelim!**
