"""
CACHE SİSTEMİ ENTEGRASYON TESTİ
Tüm modüllerin cache ile çalışmasını test et
"""
import time
from cache_manager import get_cache

print("="*70)
print("🧪 CACHE ENTEGRASYON TESTİ")
print("="*70)

cache = get_cache()

# Önce cache'i temizle
print("\n📋 Hazırlık:")
cache.clear_all()
print("   ✅ Cache temizlendi")

# Test 1: Transfer modülü
print("\n" + "="*70)
print("1️⃣ TRANSFER MOD ÜLÜ TESTİ")
print("="*70)

try:
    from transfer_impact import compare_transfer_situations
    
    print("\n   📊 İlk çağrı (API'den):")
    start = time.time()
    result1 = compare_transfer_situations(
        "Galatasaray", "Fenerbahce",
        645, 611,
        0.8, 0.7
    )
    time1 = time.time() - start
    print(f"   ⏱️  Süre: {time1:.2f}s")
    if result1:
        print(f"   ✅ Sonuç: {result1.get('comparison_category', 'N/A')}")
    
    print("\n   📊 İkinci çağrı (Cache'den):")
    start = time.time()
    result2 = compare_transfer_situations(
        "Galatasaray", "Fenerbahce",
        645, 611,
        0.8, 0.7
    )
    time2 = time.time() - start
    print(f"   ⏱️  Süre: {time2:.2f}s")
    print(f"   ⚡ Hız artışı: {(time1/time2):.1f}x daha hızlı!")
    
except Exception as e:
    print(f"   ❌ Hata: {e}")

# Test 2: Squad Experience modülü
print("\n" + "="*70)
print("2️⃣ KADRO TECRÜBESİ MODÜLÜ TESTİ")
print("="*70)

try:
    from squad_experience import compare_squad_experience
    
    print("\n   📊 İlk çağrı (API'den):")
    start = time.time()
    result1 = compare_squad_experience(
        "Galatasaray", "Fenerbahce",
        645, 611,
        1, 2
    )
    time1 = time.time() - start
    print(f"   ⏱️  Süre: {time1:.2f}s")
    if result1:
        print(f"   ✅ Sonuç: {result1.get('comparison', 'N/A')}")
    
    print("\n   📊 İkinci çağrı (Cache'den):")
    start = time.time()
    result2 = compare_squad_experience(
        "Galatasaray", "Fenerbahce",
        645, 611,
        1, 2
    )
    time2 = time.time() - start
    print(f"   ⏱️  Süre: {time2:.2f}s")
    if time1 > 0 and time2 > 0:
        print(f"   ⚡ Hız artışı: {(time1/time2):.1f}x daha hızlı!")
    
except Exception as e:
    print(f"   ❌ Hata: {e}")

# Test 3: Cache istatistikleri
print("\n" + "="*70)
print("3️⃣ CACHE İSTATİSTİKLERİ")
print("="*70)

cache.print_stats()

# Özet
print("\n" + "="*70)
print("📊 TEST SONUÇ ÖZETİ")
print("="*70)

stats = cache.get_stats()
if stats['today']['total'] > 0:
    print(f"\n✅ Toplam İşlem: {stats['today']['total']}")
    print(f"✅ Cache Hit Rate: %{stats['today']['hit_rate']}")
    print(f"💰 API Tasarrufu: {stats['today']['api_calls_saved']} çağrı")
    print(f"📦 Aktif Cache: {stats['cache']['total_active']} kayıt")
    
    if stats['today']['hit_rate'] >= 50:
        print("\n🎉 BAŞARILI! Cache sistemi çalışıyor!")
    else:
        print("\n⚠️  Hit rate düşük, daha fazla test gerekli")
else:
    print("\n⚠️  Test verisi yetersiz")

print("\n" + "="*70)
print("✅ TEST TAMAMLANDI!")
print("="*70)
