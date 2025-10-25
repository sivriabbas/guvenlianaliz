# 🚀 ADIM 4: DEPLOYMENT SCRIPT ÇALIŞTIRMA

## 🎯 Şimdi Ne Yapacağız?

`deploy-namecheap.sh` script'i çalıştırarak:
- ✅ Virtual environment oluşturacağız
- ✅ Python dependencies yükleyeceğiz
- ✅ Database'i initialize edeceğiz
- ✅ Passenger'ı başlatacağız

---

## 📋 ADIM ADIM TALİMATLAR

### 1️⃣ **cPanel Terminal'i Açın**

**cPanel ana sayfaya dönün:**
- File Manager'da sağ üstte **cPanel** logosuna tıklayın
- veya tarayıcıda yeni sekme: cPanel dashboard

**Terminal'i bulun:**
1. cPanel'de arama kutusuna **"Terminal"** yazın
2. **"Terminal"** ikonuna tıklayın
3. veya **Advanced** bölümünde **"Terminal"** bulun

✅ **Terminal ekranı açılacak (siyah ekran)**

---

### 2️⃣ **public_html Klasörüne Gidin**

Terminal'de şu komutu yazın:

```bash
cd ~/public_html
```

**Enter'a basın**

**Doğrulama - nerede olduğunuzu görmek için:**
```bash
pwd
```

**Çıktı şöyle olmalı:**
```
/home/xnggkta/public_html
```

---

### 3️⃣ **Dosyaları Kontrol Edin**

```bash
ls -la
```

**Görmeniz gerekenler:**
```
app/
assets/
deploy-namecheap.sh
passenger_wsgi.py
.htaccess
.env.shared_hosting
requirements-shared-hosting.txt
```

✅ **Hepsi varsa devam**

---

### 4️⃣ **deploy-namecheap.sh İzinlerini Kontrol**

```bash
chmod +x deploy-namecheap.sh
```

**Bu komut script'i çalıştırılabilir yapar**

---

### 5️⃣ **Deployment Script'i Çalıştırın**

```bash
./deploy-namecheap.sh
```

**⏳ Script çalışmaya başlayacak (~10 dakika):**

**Göreceğiniz adımlar:**
```
==========================================
Güvenilir Analiz - Namecheap Deployment
==========================================

1️⃣  Environment kontrol ediliyor...
✓ Python version: 3.x

2️⃣  Mevcut dosyalar yedekleniyor...

3️⃣  Virtual environment oluşturuluyor...
✓ Virtual environment oluşturuldu

4️⃣  pip güncelleniyor...
✓ pip güncellendi

5️⃣  Dependencies yükleniyor...
⏳ Bu işlem 5-10 dakika sürebilir...
```

**⚠️ ÖNEMLİ:** Script çalışırken terminal'i kapatmayın!

---

### 6️⃣ **Script Başarıyla Biterse**

**En son göreceğiniz:**
```
==========================================
✅ DEPLOYMENT TAMAMLANDI!
==========================================

📋 Deployment Bilgileri:
  - Virtual env: ~/public_html/venv
  - App location: ~/public_html/app

🌐 URL'ler:
  - Ana Sayfa: https://xn--gvenlinaliz-dlb.com
  - API Docs: https://xn--gvenlinaliz-dlb.com/docs
  - Health: https://xn--gvenlinaliz-dlb.com/api/ml/health

🎉 Deployment script tamamlandı!
```

---

## ⚠️ Olası Hatalar ve Çözümler

### ❌ Hata: "python3: command not found"

**Çözüm:** Python version kontrol
```bash
python --version
python3 --version
python3.10 --version
```

Hangi komut çalışıyorsa, `deploy-namecheap.sh` dosyasını düzenleyin:
- File Manager → deploy-namecheap.sh → Edit
- `python3` yerine çalışan versiyonu yazın

---

### ❌ Hata: "Permission denied"

**Çözüm:**
```bash
chmod +x deploy-namecheap.sh
chmod -R 755 app/
```

---

### ❌ Hata: "No module named 'pymysql'"

**Çözüm:** Dependencies manuel yükleme
```bash
cd ~/public_html
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-shared-hosting.txt
```

---

### ❌ Hata: "Database connection failed"

**Çözüm:** .env kontrol
```bash
cat app/.env | grep DB_
```

Database credentials doğru mu kontrol edin:
```
DB_NAME=xnggkta_analiz_db
DB_USER=xnggkta_dbuser
DB_PASSWORD=[sizin şifreniz]
```

---

## 🔄 Manuel Deployment (Script Çalışmazsa)

Eğer script hata verirse, manuel olarak şunları yapın:

### 1. Virtual Environment Oluştur
```bash
cd ~/public_html
python3 -m venv venv
```

### 2. Activate
```bash
source venv/bin/activate
```

### 3. Dependencies Yükle
```bash
pip install --upgrade pip
pip install -r requirements-shared-hosting.txt
```

### 4. Database Initialize
```bash
cd app
python3 -c "from elo_utils import init_database; init_database()"
```

### 5. Passenger Restart
```bash
cd ~/public_html
mkdir -p tmp
touch tmp/restart.txt
```

---

## ✅ Deployment Tamamlandı mı Kontrol

### Test 1: Virtual Environment Var mı?
```bash
ls -la ~/public_html/venv
```

**Klasör varsa ✅**

### Test 2: Dependencies Yüklü mü?
```bash
source ~/public_html/venv/bin/activate
pip list | grep fastapi
```

**fastapi görünüyorsa ✅**

### Test 3: Database Bağlantısı?
```bash
cd ~/public_html/app
source ../venv/bin/activate
python3 -c "from config import get_settings; s=get_settings(); print(f'DB: {s.DB_NAME}')"
```

**Database adını gösteriyorsa ✅**

---

## 🎯 Şimdi Ne Yapmalısınız?

1. **cPanel → Terminal** açın
2. `cd ~/public_html` komutu
3. `chmod +x deploy-namecheap.sh` komutu
4. `./deploy-namecheap.sh` çalıştırın
5. ~10 dakika bekleyin
6. Başarı mesajını görün! 🎉

---

**Terminal açtınız mı? Hangi aşamadasınız?**

- "Terminal açtım" → komutları vereceğim
- "Script çalışıyor" → harika, bekleyin!
- "Hata aldım: [hata mesajı]" → çözelim
- "Script bitti" → test edelim!

**Terminal'i açın ve "Terminal açtım" yazın, komutları vereyim!** 💻
