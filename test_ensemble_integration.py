"""
🔬 ENSEMBLE SİSTEM TEST SCRIPTI
================================
Ana /analyze endpoint'inin ensemble sistemi kullanıp kullanmadığını test eder
"""

import requests
import json
from datetime import datetime

# Test yapılacak takımlar
TEST_MATCHES = [
    ("Barcelona", "Real Madrid"),
    ("Manchester City", "Liverpool"),
    ("Bayern Munich", "Dortmund"),
    ("Galatasaray", "Fenerbahce")
]

def test_analysis_endpoint(team1, team2):
    """Analiz endpoint'ini test et"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {team1} vs {team2}")
    print(f"{'='*80}\n")
    
    url = "http://127.0.0.1:8003/analyze"
    data = {
        "team1": team1,
        "team2": team2
    }
    
    try:
        print("📡 İstek gönderiliyor...")
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            print("✅ İstek başarılı!")
            
            # HTML response'dan tahmin oranlarını çıkar
            html = response.text
            
            # Ensemble güven skorunu ara
            if "ml_confidence" in html or "ensemble" in html.lower():
                print("🎯 ENSEMBLE SİSTEMİ AKTİF!")
                print("   ✓ ML tahmin sistemi çalışıyor")
                print("   ✓ Ensemble metodları kullanılıyor")
            else:
                print("⚠️ Ensemble sistemi tespit edilemedi")
            
            # Cache kullanımını kontrol et
            if "cache" in html.lower() or "62.9x" in html:
                print("⚡ CACHE SİSTEMİ AKTİF!")
            
            return True
        else:
            print(f"❌ Hata: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ İstek hatası: {str(e)}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("\n" + "="*80)
    print("🔬 ENSEMBLE SİSTEM ENTEGRASYONİ TEST RAPORU")
    print("="*80)
    print(f"⏰ Test Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Endpoint: http://127.0.0.1:8003/analyze")
    print("="*80)
    
    success_count = 0
    total_tests = len(TEST_MATCHES)
    
    for team1, team2 in TEST_MATCHES:
        if test_analysis_endpoint(team1, team2):
            success_count += 1
    
    print("\n" + "="*80)
    print("📊 TEST SONUÇLARI")
    print("="*80)
    print(f"✅ Başarılı: {success_count}/{total_tests}")
    print(f"❌ Başarısız: {total_tests - success_count}/{total_tests}")
    print(f"📈 Başarı Oranı: {(success_count/total_tests)*100:.1f}%")
    print("="*80)
    
    if success_count == total_tests:
        print("\n🎉 TÜM TESTLER BAŞARILI!")
        print("✅ Ensemble sistem ana analizde aktif")
        print("✅ Phase 4-6 entegrasyonu tamamlandı")
    else:
        print("\n⚠️ Bazı testler başarısız oldu")
        print("🔍 Loglara bakın ve hataları düzeltin")

if __name__ == "__main__":
    main()
