# 🚀 FILEZILLA İLE NAMECHEAP DEPLOYMENT

## 📋 GEREKLİ BİLGİLER

### FTP/SFTP Bağlantı Bilgileri
```
Host: premium700.web-hosting.com
    veya ftp.güvenilanaliz.com
    veya ftp.xn--gvenlinaliz-dlb.com

Protocol: FTP (Port 21) veya SFTP (Port 22)
Username: [cPanel kullanıcı adınız]
Password: [cPanel şifreniz]
Port: 21 (FTP) veya 22 (SFTP)
```

**Not:** SFTP daha güvenlidir, tercih edin!

---

## 🔧 ADIM 1: FILEZILLA KURULUMU

### 1.1 FileZilla İndir
```
https://filezilla-project.org/download.php?type=client

Windows için: FileZilla_3.x.x_win64-setup.exe
```

### 1.2 Kur ve Başlat
- Standart kurulum yapın
- FileZilla Client'ı açın

---

## 🔌 ADIM 2: SUNUCUYA BAĞLAN

### 2.1 Site Manager Aç
```
File → Site Manager (Ctrl+S)
veya üst menüden Site Manager ikonuna tıkla
```

### 2.2 Yeni Site Ekle
1. **New Site** butonuna tıkla
2. İsim ver: "Namecheap - Güvenilanaliz"

### 2.3 Bağlantı Ayarları
```
General Tab:
├── Protocol: SFTP - SSH File Transfer Protocol (ÖNERİLEN)
│   veya FTP - File Transfer Protocol
├── Host: premium700.web-hosting.com
├── Port: 22 (SFTP) veya 21 (FTP)
├── Logon Type: Normal
├── User: [cPanel username - Namecheap'ten al]
└── Password: [cPanel password]

Advanced Tab:
├── Default remote directory: /public_html
└── Default local directory: C:\Users\Mustafa\yenianaliz_1_yedek\deploy_package
```

### 2.4 Bağlan
1. **Connect** butonuna tıkla
2. İlk bağlantıda "Unknown host key" uyarısı gelirse → **OK** / **Always trust this host**
3. Bağlantı kuruldu ✅

---

## 📦 ADIM 3: ESKİ PROJEYİ YEDEKLE

### 3.1 Remote (Sağ Panel) - Sunucu
```
/public_html dizinine git
```

### 3.2 Tüm Dosyaları İndir (Yedek)
1. Remote panelde `/public_html` içindeki **TÜM DOSYALARI** seç
2. Sağ tık → **Download**
3. Lokal dizin seç: `C:\backup_namecheap\backup_$(date)\`
4. İndirme tamamlanana kadar bekle

**Alternatif:** Sadece önemli dosyaları yedekle:
- `.env` (mevcut environment variables)
- `config.yaml` (mevcut konfigürasyon)
- Veritabanı yedekleri

### 3.3 Sunucudaki Dosyaları Sil
1. Remote panelde `/public_html` içindeki tüm dosyaları seç
2. **İSTİSNA:** `tmp/` klasörünü SILME (varsa)
3. Sağ tık → **Delete**
4. Onay ver → **Yes**

---

## ⬆️ ADIM 4: YENİ PROJEYİ YÜKLE

### 4.1 Local (Sol Panel) - Bilgisayarınız
```
C:\Users\Mustafa\yenianaliz_1_yedek\deploy_package\
```

### 4.2 Dosya Seçimi
**deploy_package klasöründeki TÜM DOSYALARI seç:**
```
Ctrl+A (Tümünü seç)

Seçilmesi gerekenler:
├── simple_fastapi.py
├── passenger_wsgi.py
├── .htaccess
├── requirements.txt (.env değil!)
├── config.yaml
├── .env.example
├── [40+ Python dosyaları]
├── models/ (klasör)
├── static/ (klasör)
└── templates/ (klasör)
```

**ÖNEMLI:** `.env` dosyasını yüklemeyin! Sunucuda oluşturacaksınız.

### 4.3 Upload Başlat
```
1. Local panelde dosyaları seç (Ctrl+A)
2. Sağ tık → Add files to queue
   veya drag & drop yapın (sürükle bırak)
3. Transfer başlar
```

### 4.4 Upload Takibi
```
Alt panelde transfer durumunu izleyin:
├── Queued files: Bekleyen dosyalar
├── Failed transfers: Başarısız (varsa tekrar dene)
└── Successful transfers: Başarılı

Bekleme süresi: ~5-15 dakika (bağlantı hızına göre)
```

---

## 🔒 ADIM 5: DOSYA YETKİLERİNİ AYARLA

### 5.1 FileZilla'dan Yetki Ayarlama
```
Remote panelde dosyaya sağ tık → File permissions

passenger_wsgi.py:
├── Numeric value: 755
├── Owner: Read, Write, Execute
├── Group: Read, Execute
└── Public: Read, Execute

.htaccess:
├── Numeric value: 644
├── Owner: Read, Write
├── Group: Read
└── Public: Read

simple_fastapi.py ve diğer .py dosyaları:
└── Numeric value: 644
```

### 5.2 Toplu Yetki Ayarlama
```
1. Tüm .py dosyalarını seç
2. Sağ tık → File permissions
3. 644 gir
4. Apply to all selected files → OK

passenger_wsgi.py için ayrıca:
1. passenger_wsgi.py seç
2. File permissions → 755
```

---

## 🗂️ ADIM 6: GEREKLI KLASÖRLERI OLUŞTUR

### 6.1 FileZilla ile Klasör Oluştur
```
Remote panelde /public_html içinde:
Sağ tık → Create directory

Oluşturulacak klasörler:
├── tmp/          (Passenger restart için)
├── logs/         (Log dosyaları için)
└── venv/         (Virtual environment - SSH'ta oluşturulacak)
```

### 6.2 restart.txt Oluştur
```
1. tmp/ klasörüne git
2. Sağ tık → Create directory
3. İsim: (boş bırak, sadece OK)
4. Sağ tık → Create file
5. İsim: restart.txt
```

---

## ⚙️ ADIM 7: .ENV DOSYASI OLUŞTUR

### 7.1 .env.example'ı İndir
```
Remote panelde .env.example bulun
Sağ tık → Download
Lokal'e kaydet
```

### 7.2 Lokal'de .env Oluştur
```
1. .env.example'ı kopyala
2. İsim: .env
3. Düzenle (Notepad++ veya VS Code):

API_KEY=your_api_football_key_here
DB_HOST=localhost
DB_NAME=[prefix]_analiz_db
DB_USER=[prefix]_dbuser
DB_PASSWORD=[veritabanı_şifreniz]
DB_PORT=3306
SECRET_KEY=[rastgele_uzun_anahtar]
ENVIRONMENT=production
DEBUG=False
REDIS_ENABLED=False
```

### 7.3 .env'i Yükle
```
1. FileZilla'da lokal .env dosyasını seç
2. Remote /public_html'e drag & drop
3. Upload tamamlandı
4. Remote'ta .env'e sağ tık → File permissions → 600
```

---

## 🔧 ADIM 8: .HTACCESS'İ DÜZENLE

### 8.1 .htaccess'i İndir
```
Remote'ta .htaccess'e sağ tık → View/Edit
FileZilla built-in editor açılır
```

### 8.2 [USERNAME] Değiştir
```apache
# Değiştir:
/home/[USERNAME]/public_html
/home/[USERNAME]/public_html/venv/bin/python3

# Şununla (kullanıcı adınızla):
/home/gerçek_kullanıcı_adı/public_html
/home/gerçek_kullanıcı_adı/public_html/venv/bin/python3
```

**Kullanıcı adını öğren:**
- cPanel → sağ üst köşe
- veya SSH: `whoami`

### 8.3 Kaydet ve Yükle
```
File → Save (Ctrl+S)
Kapatınca FileZilla "Upload to server?" sorar → Yes
```

---

## 🐍 ADIM 9: SSH İLE PYTHON KURULUMU

FileZilla ile dosya transferi tamamlandı. Şimdi SSH gerekiyor:

### 9.1 SSH Bağlantısı

**Seçenek 1: cPanel Terminal**
```
cPanel → Terminal (arama yapın)
Otomatik bağlanır
```

**Seçenek 2: PuTTY (Windows)**
```
Download: https://putty.org
Host: premium700.web-hosting.com
Port: 22
Username: [cPanel username]
Password: [cPanel password]
```

### 9.2 Setup Script Çalıştır
```bash
cd ~/public_html
chmod +x server-setup.sh
./server-setup.sh
```

**Script şunları yapar:**
- Python3 version kontrol
- Virtual environment oluşturur
- Requirements kurar
- Klasör yetkilerini ayarlar
- Logs klasörü oluşturur

---

## ✅ ADIM 10: TEST ET

### 10.1 Passenger'ı Başlat
```bash
touch ~/public_html/tmp/restart.txt
```

### 10.2 Website Testi
```
Tarayıcıda aç:
✅ https://güvenilanaliz.com
✅ https://güvenilanaliz.com/docs
✅ https://güvenilanaliz.com/health
```

### 10.3 FileZilla ile Log Kontrol
```
Remote'ta:
1. logs/ klasörüne git
2. passenger_startup.log'a sağ tık → View
3. api.log'a sağ tık → View
4. Hata var mı kontrol et
```

---

## 🔄 GÜNCELLEME YAPMAK

### Tek Dosya Güncellemesi
```
1. FileZilla'da lokal dosyayı seç
2. Remote'a drag & drop
3. "File exists" → Overwrite → OK
4. SSH: touch ~/public_html/tmp/restart.txt
```

### Çoklu Dosya Güncellemesi
```
1. Değişen dosyaları lokal'de seç
2. Remote'a upload
3. Passenger restart
```

### Otomatik Senkronizasyon
```
FileZilla → Tools → Directory Comparison
└── Enable → Compare → Upload changed files
```

---

## 🔍 SORUN GİDERME

### Upload Başarısız
```
FileZilla → Transfer → Failed transfers
Sağ tık → Reset and requeue all
Tekrar dene
```

### Bağlantı Kopuyor
```
Edit → Settings → Connection
├── Timeout: 120 seconds
├── Number of retries: 5
└── Keepalive: 20 seconds
```

### Dosya Bulunamıyor
```
View → Show hidden files (Ctrl+H)
.env, .htaccess gibi gizli dosyalar görünür
```

### Yetki Hatası
```
passenger_wsgi.py → 755
.htaccess → 644
.env → 600
Diğer .py → 644
```

---

## 📋 FILEZILLA KONTROL LİSTESİ

**Bağlantı:**
- [ ] FileZilla kuruldu
- [ ] Site Manager ayarlandı
- [ ] SFTP bağlantısı başarılı

**Yedekleme:**
- [ ] Eski dosyalar indirildi
- [ ] Yedek güvenli yerde

**Upload:**
- [ ] deploy_package tüm dosyalar yüklendi
- [ ] Klasörler oluşturuldu (tmp, logs)
- [ ] restart.txt oluşturuldu

**Konfigürasyon:**
- [ ] .env oluşturuldu ve yüklendi
- [ ] .htaccess [USERNAME] değiştirildi
- [ ] Dosya yetkileri ayarlandı

**Python Setup:**
- [ ] SSH bağlantısı yapıldı
- [ ] server-setup.sh çalıştırıldı
- [ ] Virtual environment kuruldu
- [ ] Requirements kuruldu

**Test:**
- [ ] Website açılıyor
- [ ] /docs çalışıyor
- [ ] Logs temiz

---

## 💡 İPUÇLARI

### Hızlı Upload İçin
```
Settings → Transfers
├── Maximum simultaneous transfers: 2
├── File transfer options → Skip files that are larger than 10MB
└── Speed Limits: Unlimited
```

### Güvenli Çalışma
```
1. Her zaman yedek alın
2. .env'i local'de saklamayın (gitignore)
3. SFTP kullanın (FTP değil)
4. Önemli dosyalar için bookmark oluşturun
```

### Bookmark Oluştur
```
Remote'ta /public_html'e sağ tık → Add bookmark
İsim: public_html
Hızlı erişim için Bookmarks menüsünden seç
```

---

## 🎉 BAŞARILI!

FileZilla ile deployment tamamlandı!

**Erişim:**
- 🌐 Website: https://güvenilanaliz.com
- 📚 API Docs: https://güvenilanaliz.com/docs
- 📊 Cache Stats: https://güvenilanaliz.com/cache-stats

**Güncelleme:**
1. Lokal'de değişiklik yap
2. FileZilla ile upload et
3. SSH: `touch ~/public_html/tmp/restart.txt`

**Başarılar! 🚀**
