"""
MODÜL İMPORT TESTİ - Phase 3 entegrasyonunu test et
"""
print("="*60)
print("🔍 PHASE 3 MODÜL İMPORT TESTİ")
print("="*60)

try:
    print("\n1. tactical_analysis modülünü test ediyorum...")
    from tactical_analysis import calculate_tactical_matchup
    result = calculate_tactical_matchup("Galatasaray", "Fenerbahce")
    print(f"   ✅ Taktiksel Analiz: {result.get('matchup_category', 'N/A')}")
    print(f"      Etki: {result.get('prediction_impact', 0):+.1f}%")
except Exception as e:
    print(f"   ❌ Hata: {str(e)}")

try:
    print("\n2. transfer_impact modülünü test ediyorum...")
    from transfer_impact import compare_transfer_situations
    result = compare_transfer_situations("Galatasaray", "Fenerbahce")
    print(f"   ✅ Transfer Etkisi: {result.get('comparison_category', 'N/A')}")
    print(f"      Etki: {result.get('prediction_impact', 0):+.1f}%")
except Exception as e:
    print(f"   ❌ Hata: {str(e)}")

try:
    print("\n3. squad_experience modülünü test ediyorum...")
    from squad_experience import compare_squad_experience
    result = compare_squad_experience("Galatasaray", "Fenerbahce")
    print(f"   ✅ Kadro Tecrübesi: {result.get('comparison', 'N/A')}")
    print(f"      Etki: {result.get('prediction_impact', 0):+.1f}%")
except Exception as e:
    print(f"   ❌ Hata: {str(e)}")

print("\n" + "="*60)
print("✅ TÜM MODÜLLER TEST EDİLDİ")
print("="*60)
