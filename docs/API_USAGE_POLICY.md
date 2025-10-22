# API Kullanım Politikası

## 📊 API Hakkı Yönetimi

Bu uygulama, API kaynaklarını verimli kullanmak için akıllı bir kullanım politikası uygular.

### 🎯 Sistem API'si (Ücretsiz - Kullanıcı Hakkı Tüketmez)

Aşağıdaki işlemler **sistem API hakkı** kullanır ve kullanıcı kotasından düşülmez:

#### 1. **Ana Sayfa**
- ✅ Günün öne çıkan tahminleri
- ✅ Popüler liglerdeki maçların listelenmesi
- ✅ Özet tahmin kartları
- ✅ Tüm özet analizler (`use_system_api=True`)

#### 2. **Maç Panosu**
- ✅ Tarih ve lig bazlı maç araması
- ✅ Maç listesinin görüntülenmesi
- ✅ **Özet AI tahminleri (tablo görünümü)** ← YENİ
- ✅ En iyi bahis önerileri
- ✅ AI güven puanı hesaplamaları
- ✅ 2.5 üst/alt ve KG var/yok olasılıkları

#### 3. **Manuel Analiz - Favori Ligler**
- ✅ Favori liglerdeki maçların listelenmesi (bugün/yarın)
- ✅ Lig ve takım bilgilerinin yüklenmesi

### 👤 Kullanıcı API'si (Kullanıcı Hakkı Tüketir)

Aşağıdaki işlemler **kullanıcı API hakkı** kullanır:

#### 1. **Detaylı Maç Analizi**
- ⚠️ "Detaylı Maç Analizi" butonuna basıldığında
- ⚠️ Manuel takım seçimi ile analiz yapıldığında
- ⚠️ Hızlı takım araması ile detaylı analiz yapıldığında
- ⚠️ Lig seçerek detaylı analiz yapıldığında

#### 2. **İçerik**
Detaylı analiz şunları içerir:
- Tahmin özeti
- Detaylı istatistikler
- İddaa önerileri
- Eksik oyuncular
- Puan durumu
- H2H analizi
- Hakem analizi
- Analiz parametreleri

### 📈 Optimizasyon Stratejileri

#### Cache Kullanımı
```python
@st.cache_data(ttl=86400)  # 24 saat
def analyze_fixture_summary(fixture, model_params, use_system_api=False):
    # use_system_api=True → Sistem API kullanır
    # Özet analiz cache'lenir
    # Tekrar API çağrısı yapılmaz
```

#### Sistem API ile Özet Analiz
```python
# Maç Panosunda - Sistem API kullanımı
summary = analyze_fixture_summary(
    fixture, model_params, 
    use_system_api=True  # Kullanıcı hakkı tüketmez
)
```

#### Bypass Mekanizması
```python
# Maç listesi çekme - Sistem API'si
fixtures, error = api_utils.get_fixtures_by_date(
    API_KEY, BASE_URL, selected_ids, selected_date, 
    bypass_limit_check=True  # Kullanıcı hakkı tüketmez
)

# Analiz fonksiyonlarında
api_utils.get_team_statistics(api_key, base_url, team_id, 
    league_id, season, skip_limit=True)  # Sistem API
```

### 💡 Kullanıcı İçin İpuçları

1. **Akıllı Kullanım**: Maç listesini inceleyin, sadece ilginizi çeken maçlar için detaylı analiz yapın
2. **Cache Avantajı**: Aynı maçı tekrar analiz ederseniz cache'den hızlıca yüklenir
3. **Günlük Limit**: API limitinizi aşmamak için günlük 100 sorgu limitine dikkat edin
4. **Sistem Tarafı**: Ana sayfa ve maç listesi sınırsız kullanılabilir

### 🔧 Teknik Detaylar

#### API Çağrı Yapısı

**Sistem API'si:**
```python
def make_api_request(api_key, base_url, endpoint, params, skip_limit=True):
    # skip_limit=True → Kullanıcı hakkı tüketmez
    # Sayaç artmaz
```

**Kullanıcı API'si:**
```python
def make_api_request(api_key, base_url, endpoint, params, skip_limit=False):
    # skip_limit=False → Kullanıcı hakkı tüketir
    # Sayaç artar
```

### 📊 Günlük Kullanım Örneği

| İşlem | API Tipi | Tüketim |
|-------|----------|---------|
| Ana sayfa yüklendiğinde | Sistem | 0 |
| Maç panosu araması | Sistem | 0 |
| 20 maçın özet analizi | Sistem | **0** ← YENİ |
| 1 detaylı maç analizi | Kullanıcı | ~8-12 |
| Manuel takım analizi | Kullanıcı | ~8-12 |

**ÖNCEDEN**: 20 maçın analizi ~160-240 API harcardı  
**ARTIK**: 20 maçın özet analizi 0 API harcar (Sistem API)

### ⚙️ Yapılandırma

Sistem API kullanımı için `bypass_limit_check` parametresi:

- `True`: Sistem API kullanır (ücretsiz)
- `False`: Kullanıcı API kullanır (kotadan düşer)

---

**Son Güncelleme**: 22 Ekim 2025
**Versiyon**: 2.0
