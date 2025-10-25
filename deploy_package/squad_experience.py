#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kadro Tecrübe Analiz Modülü
Ortalama yaş, tecrübe seviyesi, genç/deneyimli denge
"""

import requests
from typing import Dict, Optional, List

# Cache sistemi
try:
    from api_cache_wrapper import cache
    CACHE_ENABLED = True
except:
    CACHE_ENABLED = False

API_KEY = "6336fb21e17dea87880d3b133132a13f"
BASE_URL = "https://v3.football.api-sports.io"

def get_squad_statistics(team_id: int, season: int = 2025) -> Optional[Dict]:
    """
    Kadro istatistiklerini çek (yaş, tecrübe) - CACHE'Lİ
    """
    # Cache kontrol
    if CACHE_ENABLED:
        try:
            cached = cache.get('squad', team_id=team_id, season=season)
            if cached:
                return cached
        except:
            pass
    
    headers = {'x-apisports-key': API_KEY}
    
    try:
        url = f"{BASE_URL}/players/squads?team={team_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('response') and len(data['response']) > 0:
                squad = data['response'][0]['players']
                
                ages = []
                for player in squad:
                    age = player.get('age')
                    if age:
                        ages.append(age)
                
                if ages:
                    avg_age = sum(ages) / len(ages)
                    min_age = min(ages)
                    max_age = max(ages)
                    
                    # Yaş gruplarını say
                    young = len([a for a in ages if a < 24])  # Genç
                    prime = len([a for a in ages if 24 <= a <= 29])  # Zirvede
                    veteran = len([a for a in ages if a >= 30])  # Deneyimli
                    
                    result = {
                        'total_players': len(squad),
                        'avg_age': round(avg_age, 1),
                        'min_age': min_age,
                        'max_age': max_age,
                        'young_players': young,
                        'prime_players': prime,
                        'veteran_players': veteran
                    }
                    
                    # Cache'e kaydet (12 saat)
                    if CACHE_ENABLED:
                        try:
                            cache.set('squad', result, 43200, team_id=team_id, season=season)
                        except:
                            pass
                    
                    return result
                    
    except Exception as e:
        print(f"Kadro istatistik hatası: {e}")
    
    return None


def analyze_squad_experience(team_name: str, team_id: int = None, 
                             league_position: int = 10, season_count: int = 3) -> Dict:
    """
    Kadro tecrübe analizi
    
    Faktörler:
    - Ortalama yaş (genç/olgun/yaşlı)
    - Genç-Deneyimli dengesi
    - Lig tecrübesi (sıralamadan tahmin)
    - Fiziksel dayanıklılık
    """
    
    # Gerçek kadro verisi
    squad_data = None
    if team_id:
        squad_data = get_squad_statistics(team_id)
    
    if squad_data:
        avg_age = squad_data['avg_age']
        young = squad_data['young_players']
        prime = squad_data['prime_players']
        veteran = squad_data['veteran_players']
        total = squad_data['total_players']
        
        impact_score = 0
        factors = []
        
        # 1. Ortalama Yaş Değerlendirmesi
        if avg_age < 24:
            impact_score -= 2
            age_category = "ÇOK GENÇ"
            factors.append(f"⚠️ Genç kadro (Ort. {avg_age}) - Tecrübe eksikliği")
        elif 24 <= avg_age < 26:
            impact_score += 3
            age_category = "İDEAL (GENÇ-DİNAMİK)"
            factors.append(f"✅ İdeal yaş dengesi (Ort. {avg_age}) - Enerji + Tecrübe")
        elif 26 <= avg_age < 28:
            impact_score += 5
            age_category = "ZİRVE"
            factors.append(f"🔥 Zirvede kadro (Ort. {avg_age}) - Maksimum performans")
        elif 28 <= avg_age < 30:
            impact_score += 3
            age_category = "DENEYİMLİ"
            factors.append(f"👴 Deneyimli kadro (Ort. {avg_age}) - Tecrübe avantajı")
        else:
            impact_score -= 3
            age_category = "YAŞLI"
            factors.append(f"⚠️ Yaşlı kadro (Ort. {avg_age}) - Fiziksel dezavantaj")
        
        # 2. Genç-Deneyimli Dengesi
        young_ratio = young / total
        veteran_ratio = veteran / total
        prime_ratio = prime / total
        
        if prime_ratio > 0.5:  # %50'den fazla zirvede oyuncu
            impact_score += 3
            factors.append(f"⚡ Kadronun %{prime_ratio*100:.0f}'si zirvede (24-29 yaş)")
        
        if young_ratio > 0.4 and veteran_ratio < 0.2:
            impact_score -= 2
            factors.append(f"🆕 Fazla genç oyuncu (%{young_ratio*100:.0f}) - Tecrübe sığ")
        
        if veteran_ratio > 0.35:
            impact_score -= 2
            factors.append(f"👴 Fazla yaşlı oyuncu (%{veteran_ratio*100:.0f}) - Dayanıklılık riski")
        
        if 0.2 <= young_ratio <= 0.35 and 0.15 <= veteran_ratio <= 0.30:
            impact_score += 2
            factors.append(f"⚖️ Dengeli yaş dağılımı - Genç: %{young_ratio*100:.0f}, Deneyimli: %{veteran_ratio*100:.0f}")
        
        # 3. Lig Tecrübesi (Sıralamadan tahmin)
        if league_position <= 5:
            impact_score += 2
            factors.append(f"🏆 Şampiyonluk tecrübesi - Üst sıralarda ({league_position}.)")
        elif league_position >= 15:
            impact_score -= 1
            factors.append(f"⚠️ Küme düşme tecrübesi - Alt sıralarda ({league_position}.)")
        
        # 4. Süreklilik (Sezon sayısı)
        if season_count >= 5:
            impact_score += 2
            factors.append(f"📅 Uzun süreli kadro ({season_count} sezon) - İyi kimya")
        elif season_count <= 2:
            impact_score -= 1
            factors.append(f"🆕 Yeni oluşan kadro ({season_count} sezon)")
        
        # Kategori
        if impact_score >= 8:
            category = "ÇOK GÜÇLÜ"
        elif impact_score >= 4:
            category = "GÜÇLÜ"
        elif impact_score >= 0:
            category = "DENGELİ"
        elif impact_score >= -4:
            category = "ZAYIF"
        else:
            category = "ÇOK ZAYIF"
        
        return {
            'available': True,
            'avg_age': avg_age,
            'age_category': age_category,
            'total_players': total,
            'young_players': young,
            'prime_players': prime,
            'veteran_players': veteran,
            'young_ratio': round(young_ratio * 100, 1),
            'prime_ratio': round(prime_ratio * 100, 1),
            'veteran_ratio': round(veteran_ratio * 100, 1),
            'impact_score': impact_score,
            'category': category,
            'factors': factors,
            'prediction_impact': round(impact_score * 0.5, 1)  # -3% ile +5% arası
        }
    
    # Veri yoksa varsayılan
    else:
        # Lig pozisyonundan tahmin
        if league_position <= 3:
            impact_score = 4
            category = "GÜÇLÜ"
            note = "Veri yok - Üst sıra takımı, deneyimli kadro varsayılıyor"
        elif league_position <= 10:
            impact_score = 1
            category = "DENGELİ"
            note = "Veri yok - Orta sıra takımı, dengeli kadro varsayılıyor"
        else:
            impact_score = -1
            category = "ZAYIF"
            note = "Veri yok - Alt sıra takımı, genç kadro varsayılıyor"
        
        return {
            'available': False,
            'avg_age': 26.5,
            'age_category': "BİLİNMİYOR",
            'total_players': 0,
            'young_players': 0,
            'prime_players': 0,
            'veteran_players': 0,
            'young_ratio': 0,
            'prime_ratio': 0,
            'veteran_ratio': 0,
            'impact_score': impact_score,
            'category': category,
            'factors': [note],
            'prediction_impact': round(impact_score * 0.5, 1)
        }


def compare_squad_experience(home_team: str, away_team: str,
                             home_team_id: int = None, away_team_id: int = None,
                             home_position: int = 10, away_position: int = 10) -> Dict:
    """
    İki takımın kadro tecrübelerini karşılaştır
    """
    
    home_exp = analyze_squad_experience(home_team, home_team_id, home_position)
    away_exp = analyze_squad_experience(away_team, away_team_id, away_position)
    
    # Avantaj hesapla
    impact_diff = home_exp['impact_score'] - away_exp['impact_score']
    
    # Yaş karşılaştırması
    age_diff = home_exp['avg_age'] - away_exp['avg_age']
    
    if impact_diff > 3:
        advantage = home_team
        advantage_desc = f"{home_team} daha tecrübeli ve dengeli kadro"
    elif impact_diff < -3:
        advantage = away_team
        advantage_desc = f"{away_team} daha tecrübeli ve dengeli kadro"
    else:
        advantage = "Dengeli"
        advantage_desc = "Her iki takım da benzer tecrübe seviyesinde"
    
    # Özel durumlar
    insights = []
    if abs(age_diff) > 3:
        if age_diff > 0:
            insights.append(f"⚖️ {home_team} {abs(age_diff):.1f} yaş daha olgun - Tecrübe avantajı")
        else:
            insights.append(f"⚡ {away_team} {abs(age_diff):.1f} yaş daha genç - Enerji avantajı")
    
    if home_exp['available'] and away_exp['available']:
        if home_exp['prime_ratio'] - away_exp['prime_ratio'] > 15:
            insights.append(f"🔥 {home_team}'da %{home_exp['prime_ratio']-away_exp['prime_ratio']:.0f} daha fazla zirvede oyuncu")
    
    return {
        'home_experience': home_exp,
        'away_experience': away_exp,
        'advantage': advantage,
        'advantage_description': advantage_desc,
        'impact_difference': impact_diff,
        'age_difference': round(age_diff, 1),
        'insights': insights,
        'prediction_impact': round(impact_diff * 0.4, 1)  # -2% ile +2% arası
    }


if __name__ == "__main__":
    print("=" * 70)
    print("KADRO TECRÜBE ANALİZ TESTİ")
    print("=" * 70)
    
    # Test 1: Galatasaray (team_id: 645)
    print("\n👥 Galatasaray Kadro Analizi:")
    analysis = analyze_squad_experience("Galatasaray", 645, 1, 5)
    
    if analysis['available']:
        print(f"  Ortalama Yaş: {analysis['avg_age']} ({analysis['age_category']})")
        print(f"  Kadro Büyüklüğü: {analysis['total_players']} oyuncu")
        print(f"  Genç (<24): {analysis['young_players']} (%{analysis['young_ratio']})")
        print(f"  Zirvede (24-29): {analysis['prime_players']} (%{analysis['prime_ratio']})")
        print(f"  Deneyimli (30+): {analysis['veteran_players']} (%{analysis['veteran_ratio']})")
        print(f"  Kategori: {analysis['category']}")
        print(f"  Etki Skoru: {analysis['impact_score']}/10")
        print(f"  Tahmin Etkisi: {analysis['prediction_impact']}%")
        
        print(f"\n  Faktörler:")
        for factor in analysis['factors']:
            print(f"    {factor}")
    else:
        print(f"  Durum: {analysis['category']}")
        print(f"  Not: {analysis['factors'][0]}")
    
    # Test 2: Manchester City
    print("\n" + "=" * 70)
    print("👥 Manchester City Kadro Analizi:")
    analysis = analyze_squad_experience("Manchester City", None, 1, 8)
    print(f"  Kategori: {analysis['category']}")
    print(f"  Not: {analysis['factors'][0]}")
    
    # Test 3: Karşılaştırma
    print("\n" + "=" * 70)
    print("⚖️ Galatasaray vs Fenerbahçe Tecrübe Karşılaştırması:")
    comparison = compare_squad_experience("Galatasaray", "Fenerbahçe", 645, 611, 1, 3)
    
    print(f"\n  Avantaj: {comparison['advantage']}")
    print(f"  Açıklama: {comparison['advantage_description']}")
    print(f"  Yaş Farkı: {comparison['age_difference']} yıl")
    print(f"  Etki Farkı: {comparison['impact_difference']}")
    print(f"  Tahmin Etkisi: {comparison['prediction_impact']}%")
    
    if comparison['insights']:
        print(f"\n  💡 Özel Görüşler:")
        for insight in comparison['insights']:
            print(f"    {insight}")
