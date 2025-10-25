#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hakem Analiz Modülü
API-Football'dan gerçek hakem istatistikleri ve analiz
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime

API_KEY = "6336fb21e17dea87880d3b133132a13f"
BASE_URL = "https://v3.football.api-sports.io"

def get_referee_stats(referee_id: int, season: int = 2025) -> Optional[Dict]:
    """
    Hakem istatistiklerini API'den çek
    """
    headers = {'x-apisports-key': API_KEY}
    
    try:
        url = f"{BASE_URL}/referees?id={referee_id}&season={season}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('response') and len(data['response']) > 0:
                referee_data = data['response'][0]
                
                # İstatistikleri hesapla
                total_matches = len(referee_data.get('games', []))
                total_yellow = 0
                total_red = 0
                
                for game in referee_data.get('games', []):
                    total_yellow += game.get('cards', {}).get('yellow', {}).get('total', 0) or 0
                    total_red += game.get('cards', {}).get('red', {}).get('total', 0) or 0
                
                avg_yellow = round(total_yellow / max(total_matches, 1), 2)
                avg_red = round(total_red / max(total_matches, 1), 2)
                
                return {
                    'id': referee_data['id'],
                    'name': referee_data['name'],
                    'country': referee_data['country'],
                    'total_matches': total_matches,
                    'avg_yellow_per_match': avg_yellow,
                    'avg_red_per_match': avg_red,
                    'total_yellow': total_yellow,
                    'total_red': total_red
                }
                
    except Exception as e:
        print(f"Hakem istatistik hatası: {e}")
    
    return None


def get_league_referees(league_id: int = 203, season: int = 2025) -> List[Dict]:
    """
    Ligin hakemlerini listele
    """
    headers = {'x-apisports-key': API_KEY}
    
    try:
        url = f"{BASE_URL}/fixtures?league={league_id}&season={season}&last=50"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            referees = {}
            for fixture in data.get('response', []):
                referee_name = fixture.get('fixture', {}).get('referee')
                if referee_name and referee_name != 'None':
                    if referee_name not in referees:
                        referees[referee_name] = {
                            'name': referee_name,
                            'matches': 0,
                            'home_wins': 0,
                            'away_wins': 0,
                            'draws': 0
                        }
                    
                    referees[referee_name]['matches'] += 1
                    
                    # Maç sonucu
                    home_goals = fixture.get('goals', {}).get('home')
                    away_goals = fixture.get('goals', {}).get('away')
                    
                    if home_goals is not None and away_goals is not None:
                        if home_goals > away_goals:
                            referees[referee_name]['home_wins'] += 1
                        elif away_goals > home_goals:
                            referees[referee_name]['away_wins'] += 1
                        else:
                            referees[referee_name]['draws'] += 1
            
            # Ev sahibi kazanma oranlarını hesapla
            for referee in referees.values():
                total = referee['matches']
                if total > 0:
                    referee['home_win_rate'] = round((referee['home_wins'] / total) * 100, 1)
                    referee['away_win_rate'] = round((referee['away_wins'] / total) * 100, 1)
                    referee['draw_rate'] = round((referee['draws'] / total) * 100, 1)
            
            return list(referees.values())
            
    except Exception as e:
        print(f"Hakem listesi hatası: {e}")
    
    return []


def simulate_referee_impact(home_team: str, away_team: str, league: str = "Süper Lig") -> Dict:
    """
    Hakem etkisini simüle et (gerçek hakem atanmadıysa)
    
    Faktörler:
    - Kart ortalaması (sert/yumuşak hakem)
    - Ev sahibi avantajı bias
    - Tecrübe seviyesi
    """
    
    import random
    
    # Lig bazlı hakem profilleri
    league_profiles = {
        'Süper Lig': {
            'avg_yellow': 4.2,
            'avg_red': 0.15,
            'home_bias': 52,  # %52 ev sahibi kazanma oranı
            'experience': 'orta'
        },
        'Premier League': {
            'avg_yellow': 3.8,
            'avg_red': 0.08,
            'home_bias': 48,
            'experience': 'yüksek'
        },
        'La Liga': {
            'avg_yellow': 4.8,
            'avg_red': 0.12,
            'home_bias': 51,
            'experience': 'yüksek'
        },
        'Bundesliga': {
            'avg_yellow': 3.5,
            'avg_red': 0.06,
            'home_bias': 49,
            'experience': 'yüksek'
        },
        'Serie A': {
            'avg_yellow': 4.5,
            'avg_red': 0.18,
            'home_bias': 50,
            'experience': 'yüksek'
        }
    }
    
    profile = league_profiles.get(league, league_profiles['Süper Lig'])
    
    # Rastgele varyasyon ekle
    card_tendency = random.choice(['yumuşak', 'normal', 'sert'])
    
    if card_tendency == 'yumuşak':
        avg_yellow = profile['avg_yellow'] - random.uniform(0.5, 1.0)
        avg_red = profile['avg_red'] * 0.5
        card_impact = -2  # Teknik oyun avantajlı
    elif card_tendency == 'sert':
        avg_yellow = profile['avg_yellow'] + random.uniform(0.5, 1.5)
        avg_red = profile['avg_red'] * 1.5
        card_impact = -3  # Fiziksel oyun avantajlı
    else:
        avg_yellow = profile['avg_yellow']
        avg_red = profile['avg_red']
        card_impact = 0
    
    # Ev sahibi bias
    home_bias = profile['home_bias'] + random.uniform(-3, 3)
    
    if home_bias > 53:
        bias_category = "Ev sahibi lehine"
        bias_impact = 2
    elif home_bias < 47:
        bias_category = "Deplasman lehine"
        bias_impact = -2
    else:
        bias_category = "Dengeli"
        bias_impact = 0
    
    # Tecrübe etkisi
    experience_impact = 1 if profile['experience'] == 'yüksek' else 0
    
    # Toplam etki
    total_impact = card_impact + bias_impact + experience_impact
    total_impact = max(-5, min(5, total_impact))
    
    factors = []
    
    if card_tendency == 'sert':
        factors.append(f"🟥 Sert hakem (Ort. {avg_yellow:.1f} sarı kart)")
    elif card_tendency == 'yumuşak':
        factors.append(f"🟨 Yumuşak hakem (Ort. {avg_yellow:.1f} sarı kart)")
    else:
        factors.append(f"⚖️ Normal hakem (Ort. {avg_yellow:.1f} sarı kart)")
    
    factors.append(f"🏠 {bias_category} (%{home_bias:.1f} ev sahibi kazanma oranı)")
    
    if avg_red > 0.15:
        factors.append(f"🔴 Yüksek kırmızı kart oranı ({avg_red:.2f}/maç)")
    
    factors.append(f"📋 Tecrübe: {profile['experience'].title()}")
    
    # Kategori
    if total_impact >= 3:
        category = "EV SAHİBİ AVANTAJLI"
    elif total_impact <= -3:
        category = "DEPLASMAN AVANTAJLI"
    else:
        category = "DENGELİ"
    
    return {
        'available': True,
        'referee_name': f"Simülasyon ({league})",
        'card_tendency': card_tendency,
        'avg_yellow': round(avg_yellow, 1),
        'avg_red': round(avg_red, 2),
        'home_bias': round(home_bias, 1),
        'bias_category': bias_category,
        'experience': profile['experience'],
        'impact_score': total_impact,
        'category': category,
        'factors': factors,
        'prediction_impact': round(total_impact / 2, 1)  # -2.5% ile +2.5% arası
    }


def analyze_referee_impact(home_team: str, away_team: str, league: str = "Süper Lig", 
                           referee_name: str = None) -> Dict:
    """
    Hakem etkisini analiz et
    """
    
    # Hakem atanmışsa gerçek veri çek
    if referee_name:
        # TODO: Hakem isminden ID bul ve gerçek istatistikleri çek
        pass
    
    # Şimdilik simülasyon kullan
    return simulate_referee_impact(home_team, away_team, league)


if __name__ == "__main__":
    print("=" * 70)
    print("HAKEM ANALİZ TESTİ")
    print("=" * 70)
    
    # Test 1: Süper Lig hakemlerini listele
    print("\n📋 Süper Lig Hakemleri (Son 50 maç):")
    referees = get_league_referees(203, 2025)
    
    if referees:
        # En aktif hakemleri göster
        sorted_refs = sorted(referees, key=lambda x: x['matches'], reverse=True)[:5]
        for ref in sorted_refs:
            print(f"\n  👨‍⚖️ {ref['name']}")
            print(f"     Maçlar: {ref['matches']}")
            print(f"     Ev Sahibi Galibiyet: %{ref['home_win_rate']}")
            print(f"     Deplasman Galibiyet: %{ref['away_win_rate']}")
            print(f"     Beraberlik: %{ref['draw_rate']}")
    else:
        print("  ⚠️ Hakem verisi yok, simülasyon kullanılacak")
    
    # Test 2: Hakem etki analizi
    print("\n" + "=" * 70)
    print("HAKEM ETKİ ANALİZİ")
    print("=" * 70)
    
    print("\n⚖️ Galatasaray vs Fenerbahçe:")
    impact = analyze_referee_impact("Galatasaray", "Fenerbahçe", "Süper Lig")
    print(f"  Kategori: {impact['category']}")
    print(f"  Etki Skoru: {impact['impact_score']}/10")
    print(f"  Tahmin Etkisi: {impact['prediction_impact']}%")
    print(f"  Faktörler:")
    for factor in impact['factors']:
        print(f"    - {factor}")
    
    print("\n⚖️ Manchester City vs Liverpool:")
    impact = analyze_referee_impact("Manchester City", "Liverpool", "Premier League")
    print(f"  Kategori: {impact['category']}")
    print(f"  Kart Eğilimi: {impact['card_tendency'].upper()}")
    print(f"  Ortalama Sarı Kart: {impact['avg_yellow']}")
    print(f"  Ev Sahibi Bias: %{impact['home_bias']}")
