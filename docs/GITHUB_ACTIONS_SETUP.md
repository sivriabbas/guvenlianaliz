# 🤖 Otomatik Elo Güncelleme Sistemi

Bu proje, GitHub Actions kullanarak **her gün otomatik** olarak Elo rating'lerini günceller.

## 🎯 Nasıl Çalışır?

1. **Her gün 01:00 UTC** (Türkiye saati 04:00) otomatik çalışır
2. Dünün maç sonuçlarını API'den çeker
3. Kazanan ve kaybeden takımların Elo rating'lerini günceller
4. Değişiklikleri `elo_ratings.json` dosyasına kaydeder
5. GitHub'a otomatik commit ve push yapar
6. **Streamlit Cloud otomatik yeniden deploy eder** ✅

## ⚙️ Kurulum (İlk Sefer)

### 1. GitHub Repository Settings

1. GitHub repo'nuza gidin: `https://github.com/sivriabbas/yenianaliz`
2. **Settings** → **Secrets and variables** → **Actions** bölümüne gidin
3. **New repository secret** butonuna tıklayın
4. İsim: `API_KEY`
5. Value: API-Football anahtarınızı buraya yapıştırın
6. **Add secret** butonuna tıklayın

### 2. GitHub Actions İzinleri

1. **Settings** → **Actions** → **General** bölümüne gidin
2. **Workflow permissions** kısmında **"Read and write permissions"** seçin
3. **Save** butonuna tıklayın

### 3. Dosyaları GitHub'a Push Edin

```bash
git add .
git commit -m "🤖 Otomatik Elo güncelleme sistemi eklendi"
git push
```

## 🧪 Test Etme

### Manuel Tetikleme (Hemen Test Et)

1. GitHub repo'nuza gidin
2. **Actions** sekmesine tıklayın
3. Sol taraftan **"Update Elo Ratings Daily"** workflow'unu seçin
4. Sağ üstten **"Run workflow"** butonuna tıklayın
5. **"Run workflow"** onaylayın

Birkaç dakika içinde:
- ✅ Workflow tamamlanır
- ✅ `elo_ratings.json` güncellenir
- ✅ Otomatik commit atılır
- ✅ Streamlit Cloud yeniden deploy eder (5-10 dakika)

## 📅 Zamanlama

- **Otomatik çalışma**: Her gün 01:00 UTC (04:00 TR saati)
- **Manuel çalışma**: İstediğin zaman "Run workflow" ile

## 🔍 Sorun Giderme

### Workflow Hata Veriyorsa:

1. **Actions** sekmesinde hatalı workflow'a tıklayın
2. Hata mesajını okuyun:
   - **"API_KEY not found"** → Secret doğru kurulmadı
   - **"Permission denied"** → Workflow permissions "Read and write" olmalı
   - **"Rate limit exceeded"** → API günlük limit aşıldı (ertesi gün çalışır)

### Streamlit'e Yansımıyorsa:

1. Streamlit Cloud'da proje sayfanıza gidin
2. Son commit zamanına bakın (güncellenmiş mi?)
3. Yoksa **"Reboot app"** butonuna tıklayın

## 📊 İstatistikler

- **Toplam takım**: 25,673
- **Kapsanan ülkeler**: 171
- **Güncellenecek ligler**: Major Avrupa + Dünya ligleri
- **Güncelleme süresi**: ~2-5 dakika

## 🎮 Workflow Dosyası

Otomasyon: `.github/workflows/update_elo_daily.yml`

```yaml
# Her gün 01:00 UTC'de çalışır
schedule:
  - cron: '0 1 * * *'
```

Zamanlamayı değiştirmek için [crontab.guru](https://crontab.guru/) kullanabilirsin.

---

**🚀 Artık sistem tamamen otomatik!** GitHub Actions her gün Elo'ları güncelleyecek, Streamlit Cloud otomatik yansıtacak.
