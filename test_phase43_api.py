"""
PHASE 4.3 API TEST
Faktör ağırlık sistemini test et
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8003"

print("="*70)
print("🧪 PHASE 4.3 - FAKTÖR AĞIRLIK SİSTEMİ TEST")
print("="*70)

# Test 1: Varsayılan ağırlıklar
print("\n1️⃣ VARSAYILAN AĞIRLIKLAR")
print("-"*70)
try:
    response = requests.get(f"{BASE_URL}/api/factor-weights")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            weights = data['weights']
            print(f"✅ API çalışıyor")
            print(f"📊 Toplam faktör: {data['total_factors']}")
            print(f"\n🔝 İlk 5 faktör:")
            for i, (factor, weight) in enumerate(list(weights.items())[:5], 1):
                print(f"   {i}. {factor:20s} {weight:.2f}")
        else:
            print(f"❌ Hata: {data.get('error')}")
    else:
        print(f"❌ HTTP {response.status_code}")
except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")

# Test 2: Süper Lig ağırlıkları
print("\n2️⃣ SÜPER LİG AĞIRLIKLARI")
print("-"*70)
try:
    response = requests.get(f"{BASE_URL}/api/factor-weights", params={
        'league': 'Süper Lig'
    })
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            weights = data['weights']
            print(f"✅ Lig: {data['league']}")
            
            # Değişen faktörleri göster
            print(f"\n🔄 Lig bazlı değişiklikler:")
            special_factors = ['home_advantage', 'motivation', 'referee', 'tactical_matchup']
            for factor in special_factors:
                if factor in weights:
                    print(f"   {factor:20s} {weights[factor]:.2f}")
except Exception as e:
    print(f"❌ Hata: {e}")

# Test 3: Derbi maçı ağırlıkları
print("\n3️⃣ DERBİ MAÇI AĞIRLIKLARI (Süper Lig)")
print("-"*70)
try:
    response = requests.get(f"{BASE_URL}/api/factor-weights", params={
        'league': 'Süper Lig',
        'match_type': 'derby'
    })
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            weights = data['weights']
            print(f"✅ Lig: {data['league']}")
            print(f"✅ Maç Tipi: {data['match_type']}")
            
            # En önemli faktörler
            sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            print(f"\n🔝 En önemli 10 faktör (Derbi):")
            for i, (factor, weight) in enumerate(sorted_weights[:10], 1):
                bar = "█" * int(weight * 5)
                print(f"   {i:2d}. {factor:20s} {weight:5.2f} {bar}")
except Exception as e:
    print(f"❌ Hata: {e}")

# Test 4: Farklı lig karşılaştırması
print("\n4️⃣ LİG KARŞILAŞTIRMASI")
print("-"*70)
leagues = ['Süper Lig', 'Premier League', 'La Liga', 'Bundesliga', 'Serie A']
factors_to_compare = ['form', 'tactical_matchup', 'home_advantage']

print(f"\n{'Lig':20s} " + " ".join(f"{f:15s}" for f in factors_to_compare))
print("-" * 70)

for league in leagues:
    try:
        response = requests.get(f"{BASE_URL}/api/factor-weights", params={'league': league})
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                weights = data['weights']
                values = [f"{weights.get(f, 1.0):15.2f}" for f in factors_to_compare]
                print(f"{league:20s} " + " ".join(values))
    except:
        pass

print("\n" + "="*70)
print("✅ TEST TAMAMLANDI!")
print("="*70)
print(f"\n💡 TIP: Ağırlıkları görmek için:")
print(f"   http://127.0.0.1:8003/api/factor-weights")
print(f"   http://127.0.0.1:8003/api/factor-weights?league=Süper+Lig")
print(f"   http://127.0.0.1:8003/api/factor-weights?league=Süper+Lig&match_type=derby")
