# Railway Deployment Guide - Güvenilir Analiz

Railway ile deployment için detaylı rehber.

## 🚀 Neden Railway?

- ⚡ **En hızlı setup** - 2 dakikada deploy
- 🔋 **500 saat/ay ücretsiz** (yaklaşık 16 gün)
- 🚀 **Sleep mode yok** - her zaman aktif
- 🌐 **Otomatik SSL** ve subdomain
- 🛠️ **Kolay environment variables**
- 📊 **Güçlü monitoring** dashboard

## 📋 Deployment Adımları

### 1. Railway'e Kaydolun
1. https://railway.app adresine gidin
2. "Start a New Project" tıklayın
3. GitHub hesabınızla giriş yapın

### 2. Proje Oluşturun
1. "Deploy from GitHub repo" seçin
2. Repository'nizi seçin: `sivriabbas/yenianaliz`
3. Branch: `main`

### 3. Environment Variables Ayarlayın
Railway dashboard'da Variables sekmesinde:

```
API_KEY = 6336fb21e17dea87880d3b133132a13f
PORT = 8501
```

### 4. Deploy!
Railway otomatik olarak:
- ✅ Bağımlılıkları kurar (`requirements.txt`)
- ✅ Uygulamayı başlatır (`Procfile`)
- ✅ SSL sertifikası oluşturur
- ✅ Benzersiz URL verir

## 🌐 Erişim URL'i

Deploy sonrası uygulamanız şu formatta erişilebilir:
`https://yenianaliz-production.up.railway.app`

## 🔧 Önemli Notlar

### Performance
- **RAM**: 512MB-8GB otomatik scaling
- **CPU**: Shared compute, çok hızlı
- **Storage**: 1GB ephemeral disk

### Limits
- **Free Tier**: 500 saat/ay ($5 değerinde)
- **Network**: Unlimited bandwidth
- **Sleep**: Sleep mode YOK! Her zaman aktif

### Auto-Deploy
GitHub'a her commit'te otomatik deploy olur.

## ⚙️ Dosya Yapısı

Eklenen dosyalar:
- `railway.toml` - Railway konfigürasyonu
- `Procfile` - Uygulama başlatma komutu
- `RAILWAY_DEPLOYMENT.md` - Bu rehber

## 🆚 Diğer Platformlarla Karşılaştırma

| Platform | Free Tier | Sleep Mode | Speed | Setup |
|----------|-----------|------------|--------|--------|
| Railway | 500h/ay | ❌ Yok | ⚡ Çok Hızlı | 🟢 Kolay |
| Render | ♾️ Unlimited | ✅ 15dk sonra | 🐌 Yavaş | 🟡 Orta |
| Streamlit Cloud | ♾️ Unlimited | ❌ Yok | 🟡 Orta | 🟢 Kolay |
| Heroku | 550h/ay | ✅ 30dk sonra | 🟡 Orta | 🔴 Zor |

## 🎯 Sonuç

Railway, profesyonel projeler için ideal platform:
- Production-ready performance
- Developer-friendly dashboard  
- Güvenilir uptime
- Kolay scaling

Deploy tamamlandıktan sonra URL'inizi paylaşabilirsiniz! 🚀