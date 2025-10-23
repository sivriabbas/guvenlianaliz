# Streamlit Cloud Deployment Guide

Bu dosya, Güvenilir Analiz projesinin Streamlit Community Cloud'da nasıl yayınlanacağını açıklar.

## 🚀 Deploy Adımları

### 1. GitHub Repository Hazırlığı
✅ Proje zaten GitHub'da: `sivriabbas/yenianaliz`
✅ Tüm gerekli dosyalar mevcut
✅ requirements.txt dosyası hazır

### 2. Streamlit Community Cloud'a Giriş
1. https://share.streamlit.io adresine gidin
2. GitHub hesabınızla giriş yapın
3. "New app" butonuna tıklayın

### 3. Repository Bağlama
1. Repository: `sivriabbas/yenianaliz`
2. Branch: `main`
3. Main file path: `app.py`
4. App URL: İstediğiniz URL'i seçin (örn: `futbol-analiz-ai`)

### 4. Secrets Yapılandırması
Streamlit Cloud'da "Advanced settings" → "Secrets" bölümüne şu içeriği ekleyin:

```toml
API_KEY = "6336fb21e17dea87880d3b133132a13f"
```

### 5. Deploy
"Deploy!" butonuna tıklayın ve uygulamanızın yayına girmesini bekleyin.

## 🔧 Önemli Notlar

- **API Limitleri**: API-Football'ın günlük request limitini aşmamaya dikkat edin
- **Secrets Güvenliği**: API anahtarınızı asla GitHub'a yüklemeyin
- **Domain**: Streamlit Cloud size `appname.streamlit.app` formatında URL verecek
- **Custom Domain**: Ücretli planda custom domain ekleyebilirsiniz

## 📱 App URL'niz
Deploy edildikten sonra uygulamanız şu adreste erişilebilir olacak:
`https://your-app-name.streamlit.app`

## ⚠️ Dikkat Edilecekler

1. **Rate Limiting**: API-Football free tier 100 request/gün limit
2. **Memory**: Büyük dosyalar için dikkatli olun
3. **Session State**: Streamlit Cloud'da session state sıfırlanabilir
4. **File System**: Sadece read-only dosya sistemi

## 🔄 Güncelleme
GitHub'a yeni commit attığınızda Streamlit Cloud otomatik olarak uygulamayı yeniden deploy eder.