# -*- coding: utf-8 -*-
# analysis_logic.py

import math
from typing import Dict, Any, List, Optional
from datetime import datetime
import streamlit as st
import api_utils
import elo_utils

def process_player_stats(player_data: Optional[List[Dict]]) -> Optional[str]:
    """Oyuncu istatistik verisini işleyip okunabilir bir metin döner."""
    if not player_data or not player_data[0].get('statistics'):
        return None
    
    try:
        # Genellikle oyuncunun ana lig istatistikleri ilk sırada gelir.
        stats = player_data[0]['statistics'][0]
        games = stats['games'].get('appearences', 0)
        goals = stats['goals'].get('total', 0)
        assists = stats['goals'].get('assists', 0)
        
        if not games:
            return None
            
        return f" (Maç: {games}, Gol: {goals}, Asist: {assists or 0})"
    except (KeyError, IndexError):
        return None

def process_h2h_data(h2h_matches: List[Dict], team_a_id: int) -> Optional[Dict]:
    """H2H maç verisini işler ve özet istatistikler çıkarır."""
    if not h2h_matches:
        return None
    
    wins_a, draws, wins_b = 0, 0, 0
    goals_a, goals_b = 0, 0
    
    recent_matches_display = []

    for match in h2h_matches:
        try:
            home_id = match['teams']['home']['id']
            away_id = match['teams']['away']['id']
            score_home = match['score']['fulltime']['home']
            score_away = match['score']['fulltime']['away']

            if score_home is None or score_away is None:
                continue

            if match['teams']['home']['winner'] is True:
                if home_id == team_a_id: wins_a += 1
                else: wins_b += 1
            elif match['teams']['away']['winner'] is True:
                if away_id == team_a_id: wins_a += 1
                else: wins_b += 1
            else:
                draws += 1
            
            if home_id == team_a_id:
                goals_a += score_home
                goals_b += score_away
            else:
                goals_a += score_away
                goals_b += score_home
            
            match_date = datetime.fromtimestamp(match['fixture']['timestamp']).strftime('%d.%m.%Y')
            recent_matches_display.append({
                "Tarih": match_date,
                "Ev Sahibi": match['teams']['home']['name'],
                "Skor": f"{score_home} - {score_away}",
                "Deplasman": match['teams']['away']['name']
            })
        except (KeyError, TypeError):
            continue
            
    total_matches = len(h2h_matches)
    return {
        "summary": {"total_matches": total_matches, "wins_a": wins_a, "draws": draws, "wins_b": wins_b},
        "goals": {"goals_a": goals_a, "goals_b": goals_b, "avg_goals_a": goals_a / total_matches if total_matches > 0 else 0, "avg_goals_b": goals_b / total_matches if total_matches > 0 else 0},
        "recent_matches": recent_matches_display
    }

def process_referee_data(referee_data: Optional[Dict]) -> Optional[Dict]:
    """API'den gelen hakem verisini işler."""
    if not referee_data or not referee_data.get('fixtures'):
        return None
    try:
        name = referee_data['name']
        total_games = len(referee_data['fixtures'])
        total_yellow, total_red = 0, 0
        
        for fixture in referee_data['fixtures']:
            cards = fixture.get('cards', {})
            total_yellow += cards.get('yellow', 0)
            total_red += cards.get('red', 0)
            
        return { "name": name, "total_games": total_games, "yellow_per_game": total_yellow / total_games if total_games > 0 else 0, "red_per_game": total_red / total_games if total_games > 0 else 0, }
    except (KeyError, TypeError):
        return None

@st.cache_data(ttl=86400)
def get_league_goal_baselines(api_key: str, base_url: str, league_info: Dict, default_avg: float) -> Dict[str, float]:
    params = {
        'league': league_info['league_id'],
        'season': league_info['season'],
        'status': 'FT',
        'last': 250,
    }
    fixtures, _ = api_utils.make_api_request(api_key, base_url, "fixtures", params)
    totals: List[int] = []
    home_goals = 0
    away_goals = 0
    if fixtures:
        for item in fixtures:
            try:
                score = item['score']['fulltime']
                home_score = score.get('home')
                away_score = score.get('away')
                if home_score is None or away_score is None:
                    continue
                home_goals += home_score
                away_goals += away_score
                totals.append(home_score + away_score)
            except (KeyError, TypeError):
                continue

    match_count = len(totals)
    if match_count == 0:
        fallback_home = default_avg * 0.55
        fallback_away = max(0.4, default_avg - fallback_home)
        return {
            'total_avg': default_avg,
            'home_avg': fallback_home,
            'away_avg': fallback_away,
            'total_std': default_avg * 0.35,
            'sample_size': 0,
        }

    total_avg = (home_goals + away_goals) / match_count
    home_avg = home_goals / match_count
    away_avg = away_goals / match_count
    variance = sum((value - total_avg) ** 2 for value in totals) / match_count if match_count else 0.0
    total_std = math.sqrt(variance) if variance > 0 else default_avg * 0.35

    return {
        'total_avg': total_avg,
        'home_avg': home_avg,
        'away_avg': away_avg,
        'total_std': total_std,
        'sample_size': match_count,
    }


def get_dynamic_league_average(api_key: str, base_url: str, league_info: Dict, default_avg: float) -> float:
    baselines = get_league_goal_baselines(api_key, base_url, league_info, default_avg)
    return baselines['total_avg']

@st.cache_data(ttl=86400)
def calculate_general_stats_v2(api_key: str, base_url: str, team_id: int, league_id: int, season: int) -> Dict:
    """Genel istatistikleri ve takıma özel ev sahibi avantajını hesaplar."""
    stats_data, error = api_utils.get_team_statistics(api_key, base_url, team_id, league_id, season)
    if error or not stats_data:
        # Varsayılan değerler döndür - sistem yine de çalışabilsin
        return {
            'home': {
                'Ort. Gol ATILAN': 1.2,
                'Ort. Gol YENEN': 1.2,
                'Istikrar_Puani': 50.0
            },
            'away': {
                'Ort. Gol ATILAN': 1.0,
                'Ort. Gol YENEN': 1.3,
                'Istikrar_Puani': 45.0
            },
            'team_specific_home_adv': 1.12
        }

    def get_stats_and_ppg(data, location_key):
        fixtures = data['fixtures']['played'][location_key]
        if fixtures == 0: return {}, 0.0

        wins = data['fixtures']['wins'][location_key]
        draws = data['fixtures']['draws'][location_key]
        ppg = (wins * 3 + draws) / fixtures if fixtures > 0 else 0.0

        stats = {
            'Ort. Gol ATILAN': float(data['goals']['for']['average'][location_key] or 0),
            'Ort. Gol YENEN': float(data['goals']['against']['average'][location_key] or 0),
            'Istikrar_Puani': round(((wins / fixtures) + 0.5 * (draws / fixtures)) * 100, 1)
        }
        return stats, ppg

    home_stats, home_ppg = get_stats_and_ppg(stats_data, 'home')
    away_stats, away_ppg = get_stats_and_ppg(stats_data, 'away')

    team_specific_home_adv = 1.12  # Daha düşük varsayılan
    if home_ppg > 0 and away_ppg > 0:
        ratio = home_ppg / away_ppg
        # Oranı daha dar bir aralığa sıkıştır
        team_specific_home_adv = max(1.02, min(ratio, 1.22))
    elif home_ppg > 0 and away_ppg == 0:
        # Sadece ev verisi varsa, makul bir varsayım
        team_specific_home_adv = 1.10
    elif away_ppg > 0 and home_ppg == 0:
        # Sadece deplasman verisi varsa, düşük avantaj
        team_specific_home_adv = 1.05

    return {
        'home': home_stats if home_stats else {'Ort. Gol ATILAN': 1.2, 'Ort. Gol YENEN': 1.2, 'Istikrar_Puani': 50.0},
        'away': away_stats if away_stats else {'Ort. Gol ATILAN': 1.0, 'Ort. Gol YENEN': 1.3, 'Istikrar_Puani': 45.0},
        'team_specific_home_adv': team_specific_home_adv
    }

def calculate_weighted_stats(matches: List[Dict]) -> Dict:
    home_stats = {'goals_for': [], 'goals_against': []}
    away_stats = {'goals_for': [], 'goals_against': []}
    for match in matches:
        if match['location'] == 'home':
            home_stats['goals_for'].append(match['goals_for'])
            home_stats['goals_against'].append(match['goals_against'])
        else:
            away_stats['goals_for'].append(match['goals_for'])
            away_stats['goals_against'].append(match['goals_against'])

    def get_weighted_average(values: List[int]) -> float:
        if not values: return 0.0
        weighted_sum, total_weight = 0, 0
        for i, value in enumerate(values):
            weight = i + 1
            weighted_sum += value * weight
            total_weight += weight
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        'home': {'w_avg_goals_for': get_weighted_average(home_stats['goals_for']), 'w_avg_goals_against': get_weighted_average(home_stats['goals_against'])},
        'away': {'w_avg_goals_for': get_weighted_average(away_stats['goals_for']),'w_avg_goals_against': get_weighted_average(away_stats['goals_against'])}
    }

def calculate_form_factor(matches: Optional[List[Dict]], preferred_location: Optional[str] = None) -> float:
    """Son maç sonuçlarına göre form katsayısını hesaplar."""
    if not matches:
        return 1.0

    filtered = [m for m in matches if preferred_location is None or m.get('location') == preferred_location]
    if not filtered:
        filtered = matches

    weighted_points, total_weight = 0.0, 0
    for idx, match in enumerate(filtered, start=1):
        gf, ga = match.get('goals_for'), match.get('goals_against')
        if gf is None or ga is None:
            continue
        points = 3 if gf > ga else 1 if gf == ga else 0
        weight = idx  # daha yeni maçlara daha yüksek ağırlık
        weighted_points += points * weight
        total_weight += weight

    if total_weight == 0:
        return 1.0

    avg_points = weighted_points / total_weight
    baseline = 1.5  # nötr seviye ~1.5 puan/maç
    factor = 1 + ((avg_points - baseline) / 6)
    return max(0.85, min(1.15, round(factor, 3)))

def process_odds_data(odds_response: List[Dict]) -> Optional[Dict]:
    if not odds_response or not odds_response[0].get('bookmakers'): return None
    home_odds, draw_odds, away_odds = [], [], []
    bookmakers = odds_response[0]['bookmakers']
    for bookmaker in bookmakers:
        try:
            match_winner_bet = next(bet for bet in bookmaker['bets'] if bet['name'] == 'Match Winner')
            values = match_winner_bet['values']
            h = float(next(val['odd'] for val in values if val['value'] == 'Home'))
            d = float(next(val['odd'] for val in values if val['value'] == 'Draw'))
            a = float(next(val['odd'] for val in values if val['value'] == 'Away'))
            home_odds.append(h); draw_odds.append(d); away_odds.append(a)
        except (StopIteration, KeyError, IndexError, ValueError): continue
    if not all([home_odds, draw_odds, away_odds]): return None
    avg_home_odd, avg_draw_odd, avg_away_odd = sum(home_odds) / len(home_odds), sum(draw_odds) / len(draw_odds), sum(away_odds) / len(away_odds)
    return {'home': {'odd': avg_home_odd, 'prob': (1 / avg_home_odd) * 100}, 'draw': {'odd': avg_draw_odd, 'prob': (1 / avg_draw_odd) * 100}, 'away': {'odd': avg_away_odd, 'prob': (1 / avg_away_odd) * 100}}

def poisson_pmf(l, k):
    if l <= 0 or k < 0: return 0.0
    try: return (l**k) * math.exp(-l) / math.factorial(k)
    except (ValueError, OverflowError): return 0.0

def calculate_match_probabilities(s_a: float, s_b: float) -> Dict[str, float]:
    limits = range(11)
    accum = {'over': 0.0, 'btts': 0.0, 'win_a': 0.0, 'draw': 0.0}
    for i in limits:
        for j in limits:
            prob = poisson_pmf(s_a, i) * poisson_pmf(s_b, j)
            accum['over'] += prob if (i + j) > 2 else 0.0
            accum['btts'] += prob if (i > 0 and j > 0) else 0.0
            if i > j:
                accum['win_a'] += prob
            elif i == j:
                accum['draw'] += prob

    win_b = max(0.0, 1.0 - accum['win_a'] - accum['draw'])
    prob_dict = {
        'ust_2.5': round(accum['over'] * 100, 1),
        'alt_2.5': round((1 - accum['over']) * 100, 1),
        'kg_var': round(accum['btts'] * 100, 1),
        'kg_yok': round((1 - accum['btts']) * 100, 1),
        'win_a': round(accum['win_a'] * 100, 1),
        'win_b': round(win_b * 100, 1),
        'draw': round(accum['draw'] * 100, 1),
    }
    return prob_dict

def get_key_players(player_stats: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    if not player_stats: return {'top_scorer_ids': [], 'most_minutes_ids': []}
    max_goals, top_scorers = 0, []
    for p in player_stats:
        goals = p['statistics'][0]['goals']['total'] or 0
        if goals > max_goals:
            max_goals, top_scorers = goals, [p['player']['id']]
        elif goals == max_goals and max_goals > 0:
            top_scorers.append(p['player']['id'])
    player_stats.sort(key=lambda p: p['statistics'][0]['games']['minutes'] or 0, reverse=True)
    most_minutes = [p['player']['id'] for p in player_stats[:4]]
    return {'top_scorer_ids': top_scorers, 'most_minutes_ids': most_minutes}

def generate_prediction_reasons(analysis_data: Dict, team_names: Dict) -> List[str]:
    reasons: List[str] = []
    probs = analysis_data['probs']
    params = analysis_data['params']
    stats = analysis_data['stats']
    diff = analysis_data['diff']
    max_prob_key = max(probs, key=lambda k: probs[k] if 'win' in k or 'draw' in k else -1)
    winner_name = team_names['a'] if max_prob_key == 'win_a' else team_names['b'] if max_prob_key == 'win_b' else ""

    if diff > 20 and winner_name:
        reasons.append(f"Model, **{winner_name}** takımını net favori olarak görüyor (olasılık farkı {diff:.1f}%).")

    if max_prob_key == 'win_a' and params['home_att'] > params['away_def'] * 1.4:
        reasons.append(f"**{team_names['a']}** hücum verileri ({params['home_att']:.2f} gol) rakibin savunmasından ({params['away_def']:.2f}) belirgin şekilde üstün.")
    elif max_prob_key == 'win_b' and params['away_att'] > params['home_def'] * 1.4:
        reasons.append(f"**{team_names['b']}** deplasman hücumu ({params['away_att']:.2f} gol), ev sahibi savunmasını ({params['home_def']:.2f}) baskı altına alacak güçte görünüyor.")

    stab_a = stats['a'].get('home', {}).get('Istikrar_Puani', 0)
    stab_b = stats['b'].get('away', {}).get('Istikrar_Puani', 0)
    if abs(stab_a - stab_b) > 15:
        if stab_a > stab_b and max_prob_key == 'win_a':
            reasons.append(f"Ev sahibi istikrar puanı ({stab_a:.1f}), rakibine ({stab_b:.1f}) göre belirgin biçimde yüksek.")
        elif stab_b > stab_a and max_prob_key == 'win_b':
            reasons.append(f"Deplasman istikrarı ({stab_b:.1f}), ev sahibine ({stab_a:.1f}) kıyasla daha güven veriyor.")

    if params['att_mult_b'] < 1.0 and max_prob_key == 'win_a':
        reasons.append(f"**{team_names['b']}** tarafındaki kilit hücum eksikleri, üretkenliklerini düşürüyor.")
    if params['att_mult_a'] < 1.0 and max_prob_key == 'win_b':
        reasons.append(f"**{team_names['a']}** cephesindeki önemli eksikler, ev sahibi avantajını törpülüyor.")

    form_a = params.get('form_factor_a', 1.0)
    form_b = params.get('form_factor_b', 1.0)
    form_diff = form_a - form_b
    if abs(form_diff) >= 0.08:
        if form_diff > 0:
            reasons.append(f"Son maç formu **{team_names['a']}** lehine (x{form_a:.2f} vs x{form_b:.2f}).")
        else:
            reasons.append(f"Güncel form verisi **{team_names['b']}** tarafını öne çıkarıyor (x{form_b:.2f} vs x{form_a:.2f}).")

    elo_diff = params.get('elo_diff', 0)
    if abs(elo_diff) >= 60:
        elo_fav = team_names['a'] if elo_diff > 0 else team_names['b']
        reasons.append(f"Elo farkı {abs(elo_diff):.0f} puan ve {elo_fav} lehine, kalite avantajı yaratıyor.")

    pace_idx = params.get('pace_index', 1.0)
    if pace_idx >= 1.15:
        reasons.append("Tempo beklenenin üzerinde; yüksek ritim favori tarafın lehine sonuç üretme şansını artırıyor.")

    if not reasons and winner_name:
        reasons.append(f"Genel parametre dengesi **{winner_name}** tarafını öne çıkarıyor.")

    return reasons[:3]

@st.cache_data(ttl=86400)
def run_core_analysis(api_key, base_url, id_a, id_b, name_a, name_b, fixture_id, league_info, model_params, default_avg):
    baselines = get_league_goal_baselines(api_key, base_url, league_info, default_avg)
    avg_goals = baselines['total_avg'] or default_avg
    avg_home_goals = baselines['home_avg'] or (avg_goals * 0.55)
    avg_away_goals = baselines['away_avg'] or max(0.4, avg_goals - avg_home_goals)

    stats_a = calculate_general_stats_v2(api_key, base_url, id_a, league_info['league_id'], league_info['season'])
    stats_b = calculate_general_stats_v2(api_key, base_url, id_b, league_info['league_id'], league_info['season'])
    # Artık her zaman varsayılan değerler dönüyor, None kontrolü gereksiz

    team_home_adv = stats_a.get('team_specific_home_adv', 1.12)
    league_bias = avg_home_goals / max(0.5, avg_away_goals)
    
    # Ev sahibi avantajını takım kalitesine göre ayarla
    ratings = elo_utils.read_ratings()
    rating_home = elo_utils.get_team_rating(id_a, ratings)
    rating_away = elo_utils.get_team_rating(id_b, ratings)
    
    # Güçlü takımlar deplasmanda daha iyi oynar, ev sahibi avantajı azalır
    if rating_away > rating_home + 100:
        quality_adjust = 0.95  # Deplasman takımı çok güçlüyse ev avantajını azalt
    elif rating_away > rating_home + 50:
        quality_adjust = 0.97
    elif rating_home > rating_away + 100:
        quality_adjust = 1.08  # Ev sahibi çok güçlüyse avantaj artır
    elif rating_home > rating_away + 50:
        quality_adjust = 1.05
    else:
        quality_adjust = 1.0
    
    home_advantage = team_home_adv * max(0.96, min(1.12, league_bias)) * quality_adjust
    home_advantage = max(1.02, min(1.20, home_advantage))

    last_matches_a = api_utils.get_team_last_matches_stats(api_key, base_url, id_a)
    last_matches_b = api_utils.get_team_last_matches_stats(api_key, base_url, id_b)
    weighted_stats_a = calculate_weighted_stats(last_matches_a) if last_matches_a else {}
    weighted_stats_b = calculate_weighted_stats(last_matches_b) if last_matches_b else {}

    FORM_WEIGHT, SEASON_WEIGHT = 0.6, 0.4

    def get_blended_stat(s_stats, w_stats, loc, s_key, w_key):
        season_val = s_stats.get(loc, {}).get(s_key, 0)
        weighted_val = w_stats.get(loc, {}).get(w_key, 0)
        
        # Eğer season verisi varsa ama weighted yoksa, season verisini kullan
        if season_val > 0 and weighted_val == 0:
            weighted_val = season_val
        
        # Eğer weighted verisi varsa ama season yoksa, weighted'ı kullan
        if weighted_val > 0 and season_val == 0:
            season_val = weighted_val
        
        # Her ikisi de yoksa minimum değer döndür
        if season_val == 0 and weighted_val == 0:
            return 0.2
        
        blended = (weighted_val * FORM_WEIGHT) + (season_val * SEASON_WEIGHT)
        return max(0.2, min(blended, 2.5))

    home_att = get_blended_stat(stats_a, weighted_stats_a, 'home', 'Ort. Gol ATILAN', 'w_avg_goals_for')
    home_def = get_blended_stat(stats_a, weighted_stats_a, 'home', 'Ort. Gol YENEN', 'w_avg_goals_against')
    away_att = get_blended_stat(stats_b, weighted_stats_b, 'away', 'Ort. Gol ATILAN', 'w_avg_goals_for')
    away_def = get_blended_stat(stats_b, weighted_stats_b, 'away', 'Ort. Gol YENEN', 'w_avg_goals_against')

    def clamp(value: float, lower: float = 0.55, upper: float = 1.8) -> float:
        return max(lower, min(upper, value))

    home_attack_idx = clamp(home_att / max(0.3, avg_home_goals))
    away_attack_idx = clamp(away_att / max(0.3, avg_away_goals))
    home_def_idx = clamp(home_def / max(0.3, avg_away_goals))
    away_def_idx = clamp(away_def / max(0.3, avg_home_goals))

    injuries, _ = api_utils.get_fixture_injuries(api_key, base_url, fixture_id)
    injured_ids = {p['player']['id'] for p in injuries} if injuries else set()

    p_stats_a, _ = api_utils.get_squad_player_stats(api_key, base_url, id_a, league_info['season'])
    p_stats_b, _ = api_utils.get_squad_player_stats(api_key, base_url, id_b, league_info['season'])
    key_a = get_key_players(p_stats_a) if p_stats_a else {}
    key_b = get_key_players(p_stats_b) if p_stats_b else {}

    injury_impact = model_params['injury_impact']
    max_goals = model_params['max_goals']

    att_mult_a = injury_impact if any(pid in injured_ids for pid in key_a.get('top_scorer_ids', [])) else 1.0
    def_mult_a = (1 / injury_impact) if any(pid in injured_ids for pid in key_a.get('most_minutes_ids', [])) else 1.0
    att_mult_b = injury_impact if any(pid in injured_ids for pid in key_b.get('top_scorer_ids', [])) else 1.0
    def_mult_b = (1 / injury_impact) if any(pid in injured_ids for pid in key_b.get('most_minutes_ids', [])) else 1.0

    form_factor_a = calculate_form_factor(last_matches_a, 'home')
    form_factor_b = calculate_form_factor(last_matches_b, 'away')

    # Önce Elo farkını hesapla ve temel ayarlamayı yap
    elo_diff = rating_home - rating_away
    
    # Elo farkına göre çok daha agresif ayarlama
    if elo_diff < -150:  # Deplasman çok güçlü (örn: PSG)
        elo_boost_away = 1.35
        elo_nerf_home = 0.75
    elif elo_diff < -80:
        elo_boost_away = 1.25
        elo_nerf_home = 0.82
    elif elo_diff < -30:
        elo_boost_away = 1.15
        elo_nerf_home = 0.90
    elif elo_diff > 150:  # Ev sahibi çok güçlü
        elo_boost_away = 0.75
        elo_nerf_home = 1.30
    elif elo_diff > 80:
        elo_boost_away = 0.82
        elo_nerf_home = 1.22
    elif elo_diff > 30:
        elo_boost_away = 0.90
        elo_nerf_home = 1.12
    else:  # Dengeli
        elo_boost_away = 1.0
        elo_nerf_home = 1.0

    base_lambda_a = avg_home_goals * home_attack_idx * away_def_idx * elo_nerf_home
    base_lambda_b = avg_away_goals * away_attack_idx * home_def_idx * elo_boost_away

    # Ev sahibi avantajını sadece dengeli maçlarda uygula
    if abs(elo_diff) < 80:
        lambda_a = base_lambda_a * att_mult_a * def_mult_b * home_advantage
    else:
        # Büyük kalite farkında ev avantajını minimize et
        reduced_home_adv = 1.0 + ((home_advantage - 1.0) * 0.4)
        lambda_a = base_lambda_a * att_mult_a * def_mult_b * reduced_home_adv
    
    lambda_b = base_lambda_b * att_mult_b * def_mult_a

    lambda_a *= min(1.08, max(0.92, form_factor_a))
    lambda_b *= min(1.08, max(0.92, form_factor_b))

    # Kalite farkı yüksekse regresyonu azalt
    quality_gap = abs(elo_diff)
    if quality_gap > 150:
        regression_factor = 0.90  # Büyük fark varsa modele çok güven
    elif quality_gap > 80:
        regression_factor = 0.87
    else:
        regression_factor = 0.80  # Dengeli maçlarda muhafazakar
    
    lambda_a = (lambda_a * regression_factor) + (avg_home_goals * (1 - regression_factor))
    lambda_b = (lambda_b * regression_factor) + (avg_away_goals * (1 - regression_factor))

    lambda_a = max(0.3, min(lambda_a, max_goals))
    lambda_b = max(0.3, min(lambda_b, max_goals))

    score_a = round(lambda_a, 2)
    score_b = round(lambda_b, 2)

    probs = calculate_match_probabilities(score_a, score_b)
    ranking = sorted([probs['win_a'], probs['win_b'], probs['draw']], reverse=True)
    diff = round(ranking[0] - ranking[1], 1)

    stability_a = stats_a.get('home', {}).get('Istikrar_Puani', 0)
    stability_b = stats_b.get('away', {}).get('Istikrar_Puani', 0)
    avg_stab = (stability_a + stability_b) / 2 if stability_a and stability_b else 0

    volatility_ratio = baselines['total_std'] / max(0.3, baselines['total_avg'])
    volatility_ratio = max(0.1, min(1.5, volatility_ratio))
    sample_factor = min(1.0, baselines['sample_size'] / 160) if baselines['sample_size'] else 0.4
    elo_signal = min(0.5, abs(elo_diff) / 320)
    stability_component = 0.55 + (avg_stab / 200)
    confidence_multiplier = stability_component * (0.75 + 0.25 * sample_factor) * (1 - 0.25 * volatility_ratio) * (1 + 0.5 * elo_signal)
    confidence = round(min(100.0, max(5.0, diff * max(0.4, confidence_multiplier))), 1)

    pace_index = (home_att + away_att) / max(0.2, avg_home_goals + avg_away_goals)

    analysis_result = {
        'score_a': score_a,
        'score_b': score_b,
        'expected_total': round(lambda_a + lambda_b, 2),
        'goal_spread': round(lambda_a - lambda_b, 2),
        'probs': probs,
        'confidence': confidence,
        'diff': diff,
        'params': {
            'avg_goals': avg_goals,
            'avg_home_goals': avg_home_goals,
            'avg_away_goals': avg_away_goals,
            'home_att': home_att,
            'home_def': home_def,
            'away_att': away_att,
            'away_def': away_def,
            'home_attack_idx': home_attack_idx,
            'away_attack_idx': away_attack_idx,
            'home_def_idx': home_def_idx,
            'away_def_idx': away_def_idx,
            'att_mult_a': att_mult_a,
            'def_mult_a': def_mult_a,
            'att_mult_b': att_mult_b,
            'def_mult_b': def_mult_b,
            'home_advantage': home_advantage,
            'form_factor_a': form_factor_a,
            'form_factor_b': form_factor_b,
            'elo_home': rating_home,
            'elo_away': rating_away,
            'elo_diff': elo_diff,
            'elo_boost_away': elo_boost_away,
            'elo_nerf_home': elo_nerf_home,
            'baseline_std': baselines['total_std'],
            'sample_size': baselines['sample_size'],
            'pace_index': pace_index,
        },
        'stats': {'a': stats_a, 'b': stats_b},
    }

    reasons = generate_prediction_reasons(analysis_result, {'a': name_a, 'b': name_b})
    analysis_result['reasons'] = reasons

    return analysis_result