# 📝 FILEZILLA SITE MANAGER AYARLARI

## 🔧 HIZLI KURULUM

### Site Manager Konfigürasyonu

```
GENEL (General) TAB:
═══════════════════════════════════════════

Protocol:
  ☑ SFTP - SSH File Transfer Protocol
  (Daha güvenli - önerilir)
  
  veya
  
  ☐ FTP - File Transfer Protocol
  (Alternatif)

Host:
  premium700.web-hosting.com

Port:
  22  (SFTP için)
  21  (FTP için)

Encryption:
  ☐ Use explicit FTP over TLS if available
  (SFTP kullanıyorsanız gerekli değil)

Logon Type:
  ☑ Normal

User:
  [cPanel kullanıcı adınız]
  Örnek: cpanel_username

Password:
  [cPanel şifreniz]
  (Güvenlik için boş bırakabilirsiniz - her seferinde sorar)
```

```
GELİŞMİŞ (Advanced) TAB:
═══════════════════════════════════════════

Default local directory:
  C:\Users\Mustafa\yenianaliz_1_yedek\deploy_package
  (Lokal proje klasörünüz)

☑ Use synchronized browsing

Default remote directory:
  /public_html
  veya
  /home/[username]/public_html

☑ Bypass proxy

Server Type:
  ☐ Unix (Otomatik algılanır)
```

```
TRANSFER AYARLARI (Transfer Settings) TAB:
═══════════════════════════════════════════

Transfer mode:
  ☑ Default

Maximum number of connections:
  2

☐ Limit number of simultaneous connections
```

---

## 🔌 BAĞLANTI BİLGİLERİ

### Namecheap cPanel Bilgileri

```
═══════════════════════════════════════════
SFTP (Önerilen - Güvenli)
═══════════════════════════════════════════

Host:        premium700.web-hosting.com
Protocol:    SFTP (SSH)
Port:        22
Username:    [cPanel username]
Password:    [cPanel password]
Remote path: /public_html
```

```
═══════════════════════════════════════════
FTP (Alternatif)
═══════════════════════════════════════════

Host:        premium700.web-hosting.com
            veya
            ftp.güvenilanaliz.com
            ftp.xn--gvenlinaliz-dlb.com
            
Protocol:    FTP
Port:        21
Username:    [cPanel username]
Password:    [cPanel password]
Remote path: /public_html
```

---

## 📋 BİLGİLERİ NEREDEN BULACAKSINIZ?

### cPanel Username ve Password

**1. Namecheap Dashboard:**
```
1. https://www.namecheap.com
2. Sign in
3. Account → Dashboard
4. Products → Hosting List
5. "Manage" butonuna tıkla
6. "Access cPanel" altında bilgiler
```

**2. cPanel'den:**
```
https://premium700.web-hosting.com:2083
Sağ üst köşede kullanıcı adınız görünür
```

**3. Email:**
```
Namecheap'ten gelen "Hosting Activated" emaili
cPanel URL, username içerir
```

---

## ✅ BAĞLANTI TESTİ

### Adım Adım Test

**1. FileZilla Aç**
```
File → Site Manager (Ctrl+S)
```

**2. Site Ekle**
```
New Site → İsim: "Namecheap - Production"
```

**3. Bilgileri Gir**
```
Protocol: SFTP
Host: premium700.web-hosting.com
Port: 22
User: [username]
Password: [password]
```

**4. Bağlan**
```
Connect
```

**5. İlk Bağlantı Uyarısı**
```
"Unknown host key" uyarısı:
☑ Always trust this host, add this key to cache
OK
```

**6. Başarılı Bağlantı**
```
Remote site: bölümünde dosyalar görünür
Status: Connected
Directory listing: /public_html
```

---

## 🔒 GÜVENLİK AYARLARI

### Şifre Yöneticisi

```
FileZilla → Settings → Passwords

Master password protection:
☑ Use master password
[Güçlü bir master password belirle]
```

### Bağlantı Güvenliği

```
Settings → Connection → FTP

Passive mode:
☑ Use passive mode

Timeout settings:
└── Timeout in seconds: 120
```

### Güvenli Dosya Transferi

```
Settings → Transfers → File Types

Default transfer type:
☑ Binary
```

---

## 📊 TRANSFER AYARLARI

### Optimum Performans

```
Settings → Transfers

Maximum simultaneous transfers: 2

File transfer options:
☑ Skip files that are larger than 10 MB (opsiyonel)

Speed Limits:
Download: Unlimited
Upload: Unlimited
```

### Retry Ayarları

```
Settings → Connection

Number of retries: 5
Delay between retry attempts: 5 seconds
```

---

## 🎯 HIZLI ERİŞİM BOOKMARKS

### Önemli Klasörler için Bookmark

**1. public_html (Ana Dizin)**
```
Remote'ta /public_html klasörüne sağ tık
→ Add bookmark
Name: 🏠 Ana Dizin
```

**2. logs Klasörü**
```
/public_html/logs
→ Add bookmark  
Name: 📋 Logs
```

**3. models Klasörü**
```
/public_html/models
→ Add bookmark
Name: 🤖 ML Models
```

**4. tmp Klasörü**
```
/public_html/tmp
→ Add bookmark
Name: 🔄 Restart
```

### Bookmark Kullanımı

```
Bookmarks → [Bookmark adı]
Anında o klasöre gider
```

---

## 🔄 OTOMATİK SENKRONİZASYON

### Directory Comparison

```
FileZilla → View → Directory Comparison
→ ☑ Enable
→ Compare

Farklılıklar renklerle gösterilir:
🟡 Sarı: Farklı dosyalar
🟢 Yeşil: Sadece local'de var
🔵 Mavi: Sadece remote'ta var
```

### Synchronized Browsing

```
Site Manager → Advanced tab
☑ Use synchronized browsing

Her iki panelde aynı alt klasöre gidersiniz
```

---

## 🎨 GÖRSEL AYARLAR

### Renk Temaları

```
Settings → Interface → Themes

Tema seçenekleri:
- Minimal (Dark)
- Minimal (Light)  
- Default
- Tango
```

### Kolon Ayarları

```
Remote panel'de başlıklara sağ tık

Gösterilecek kolonlar:
☑ Filename
☑ Filesize
☑ Filetype
☑ Last modified
☑ Permissions
☐ Owner/Group (opsiyonel)
```

---

## 💾 YEDEKLEME STRATEJİSİ

### Deployment Öncesi Yedek

```
1. Remote'ta /public_html tümünü seç
2. Local'de yedek klasör oluştur:
   C:\backup_namecheap\[tarih]\
3. Download → Tümünü indir
4. Yedek tamamlanınca deployment başlat
```

### Kritik Dosyalar

```
Mutlaka yedekle:
├── .env
├── config.yaml
├── *.db (database dosyaları)
├── logs/ (son 7 gün)
└── models/ (ML modelleri)
```

---

## 🆘 HATA GİDERME

### Bağlantı Hataları

**"Could not connect to server"**
```
1. Host adresini kontrol et
2. Port'u kontrol et (22 veya 21)
3. Internet bağlantınızı test et
4. Firewall ayarlarını kontrol et
```

**"Authentication failed"**
```
1. Username'i kontrol et (büyük/küçük harf)
2. Password'u kontrol et
3. cPanel'den şifre sıfırla
4. Namecheap support ile iletişime geç
```

**"Connection timed out"**
```
Settings → Connection
Timeout: 120 saniye
Keepalive: 20 saniye
```

### Transfer Hataları

**"Permission denied"**
```
Remote'ta klasör yetkilerini kontrol et
Klasöre sağ tık → File permissions
Minimum: 755 (klasörler için)
```

**"File exists"**
```
Overwrite seçenekleri:
- Overwrite: Üzerine yaz
- Resume: Devam et
- Rename: Yeniden adlandır
- Skip: Atla
```

---

## 📝 KONTROL LİSTESİ

**Kurulum:**
- [ ] FileZilla indirildi ve kuruldu
- [ ] Site Manager ayarlandı
- [ ] SFTP bağlantısı test edildi
- [ ] Bookmarks oluşturuldu

**Güvenlik:**
- [ ] Master password ayarlandı
- [ ] SFTP kullanılıyor (FTP değil)
- [ ] Password kaydedilmedi (opsiyonel)

**Ayarlar:**
- [ ] Transfer ayarları optimize edildi
- [ ] Directory comparison aktif
- [ ] Synchronized browsing ayarlandı
- [ ] Timeout artırıldı

**Deployment:**
- [ ] Eski proje yedeklendi
- [ ] Yeni dosyalar yüklendi
- [ ] Dosya yetkileri ayarlandı
- [ ] .env ve .htaccess güncellendi

---

## 🎉 HAZIRSINIZ!

FileZilla ayarları tamamlandı.

**İlk Deployment:**
→ FILEZILLA_DEPLOYMENT.md dosyasını takip edin

**Hızlı Erişim:**
- Site Manager: Ctrl+S
- Quick Connect: Ctrl+Q
- Disconnect: Ctrl+D

**Başarılar! 🚀**
