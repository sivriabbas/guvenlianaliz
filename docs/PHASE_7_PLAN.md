# 📊 PHASE 7: Model Optimizasyonu & Gerçek Veri Toplama

**Durum:** 🔄 Planlanıyor  
**Öncelik:** 🔴 YÜKSEK  
**Tahmini Süre:** 4-6 saat  

---

## 🎯 Hedefler

### 1. Gerçek Maç Sonuçları ile Model Eğitimi
- Geçmiş maç sonuçlarını topla (son 2 sezon)
- Her maçın 17 faktörünü hesapla
- Gerçek sonuçlarla karşılaştır
- ML modellerini yeniden eğit

### 2. Model Doğruluk Testleri
- Test dataset oluştur (20% veri)
- Precision, Recall, F1-Score hesapla
- Confusion matrix analizi
- Feature importance güncelle

### 3. Ensemble Weight Optimizasyonu
- Gerçek sonuçlara göre ağırlık ayarla
- XGBoost vs LightGBM performans karşılaştırması
- Weighted ensemble optimal ağırlıkları bul

### 4. Canlı Test & Feedback Loop
- Günlük tahminleri kaydet
- Gerçek sonuçlarla karşılaştır
- Model accuracy tracking dashboard
- Otomatik yeniden eğitim sistemi

---

## 📋 Görevler

### A. Veri Toplama Modülü

#### A1. Geçmiş Maç Verisi Toplama
```python
# historical_data_collector.py
- Lig seçimi (Premier League, La Liga, vb.)
- Sezon seçimi (2023/24, 2024/25)
- Maç verilerini çek
- 17 faktörü hesapla ve kaydet
```

**Çıktı:** `historical_matches.db` (SQLite)

#### A2. Faktör Hesaplama Pipeline
```python
# calculate_historical_factors.py
- Her maç için:
  * ELO ratings (geçmiş tarihli)
  * Form analysis
  * H2H statistics
  * Injury impact
  * Weather data (geçmiş)
  * Betting odds (geçmiş)
  * Tactical data
  * Transfer impact
  * ... 17 faktör
```

**Çıktı:** `training_dataset.csv` (5000+ maç)

### B. Model Yeniden Eğitimi

#### B1. Dataset Hazırlama
```python
# prepare_training_data.py
- CSV'yi yükle
- Feature engineering
- Train/Test split (80/20)
- Normalization/Scaling
```

#### B2. XGBoost Tuning
```python
# tune_xgboost.py
- GridSearchCV ile hyperparameter tuning
- Cross-validation (5-fold)
- Best params kaydet
- Model yeniden eğit
```

**Parametreler:**
- `max_depth`: [3, 5, 7, 10]
- `learning_rate`: [0.01, 0.05, 0.1, 0.2]
- `n_estimators`: [100, 200, 500, 1000]
- `subsample`: [0.6, 0.8, 1.0]

#### B3. LightGBM Tuning
```python
# tune_lightgbm.py
- Optuna ile hyperparameter optimization
- Cross-validation
- Best params kaydet
- Model yeniden eğit
```

**Parametreler:**
- `num_leaves`: [31, 63, 127]
- `learning_rate`: [0.01, 0.05, 0.1]
- `n_estimators`: [100, 200, 500]
- `min_child_samples`: [5, 10, 20]

#### B4. Model Evaluation
```python
# evaluate_models.py
- Test dataseti üzerinde tahmin
- Metrics hesapla:
  * Accuracy
  * Precision (Home/Draw/Away)
  * Recall
  * F1-Score
  * AUC-ROC
- Confusion matrix
- Feature importance plot
```

### C. Ensemble Optimizasyonu

#### C1. Weight Optimization
```python
# optimize_ensemble_weights.py
- Grid search ensemble ağırlıkları:
  * xgb_weight: [0.3, 0.4, 0.5, 0.6, 0.7]
  * lgb_weight: [0.3, 0.4, 0.5, 0.6, 0.7]
  * weighted_pred_weight: [0.0, 0.1, 0.2]
- En iyi kombinasyonu bul
- Yeni ağırlıkları kaydet
```

#### C2. Ensemble Method Comparison
```python
# compare_ensemble_methods.py
- Voting accuracy
- Averaging accuracy
- Weighted accuracy
- Soft voting vs hard voting
- En iyi metodu seç
```

### D. Canlı Test Sistemi

#### D1. Tahmin Loglama
```python
# prediction_logger.py
- Her tahmin yapıldığında:
  * Match info
  * Predicted probabilities
  * ML confidence
  * Timestamp
  * Features used
- SQLite'a kaydet
```

**Tablo:** `predictions_log`

#### D2. Sonuç Karşılaştırma
```python
# result_checker.py
- Günlük çalışan script
- Tahmin edilen maçların gerçek sonuçlarını çek
- Doğruluk hesapla
- Yanlış tahminleri analiz et
- Feedback loop için kaydet
```

#### D3. Performance Dashboard
```python
# performance_dashboard.py (Streamlit)
- Günlük accuracy grafiği
- Lig bazında performans
- Maç tipi bazında performans
- Model comparison chart
- Feature importance evolution
```

#### D4. Auto-Retraining
```python
# auto_retrain.py
- Haftada 1 kez otomatik çalış
- Son 100 tahmin + sonuç al
- Yeni verilerle modeli güncelle
- Incremental learning
- Performans karşılaştır (eski vs yeni)
```

---

## 📊 Veri Kaynakları

### Geçmiş Maç Verileri
1. **API-Football** (ana kaynak)
   - Maç sonuçları
   - İstatistikler
   - Kadro bilgileri

2. **Football-Data.org**
   - Geçmiş bahis oranları
   - Maç sonuçları

3. **Kaggle Datasets**
   - European Soccer Database
   - Premier League matches

### Faktör Hesaplama
- **ELO Ratings:** Manuel hesaplama (geçmişe dönük)
- **Weather:** OpenWeatherMap historical API
- **Betting Odds:** Odds API historical data
- **Transfers:** Transfermarkt scraping (etik sınırlar içinde)

---

## 🛠️ Teknolojiler

### Veri Toplama
- `requests` + `aiohttp` (API çağrıları)
- `beautifulsoup4` (web scraping)
- `pandas` (veri işleme)
- `sqlite3` (veri depolama)

### Model Eğitimi
- `xgboost` (gradient boosting)
- `lightgbm` (light gradient boosting)
- `scikit-learn` (utilities, metrics)
- `optuna` (hyperparameter tuning)

### Görselleştirme
- `matplotlib` + `seaborn` (grafikler)
- `plotly` (interaktif grafikler)
- `streamlit` (dashboard)

### Otomasyon
- `schedule` (periyodik görevler)
- `logging` (log yönetimi)

---

## 📈 Beklenen Sonuçlar

### Performans İyileştirmesi
- **Mevcut Accuracy:** ~88-89% (varsayımsal)
- **Hedef Accuracy:** %92-95% (gerçek veri ile)

### Model Güvenilirliği
- Test dataseti üzerinde tutarlı performans
- Farklı liglerde dengeli doğruluk
- Overfit problemi olmaması

### Canlı Performans
- Günlük tahminlerde %90+ doğruluk
- Haftalık tracking ile sürekli iyileşme
- Otomatik re-training ile adaptasyon

---

## ⏱️ Zaman Planı

### Hafta 1: Veri Toplama (2-3 gün)
- Gün 1: Historical data collector script
- Gün 2: Faktör hesaplama pipeline
- Gün 3: Dataset oluşturma (5000+ maç)

### Hafta 2: Model Tuning (2-3 gün)
- Gün 1: XGBoost hyperparameter tuning
- Gün 2: LightGBM hyperparameter tuning
- Gün 3: Ensemble weight optimization

### Hafta 3: Test & Deploy (1-2 gün)
- Gün 1: Model evaluation & comparison
- Gün 2: Canlı test sistemi kurulumu
- Gün 3: Performance dashboard

---

## 🔄 Sonraki Adımlar (Phase 8+)

### Phase 8: UI/UX İyileştirmesi
- Modern web arayüzü
- Responsive design
- Real-time predictions
- User authentication

### Phase 9: API Servisi
- REST API endpoints
- Rate limiting
- API documentation
- Premium features

### Phase 10: Mobile App
- React Native app
- Push notifications
- Live match tracking
- Betting suggestions

---

## ✅ Başarı Kriterleri

### Veri Kalitesi
- ✅ 5000+ geçmiş maç verisi
- ✅ 17 faktör tamamlanmış
- ✅ Hata oranı <%5

### Model Performansı
- ✅ Test accuracy >%90
- ✅ Overfit yok (train vs test farkı <%3)
- ✅ Tüm liglerde dengeli performans

### Sistem Stabilitesi
- ✅ Otomatik re-training çalışıyor
- ✅ Canlı testler tracking yapılıyor
- ✅ Hata durumlarında fallback var

---

**Hazırlayan:** GitHub Copilot  
**Son Güncelleme:** 24 Ekim 2025  
**Durum:** 📋 Plan Tamamlandı, Implementasyon Bekliyor
