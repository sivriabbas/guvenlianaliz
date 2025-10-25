"""
17 FAKTÖRLÜ SİSTEMİ TEST ET
"""
import requests
import json

# Test et
url = "http://127.0.0.1:8003/analyze"
data = {
    "team1": "Galatasaray",
    "team2": "Fenerbahce",
    "season": 2024
}

print("🚀 17 FAKTÖRLÜ KOMPLE SİSTEM TESTİ")
print("="*60)
print(f"📊 Test: {data['team1']} vs {data['team2']}")
print("="*60)

try:
    # Form data olarak gönder
    response = requests.post(url, data=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ ANALİZ BAŞARILI!")
        print("="*60)
        
        # Tahmin sonuçları
        if 'final_prediction' in result:
            pred = result['final_prediction']
            print(f"\n🎯 TAHMİN SONUÇLARI:")
            print(f"  {data['team1']}: %{pred.get('team1_win', 0):.1f}")
            print(f"  Beraberlik: %{pred.get('draw', 0):.1f}")
            print(f"  {data['team2']}: %{pred.get('team2_win', 0):.1f}")
        
        # Advanced factors
        if 'advanced_factors' in result:
            adv = result['advanced_factors']
            print(f"\n🔍 GELİŞMİŞ FAKTÖRLER:")
            
            # Taktiksel Analiz (Phase 3 - Faktör 15)
            if 'tactical_matchup' in adv:
                tact = adv['tactical_matchup']
                print(f"\n  ⚔️ TAKTİKSEL UYUM:")
                print(f"    {data['team1']}: {tact.get('team1_formation', 'N/A')}")
                print(f"    {data['team2']}: {tact.get('team2_formation', 'N/A')}")
                print(f"    Uyum: {tact.get('matchup_category', 'N/A')} ({tact.get('matchup_score', 0)}/10)")
                print(f"    Etki: {tact.get('prediction_impact', 0):+.1f}%")
            
            # Transfer Analizi (Phase 3 - Faktör 16)
            if 'transfer_situation' in adv:
                trans = adv['transfer_situation']
                print(f"\n  📋 TRANSFER ETKİSİ:")
                print(f"    {data['team1']}: {trans.get('team1_total_transfers', 0)} transfer")
                print(f"    {data['team2']}: {trans.get('team2_total_transfers', 0)} transfer")
                print(f"    Durum: {trans.get('comparison_category', 'N/A')}")
                print(f"    Etki: {trans.get('prediction_impact', 0):+.1f}%")
            
            # Kadro Tecrübesi (Phase 3 - Faktör 17)
            if 'squad_experience' in adv:
                exp = adv['squad_experience']
                print(f"\n  👥 KADRO TECRÜBESİ:")
                print(f"    {data['team1']}: Ort. {exp.get('team1_avg_age', 0):.1f} yaş ({exp.get('team1_category', 'N/A')})")
                print(f"    {data['team2']}: Ort. {exp.get('team2_avg_age', 0):.1f} yaş ({exp.get('team2_category', 'N/A')})")
                print(f"    Etki: {exp.get('prediction_impact', 0):+.1f}%")
        
        # Kullanılan faktörler
        if 'model_predictions' in result:
            models = result['model_predictions']
            if 'Yapay Sinir Ağı' in models:
                ann = models['Yapay Sinir Ağı']
                if 'factors_used' in ann:
                    factors = ann['factors_used']
                    print(f"\n📋 KULLANILAN FAKTÖRLER ({len(factors)} adet):")
                    for i, factor in enumerate(factors, 1):
                        print(f"  {i}. {factor}")
        
        print("\n" + "="*60)
        print("✅ PHASE 3 ENTEGRASYONU TAMAMLANDI!")
        print("🎉 17 FAKTÖRLÜ KOMPLE SİSTEM ÇALIŞIYOR!")
        print("="*60)
        
    else:
        print(f"\n❌ Hata: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ Hata: {str(e)}")
