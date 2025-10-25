"""
HATA AYIKLAMA - Hangi modülde hata var?
"""
print("="*60)
print("🔍 PHASE 3 MODÜL TEST")
print("="*60)

# Test 1: Import'ları kontrol et
print("\n1️⃣ Import testleri...")
try:
    from tactical_analysis import calculate_tactical_matchup
    print("   ✅ tactical_analysis import edildi")
except Exception as e:
    print(f"   ❌ tactical_analysis hatası: {e}")

try:
    from transfer_impact import compare_transfer_situations
    print("   ✅ transfer_impact import edildi")
except Exception as e:
    print(f"   ❌ transfer_impact hatası: {e}")

try:
    from squad_experience import compare_squad_experience
    print("   ✅ squad_experience import edildi")
except Exception as e:
    print(f"   ❌ squad_experience hatası: {e}")

# Test 2: Fonksiyon çağrıları
print("\n2️⃣ Fonksiyon çağrı testleri...")

try:
    print("   • Taktiksel analiz test ediliyor...")
    result1 = calculate_tactical_matchup("Galatasaray", "Fenerbahce")
    print(f"   ✅ Taktiksel: {result1.get('matchup_category', 'N/A')}")
except Exception as e:
    print(f"   ❌ Taktiksel hata: {e}")

try:
    print("   • Transfer analizi test ediliyor...")
    result2 = compare_transfer_situations(
        "Galatasaray", "Fenerbahce",
        645, 611,  # Team ID'leri
        0.8, 0.7   # Form değerleri
    )
    print(f"   ✅ Transfer: {result2.get('comparison_category', 'N/A')}")
except Exception as e:
    print(f"   ❌ Transfer hata: {e}")

try:
    print("   • Kadro tecrübe analizi test ediliyor...")
    result3 = compare_squad_experience(
        "Galatasaray", "Fenerbahce",
        645, 611,  # Team ID'leri
        1, 2       # League positions
    )
    print(f"   ✅ Tecrübe: {result3.get('comparison', 'N/A')}")
except Exception as e:
    print(f"   ❌ Tecrübe hata: {e}")

print("\n" + "="*60)
print("✅ TEST TAMAMLANDI")
print("="*60)
