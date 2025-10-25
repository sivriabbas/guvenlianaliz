"""
PHASE 6 ENSEMBLE API TEST
Ensemble tahmin endpoint'ini test eder
"""
import requests
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:8003"

def test_ensemble_predict():
    """Ensemble tahmin API'sini test et"""
    print("\n" + "="*70)
    print("🔮 ENSEMBLE PREDICT TEST")
    print("="*70)
    
    # Test verisi - Güçlü ev sahibi
    test_data = {
        "team1_factors": {
            "form": 0.75,
            "elo_diff": 100,
            "home_advantage": 0.7,
            "h2h": 0.65,
            "league_position": 0.8,
            "injuries": 0.3,
            "motivation": 0.7,
            "recent_xg": 0.6,
            "weather": 0.5,
            "referee": 0.5,
            "betting_odds": 0.6,
            "tactical_matchup": 0.65,
            "transfer_impact": 0.6,
            "squad_experience": 0.7,
            "match_importance": 0.6,
            "fatigue": 0.4,
            "recent_performance": 0.7
        },
        "team2_factors": {
            "form": 0.4,
            "elo_diff": -100,
            "home_advantage": 0.3,
            "h2h": 0.35,
            "league_position": 0.4,
            "injuries": 0.6,
            "motivation": 0.5,
            "recent_xg": 0.4,
            "weather": 0.5,
            "referee": 0.5,
            "betting_odds": 0.4,
            "tactical_matchup": 0.4,
            "transfer_impact": 0.5,
            "squad_experience": 0.5,
            "match_importance": 0.6,
            "fatigue": 0.6,
            "recent_performance": 0.4
        },
        "league": "super_lig",
        "match_type": "mid_table",
        "ensemble_method": "voting"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ensemble-predict",
            json=test_data
        )
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("\n✅ ENSEMBLE TAHMİN BAŞARILI!")
                print("\n" + "="*70)
                print(data['explanation'])
                print("="*70)
            else:
                print(f"\n❌ Hata: {data.get('error')}")
        else:
            print(f"\n❌ HTTP Hatası: {response.text}")
            
    except Exception as e:
        print(f"\n❌ API hatası: {e}")

def test_all_ensemble_methods():
    """3 ensemble yöntemini karşılaştır"""
    print("\n" + "="*70)
    print("⚔️ TÜM ENSEMBLE YÖNTEMLERİ TEST")
    print("="*70)
    
    # Dengeli maç verisi
    base_data = {
        "team1_factors": {
            "form": 0.6, "elo_diff": 30, "home_advantage": 0.6,
            "h2h": 0.55, "league_position": 0.6, "injuries": 0.4,
            "motivation": 0.6, "recent_xg": 0.55, "weather": 0.5,
            "referee": 0.5, "betting_odds": 0.55, "tactical_matchup": 0.55,
            "transfer_impact": 0.5, "squad_experience": 0.6,
            "match_importance": 0.6, "fatigue": 0.5, "recent_performance": 0.6
        },
        "team2_factors": {
            "form": 0.5, "elo_diff": -30, "home_advantage": 0.4,
            "h2h": 0.45, "league_position": 0.5, "injuries": 0.5,
            "motivation": 0.5, "recent_xg": 0.45, "weather": 0.5,
            "referee": 0.5, "betting_odds": 0.45, "tactical_matchup": 0.45,
            "transfer_impact": 0.5, "squad_experience": 0.5,
            "match_importance": 0.6, "fatigue": 0.5, "recent_performance": 0.5
        },
        "league": "super_lig",
        "match_type": "mid_table"
    }
    
    methods = ["voting", "averaging", "weighted"]
    results = {}
    
    for method in methods:
        print(f"\n{'─'*70}")
        print(f"🎯 Yöntem: {method.upper()}")
        print(f"{'─'*70}")
        
        test_data = base_data.copy()
        test_data["ensemble_method"] = method
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/ensemble-predict",
                json=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    pred = data['prediction']['ensemble_prediction']
                    results[method] = pred
                    
                    print(f"✅ Tahmin: {pred['prediction'].upper()}")
                    print(f"📊 Güven: {pred['confidence']:.2%}")
                    print(f"🎯 Yöntem: {pred['method']}")
                else:
                    print(f"❌ Hata: {data.get('error')}")
        except Exception as e:
            print(f"❌ {method} hatası: {e}")
    
    # Karşılaştırma
    if len(results) >= 2:
        print(f"\n{'='*70}")
        print("📊 YÖNTEM KARŞILAŞTIRMA")
        print(f"{'='*70}")
        
        for method, pred in results.items():
            print(f"\n{method.upper()}:")
            print(f"  Tahmin: {pred['prediction']}")
            print(f"  Güven: {pred['confidence']:.2%}")

def test_api_health():
    """API sağlık kontrolü"""
    print("\n" + "="*70)
    print("🏥 API SAĞLIK KONTROLÜ")
    print("="*70)
    
    endpoints = [
        ("/", "Ana Sayfa"),
        ("/api/cache-stats", "Cache Stats"),
        ("/api/ml-models", "ML Models"),
        ("/api/factor-weights", "Factor Weights"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name:20s} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {name:20s} - Error: {str(e)[:40]}")

if __name__ == "__main__":
    print("\n🚀 PHASE 6: ENSEMBLE API TEST BAŞLIYOR...\n")
    
    import time
    print("⏳ API'nin başlaması için 10 saniye bekleniyor...")
    time.sleep(10)
    
    # Sağlık kontrolü
    test_api_health()
    
    # Ensemble test
    test_ensemble_predict()
    
    # Tüm yöntemleri test et
    test_all_ensemble_methods()
    
    print("\n" + "="*70)
    print("✅ TÜM TESTLER TAMAMLANDI!")
    print("="*70 + "\n")
