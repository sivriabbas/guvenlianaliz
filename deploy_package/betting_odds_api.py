#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bahis Oranları Analiz Modülü
API-Football'dan gerçek bahis oranları ve piyasa beklentileri
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime

API_KEY = "6336fb21e17dea87880d3b133132a13f"
BASE_URL = "https://v3.football.api-sports.io"

def get_fixture_odds(fixture_id: int) -> Optional[Dict]:
    """
    Maç için bahis oranlarını çek
    """
    headers = {'x-apisports-key': API_KEY}
    
    try:
        url = f"{BASE_URL}/odds?fixture={fixture_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('response') and len(data['response']) > 0:
                # İlk bookmaker'ın oranlarını al (genelde Bet365)
                odds_data = data['response'][0]
                bookmaker = odds_data['bookmakers'][0] if odds_data.get('bookmakers') else None
                
                if bookmaker:
                    # Match Winner oranlarını bul
                    for bet in bookmaker['bets']:
                        if bet['name'] == 'Match Winner':
                            values = bet['values']
                            
                            home_odd = None
                            draw_odd = None
                            away_odd = None
                            
                            for val in values:
                                if val['value'] == 'Home':
                                    home_odd = float(val['odd'])
                                elif val['value'] == 'Draw':
                                    draw_odd = float(val['odd'])
                                elif val['value'] == 'Away':
                                    away_odd = float(val['odd'])
                            
                            if home_odd and draw_odd and away_odd:
                                return {
                                    'bookmaker': bookmaker['name'],
                                    'home_odd': home_odd,
                                    'draw_odd': draw_odd,
                                    'away_odd': away_odd
                                }
                
    except Exception as e:
        print(f"Bahis oranları hatası: {e}")
    
    return None


def find_fixture_by_teams(team1_id: int, team2_id: int, season: int = 2025) -> Optional[int]:
    """
    İki takım arasındaki yaklaşan maçın fixture ID'sini bul
    """
    headers = {'x-apisports-key': API_KEY}
    
    try:
        # Önce ev sahibi team1
        url = f"{BASE_URL}/fixtures?team={team1_id}&season={season}&next=10"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for fixture in data.get('response', []):
                home_id = fixture['teams']['home']['id']
                away_id = fixture['teams']['away']['id']
                
                if (home_id == team1_id and away_id == team2_id) or \
                   (home_id == team2_id and away_id == team1_id):
                    return fixture['fixture']['id']
        
    except Exception as e:
        print(f"Fixture arama hatası: {e}")
    
    return None


def odds_to_probability(odd: float) -> float:
    """
    Bahis oranını olasılığa çevir
    """
    return (1 / odd) * 100


def simulate_betting_odds(home_team: str, away_team: str, home_elo: int, away_elo: int) -> Dict:
    """
    Bahis oranlarını simüle et (ELO bazlı)
    """
    
    # ELO farkından beklenen skoru hesapla
    elo_diff = home_elo - away_elo
    home_prob = 1 / (1 + 10 ** (-elo_diff / 400))
    
    # Ev avantajı ekle
    home_prob = min(0.75, home_prob * 1.1)
    
    # Beraberlik ve deplasman olasılıkları
    draw_prob = 0.25
    away_prob = max(0.05, 1 - home_prob - draw_prob)  # Minimum %5
    
    # Normalize
    total = home_prob + draw_prob + away_prob
    home_prob /= total
    draw_prob /= total
    away_prob /= total
    
    # Oranları hesapla (bookmaker marjı %5)
    margin = 1.05
    home_odd = round((1 / max(home_prob, 0.01)) * margin, 2)
    draw_odd = round((1 / max(draw_prob, 0.01)) * margin, 2)
    away_odd = round((1 / max(away_prob, 0.01)) * margin, 2)
    
    return {
        'bookmaker': 'Simülasyon (ELO)',
        'home_odd': home_odd,
        'draw_odd': draw_odd,
        'away_odd': away_odd,
        'home_prob': round(home_prob * 100, 1),
        'draw_prob': round(draw_prob * 100, 1),
        'away_prob': round(away_prob * 100, 1)
    }


def analyze_betting_odds(home_team: str, away_team: str, home_elo: int = 1600, away_elo: int = 1500,
                         team1_id: int = None, team2_id: int = None) -> Dict:
    """
    Bahis oranlarını analiz et ve değer bahis tespiti yap
    """
    
    # Gerçek oranları bulmaya çalış
    odds_data = None
    if team1_id and team2_id:
        fixture_id = find_fixture_by_teams(team1_id, team2_id)
        if fixture_id:
            odds_data = get_fixture_odds(fixture_id)
    
    # Bulunamadıysa simülasyon yap
    if not odds_data:
        odds_data = simulate_betting_odds(home_team, away_team, home_elo, away_elo)
    
    # Olasılıkları hesapla
    home_prob = odds_to_probability(odds_data['home_odd'])
    draw_prob = odds_to_probability(odds_data['draw_odd'])
    away_prob = odds_to_probability(odds_data['away_odd'])
    
    # Piyasa beklentisi
    if home_prob > 50:
        market_favorite = home_team
        favorite_prob = home_prob
    elif away_prob > 40:
        market_favorite = away_team
        favorite_prob = away_prob
    else:
        market_favorite = "Dengeli"
        favorite_prob = max(home_prob, away_prob)
    
    # Değer bahis analizi
    value_bets = []
    
    # Basit değer bahis tespiti (gerçek modelimizle karşılaştır)
    if home_elo > away_elo + 150:
        if odds_data['home_odd'] > 2.0:
            value_bets.append(f"Ev sahibi değer bahis (oran {odds_data['home_odd']})")
    
    if away_elo > home_elo + 100:
        if odds_data['away_odd'] > 2.5:
            value_bets.append(f"Deplasman değer bahis (oran {odds_data['away_odd']})")
    
    if abs(home_elo - away_elo) < 50:
        if odds_data['draw_odd'] < 3.5:
            value_bets.append(f"Beraberlik değer bahis (oran {odds_data['draw_odd']})")
    
    # Etki hesapla
    impact_score = 0
    
    # Piyasa favori bizim tahminimizle uyuşuyorsa +etki
    if (market_favorite == home_team and home_elo > away_elo) or \
       (market_favorite == away_team and away_elo > home_elo):
        impact_score += 2
    else:
        impact_score -= 2
    
    # Oran dengesi
    if max(home_prob, away_prob) > 60:
        impact_score += 1  # Net favori var
    
    factors = []
    factors.append(f"📊 Piyasa favorisi: {market_favorite} (%{favorite_prob:.1f})")
    factors.append(f"🏠 Ev sahibi: {odds_data['home_odd']} (Olasılık: %{home_prob:.1f})")
    factors.append(f"🤝 Beraberlik: {odds_data['draw_odd']} (Olasılık: %{draw_prob:.1f})")
    factors.append(f"✈️ Deplasman: {odds_data['away_odd']} (Olasılık: %{away_prob:.1f})")
    
    if value_bets:
        factors.append(f"💰 Değer Bahisler: {', '.join(value_bets)}")
    
    return {
        'available': True,
        'bookmaker': odds_data['bookmaker'],
        'home_odd': odds_data['home_odd'],
        'draw_odd': odds_data['draw_odd'],
        'away_odd': odds_data['away_odd'],
        'home_probability': round(home_prob, 1),
        'draw_probability': round(draw_prob, 1),
        'away_probability': round(away_prob, 1),
        'market_favorite': market_favorite,
        'favorite_probability': round(favorite_prob, 1),
        'value_bets': value_bets,
        'impact_score': impact_score,
        'factors': factors,
        'prediction_impact': round(impact_score / 2, 1)  # -1% ile +1% arası
    }


if __name__ == "__main__":
    print("=" * 70)
    print("BAHİS ORANLARI ANALİZ TESTİ")
    print("=" * 70)
    
    # Test 1: Simülasyon (ELO bazlı)
    print("\n💰 Galatasaray (1700) vs Fenerbahçe (1500):")
    analysis = analyze_betting_odds("Galatasaray", "Fenerbahçe", 1700, 1500)
    
    print(f"  Bookmaker: {analysis['bookmaker']}")
    print(f"  Oranlar: {analysis['home_odd']} - {analysis['draw_odd']} - {analysis['away_odd']}")
    print(f"  Piyasa Favorisi: {analysis['market_favorite']} (%{analysis['favorite_probability']})")
    print(f"  Etki Skoru: {analysis['impact_score']}/10")
    print(f"  Tahmin Etkisi: {analysis['prediction_impact']}%")
    
    if analysis['value_bets']:
        print(f"  💎 Değer Bahisler:")
        for vb in analysis['value_bets']:
            print(f"    - {vb}")
    
    # Test 2: Dengeli maç
    print("\n💰 Manchester City (1900) vs Liverpool (1880):")
    analysis = analyze_betting_odds("Manchester City", "Liverpool", 1900, 1880)
    
    print(f"  Oranlar: {analysis['home_odd']} - {analysis['draw_odd']} - {analysis['away_odd']}")
    print(f"  Piyasa: {analysis['market_favorite']}")
    
    # Test 3: Sürpriz potansiyeli
    print("\n💰 Real Madrid (1950) vs Barcelona (1920):")
    analysis = analyze_betting_odds("Real Madrid", "Barcelona", 1950, 1920)
    
    print(f"  Oranlar: {analysis['home_odd']} - {analysis['draw_odd']} - {analysis['away_odd']}")
    print(f"  Ev Sahibi Olasılık: %{analysis['home_probability']}")
    print(f"  Deplasman Olasılık: %{analysis['away_probability']}")
