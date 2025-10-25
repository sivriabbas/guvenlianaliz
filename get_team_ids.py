#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import yaml

config = {
    'api_football': {
        'base_url': 'https://v3.football.api-sports.io',
        'api_key': '6336fb21e17dea87880d3b133132a13f'
    }
}

def search_team(team_name):
    """Takım adıyla API'den takım ID'si bul"""
    headers = {'x-apisports-key': config['api_football']['api_key']}
    url = f"{config['api_football']['base_url']}/teams?search={team_name}"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        print(f"\n🔍 '{team_name}' Arama Sonucu:")
        print("=" * 50)
        
        if data.get('response'):
            for team in data['response']:
                team_info = team['team']
                venue_info = team.get('venue', {})
                print(f"ID: {team_info['id']}")
                print(f"Ad: {team_info['name']}")
                print(f"Ülke: {team_info['country']}")
                print(f"Kuruluş: {team_info.get('founded', 'Bilinmiyor')}")
                print(f"Stadyum: {venue_info.get('name', 'Bilinmiyor')}")
                print(f"Logo: {team_info['logo']}")
                print("-" * 30)
        else:
            print("❌ Takım bulunamadı!")
            
    except Exception as e:
        print(f"❌ Hata: {e}")

def get_turkish_league_standings():
    """Türkiye Süper Lig puan durumunu çek"""
    headers = {'x-apisports-key': config['api_football']['api_key']}
    # Türkiye Süper Lig ID: 203, 2025 sezonu (en güncel)
    url = f"{config['api_football']['base_url']}/standings?league=203&season=2025"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        print(f"\n🏆 Türkiye Süper Lig Puan Durumu (2025 - GÜNCEL):")
        print("=" * 70)
        
        if data.get('response') and len(data['response']) > 0:
            standings = data['response'][0]['league']['standings'][0]
            
            print(f"{'Sıra':<4} {'Takım':<20} {'O':<3} {'G':<3} {'B':<3} {'M':<3} {'A':<3} {'Y':<3} {'Avg':<4} {'Puan':<5}")
            print("-" * 70)
            
            for team in standings:
                rank = team['rank']
                team_name = team['team']['name']
                team_id = team['team']['id']
                played = team['all']['played']
                wins = team['all']['win']
                draws = team['all']['draw']
                losses = team['all']['lose']
                goals_for = team['all']['goals']['for']
                goals_against = team['all']['goals']['against']
                goal_diff = goals_for - goals_against
                points = team['points']
                
                avg = f"{goals_for/played:.1f}" if played > 0 else "0.0"
                
                print(f"{rank:<4} {team_name:<20} {played:<3} {wins:<3} {draws:<3} {losses:<3} {goals_for:<3} {goals_against:<3} {avg:<4} {points:<5}")
                
                # Galatasaray ve Göztepe için özel bilgi
                if 'galatasaray' in team_name.lower():
                    print(f"    🔥 Galatasaray ID: {team_id}")
                elif 'göztepe' in team_name.lower() or 'goztepe' in team_name.lower():
                    print(f"    ⚽ Göztepe ID: {team_id}")
                    
        else:
            print("❌ Puan durumu bulunamadı!")
            
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    # Takım ara
    search_team("Galatasaray")
    search_team("Göztepe")
    
    # Süper Lig puan durumunu göster
    get_turkish_league_standings()