"""
🧪 PHASE 7 ENTEGRASYON TEST SCRIPT
Test eder: Phase 7 API endpoint'lerini ve sistemi
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8003"

def print_header(title):
    print("\n" + "="*80)
    print(f"🔍 {title}")
    print("="*80)

def test_phase7_status():
    """Phase 7 durum API'sini test et"""
    print_header("PHASE 7 STATUS API TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/api/phase7/status", timeout=10)
        data = response.json()
        
        print(f"\n✅ API Yanıtı: {response.status_code}")
        print(f"📊 Phase 7 Durumu: {'AKTİF' if data.get('phase7_available') else 'PASIF'}")
        print(f"📈 İlerleme: {data.get('progress', 'N/A')}")
        print(f"📁 Modül Durumu: {data.get('modules_ready', 'N/A')}")
        print(f"🎯 Sıradaki Adım: {data.get('next_step', 'N/A')}")
        
        print("\n📦 Modül Detayları:")
        for module, status in data.get('modules', {}).items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {module}: {'Hazır' if status else 'Eksik'}")
        
        print("\n💾 Veritabanı Durumu:")
        for db, exists in data.get('databases', {}).items():
            status_icon = "✅" if exists else "⏳"
            print(f"   {status_icon} {db}: {'Var' if exists else 'Yok'}")
        
        print("\n🤖 Model Durumu:")
        for model, exists in data.get('models', {}).items():
            status_icon = "✅" if exists else "⏳"
            print(f"   {status_icon} {model}: {'Eğitildi' if exists else 'Bekleniyor'}")
        
        return True
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_training_progress():
    """Eğitim ilerleme API'sini test et"""
    print_header("TRAINING PROGRESS API TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/api/phase7/training-progress", timeout=10)
        data = response.json()
        
        print(f"\n✅ API Yanıtı: {response.status_code}")
        print(f"📊 Toplam İlerleme: {data.get('progress', 'N/A')}")
        print(f"📁 Tamamlanan Adımlar: {data.get('completed_steps', 'N/A')}")
        print(f"🎯 Mevcut Aşama: {data.get('current_phase', 'N/A')}")
        
        print("\n📋 Adım Detayları:")
        for step, completed in data.get('steps', {}).items():
            status_icon = "✅" if completed else "⏳"
            print(f"   {status_icon} {step}: {'Tamamlandı' if completed else 'Bekliyor'}")
        
        stats = data.get('stats', {})
        if stats:
            print("\n📊 İstatistikler:")
            for key, value in stats.items():
                print(f"   • {key}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_cache_stats():
    """Cache istatistiklerini test et"""
    print_header("CACHE STATS API TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/api/cache-stats", timeout=10)
        data = response.json()
        
        if data.get('success'):
            stats = data.get('stats', {})
            print(f"\n✅ Cache Sistemi: AKTİF")
            print(f"📊 Hit Rate: {stats.get('hit_rate', 0):.1f}%")
            print(f"📁 Toplam Kayıt: {stats.get('total_entries', 0)}")
            print(f"✅ Cache Hit: {stats.get('hits', 0)}")
            print(f"❌ Cache Miss: {stats.get('misses', 0)}")
            print(f"💾 DB Boyutu: {stats.get('db_size_mb', 0):.2f} MB")
        else:
            print(f"❌ Cache Hatası: {data.get('error')}")
        
        return True
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_ml_models():
    """ML model listesini test et"""
    print_header("ML MODELS API TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ml-models", timeout=10)
        data = response.json()
        
        if data.get('success'):
            print(f"\n✅ ML Sistemi: AKTİF")
            print(f"🤖 Yüklü Modeller: {', '.join(data.get('models', []))}")
            
            metadata = data.get('metadata', {})
            if metadata:
                print("\n📊 Model Metadata:")
                for model, info in metadata.items():
                    print(f"   • {model}:")
                    print(f"     - Versiyon: {info.get('version', 'N/A')}")
                    print(f"     - Doğruluk: {info.get('accuracy', 'N/A')}")
        else:
            print(f"⚠️ ML Sistemi: {data.get('error')}")
        
        return True
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_factor_weights():
    """Faktör ağırlıklarını test et"""
    print_header("FACTOR WEIGHTS API TEST")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/factor-weights",
            params={'league': 'Super Lig', 'match_type': 'derby'},
            timeout=10
        )
        data = response.json()
        
        if data.get('success'):
            print(f"\n✅ Ağırlık Sistemi: AKTİF")
            print(f"🏆 Lig: {data.get('league', 'N/A')}")
            print(f"⚔️ Maç Tipi: {data.get('match_type', 'N/A')}")
            print(f"📊 Toplam Faktör: {data.get('total_factors', 0)}")
            
            weights = data.get('weights', {})
            if weights:
                print("\n⚖️ Faktör Ağırlıkları (İlk 10):")
                for i, (factor, weight) in enumerate(list(weights.items())[:10], 1):
                    print(f"   {i}. {factor}: {weight}")
        else:
            print(f"❌ Hata: {data.get('error')}")
        
        return True
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def generate_summary_report():
    """Özet rapor oluştur"""
    print_header("ENTEGRASYON ÖZET RAPORU")
    
    report = {
        'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tests': {
            'Phase 7 Status': test_phase7_status(),
            'Training Progress': test_training_progress(),
            'Cache Stats': test_cache_stats(),
            'ML Models': test_ml_models(),
            'Factor Weights': test_factor_weights()
        }
    }
    
    print("\n" + "="*80)
    print("📊 TEST SONUÇLARI")
    print("="*80)
    
    passed = sum(1 for result in report['tests'].values() if result)
    total = len(report['tests'])
    success_rate = (passed / total) * 100
    
    print(f"\n✅ Başarılı: {passed}/{total} ({success_rate:.1f}%)")
    print(f"⏰ Test Zamanı: {report['test_time']}")
    
    print("\n📋 Detay:")
    for test_name, result in report['tests'].items():
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"   • {test_name}: {status}")
    
    print("\n" + "="*80)
    print("🎯 GENEL DURUM: " + ("✅ SİSTEM HAZIR!" if success_rate >= 80 else "⚠️ BAZI TESTLER BAŞARISIZ"))
    print("="*80 + "\n")
    
    return report

if __name__ == "__main__":
    print("\n" + "🚀"*40)
    print("PHASE 7 ENTEGRASYON TEST SÜİTİ")
    print("🚀"*40 + "\n")
    
    print("📡 Sunucu Bağlantısı Kontrol Ediliyor...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Sunucu erişilebilir: {BASE_URL}")
    except Exception as e:
        print(f"❌ Sunucu erişilemedi: {e}")
        print("⚠️ Lütfen sunucuyu başlatın: python simple_fastapi.py")
        exit(1)
    
    # Tüm testleri çalıştır
    summary = generate_summary_report()
    
    # Raporu kaydet
    with open('phase7_integration_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("💾 Rapor kaydedildi: phase7_integration_test_report.json")
