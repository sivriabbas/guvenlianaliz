"""
PHASE 4.2 ENTEGRASYON TESTİ
Ana sistemde paralel API + cache performansını test et
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8003"

print("="*70)
print("🧪 PHASE 4.2 ENTEGRASYON TESTİ")
print("="*70)

# Test 1: Cache istatistikleri API
print("\n1️⃣ CACHE İSTATİSTİKLERİ API")
print("-"*70)
try:
    response = requests.get(f"{BASE_URL}/api/cache-stats")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            stats = data['stats']
            print(f"✅ Cache API çalışıyor")
            print(f"📊 Hit Rate: {stats['statistics']['hit_rate']:.1f}%")
            print(f"✅ Cache Hit: {stats['statistics']['cache_hits']}")
            print(f"❌ Cache Miss: {stats['statistics']['cache_misses']}")
            print(f"💾 Toplam Kayıt: {stats['cache']['total_entries']}")
        else:
            print(f"❌ API hatası: {data.get('error')}")
    else:
        print(f"❌ HTTP {response.status_code}")
except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")

# Test 2: Maç analizi ile cache testi
print("\n2️⃣ MAÇ ANALİZİ - İLK ÇAĞRI (API'DEN)")
print("-"*70)
team1 = "Galatasaray"
team2 = "Fenerbahce"

print(f"📋 Analiz: {team1} vs {team2}")
print(f"⏱️  Başlangıç zamanı: {time.strftime('%H:%M:%S')}")

start = time.time()
try:
    # Analiz formu gönder
    response = requests.post(
        f"{BASE_URL}/analyze",
        data={
            'team1': team1,
            'team2': team2
        },
        allow_redirects=False
    )
    elapsed = time.time() - start
    
    if response.status_code in [200, 303]:
        print(f"✅ Analiz tamamlandı")
        print(f"⏱️  Süre: {elapsed:.2f}s")
    else:
        print(f"❌ HTTP {response.status_code}")
        
except Exception as e:
    elapsed = time.time() - start
    print(f"⚠️  Hata: {e}")
    print(f"⏱️  Süre: {elapsed:.2f}s")

# Biraz bekle
time.sleep(2)

# Test 3: İkinci analiz (cache'den olmalı)
print("\n3️⃣ MAÇ ANALİZİ - İKİNCİ ÇAĞRI (CACHE'DEN)")
print("-"*70)
print(f"📋 Analiz: {team1} vs {team2}")
print(f"⏱️  Başlangıç zamanı: {time.strftime('%H:%M:%S')}")

start = time.time()
try:
    response = requests.post(
        f"{BASE_URL}/analyze",
        data={
            'team1': team1,
            'team2': team2
        },
        allow_redirects=False
    )
    elapsed_cache = time.time() - start
    
    if response.status_code in [200, 303]:
        print(f"✅ Analiz tamamlandı (CACHE)")
        print(f"⏱️  Süre: {elapsed_cache:.2f}s")
        print(f"⚡ Hız artışı: {(elapsed/elapsed_cache):.1f}x")
    else:
        print(f"❌ HTTP {response.status_code}")
        
except Exception as e:
    elapsed_cache = time.time() - start
    print(f"⚠️  Hata: {e}")
    print(f"⏱️  Süre: {elapsed_cache:.2f}s")

# Test 4: Güncellenmiş cache istatistikleri
print("\n4️⃣ GÜNCELLENMİŞ CACHE İSTATİSTİKLERİ")
print("-"*70)
try:
    response = requests.get(f"{BASE_URL}/api/cache-stats")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            stats = data['stats']
            print(f"✅ Güncellenmiş İstatistikler:")
            print(f"📊 Hit Rate: {stats['statistics']['hit_rate']:.1f}%")
            print(f"✅ Cache Hit: {stats['statistics']['cache_hits']}")
            print(f"❌ Cache Miss: {stats['statistics']['cache_misses']}")
            print(f"💾 Toplam Kayıt: {stats['cache']['total_entries']}")
            print(f"💰 API Tasarrufu: {stats['statistics']['api_calls_saved']} çağrı")
            
            print(f"\n📂 Kategoriler:")
            for category, count in stats['cache']['by_category'].items():
                print(f"   • {category}: {count} kayıt")
except Exception as e:
    print(f"❌ Hata: {e}")

print("\n" + "="*70)
print("✅ TEST TAMAMLANDI!")
print("="*70)
print(f"\n💡 TIP: Cache sayfasını görüntüle: http://127.0.0.1:8003/cache-stats")
