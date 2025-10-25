#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerçek Zamanlı API Veri Çekme Modülü
Tüm takım verileri API'den gerçek zamanlı çekilir
"""

import requests
import json
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from team_value_api import get_team_market_value

# API Configuration
API_KEY = '6336fb21e17dea87880d3b133132a13f'
BASE_URL = 'https://v3.football.api-sports.io'

def get_team_by_name(team_name: str) -> Optional[Dict]:
    """Takım adıyla API'den takım bilgilerini çek"""
    headers = {'x-apisports-key': API_KEY}
    
    # Türkçe karakter düzeltmeleri
    search_name = team_name.replace('ö', 'o').replace('Ö', 'O').replace('ş', 's').replace('Ş', 'S')
    search_name = search_name.replace('ü', 'u').replace('Ü', 'U').replace('ı', 'i').replace('İ', 'I')
    search_name = search_name.replace('ç', 'c').replace('Ç', 'C').replace('ğ', 'g').replace('Ğ', 'G')
    
    url = f"{BASE_URL}/teams?search={search_name}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('response') and len(data['response']) > 0:
            # Takım adında Türkiye varsa veya en yakın eşleşmeyi al
            for team_data in data['response']:
                team_country = team_data['team']['country']
                # Türk takımları için Türkiye kontrolü
                if 'Turkey' in team_country or 'turkey' in team_country.lower():
                    return {
                        'id': team_data['team']['id'],
                        'name': team_data['team']['name'],
                        'country': team_data['team']['country'],
                        'founded': team_data['team'].get('founded'),
                        'logo': team_data['team']['logo'],
                        'venue': team_data['venue']['name'] if team_data.get('venue') else None
                    }
            
            # Türk takımı değilse ilk sonucu al
            team_data = data['response'][0]
            return {
                'id': team_data['team']['id'],
                'name': team_data['team']['name'],
                'country': team_data['team']['country'],
                'founded': team_data['team'].get('founded'),
                'logo': team_data['team']['logo'],
                'venue': team_data['venue']['name'] if team_data.get('venue') else None
            }
    except Exception as e:
        print(f"Takım arama hatası ({team_name}): {e}")
    
    return None

def get_team_current_season_stats(team_id: int) -> Optional[Dict]:
    """Takımın mevcut sezon istatistiklerini çek (tüm ligler) - 2025 SEZON GÜNCEL VERİ"""
    headers = {'x-apisports-key': API_KEY}
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Sezon belirleme: Temmuz-Aralık arası current_year, Ocak-Haziran arası current_year-1
    if current_month >= 7:  # Temmuz ve sonrası yeni sezon
        season = current_year
    else:  # Ocak-Haziran önceki sezonun devamı
        season = current_year - 1
    
    print(f"🔍 Takım ID {team_id} için {season} sezonu verileri çekiliyor...")
    
    try:
        # Son maçlardan ligini tespit et (2025 sezonu için)
        fixtures_url = f"{BASE_URL}/fixtures?team={team_id}&season={season}&last=20"
        fixtures_response = requests.get(fixtures_url, headers=headers, timeout=10)
        fixtures_data = fixtures_response.json()
        
        if not fixtures_data.get('response'):
            print(f"⚠️ {team_id} için {season} sezonunda maç bulunamadı!")
            return None
        
        # En son oynanan lig maçından lig ID'sini al
        league_id = None
        league_name = None
        
        # Kupa isimlerini tanımla (bunları atla)
        cup_keywords = ['Cup', 'Kupa', 'Champions', 'Europa', 'Conference', 'Trophy', 'Super Cup']
        
        for fixture in fixtures_data['response']:
            fixture_league_name = fixture['league']['name']
            
            # Kupa maçlarını atla
            is_cup = any(keyword.lower() in fixture_league_name.lower() for keyword in cup_keywords)
            
            # Sadece lig maçlarını al
            if not is_cup and fixture['fixture']['status']['short'] == 'FT':
                league_id = fixture['league']['id']
                league_name = fixture_league_name
                print(f"✅ Lig bulundu: {league_name} (ID: {league_id})")
                break
        
        if not league_id:
            # Tamamlanmış maç yoksa, planlanan lig maçlardan al
            for fixture in fixtures_data['response']:
                fixture_league_name = fixture['league']['name']
                is_cup = any(keyword.lower() in fixture_league_name.lower() for keyword in cup_keywords)
                
                if not is_cup:
                    league_id = fixture['league']['id']
                    league_name = fixture_league_name
                    print(f"📅 Planlanan maçlardan lig bulundu: {league_name}")
                    break
        
        if not league_id:
            print(f"❌ {team_id} için lig bulunamadı!")
            return None
        
        # Lig puan durumunu çek (GÜNCEL SEZON)
        standings_url = f"{BASE_URL}/standings?league={league_id}&season={season}"
        print(f"🔄 Puan durumu çekiliyor: {standings_url}")
        standings_response = requests.get(standings_url, headers=headers, timeout=10)
        standings_data = standings_response.json()
        
        if standings_data.get('response') and len(standings_data['response']) > 0:
            standings = standings_data['response'][0]['league']['standings'][0]
            
            # Bu takımı bul
            for team_standing in standings:
                if team_standing['team']['id'] == team_id:
                    # İstatistikleri hesapla
                    all_stats = team_standing['all']
                    home_stats = team_standing['home']
                    away_stats = team_standing['away']
                    
                    team_info = {
                        'league_id': league_id,
                        'league_name': standings_data['response'][0]['league']['name'],
                        'league_country': standings_data['response'][0]['league']['country'],
                        'season': season,
                        'position': team_standing['rank'],
                        'points': team_standing['points'],
                        'played': all_stats['played'],
                        'wins': all_stats['win'],
                        'draws': all_stats['draw'],
                        'losses': all_stats['lose'],
                        'goals_for': all_stats['goals']['for'],
                        'goals_against': all_stats['goals']['against'],
                        'goal_diff': team_standing['goalsDiff'],
                        'form': team_standing['form'],
                        # Ev sahibi istatistikleri
                        'home_played': home_stats['played'],
                        'home_wins': home_stats['win'],
                        'home_draws': home_stats['draw'],
                        'home_losses': home_stats['lose'],
                        'home_goals_for': home_stats['goals']['for'],
                        'home_goals_against': home_stats['goals']['against'],
                        # Deplasman istatistikleri
                        'away_played': away_stats['played'],
                        'away_wins': away_stats['win'],
                        'away_draws': away_stats['draw'],
                        'away_losses': away_stats['lose'],
                        'away_goals_for': away_stats['goals']['for'],
                        'away_goals_against': away_stats['goals']['against'],
                        # Hesaplanmış metrikler
                        'ppg': round(team_standing['points'] / max(all_stats['played'], 1), 2),
                        'home_win_rate': round(home_stats['win'] / max(home_stats['played'], 1) * 100, 1),
                        'away_win_rate': round(away_stats['win'] / max(away_stats['played'], 1) * 100, 1),
                        'goals_per_game': round(all_stats['goals']['for'] / max(all_stats['played'], 1), 2),
                        'goals_conceded_per_game': round(all_stats['goals']['against'] / max(all_stats['played'], 1), 2),
                        'clean_sheets': 0,  # API'den gelmezse
                        'failed_to_score': 0  # API'den gelmezse
                    }
                    
                    print(f"✅ {team_standing['team']['name']}: {team_standing['rank']}. sıra, {team_standing['points']} puan ({season} sezonu)")
                    return team_info
            
            print(f"⚠️ Takım ID {team_id} puan durumunda bulunamadı!")
        else:
            print(f"❌ Puan durumu verisi yok: {standings_data.get('message', 'Bilinmeyen hata')}")
        
    except Exception as e:
        print(f"❌ İstatistik çekme hatası (team_id: {team_id}): {e}")
        import traceback
        traceback.print_exc()
    
    return None

def get_team_value_estimate(team_name: str, league_name: str = None) -> int:
    """Takım değerini tahmin et (lig ve performansa göre)"""
    # Elite takımlar
    elite_teams = {
        'manchester city': 950, 'real madrid': 1100, 'barcelona': 920,
        'psg': 890, 'bayern munich': 980, 'liverpool': 850,
        'manchester united': 690, 'arsenal': 750, 'chelsea': 780,
        'juventus': 650, 'inter': 600, 'ac milan': 580,
        'atletico madrid': 520, 'tottenham': 680, 'borussia dortmund': 520
    }
    
    # Türk takımları (güncel piyasa değerleri)
    turkish_teams = {
        'galatasaray': 285, 'fenerbahçe': 270, 'fenerbahce': 270,
        'beşiktaş': 195, 'besiktas': 195,
        'trabzonspor': 145, 'başakşehir': 55, 'basaksehir': 55,
        'göztepe': 30, 'goztepe': 30,
        'samsunspor': 45, 'konyaspor': 40, 'antalyaspor': 35,
        'kasımpaşa': 35, 'kasimpasa': 35,
        'alanyaspor': 30, 'kayserispor': 25, 'rizespor': 20,
        'eyüpspor': 25, 'eyupspor': 25,
        'kocaelispor': 20, 'gençlerbirliği': 25, 'genclerbirligi': 25
    }
    
    team_lower = team_name.lower()
    
    # Önce özel listelerden kontrol et
    if team_lower in elite_teams:
        return elite_teams[team_lower]
    if team_lower in turkish_teams:
        return turkish_teams[team_lower]
    
    # Lige göre tahmin
    if league_name:
        league_lower = league_name.lower()
        if 'premier league' in league_lower:
            return 200
        elif 'la liga' in league_lower or 'liga' in league_lower:
            return 180
        elif 'bundesliga' in league_lower:
            return 170
        elif 'serie a' in league_lower:
            return 160
        elif 'ligue 1' in league_lower:
            return 150
        elif 'süper lig' in league_lower or 'super lig' in league_lower:
            return 35
        elif 'championship' in league_lower:
            return 80
        elif 'eredivisie' in league_lower:
            return 60
    
    # Varsayılan
    return 30

def get_h2h_data(team1_id: int, team2_id: int) -> Optional[Dict]:
    """İki takım arasındaki son karşılaşmaları çek"""
    headers = {'x-apisports-key': API_KEY}
    url = f"{BASE_URL}/fixtures/headtohead?h2h={team1_id}-{team2_id}&last=10"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if not data.get('response'):
            return None
        
        fixtures = data['response']
        if not fixtures:
            return None
        
        team1_wins = 0
        team2_wins = 0
        draws = 0
        total_matches = len(fixtures)
        team1_goals_total = 0
        team2_goals_total = 0
        last_5_results = []
        
        for fixture in fixtures[:10]:  # Son 10 maç
            home_team_id = fixture['teams']['home']['id']
            away_team_id = fixture['teams']['away']['id']
            home_goals = fixture['goals']['home']
            away_goals = fixture['goals']['away']
            
            # Hangi takım ev sahibi/deplasman
            if home_team_id == team1_id:
                team1_goals_total += home_goals
                team2_goals_total += away_goals
                if home_goals > away_goals:
                    team1_wins += 1
                    last_5_results.append('W1')
                elif home_goals < away_goals:
                    team2_wins += 1
                    last_5_results.append('W2')
                else:
                    draws += 1
                    last_5_results.append('D')
            else:
                team1_goals_total += away_goals
                team2_goals_total += home_goals
                if away_goals > home_goals:
                    team1_wins += 1
                    last_5_results.append('W1')
                elif away_goals < home_goals:
                    team2_wins += 1
                    last_5_results.append('W2')
                else:
                    draws += 1
                    last_5_results.append('D')
        
        # Son maç bilgisi
        last_fixture = fixtures[0]
        last_match_date = last_fixture['fixture']['date']
        last_match_score = f"{last_fixture['goals']['home']}-{last_fixture['goals']['away']}"
        
        return {
            'total_matches': total_matches,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'team1_goals_avg': round(team1_goals_total / total_matches, 2) if total_matches > 0 else 0,
            'team2_goals_avg': round(team2_goals_total / total_matches, 2) if total_matches > 0 else 0,
            'team1_win_rate': round(team1_wins / total_matches * 100, 1) if total_matches > 0 else 0,
            'team2_win_rate': round(team2_wins / total_matches * 100, 1) if total_matches > 0 else 0,
            'draw_rate': round(draws / total_matches * 100, 1) if total_matches > 0 else 0,
            'last_match_date': last_match_date,
            'last_match_score': last_match_score,
            'last_5_results': last_5_results[:5],
            'dominance': 'team1' if team1_wins > team2_wins else 'team2' if team2_wins > team1_wins else 'balanced'
        }
    
    except Exception as e:
        print(f"H2H veri çekme hatası: {e}")
        return None


def get_last_5_matches_detailed(team_id: int) -> Optional[List[Dict]]:
    """Takımın son 5 maçını detaylı şekilde çek"""
    headers = {'x-apisports-key': API_KEY}
    url = f"{BASE_URL}/fixtures?team={team_id}&last=5"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if not data.get('response'):
            return None
        
        matches = []
        for fixture in data['response']:
            home_team = fixture['teams']['home']
            away_team = fixture['teams']['away']
            goals_home = fixture['goals']['home']
            goals_away = fixture['goals']['away']
            
            is_home = home_team['id'] == team_id
            opponent = away_team if is_home else home_team
            team_goals = goals_home if is_home else goals_away
            opponent_goals = goals_away if is_home else goals_home
            
            if team_goals > opponent_goals:
                result = 'W'
            elif team_goals < opponent_goals:
                result = 'L'
            else:
                result = 'D'
            
            matches.append({
                'date': fixture['fixture']['date'],
                'opponent': opponent['name'],
                'opponent_id': opponent['id'],
                'is_home': is_home,
                'team_goals': team_goals,
                'opponent_goals': opponent_goals,
                'result': result,
                'score': f"{team_goals}-{opponent_goals}",
                'league': fixture['league']['name']
            })
        
        return matches
    
    except Exception as e:
        print(f"Son 5 maç detay hatası: {e}")
        return None


def calculate_momentum_score(matches: List[Dict]) -> Dict:
    """Son maçlara göre momentum skoru hesapla"""
    if not matches:
        return {'score': 50.0, 'trend': 'Stable', 'recent_form': 'N/A'}
    
    # Son maçlara daha fazla ağırlık ver
    weights = [5, 4, 3, 2, 1]  # En son maç en önemli
    momentum = 0
    
    for i, match in enumerate(matches[:5]):
        weight = weights[i] if i < len(weights) else 1
        
        if match['result'] == 'W':
            momentum += 100 * weight
        elif match['result'] == 'D':
            momentum += 50 * weight
        else:
            momentum += 0 * weight
    
    # Normalize (0-100 arası)
    max_momentum = sum(weights) * 100
    momentum_score = (momentum / max_momentum) * 100
    
    # Trend belirleme
    if momentum_score >= 70:
        trend = 'Very Positive'
    elif momentum_score >= 55:
        trend = 'Positive'
    elif momentum_score >= 45:
        trend = 'Stable'
    elif momentum_score >= 30:
        trend = 'Negative'
    else:
        trend = 'Very Negative'
    
    # Son form string
    form_string = ''.join([m['result'] for m in matches[:5]])
    
    return {
        'score': round(momentum_score, 1),
        'trend': trend,
        'recent_form': form_string
    }


def get_complete_team_data(team_name: str) -> Optional[Dict]:
    """Takımın tüm verilerini API'den çek ve birleştir"""
    print(f"🔍 '{team_name}' için API'den veri çekiliyor...")
    
    # 1. Takım bilgilerini al
    team_info = get_team_by_name(team_name)
    if not team_info:
        print(f"❌ Takım bulunamadı: {team_name}")
        return None
    
    print(f"✅ Takım bulundu: {team_info['name']} (ID: {team_info['id']})")
    
    # 2. Sezon istatistiklerini al
    season_stats = get_team_current_season_stats(team_info['id'])
    if not season_stats:
        print(f"⚠️ İstatistik bulunamadı, varsayılan değerler kullanılacak")
        return {
            'id': team_info['id'],
            'name': team_info['name'],
            'country': team_info['country'],
            'logo': team_info['logo'],
            'value': get_team_value_estimate(team_name),
            'elo': 1500,  # Varsayılan ELO
            'league': 'Unknown',
            'league_pos': 10,
            'points': 0,
            'played': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'form': 50.0,
            'goals_for': 0,
            'goals_against': 0,
            'home_win_rate': 50.0,
            'away_win_rate': 40.0,
            'ppg': 0.0,
            'goals_per_game': 0.0,
            'goals_conceded_per_game': 0.0
        }
    
    print(f"✅ İstatistikler bulundu: {season_stats['league_name']}, {season_stats['position']}. sıra")
    
    # 3. Son 5 maç detayları
    last_5_matches = get_last_5_matches_detailed(team_info['id'])
    momentum = calculate_momentum_score(last_5_matches) if last_5_matches else {'score': 50.0, 'trend': 'Stable', 'recent_form': 'N/A'}
    
    # 4. ELO puanını sistemden çek
    try:
        with open('elo_ratings.json', 'r') as f:
            elo_data = json.load(f)
            elo_rating = elo_data.get(str(team_info['id']), {}).get('rating', 1500)
    except:
        elo_rating = 1500
    
    # Gelişmiş ELO hesaplama (Ev/Deplasman ayrımı)
    # Ev performansına göre ELO ayarlama
    home_win_rate = season_stats.get('home_win_rate', 50.0)
    away_win_rate = season_stats.get('away_win_rate', 40.0)
    
    # Ev ELO = Base ELO + (ev performansı - 50) * 2
    home_elo = elo_rating + ((home_win_rate - 50) * 2)
    # Deplasman ELO = Base ELO + (deplasman performansı - 40) * 2
    away_elo = elo_rating + ((away_win_rate - 40) * 2)
    
    # Son 10 maç performansına göre form ELO
    if last_5_matches and len(last_5_matches) >= 3:
        recent_wins = sum(1 for m in last_5_matches[:10] if m['result'] == 'W')
        recent_total = min(len(last_5_matches), 10)
        recent_win_rate = (recent_wins / recent_total) * 100
        form_elo = elo_rating + ((recent_win_rate - 50) * 1.5)
    else:
        form_elo = elo_rating
    
    # 5. Takım değerini al (Gerçek piyasa değeri)
    team_value = get_team_market_value(team_name, season_stats['league_name'])
    
    # 6. Form hesapla (son 5 maç)
    form_string = season_stats.get('form', 'DDDDD')
    if form_string:
        recent_form = form_string[-5:] if len(form_string) >= 5 else form_string
        wins = recent_form.count('W')
        draws = recent_form.count('D')
        form_percentage = (wins * 3 + draws * 1) / (len(recent_form) * 3) * 100
    else:
        # Genel performanstan hesapla
        if season_stats['played'] > 0:
            form_percentage = (season_stats['wins'] * 3 + season_stats['draws']) / (season_stats['played'] * 3) * 100
        else:
            form_percentage = 50.0
    
    return {
        'id': team_info['id'],
        'name': team_info['name'],
        'country': team_info['country'],
        'logo': team_info['logo'],
        'value': team_value,
        'elo': elo_rating,
        'home_elo': round(home_elo, 0),
        'away_elo': round(away_elo, 0),
        'form_elo': round(form_elo, 0),
        'league': season_stats['league_name'],
        'league_country': season_stats['league_country'],
        'league_pos': season_stats['position'],
        'points': season_stats['points'],
        'played': season_stats['played'],
        'wins': season_stats['wins'],
        'draws': season_stats['draws'],
        'losses': season_stats['losses'],
        'goals_for': season_stats['goals_for'],
        'goals_against': season_stats['goals_against'],
        'goal_diff': season_stats['goal_diff'],
        'form': round(form_percentage, 1),
        'form_string': form_string[-10:] if form_string else 'N/A',
        'season': season_stats['season'],
        # Ev/Deplasman verileri
        'home_played': season_stats.get('home_played', 0),
        'home_wins': season_stats.get('home_wins', 0),
        'home_draws': season_stats.get('home_draws', 0),
        'home_losses': season_stats.get('home_losses', 0),
        'home_goals_for': season_stats.get('home_goals_for', 0),
        'home_goals_against': season_stats.get('home_goals_against', 0),
        'away_played': season_stats.get('away_played', 0),
        'away_wins': season_stats.get('away_wins', 0),
        'away_draws': season_stats.get('away_draws', 0),
        'away_losses': season_stats.get('away_losses', 0),
        'away_goals_for': season_stats.get('away_goals_for', 0),
        'away_goals_against': season_stats.get('away_goals_against', 0),
        # Hesaplanmış metrikler
        'ppg': season_stats.get('ppg', 0.0),
        'home_win_rate': season_stats.get('home_win_rate', 50.0),
        'away_win_rate': season_stats.get('away_win_rate', 40.0),
        'goals_per_game': season_stats.get('goals_per_game', 0.0),
        'goals_conceded_per_game': season_stats.get('goals_conceded_per_game', 0.0),
        'attack_strength': round((season_stats.get('goals_per_game', 1.0) / 1.5) * 100, 1),
        'defense_strength': round(100 - (season_stats.get('goals_conceded_per_game', 1.0) / 1.5) * 100, 1),
        # Momentum ve son maçlar
        'momentum_score': momentum['score'],
        'momentum_trend': momentum['trend'],
        'last_5_matches': last_5_matches if last_5_matches else [],
        'recent_form_detailed': momentum['recent_form']
    }

if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("GERÇEK ZAMANLI VERİ ÇEKME TESTİ")
    print("=" * 60)
    
    test_teams = ["Galatasaray", "Göztepe", "Manchester City", "Barcelona"]
    
    for team_name in test_teams:
        print(f"\n{'='*60}")
        data = get_complete_team_data(team_name)
        if data:
            print(f"\n📊 {data['name']} - TAM VERİ:")
            print(f"  🏆 Lig: {data['league']} ({data['league_country']})")
            print(f"  📍 Sıra: {data['league_pos']}. sıra")
            print(f"  📊 Puan: {data['points']} puan ({data['played']} maç)")
            print(f"  🎯 Performans: {data['wins']}G-{data['draws']}B-{data['losses']}M")
            print(f"  ⚽ Goller: {data['goals_for']}-{data['goals_against']}")
            print(f"  📈 Form: %{data['form']} ({data['form_string']})")
            print(f"  💰 Değer: €{data['value']}M")
            print(f"  🎖️ ELO: {data['elo']}")
