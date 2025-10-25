# 📝 ADIM 1: MySQL DATABASE OLUŞTURMA

## 🎯 Yapılacaklar
1. cPanel'e giriş
2. MySQL Database Manager'a git
3. Database oluştur
4. Database user oluştur
5. User'ı database'e ata
6. Credentials'ı kaydet

---

## 🚀 Detaylı Adımlar

### 1️⃣ cPanel'e Giriş Yap

**Seçenek A: Namecheap Dashboard'dan**
1. Namecheap'e giriş yap: https://www.namecheap.com
2. Domain List'e git
3. `xn--gvenlinaliz-dlb.com` yanındaki **MANAGE** butonuna tıkla
4. **GO TO CPANEL** butonuna tıkla

**Seçenek B: Direkt cPanel URL**
```
https://premium700.web-hosting.com:2083
```
veya
```
https://xn--gvenlinaliz-dlb.com/cpanel
```

**Login bilgileri:** Namecheap hesabınızdan alabilirsiniz

---

### 2️⃣ MySQL Database Manager'ı Aç

cPanel ana sayfasında:

1. **"Databases"** bölümünü bul (genelde sol tarafta veya ortada)
2. **"MySQL® Databases"** ikonuna tıkla

veya

- Arama kutusuna "MySQL" yaz → **MySQL® Databases**

---

### 3️⃣ Yeni Database Oluştur

**"Create New Database" bölümünde:**

```
New Database: analiz_db
```

**Önemli Notlar:**
- ✅ Küçük harf kullanın: `analiz_db`
- ✅ Türkçe karakter yok
- ✅ Alt çizgi (_) kullanabilirsiniz
- ❌ Nokta, boşluk kullanmayın

**cPanel otomatik olarak prefix ekler:**
```
Tam database adı: xnggra_analiz_db
```

**"Create Database"** butonuna tıklayın.

✅ **Success mesajı gelecek.**

---

### 4️⃣ Database User Oluştur

**"Create New User" bölümüne gidin:**

```
Username: dbuser
Password: [Güçlü şifre oluştur]
```

**Güçlü Şifre Önerileri:**
- En az 12 karakter
- Büyük/küçük harf, sayı, özel karakter karışımı
- cPanel'in "Password Generator" butonunu kullanabilirsiniz

**Örnek güçlü şifre:** `Xk9#mP2$nQ5@wL8!`

**Önemli:** Bu şifreyi **mutlaka kaydedin!** (Notepad'e yazın)

**"Create User"** butonuna tıklayın.

✅ **User oluşturuldu.**

---

### 5️⃣ User'ı Database'e Ekle

**"Add User to Database" bölümünde:**

1. **User:** Dropdown'dan → `xnggra_dbuser` seçin
2. **Database:** Dropdown'dan → `xnggra_analiz_db` seçin
3. **"Add"** butonuna tıklayın

**Privilege ekranı açılacak:**

4. **"ALL PRIVILEGES"** seçeneğini işaretleyin (en üstteki checkbox)
   - Veya manuel: SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER

5. **"Make Changes"** butonuna tıklayın

✅ **User database'e eklendi.**

---

### 6️⃣ Credentials'ı Kaydet

**📋 Aşağıdaki bilgileri bir yere kaydedin:**

```ini
# ==========================================
# MySQL Database Credentials
# ==========================================
# (Bu bilgileri .env dosyasında kullanacağız)

DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=xnggra_analiz_db
DB_USER=xnggra_dbuser
DB_PASSWORD=BURAYA_SİZİN_ŞİFRENİZ_GELECEK

# Örnek (kendi şifrenizi yazın):
# DB_PASSWORD=Xk9#mP2$nQ5@wL8!
```

**Bu bilgileri nereye kaydedin:**
- ✅ Notepad veya metin editörü
- ✅ Güvenli password manager
- ✅ Ekran görüntüsü alın
- ❌ Herkesin görebileceği yerlere yazmayın

---

## ✅ Kontrol Listesi

Database kurulumu tamamlandı mı?

- [ ] cPanel'e giriş yaptım
- [ ] MySQL® Databases bölümünü açtım
- [ ] Database oluşturdum: `xnggra_analiz_db`
- [ ] User oluşturdum: `xnggra_dbuser`
- [ ] User'a şifre verdim (kaydettim)
- [ ] User'ı database'e ekledim
- [ ] ALL PRIVILEGES verdim
- [ ] Tüm credentials'ı kaydettim

**Hepsi ✅ ise → Adım 2'ye geçebiliriz!**

---

## 🔍 Doğrulama (Opsiyonel)

Database'in çalıştığını test edin:

1. **cPanel → phpMyAdmin**
2. Sol tarafta `xnggra_analiz_db` database'ini görmelisiniz
3. Tıklayın → Henüz tablo yok (normal)

**veya**

1. **cPanel → Terminal** (varsa)
2. Şu komutu çalıştırın:

```bash
mysql -u xnggra_dbuser -p xnggra_analiz_db
# Şifrenizi girin
# Bağlantı başarılıysa: mysql> prompt göreceksiniz
# Çıkmak için: exit
```

---

## ❓ Sık Sorulan Sorular

**S: Database adı farklı olabilir mi?**  
A: Evet, ama .env dosyasına aynı adı yazmalısınız. Basit tutun: `analiz_db`

**S: User şifremi unuttum!**  
A: cPanel → MySQL Databases → "Change Password" ile değiştirebilirsiniz.

**S: ALL PRIVILEGES neden?**  
A: Uygulama tablo oluşturma, güncelleme, silme yapacak. Tüm izinler gerekli.

**S: Birden fazla database oluşturabilir miyim?**  
A: Evet, ama shared hosting'de limit olabilir. Tek database yeterli.

---

## 📸 Ekran Görüntüleri (Referans)

**MySQL Databases Ekranı:**
```
┌─────────────────────────────────────────┐
│ Create New Database                     │
│ ┌─────────────────┐                    │
│ │ New Database: analiz_db  [Create]   │
│ └─────────────────┘                    │
│                                         │
│ Current Databases:                      │
│ • xnggra_analiz_db                     │
└─────────────────────────────────────────┘
```

**Add User to Database:**
```
┌─────────────────────────────────────────┐
│ User: xnggra_dbuser          ▼         │
│ Database: xnggra_analiz_db   ▼         │
│                        [Add]            │
└─────────────────────────────────────────┘
```

**Privileges:**
```
┌─────────────────────────────────────────┐
│ ☑ ALL PRIVILEGES                       │
│   ☑ SELECT                             │
│   ☑ INSERT                             │
│   ☑ UPDATE                             │
│   ☑ DELETE                             │
│   ...                                   │
│                  [Make Changes]         │
└─────────────────────────────────────────┘
```

---

## ✅ Tamamlandı!

Database kurulumu başarıyla tamamlandı! 🎉

**Kaydedilmesi gerekenler:**
```
DB_HOST=localhost
DB_NAME=xnggra_analiz_db
DB_USER=xnggra_dbuser
DB_PASSWORD=[sizin şifreniz]
```

---

## 🎯 Sonraki Adım

**Adım 2: Dosya Yükleme**

Şimdi projeyi cPanel'e yükleyeceğiz:
- File Manager kullanarak (kolay)
- veya FTP ile (profesyonel)

**Hazırsanız devam edelim!** 🚀
