"""
PHASE 5 ML TEST - ML Model API'lerini test eder
"""
import requests
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:8003"

def test_ml_models():
    """Mevcut ML modellerini listele"""
    print("\n" + "="*70)
    print("🤖 ML MODELS TEST")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/ml-models")
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ {len(data.get('models', []))} model bulundu:")
            
            for model in data.get('models', []):
                print(f"\n📊 Model: {model['model_id']}")
                print(f"   Algoritma: {model['algorithm']}")
                print(f"   Accuracy: {model['metrics']['accuracy']:.2%}")
                print(f"   Log Loss: {model['metrics']['log_loss']:.4f}")
                print(f"   Features: {model['n_features']}")
                print(f"   Tarih: {model['created_at']}")
        else:
            print(f"❌ Hata: {response.text}")
            
    except Exception as e:
        print(f"❌ API hatası: {e}")

def test_ml_prediction():
    """ML tahmin API'sini test et"""
    print("\n" + "="*70)
    print("🎯 ML PREDICTION TEST")
    print("="*70)
    
    # Test verileri - Güçlü ev sahibi örneği
    test_data = {
        "team1_factors": {  # Ev sahibi (güçlü)
            "form": 0.8,
            "elo_diff": 150,
            "home_advantage": 0.7,
            "h2h": 0.75,
            "injuries": 0.2,
            "motivation": 0.8,
            "recent_xg": 0.7,
            "weather": 0.6,
            "referee": 0.5,
            "betting_odds": 0.65,
            "tactical_matchup": 0.7,
            "transfer_impact": 0.6,
            "squad_experience": 0.75,
            "league_position": 0.8,
            "match_importance": 0.6,
            "fatigue": 0.3,
            "recent_performance": 0.75
        },
        "team2_factors": {  # Deplasman (zayıf)
            "form": 0.3,
            "elo_diff": -150,
            "home_advantage": 0.3,
            "h2h": 0.25,
            "injuries": 0.6,
            "motivation": 0.4,
            "recent_xg": 0.3,
            "weather": 0.6,
            "referee": 0.5,
            "betting_odds": 0.35,
            "tactical_matchup": 0.3,
            "transfer_impact": 0.4,
            "squad_experience": 0.4,
            "league_position": 0.3,
            "match_importance": 0.6,
            "fatigue": 0.7,
            "recent_performance": 0.3
        },
        "model_name": "xgb_v1"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ml-predict",
            json=test_data
        )
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                pred = data['prediction']
                print(f"\n✅ Tahmin başarılı!")
                print(f"🤖 Model: {test_data['model_name']}")
                print(f"📊 Tahmin: {pred}")
            else:
                print(f"❌ Hata: {data.get('error')}")
            
        else:
            print(f"❌ Hata: {response.text}")
            
    except Exception as e:
        print(f"❌ API hatası: {e}")

def test_both_models():
    """Her iki modeli karşılaştır"""
    print("\n" + "="*70)
    print("⚔️ MODEL KARŞILAŞTIRMA")
    print("="*70)
    
    base_factors_team1 = {
        "form": 0.6,
        "elo_diff": 50,
        "home_advantage": 0.6,
        "h2h": 0.55,
        "injuries": 0.3,
        "motivation": 0.6,
        "recent_xg": 0.5,
        "weather": 0.5,
        "referee": 0.5,
        "betting_odds": 0.5,
        "tactical_matchup": 0.5,
        "transfer_impact": 0.5,
        "squad_experience": 0.6,
        "league_position": 0.6,
        "match_importance": 0.5,
        "fatigue": 0.4,
        "recent_performance": 0.55
    }
    
    base_factors_team2 = {
        "form": 0.4,
        "elo_diff": -50,
        "home_advantage": 0.4,
        "h2h": 0.45,
        "injuries": 0.5,
        "motivation": 0.5,
        "recent_xg": 0.4,
        "weather": 0.5,
        "referee": 0.5,
        "betting_odds": 0.5,
        "tactical_matchup": 0.5,
        "transfer_impact": 0.5,
        "squad_experience": 0.5,
        "league_position": 0.4,
        "match_importance": 0.5,
        "fatigue": 0.6,
        "recent_performance": 0.45
    }
    
    for model_name in ["xgb_v1", "lgb_v1"]:
        test_data = {
            "team1_factors": base_factors_team1,
            "team2_factors": base_factors_team2,
            "model_name": model_name
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/ml-predict",
                json=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"\n{'XGBoost' if 'xgb' in model_name else 'LightGBM'}:")
                    print(f"  Tahmin: {data['prediction']}")
                else:
                    print(f"❌ {model_name} hatası: {data.get('error')}")
                
        except Exception as e:
            print(f"❌ {model_name} hatası: {e}")

if __name__ == "__main__":
    print("\n🚀 PHASE 5: ML API TEST BAŞLIYOR...\n")
    
    # Modelleri listele
    test_ml_models()
    
    # Tahmin yap
    test_ml_prediction()
    
    # Modelleri karşılaştır
    test_both_models()
    
    print("\n" + "="*70)
    print("✅ TÜM ML TESTLER TAMAMLANDI!")
    print("="*70 + "\n")
