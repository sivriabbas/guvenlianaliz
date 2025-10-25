#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expected Goals (xG) Analiz Modülü
"""

import requests
from typing import Dict, Optional

API_KEY = "6336fb21e17dea87880d3b133132a13f"
BASE_URL = "https://v3.football.api-sports.io"

def get_xg_data(team_id: int, last_matches: int = 10) -> Dict:
    """
    Takımın son maçlarındaki xG (beklenen gol) verilerini al
    """
    
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': API_KEY
    }
    
    # Son maçları al
    url = f"{BASE_URL}/fixtures"
    params = {
        'team': team_id,
        'last': last_matches,
        'timezone': 'Europe/Istanbul'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get('response', [])
            
            xg_data = []
            total_xg_for = 0
            total_xg_against = 0
            total_goals_for = 0
            total_goals_against = 0
            
            for match in fixtures:
                # xG verileri varsa kullan (API'de olmayabilir)
                # Şimdilik gerçek gol verilerinden tahmin ediyoruz
                
                home_team = match['teams']['home']
                away_team = match['teams']['away']
                home_goals = match['goals']['home'] or 0
                away_goals = match['goals']['away'] or 0
                
                is_home = home_team['id'] == team_id
                
                if is_home:
                    team_goals = home_goals
                    opponent_goals = away_goals
                else:
                    team_goals = away_goals
                    opponent_goals = home_goals
                
                # xG tahmini (basit yaklaşım: şut sayısı ve pozisyondan)
                stats = match.get('statistics', [])
                team_xg = estimate_xg_from_stats(stats, team_id, is_home)
                opponent_xg = estimate_xg_from_stats(stats, team_id, not is_home)
                
                total_xg_for += team_xg
                total_xg_against += opponent_xg
                total_goals_for += team_goals
                total_goals_against += opponent_goals
                
                xg_data.append({
                    'date': match['fixture']['date'],
                    'opponent': away_team['name'] if is_home else home_team['name'],
                    'team_goals': team_goals,
                    'team_xg': round(team_xg, 2),
                    'opponent_goals': opponent_goals,
                    'opponent_xg': round(opponent_xg, 2),
                    'xg_diff': round(team_xg - opponent_xg, 2)
                })
            
            # Performans analizi
            avg_xg_for = total_xg_for / len(fixtures) if fixtures else 0
            avg_xg_against = total_xg_against / len(fixtures) if fixtures else 0
            avg_goals_for = total_goals_for / len(fixtures) if fixtures else 0
            avg_goals_against = total_goals_against / len(fixtures) if fixtures else 0
            
            # Şans faktörü (gerçek gol vs beklenen gol)
            luck_factor = (total_goals_for - total_xg_for) / max(total_xg_for, 1)
            
            return {
                'total_matches': len(fixtures),
                'avg_xg_for': round(avg_xg_for, 2),
                'avg_xg_against': round(avg_xg_against, 2),
                'avg_goals_for': round(avg_goals_for, 2),
                'avg_goals_against': round(avg_goals_against, 2),
                'xg_difference': round(avg_xg_for - avg_xg_against, 2),
                'luck_factor': round(luck_factor * 100, 1),  # Yüzde olarak
                'matches': xg_data[:5]  # Son 5 maç detayı
            }
            
    except Exception as e:
        print(f"xG veri hatası: {e}")
    
    return None


def estimate_xg_from_stats(stats: list, team_id: int, is_home: bool) -> float:
    """
    İstatistiklerden xG tahmini yap
    """
    
    if not stats:
        return 1.2  # Ortalama değer
    
    team_stats = None
    for stat in stats:
        if stat['team']['id'] == team_id:
            team_stats = stat['statistics']
            break
    
    if not team_stats:
        return 1.2
    
    xg = 0.5  # Base xG
    
    for stat in team_stats:
        stat_type = stat.get('type', '')
        value = stat.get('value')
        
        # Şutlar
        if stat_type == 'Shots on Goal' and value:
            try:
                shots_on_target = int(value)
                xg += shots_on_target * 0.25  # Her isabetli şut ~0.25 xG
            except:
                pass
        
        # Toplam şutlar
        elif stat_type == 'Total Shots' and value:
            try:
                total_shots = int(value)
                xg += total_shots * 0.08  # Her şut ~0.08 xG
            except:
                pass
        
        # Korner
        elif stat_type == 'Corner Kicks' and value:
            try:
                corners = int(value)
                xg += corners * 0.03  # Her korner ~0.03 xG
            except:
                pass
        
        # Top sahipliği
        elif stat_type == 'Ball Possession' and value:
            try:
                possession = int(value.replace('%', ''))
                if possession > 50:
                    xg += (possession - 50) * 0.01  # Fazla top sahipliği bonus
            except:
                pass
    
    return min(xg, 4.0)  # Maksimum 4.0 xG


def compare_xg_teams(team1_id: int, team2_id: int, team1_name: str, team2_name: str) -> Dict:
    """
    İki takımın xG performansını karşılaştır
    """
    
    team1_xg = get_xg_data(team1_id)
    team2_xg = get_xg_data(team2_id)
    
    if not team1_xg or not team2_xg:
        return None
    
    # Avantaj hesapla
    xg_diff = team1_xg['xg_difference'] - team2_xg['xg_difference']
    
    if xg_diff > 0.5:
        xg_advantage = team1_name
        advantage_value = round(xg_diff * 10, 1)  # Yüzde olarak
    elif xg_diff < -0.5:
        xg_advantage = team2_name
        advantage_value = round(abs(xg_diff) * 10, 1)
    else:
        xg_advantage = "Dengeli"
        advantage_value = 0
    
    # Şans faktörü karşılaştırması
    luck_comparison = ""
    if team1_xg['luck_factor'] > 10:
        luck_comparison += f"{team1_name} şanslı oynuyor (+{team1_xg['luck_factor']}%). "
    elif team1_xg['luck_factor'] < -10:
        luck_comparison += f"{team1_name} şanssız ({team1_xg['luck_factor']}%). "
    
    if team2_xg['luck_factor'] > 10:
        luck_comparison += f"{team2_name} şanslı oynuyor (+{team2_xg['luck_factor']}%)."
    elif team2_xg['luck_factor'] < -10:
        luck_comparison += f"{team2_name} şanssız ({team2_xg['luck_factor']}%)."
    
    if not luck_comparison:
        luck_comparison = "Her iki takım da beklenen performansında."
    
    return {
        'team1': {
            'name': team1_name,
            'avg_xg_for': team1_xg['avg_xg_for'],
            'avg_xg_against': team1_xg['avg_xg_against'],
            'xg_difference': team1_xg['xg_difference'],
            'luck_factor': team1_xg['luck_factor']
        },
        'team2': {
            'name': team2_name,
            'avg_xg_for': team2_xg['avg_xg_for'],
            'avg_xg_against': team2_xg['avg_xg_against'],
            'xg_difference': team2_xg['xg_difference'],
            'luck_factor': team2_xg['luck_factor']
        },
        'xg_advantage': xg_advantage,
        'advantage_value': advantage_value,
        'luck_comparison': luck_comparison,
        'prediction_impact': round(advantage_value / 2, 1)  # xG avantajının tahmine etkisi
    }


if __name__ == "__main__":
    print("=" * 60)
    print("xG ANALİZ TESTİ")
    print("=" * 60)
    
    # Galatasaray test (team_id: 548)
    print("\n📊 Galatasaray xG Analizi:")
    gs_xg = get_xg_data(548, 5)
    if gs_xg:
        print(f"  Ort. xG For: {gs_xg['avg_xg_for']}")
        print(f"  Ort. xG Against: {gs_xg['avg_xg_against']}")
        print(f"  xG Fark: {gs_xg['xg_difference']}")
        print(f"  Şans Faktörü: {gs_xg['luck_factor']}%")
    
    # Beşiktaş test (team_id: 549)
    print("\n📊 Beşiktaş xG Analizi:")
    bjk_xg = get_xg_data(549, 5)
    if bjk_xg:
        print(f"  Ort. xG For: {bjk_xg['avg_xg_for']}")
        print(f"  Ort. xG Against: {bjk_xg['avg_xg_against']}")
        print(f"  xG Fark: {bjk_xg['xg_difference']}")
        print(f"  Şans Faktörü: {bjk_xg['luck_factor']}%")
    
    # Karşılaştırma
    print("\n🔍 Galatasaray vs Beşiktaş xG Karşılaştırması:")
    comparison = compare_xg_teams(548, 549, "Galatasaray", "Beşiktaş")
    if comparison:
        print(f"  xG Avantajı: {comparison['xg_advantage']}")
        print(f"  Avantaj Değeri: {comparison['advantage_value']}%")
        print(f"  Şans Durumu: {comparison['luck_comparison']}")
        print(f"  Tahmin Etkisi: {comparison['prediction_impact']}%")
