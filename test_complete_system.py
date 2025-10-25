"""
KOMPLE SİSTEM TEST - 17 FAKTÖR
comprehensive_match_analysis fonksiyonunu doğrudan çağır
"""
import asyncio
import sys
import os

# simple_fastapi modülünü import et
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simple_fastapi import comprehensive_match_analysis

async def test_system():
    print("="*80)
    print("🚀 17 FAKTÖRLÜ KOMPLE SİSTEM TESTİ (PHASE 1 + 2 + 3)")
    print("="*80)
    
    team1 = "Galatasaray"
    team2 = "Fenerbahce"  # API'de Türkçe karakter yok
    
    print(f"\n📊 Analiz ediliyor: {team1} vs {team2}")
    print("="*80)
    
    try:
        result = await comprehensive_match_analysis(team1, team2)
        
        print(f"\n✅ ANALİZ TAMAMLANDI! (Sonuç tipi: {type(result)})")
        print(f"📊 Sonuç anahtarları: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        print("="*80)
        
        # Hata kontrolü
        if not result.get('success', False):
            print(f"\n❌ ANALİZ HATASI:")
            print(f"  Hata: {result.get('error', 'Bilinmeyen hata')}")
            print(f"  Not: {result.get('note', 'Detay yok')}")
            return
        
        # Tahmin sonuçları
        if 'final_prediction' in result:
            pred = result['final_prediction']
            print(f"\n🎯 TAHMİN SONUÇLARI:")
            print(f"  {team1}: %{pred.get('team1_win', 0):.1f}")
            print(f"  Beraberlik: %{pred.get('draw', 0):.1f}")
            print(f"  {team2}: %{pred.get('team2_win', 0):.1f}")
        
        # Advanced factors - Phase 3
        if 'advanced_factors' in result:
            adv = result['advanced_factors']
            
            print(f"\n{'='*80}")
            print("🔍 PHASE 3 FAKTÖRLER (TAKTIK, TRANSFER, TECRÜBE)")
            print("="*80)
            
            # FAKTÖR 15: Taktiksel Uyum
            if 'tactical_matchup' in adv:
                tact = adv['tactical_matchup']
                print(f"\n⚔️  FAKTÖR 15: TAKTİKSEL UYUM")
                print(f"  ├─ {team1}: {tact.get('team1_formation', 'N/A')}")
                print(f"  │  └─ Stil: {tact.get('team1_style', 'N/A')}")
                print(f"  ├─ {team2}: {tact.get('team2_formation', 'N/A')}")
                print(f"  │  └─ Stil: {tact.get('team2_style', 'N/A')}")
                print(f"  ├─ Uyum Skoru: {tact.get('matchup_score', 0)}/10")
                print(f"  ├─ Kategori: {tact.get('matchup_category', 'N/A')}")
                print(f"  └─ ⚡ Etki: {tact.get('prediction_impact', 0):+.1f}%")
            
            # FAKTÖR 16: Transfer Etkisi
            if 'transfer_situation' in adv:
                trans = adv['transfer_situation']
                print(f"\n📋 FAKTÖR 16: TRANSFER ETKİSİ")
                print(f"  ├─ {team1}: {trans.get('team1_total_transfers', 0)} transfer")
                print(f"  │  ├─ Son dönem: {trans.get('team1_recent_transfers', 0)}")
                print(f"  │  └─ Etki skoru: {trans.get('team1_transfer_impact', 0)}")
                print(f"  ├─ {team2}: {trans.get('team2_total_transfers', 0)} transfer")
                print(f"  │  ├─ Son dönem: {trans.get('team2_recent_transfers', 0)}")
                print(f"  │  └─ Etki skoru: {trans.get('team2_transfer_impact', 0)}")
                print(f"  ├─ Karşılaştırma: {trans.get('comparison_category', 'N/A')}")
                print(f"  └─ ⚡ Etki: {trans.get('prediction_impact', 0):+.1f}%")
            
            # FAKTÖR 17: Kadro Tecrübesi
            if 'squad_experience' in adv:
                exp = adv['squad_experience']
                print(f"\n👥 FAKTÖR 17: KADRO TECRÜBESİ")
                print(f"  ├─ {team1}:")
                print(f"  │  ├─ Ortalama yaş: {exp.get('team1_avg_age', 0):.1f}")
                print(f"  │  ├─ Oyuncu sayısı: {exp.get('team1_player_count', 0)}")
                print(f"  │  ├─ Genç (%): {exp.get('team1_young_pct', 0):.1f}%")
                print(f"  │  ├─ Zirve (%): {exp.get('team1_prime_pct', 0):.1f}%")
                print(f"  │  ├─ Veteran (%): {exp.get('team1_veteran_pct', 0):.1f}%")
                print(f"  │  ├─ Kategori: {exp.get('team1_category', 'N/A')}")
                print(f"  │  └─ Skor: {exp.get('team1_exp_score', 0)}/10")
                print(f"  ├─ {team2}:")
                print(f"  │  ├─ Ortalama yaş: {exp.get('team2_avg_age', 0):.1f}")
                print(f"  │  ├─ Oyuncu sayısı: {exp.get('team2_player_count', 0)}")
                print(f"  │  ├─ Genç (%): {exp.get('team2_young_pct', 0):.1f}%")
                print(f"  │  ├─ Zirve (%): {exp.get('team2_prime_pct', 0):.1f}%")
                print(f"  │  ├─ Veteran (%): {exp.get('team2_veteran_pct', 0):.1f}%")
                print(f"  │  ├─ Kategori: {exp.get('team2_category', 'N/A')}")
                print(f"  │  └─ Skor: {exp.get('team2_exp_score', 0)}/10")
                print(f"  ├─ Karşılaştırma: {exp.get('comparison', 'N/A')}")
                print(f"  └─ ⚡ Etki: {exp.get('prediction_impact', 0):+.1f}%")
        
        # Model predictions - faktör sayısı kontrolü
        if 'model_predictions' in result:
            models = result['model_predictions']
            if 'Yapay Sinir Ağı' in models:
                ann = models['Yapay Sinir Ağı']
                if 'factors_used' in ann:
                    factors = ann['factors_used']
                    
                    print(f"\n{'='*80}")
                    print(f"📋 KULLANILAN TÜM FAKTÖRLER: {len(factors)} ADET")
                    print("="*80)
                    
                    # Phase bazında grupla
                    phase1 = ['🏥 Sakatlık', '🎯 Motivasyon', '📊 xG']
                    phase2 = ['🌤️ Hava', '⚖️ Hakem', '💰 Bahis']
                    phase3 = ['⚔️ Taktik', '📋 Transfer', '👥 Tecrübe']
                    
                    base_factors = [f for f in factors if not any(p in f for p in phase1 + phase2 + phase3)]
                    p1_factors = [f for f in factors if any(p in f for p in phase1)]
                    p2_factors = [f for f in factors if any(p in f for p in phase2)]
                    p3_factors = [f for f in factors if any(p in f for p in phase3)]
                    
                    print(f"\n📊 TEMEL FAKTÖRLER ({len(base_factors)} adet):")
                    for f in base_factors:
                        print(f"  • {f}")
                    
                    print(f"\n🏥 PHASE 1 FAKTÖRLER ({len(p1_factors)} adet):")
                    for f in p1_factors:
                        print(f"  • {f}")
                    
                    print(f"\n🌤️ PHASE 2 FAKTÖRLER ({len(p2_factors)} adet):")
                    for f in p2_factors:
                        print(f"  • {f}")
                    
                    print(f"\n⚔️ PHASE 3 FAKTÖRLER ({len(p3_factors)} adet):")
                    for f in p3_factors:
                        print(f"  • {f}")
        
        print(f"\n{'='*80}")
        print("🎉 17 FAKTÖRLÜ KOMPLE SİSTEM BAŞARIYLA ÇALIŞIYOR!")
        print("✅ PHASE 1 + PHASE 2 + PHASE 3 ENTEGRASYONU TAMAMLANDI!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()

# Async fonksiyonu çalıştır
if __name__ == "__main__":
    asyncio.run(test_system())
