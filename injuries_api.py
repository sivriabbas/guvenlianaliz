#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sakatlık ve Cezalı Oyuncu API Modülü
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime

API_KEY = '6336fb21e17dea87880d3b133132a13f'
BASE_URL = 'https://v3.football.api-sports.io'

def get_team_injuries(team_id: int) -> Optional[Dict]:
    """Takımın sakatlık ve cezalı oyuncularını çek"""
    headers = {'x-apisports-key': API_KEY}
    url = f"{BASE_URL}/injuries?team={team_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if not data.get('response'):
            return None
        
        injuries = data['response']
        
        # Aktif sakatlıkları filtrele
        active_injuries = []
        for injury in injuries:
            player_name = injury['player']['name']
            injury_type = injury['player']['type']
            reason = injury['player']['reason']
            
            active_injuries.append({
                'player': player_name,
                'type': injury_type,
                'reason': reason
            })
        
        # Önem derecesi hesapla
        total_injuries = len(active_injuries)
        key_players = sum(1 for i in active_injuries if 'key' in str(i).lower())
        
        # Etki seviyesi
        if total_injuries == 0:
            impact = 'Yok'
            impact_score = 0
        elif total_injuries <= 2:
            impact = 'Düşük'
            impact_score = -3
        elif total_injuries <= 4:
            impact = 'Orta'
            impact_score = -7
        else:
            impact = 'Yüksek'
            impact_score = -12
        
        return {
            'total_injuries': total_injuries,
            'injuries': active_injuries[:5],  # İlk 5'i göster
            'key_players_missing': key_players,
            'impact': impact,
            'impact_score': impact_score
        }
    
    except Exception as e:
        print(f"Sakatlık verisi çekme hatası: {e}")
        return {
            'total_injuries': 0,
            'injuries': [],
            'key_players_missing': 0,
            'impact': 'Bilinmiyor',
            'impact_score': 0
        }


def calculate_injury_impact(team1_injuries: Dict, team2_injuries: Dict) -> Dict:
    """İki takımın sakatlık durumunu karşılaştır"""
    
    team1_score = team1_injuries.get('impact_score', 0)
    team2_score = team2_injuries.get('impact_score', 0)
    
    # Sakatlık avantajı
    if abs(team1_score - team2_score) > 5:
        if team1_score < team2_score:
            advantage = 'team2'  # team2 daha az sakatlık var
            advantage_percentage = abs(team1_score - team2_score) / 2
        else:
            advantage = 'team1'
            advantage_percentage = abs(team2_score - team1_score) / 2
    else:
        advantage = 'balanced'
        advantage_percentage = 0
    
    return {
        'team1_impact': team1_injuries.get('impact', 'Bilinmiyor'),
        'team2_impact': team2_injuries.get('impact', 'Bilinmiyor'),
        'advantage': advantage,
        'advantage_percentage': round(advantage_percentage, 1),
        'team1_missing': team1_injuries.get('total_injuries', 0),
        'team2_missing': team2_injuries.get('total_injuries', 0)
    }


if __name__ == "__main__":
    print("=" * 60)
    print("SAKATLIK VERİSİ TESTİ")
    print("=" * 60)
    
    # Test: Galatasaray
    team_id = 645
    injuries = get_team_injuries(team_id)
    if injuries:
        print(f"\n✅ Galatasaray Sakatlıklar:")
        print(f"  Toplam: {injuries['total_injuries']}")
        print(f"  Etki: {injuries['impact']} ({injuries['impact_score']}%)")
        if injuries['injuries']:
            for inj in injuries['injuries'][:3]:
                print(f"  - {inj['player']}: {inj['reason']}")
