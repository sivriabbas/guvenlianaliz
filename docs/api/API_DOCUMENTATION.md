# Güvenilir Analiz API Documentation

**Version:** 8.0.0  
**Base URL:** `http://127.0.0.1:8003`  
**Last Updated:** 2025-10-24 14:34:33

## 🎯 Overview

Güvenilir Analiz API, futbol maçları için yapay zeka destekli analiz ve tahmin hizmeti sunar.

### Features
- ⚡ Paralel API processing (62.9x speedup)
- 📊 Advanced caching system (44.4% hit rate)
- 🤖 ML predictions (XGBoost + LightGBM)
- 🎯 Ensemble predictions
- 🔒 API security & rate limiting
- 📈 Real-time monitoring & analytics

---

## 🔐 Authentication

API anahtarı ile kimlik doğrulama:

```bash
curl -H "X-API-Key: your_api_key_here" http://127.0.0.1:8003/api/endpoint
```

---

## 📍 Endpoints


### AUTO-RETRAIN

#### `POST` /api/auto-retrain

🔧 Otomatik re-training tetikle

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/auto-retrain" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---


### CACHE-STATS

#### `GET` /api/cache-stats

⚡ Cache istatistikleri API (Phase 4.2)

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/cache-stats"
```

---


### CHECK-RESULTS

#### `POST` /api/check-results

🔍 Sonuçları kontrol et

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/check-results" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---


### COMPARE-ENSEMBLE-METHODS

#### `POST` /api/compare-ensemble-methods

🎯 Ensemble metodlarını karşılaştır

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/compare-ensemble-methods" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---


### DOCS

#### `GET` /api/docs/openapi

📄 OpenAPI 3.0 Specification

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/docs/openapi"
```

---

#### `GET` /api/docs/postman

📮 Postman Collection v2.1

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/docs/postman"
```

---

#### `GET` /api/docs/markdown

📝 Markdown Documentation

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/docs/markdown"
```

---

#### `POST` /api/docs/export

💾 Export All Documentation

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/docs/export" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `GET` /api/docs/endpoints

📍 List All API Endpoints

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/docs/endpoints"
```

---

#### `GET` /api/docs/examples/{endpoint_path:path}

💡 Get Code Examples for Endpoint

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/docs/examples/{endpoint_path:path}"
```

---


### ENSEMBLE-PREDICT

#### `POST` /api/ensemble-predict

🔮 Ensemble tahmin API (Phase 6) + Production Logging (Phase 7.D)

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/ensemble-predict" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---


### FACTOR-WEIGHTS

#### `GET` /api/factor-weights

⚖️ Faktör ağırlıkları API (Phase 4.3)

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/factor-weights"
```

---


### GENERAL

#### `GET` /openapi.json

openapi

**Example:**

```bash
curl -X HEAD "http://127.0.0.1:8003/openapi.json"
```

---

#### `GET` /docs

swagger_ui_html

**Example:**

```bash
curl -X HEAD "http://127.0.0.1:8003/docs"
```

---

#### `GET` /docs/oauth2-redirect

swagger_ui_redirect

**Example:**

```bash
curl -X HEAD "http://127.0.0.1:8003/docs/oauth2-redirect"
```

---

#### `GET` /redoc

redoc_html

**Example:**

```bash
curl -X HEAD "http://127.0.0.1:8003/redoc"
```

---

#### `GET` /

Ana sayfa - basit ve hızlı yüklenen versiyon

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/"
```

---

#### `GET` /login

login_page

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/login"
```

---

#### `POST` /login

login

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/login" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `GET` /analysis

analysis_page

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/analysis"
```

---

#### `GET` /dashboard

API-Football'dan gerçek maç verilerini göster

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/dashboard"
```

---

#### `POST` /analyze

🔥 ENSEMBLE ML + AI Hibrit Analiz Sistemi - Phase 4-6 Entegrasyonu

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/analyze" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `GET` /analyze

analyze_get

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/analyze"
```

---

#### `GET` /statistics

statistics_page

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/statistics"
```

---

#### `GET` /cache-stats

📊 Cache istatistikleri sayfası (Phase 4.2)

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/cache-stats"
```

---

#### `GET` /monitoring-dashboard

📊 Monitoring Dashboard HTML sayfası

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/monitoring-dashboard"
```

---

#### `GET` /api-tester

🧪 Interactive API Testing Tool

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api-tester"
```

---


### LEAGUES

#### `GET` /api/leagues

Lig listesi API

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/leagues"
```

---


### LOGS

#### `GET` /api/logs/errors

📋 Log dosyasından hata özetini getir

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/logs/errors"
```

---

#### `GET` /api/logs/performance

⚡ Log dosyasından performans metriklerini getir

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/logs/performance"
```

---


### METRICS

#### `GET` /api/metrics

📊 Genel API metriklerini getir

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/metrics"
```

---

#### `GET` /api/metrics/endpoint/{endpoint_path:path}

📍 Belirli bir endpoint için metrikleri getir

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/metrics/endpoint/{endpoint_path:path}"
```

---

#### `GET` /api/metrics/historical

📈 Geçmiş metrikleri getir

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/metrics/historical"
```

---

#### `GET` /api/metrics/slow

🐌 Yavaş endpoint'leri getir

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/metrics/slow"
```

---

#### `GET` /api/metrics/errors

⚠️ Hata analizini getir

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/metrics/errors"
```

---

#### `POST` /api/metrics/reset

🔄 In-memory metrikleri sıfırla (sadece admin)

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/metrics/reset" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `GET` /api/metrics/export

💾 Metrikleri JSON dosyasına export et

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/metrics/export"
```

---


### ML-MODELS

#### `GET` /api/ml-models

🤖 ML model listesi API (Phase 5)

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/ml-models"
```

---


### ML-PREDICT

#### `POST` /api/ml-predict

🤖 ML ile tahmin API (Phase 5) + Production Logging (Phase 7.D)

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/ml-predict" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---


### OPTIMIZE-ENSEMBLE-WEIGHTS

#### `POST` /api/optimize-ensemble-weights

⚖️ Ensemble ağırlıklarını optimize et

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/optimize-ensemble-weights" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---


### PHASE7

#### `GET` /api/phase7/status

📊 Phase 7 durum kontrolü

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/phase7/status"
```

---

#### `POST` /api/phase7/collect-data

📥 Geçmiş maç verisi topla (Phase 7.A1)

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/phase7/collect-data" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `POST` /api/phase7/calculate-factors

🧮 17 faktörü hesapla (Phase 7.A2)

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/phase7/calculate-factors" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `POST` /api/phase7/prepare-dataset

📊 Dataset hazırla (Phase 7.B1)

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/phase7/prepare-dataset" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `GET` /api/phase7/training-progress

📈 Model eğitim ilerlemesi

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/phase7/training-progress"
```

---


### PREDICTION-STATS

#### `GET` /api/prediction-stats

📊 Tahmin istatistikleri

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/prediction-stats"
```

---


### PREMIUM

#### `GET` /api/premium/advanced-analysis

💎 Premium analiz endpoint'i (API key + premium yetki gerekli)

Usage: Header'a ekle -> X-API-Key: your_premium_key

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/premium/advanced-analysis"
```

---


### RECENT-PREDICTIONS

#### `GET` /api/recent-predictions

📋 Son tahminler

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/recent-predictions"
```

---


### SEARCH-TEAMS

#### `GET` /api/search-teams

Takım arama API

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/search-teams"
```

---


### SECURITY

#### `POST` /api/security/create-key

🔑 Yeni API key oluştur (Admin yetkisi gerekli)

Body:
{
    "name": "Key ismi",
    "owner": "Sahip (opsiyonel)",
    "expires_days": 30,
    "rate_limit": 100,
    "permissions": "basic|premium|admin"
}

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/security/create-key" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `GET` /api/security/key-stats

📊 API key istatistikleri

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/security/key-stats"
```

---

#### `POST` /api/security/deactivate-key

🔒 API key'i deaktif et (Admin yetkisi gerekli)

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/security/deactivate-key" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

#### `GET` /api/security/rate-limit-status

⏱️ Mevcut rate limit durumu

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/security/rate-limit-status"
```

---


### SYSTEM-STATUS

#### `GET` /api/system-status

🎯 Sistem durumu (tüm phase'ler)

**Example:**

```bash
curl -X GET "http://127.0.0.1:8003/api/system-status"
```

---


### UPDATE-WEIGHTS

#### `POST` /api/update-weights

⚖️ Ağırlıkları güncelle API (Phase 4.3)

**Example:**

```bash
curl -X POST "http://127.0.0.1:8003/api/update-weights" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

