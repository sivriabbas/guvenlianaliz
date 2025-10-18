# analysis_logic.py

import math
from typing import Dict, Any, List, Optional
from datetime import datetime
import streamlit as st
import api_utils

def process_player_stats(player_data: Optional[List[Dict]]) -> Optional[str]:
    """Oyuncu istatistik verisini işleyip okunabilir bir metin döner."""
    if not player_data or not player_data[0].get('statistics'):
        return None
    
    try:
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
def get_dynamic_league_average(api_key: str, base_url: str, league_info: Dict, default_avg: float) -> float:
    params = {'league': league_info['league_id'], 'season': league_info['season'], 'status': 'FT', 'last': 100}
    fixtures, _ = api_utils.make_api_request(api_key, base_url, "fixtures", params)
    if not fixtures: return default_avg
    goals, count = 0, 0
    for f in fixtures:
        score = f['score']['fulltime']
        if score['home'] is not None and score['away'] is not None:
            goals += score['home'] + score['away']; count += 1
    return (goals / count) if count > 0 else default_avg

@st.cache_data(ttl=86400)
def calculate_general_stats_v2(api_key: str, base_url: str, team_id: int, league_id: int, season: int) -> Dict:
    stats_data, error = api_utils.get_team_statistics(api_key, base_url, team_id, league_id, season)
    if error or not stats_data:
        return {}
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
    team_specific_home_adv = 1.15
    if home_ppg > 0 and away_ppg > 0:
        ratio = home_ppg / away_ppg
        team_specific_home_adv = max(1.0, min(ratio, 1.35))
    return {
        'home': home_stats,
        'away': away_stats,
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

def process_odds_data(odds_response: List[Dict]) -> Optional[Dict]:
    if not odds_response or not odds_response[0]['bookmakers']: return None
    try:
        odds_values = odds_response[0]['bookmakers'][0]['bets'][0]['values']
        home_odd = float(next(item['odd'] for item in odds_values if item['value'] == 'Home'))
        draw_odd = float(next(item['odd'] for item in odds_values if item['value'] == 'Draw'))
        away_odd = float(next(item['odd'] for item in odds_values if item['value'] == 'Away'))
        return {'home': {'odd': home_odd, 'prob': (1 / home_odd) * 100}, 'draw': {'odd': draw_odd, 'prob': (1 / draw_odd) * 100}, 'away': {'odd': away_odd, 'prob': (1 / away_odd) * 100}}
    except (StopIteration, KeyError, IndexError, ValueError):
        return None

def poisson_pmf(l, k):
    if l <= 0 or k < 0: return 0.0
    try: return (l**k) * math.exp(-l) / math.factorial(k)
    except (ValueError, OverflowError): return 0.0

def calculate_match_probabilities(s_a, s_b):
    p={'u25':0.0,'kgv':0.0,'w_a':0.0,'d':0.0}
    for i in range(7):
        for j in range(7):
            prob = poisson_pmf(s_a,i)*poisson_pmf(s_b,j)
            if i+j > 2.5: p['u25'] += prob
            if i>0 and j>0: p['kgv'] += prob
            if i>j: p['w_a'] += prob
            elif i==j: p['d'] += prob
    return {'ust_2.5':round(p['u25']*100,1),'alt_2.5':round((1-p['u25'])*100,1),'kg_var':round(p['kgv']*100,1),'kg_yok':round((1-p['kgv'])*100,1),'win_a':round(p['w_a']*100,1),'win_b':round((1-p['w_a']-p['d'])*100,1),'draw':round(p['d']*100,1)}

def get_key_players(player_stats: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    if not player_stats: return {'top_scorer_ids': [], 'most_minutes_ids': []}
    max_goals = 0; top_scorers = []
    for p in player_stats:
        goals = p['statistics'][0]['goals']['total'] or 0
        if goals > max_goals:
            max_goals = goals; top_scorers = [p['player']['id']]
        elif goals == max_goals and max_goals > 0:
            top_scorers.append(p['player']['id'])
    player_stats.sort(key=lambda p: p['statistics'][0]['games']['minutes'] or 0, reverse=True)
    most_minutes = [p['player']['id'] for p in player_stats[:4]]
    return {'top_scorer_ids': top_scorers, 'most_minutes_ids': most_minutes}

def generate_prediction_reasons(analysis_data: Dict, team_names: Dict) -> List[str]:
    reasons = []
    probs, params, stats, diff = analysis_data['probs'], analysis_data['params'], analysis_data['stats'], analysis_data['diff']
    max_prob_key = max(probs, key=lambda k: probs[k] if 'win' in k or 'draw' in k else -1)
    winner_name = ""
    if max_prob_key == 'win_a': winner_name = team_names['a']
    elif max_prob_key == 'win_b': winner_name = team_names['b']
    if diff > 20: reasons.append(f"Model, **{winner_name}** takımını net favori olarak görüyor (Olasılık farkı: {diff:.1f}%).")
    if max_prob_key == 'win_a' and params['home_att'] > params['away_def'] * 1.5: reasons.append(f"**{team_names['a']}** takımının hücum gücü ({params['home_att']:.2f}), rakibin savunma gücüne ({params['away_def']:.2f}) kıyasla oldukça yüksek.")
    elif max_prob_key == 'win_b' and params['away_att'] > params['home_def'] * 1.5: reasons.append(f"**{team_names['b']}** takımının deplasman hücum gücü ({params['away_att']:.2f}), ev sahibinin savunma gücüne ({params['home_def']:.2f}) göre dikkat çekici.")
    stab_a, stab_b = stats['a'].get('home', {}).get('Istikrar_Puani', 0), stats['b'].get('away', {}).get('Istikrar_Puani', 0)
    if abs(stab_a - stab_b) > 15:
        if stab_a > stab_b and max_prob_key == 'win_a': reasons.append(f"Ev sahibi takımın istikrar puanı ({stab_a:.1f}), rakibine ({stab_b:.1f}) göre daha yüksek, bu da daha tutarlı sonuçlar aldığını gösteriyor.")
        elif stab_b > stab_a and max_prob_key == 'win_b': reasons.append(f"Deplasman takımının istikrar puanı ({stab_b:.1f}), rakibine ({stab_a:.1f}) göre daha yüksek, bu da deplasmanda bile tutarlı olduğunu gösteriyor.")
    if params['att_mult_b'] < 1.0 and max_prob_key == 'win_a': reasons.append(f"**{team_names['b']}** takımındaki kilit oyuncu eksiği, hücum potansiyellerini düşürüyor.")
    if params['att_mult_a'] < 1.0 and max_prob_key == 'win_b': reasons.append(f"**{team_names['a']}** takımındaki kilit oyuncu eksiği, ev sahibi avantajını azaltıyor.")
    if not reasons and winner_name: reasons.append(f"Genel istatistiksel üstünlükler ve form durumu, **{winner_name}** takımını bir adım önde gösteriyor.")
    return reasons[:3]

@st.cache_data(ttl=86400)
def run_core_analysis(api_key, base_url, id_a, id_b, name_a, name_b, fixture_id, league_info, model_params, default_avg):
    avg_goals = get_dynamic_league_average(api_key, base_url, league_info, default_avg)
    stats_a = calculate_general_stats_v2(api_key, base_url, id_a, league_info['league_id'], league_info['season'])
    stats_b = calculate_general_stats_v2(api_key, base_url, id_b, league_info['league_id'], league_info['season'])
    if not stats_a or not stats_b:
        return None
    home_advantage = stats_a.get('team_specific_home_adv', 1.15)
    last_matches_a = api_utils.get_team_last_matches_stats(api_key, base_url, id_a)
    last_matches_b = api_utils.get_team_last_matches_stats(api_key, base_url, id_b)
    weighted_stats_a = calculate_weighted_stats(last_matches_a) if last_matches_a else {}
    weighted_stats_b = calculate_weighted_stats(last_matches_b) if last_matches_b else {}
    FORM_WEIGHT, SEASON_WEIGHT = 0.7, 0.3
    def get_blended_stat(s_stats, w_stats, loc, s_key, w_key):
        season_val = s_stats.get(loc, {}).get(s_key, 0)
        weighted_val = w_stats.get(loc, {}).get(w_key, season_val)
        if season_val == 0 and weighted_val == 0: return 0.1
        return (weighted_val * FORM_WEIGHT) + (season_val * SEASON_WEIGHT)
    home_att = get_blended_stat(stats_a, weighted_stats_a, 'home', 'Ort. Gol ATILAN', 'w_avg_goals_for')
    home_def = get_blended_stat(stats_a, weighted_stats_a, 'home', 'Ort. Gol YENEN', 'w_avg_goals_against')
    away_att = get_blended_stat(stats_b, weighted_stats_b, 'away', 'Ort. Gol ATILAN', 'w_avg_goals_for')
    away_def = get_blended_stat(stats_b, weighted_stats_b, 'away', 'Ort. Gol YENEN', 'w_avg_goals_against')
    injuries, _ = api_utils.get_fixture_injuries(api_key, base_url, fixture_id)
    injured_ids = {p['player']['id'] for p in injuries} if injuries else set()
    p_stats_a, _ = api_utils.get_squad_player_stats(api_key, base_url, id_a, league_info['season'])
    p_stats_b, _ = api_utils.get_squad_player_stats(api_key, base_url, id_b, league_info['season'])
    key_a = get_key_players(p_stats_a) if p_stats_a else {}
    key_b = get_key_players(p_stats_b) if p_stats_b else {}
    injury_impact, max_goals = model_params['injury_impact'], model_params['max_goals']
    att_mult_a = injury_impact if any(p in injured_ids for p in key_a.get('top_scorer_ids', [])) else 1.0
    def_mult_a = 1/injury_impact if any(p in injured_ids for p in key_a.get('most_minutes_ids', [])) else 1.0
    att_mult_b = injury_impact if any(p in injured_ids for p in key_b.get('top_scorer_ids', [])) else 1.0
    def_mult_b = 1/injury_impact if any(p in injured_ids for p in key_b.get('most_minutes_ids', [])) else 1.0
    lambda_a = ((home_att * att_mult_a) / avg_goals) * ((away_def * def_mult_b) / avg_goals) * avg_goals * home_advantage
    lambda_b = ((away_att * att_mult_b) / avg_goals) * ((home_def * def_mult_a) / avg_goals) * avg_goals
    score_a, score_b = min(lambda_a, max_goals), min(lambda_b, max_goals)
    probs = calculate_match_probabilities(score_a, score_b)
    prob_list = sorted([probs['win_a'], probs['win_b'], probs['draw']], reverse=True)
    diff = round(prob_list[0]-prob_list[1],1)
    stability_a = stats_a.get('home',{}).get('Istikrar_Puani', 0)
    stability_b = stats_b.get('away',{}).get('Istikrar_Puani', 0)
    avg_stab = (stability_a+stability_b)/2 if stability_a and stability_b else 0
    confidence = round((diff*avg_stab)/100, 1)
    analysis_result = {'score_a':score_a, 'score_b':score_b, 'probs':probs, 'confidence':confidence, 'diff':diff,
                       'params': {'avg_goals': avg_goals, 'home_att': home_att, 'away_def': away_def, 'away_att': away_att, 'home_def': home_def,
                                  'att_mult_a': att_mult_a, 'def_mult_a': def_mult_a, 'att_mult_b': att_mult_b, 'def_mult_b': def_mult_b,
                                  'home_advantage': home_advantage},
                       'stats': {'a': stats_a, 'b': stats_b}}
    reasons = generate_prediction_reasons(analysis_result, {'a': name_a, 'b': name_b})
    analysis_result['reasons'] = reasons
    return analysis_result