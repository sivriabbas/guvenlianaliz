# Render.com Deployment Guide

Render.com ile tamamen ücretsiz deployment.

## 🌊 Neden Render?

- 🆓 **Tamamen ücretsiz** web service
- 🔄 **Otomatik deploy** GitHub'dan  
- 🔒 **SSL dahil** - HTTPS otomatik
- 🌐 **Custom domain** - ücretsiz
- 📊 **Monitoring** dashboard
- 🛠️ **Environment variables** kolay

## ⚠️ Dezavantajları

- 😴 **Sleep mode** - 15 dakika inaktiflik sonrası uyur
- 🐌 **Cold start** - İlk istek 30+ saniye sürebilir
- 💾 **512MB RAM** limit

## 📋 Deployment Adımları

### 1. Render'a Kaydolun
1. https://render.com adresine gidin
2. "Sign Up" → GitHub ile giriş yapın

### 2. Web Service Oluşturun
1. Dashboard'da "New +" → "Web Service"
2. GitHub repository'nizi bağlayın: `sivriabbas/yenianaliz`
3. Şu ayarları yapın:

```
Name: futbol-analiz-ai
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### 3. Environment Variables
Environment Variables bölümünde:

```
API_KEY = 6336fb21e17dea87880d3b133132a13f
```

### 4. Deploy!
"Create Web Service" tıklayın ve 5-10 dakika bekleyin.

## 🌐 URL Format
`https://futbol-analiz-ai.onrender.com`

## 💡 Sleep Mode Sorunu Çözümü

Render'da sleep mode sorunu için:

1. **UptimeRobot** kullanın (ücretsiz)
2. Her 5 dakikada ping atmasını ayarlayın
3. URL: https://uptimerobot.com

## 🎯 Sonuç

Render, hobi projeleri için mükemmel:
- Tamamen ücretsiz
- Güvenilir
- Kolay setup

Fakat Railway daha profesyonel! 🚀