# Streamlit compatibility check
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("⚠️ Warning: Streamlit not available. Some features may not work.")
    
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import time
from api_utils import (
    get_api_predictions, get_betting_odds, get_team_top_players,
    get_fixtures_lineups, get_fixture_players_stats, get_team_transfers,
    get_league_top_scorers, get_league_top_assists, get_fixtures_by_date,
    search_team_fixtures_advanced, get_team_upcoming_fixtures
)

def display_enhanced_match_analysis(api_key: str, base_url: str):
    """Gelişmiş maç analizi sayfası"""
    st.title("🔍 Gelişmiş Maç Analizi")
    st.markdown("---")
    
    # Analiz türü seçimi
    analysis_type = st.radio(
        "Analiz Türü Seçin:",
        ["📅 Belirli Tarih Maçları", "⚽ Takım Bazlı Analiz", "🏆 Lig İstatistikleri"],
        horizontal=True
    )
    
    if analysis_type == "📅 Belirli Tarih Maçları":
        display_date_analysis(api_key, base_url)
    elif analysis_type == "⚽ Takım Bazlı Analiz":
        display_team_analysis(api_key, base_url)
    else:
        display_league_statistics(api_key, base_url)

def display_date_analysis(api_key: str, base_url: str):
    """Belirli tarih için maç analizi"""
    st.subheader("📅 Tarih Bazlı Maç Analizi")
    
    selected_date = st.date_input(
        "Analiz Edilecek Tarihi Seçin:",
        value=date.today(),
        min_value=date.today() - timedelta(days=7),
        max_value=date.today() + timedelta(days=30)
    )
    
    # Popüler ligler
    league_options = {
        "Süper Lig": 203,
        "Premier League": 39,
        "La Liga": 140,
        "Bundesliga": 78,
        "Serie A": 135,
        "Ligue 1": 61,
        "Champions League": 2
    }
    
    selected_leagues = st.multiselect(
        "Analiz Edilecek Ligleri Seçin:",
        options=list(league_options.keys()),
        default=["Süper Lig", "Premier League"]
    )
    
    if st.button("📊 Maçları Analiz Et", type="primary"):
        if not selected_leagues:
            st.warning("Lütfen en az bir lig seçin!")
            return
            
        league_ids = [league_options[league] for league in selected_leagues]
        
        with st.spinner("Maçlar getiriliyor..."):
            fixtures, error = get_fixtures_by_date(api_key, base_url, league_ids, selected_date)
            
        if error:
            st.error(f"Maçlar alınırken hata: {error}")
            return
            
        if not fixtures:
            st.info("Seçilen tarih ve ligler için maç bulunamadı.")
            return
            
        st.success(f"{len(fixtures)} maç bulundu!")
        
        for fixture in fixtures:
            display_enhanced_fixture_card(api_key, base_url, fixture)

def display_team_analysis(api_key: str, base_url: str):
    """Takım bazlı detaylı analiz"""
    st.subheader("⚽ Takım Bazlı Detaylı Analiz")
    
    team_name = st.text_input("🔍 Takım Adını Girin:", placeholder="Örn: Galatasaray, Real Madrid")
    
    if team_name and st.button("🔍 Takım Analizi Yap", type="primary"):
        with st.spinner(f"{team_name} takımı analiz ediliyor..."):
            # Yaklaşan maçları bul
            fixtures, error = get_team_upcoming_fixtures(api_key, base_url, team_name)
            
        if error:
            st.error(f"Takım bulunamadı: {error}")
            return
            
        if not fixtures:
            st.warning("Bu takım için yaklaşan maç bulunamadı.")
            return
            
        # Takım bilgilerini göster
        team_info = fixtures[0]['teams']['home'] if fixtures[0]['teams']['home']['name'].lower() in team_name.lower() else fixtures[0]['teams']['away']
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if team_info.get('logo'):
                st.image(team_info['logo'], width=100)
        with col2:
            st.markdown(f"### {team_info['name']}")
            st.markdown(f"**Kuruluş:** {team_info.get('founded', 'Bilinmiyor')}")
            
        # Yaklaşan maçlar
        st.markdown("### 📅 Yaklaşan Maçlar")
        for fixture in fixtures[:3]:  # İlk 3 maçı göster
            display_enhanced_fixture_card(api_key, base_url, fixture)
            
        # Oyuncu istatistikleri
        display_team_players_analysis(api_key, base_url, team_info['id'], 2024)

def display_league_statistics(api_key: str, base_url: str):
    """Lig istatistikleri"""
    st.subheader("🏆 Lig İstatistikleri")
    
    league_options = {
        "Süper Lig": 203,
        "Premier League": 39,
        "La Liga": 140,
        "Bundesliga": 78,
        "Serie A": 135,
        "Ligue 1": 61
    }
    
    selected_league = st.selectbox("Lig Seçin:", list(league_options.keys()))
    league_id = league_options[selected_league]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥅 Gol Krallığı")
        with st.spinner("Gol kralları getiriliyor..."):
            scorers, error = get_league_top_scorers(api_key, base_url, league_id, 2024)
            
        if scorers and not error:
            for i, player in enumerate(scorers[:10], 1):
                player_data = player['player']
                stats = player['statistics'][0]
                
                col_rank, col_player, col_goals = st.columns([1, 3, 1])
                with col_rank:
                    st.markdown(f"**{i}.**")
                with col_player:
                    st.markdown(f"{player_data['name']}")
                    st.caption(f"{stats['team']['name']}")
                with col_goals:
                    st.markdown(f"**{stats['goals']['total']}** ⚽")
                    
    with col2:
        st.markdown("#### 🎯 Asist Krallığı")
        with st.spinner("Asist kralları getiriliyor..."):
            assists, error = get_league_top_assists(api_key, base_url, league_id, 2024)
            
        if assists and not error:
            for i, player in enumerate(assists[:10], 1):
                player_data = player['player']
                stats = player['statistics'][0]
                
                col_rank, col_player, col_assists = st.columns([1, 3, 1])
                with col_rank:
                    st.markdown(f"**{i}.**")
                with col_player:
                    st.markdown(f"{player_data['name']}")
                    st.caption(f"{stats['team']['name']}")
                with col_assists:
                    st.markdown(f"**{stats['goals']['assists']}** 🎯")

def display_enhanced_fixture_card(api_key: str, base_url: str, fixture: Dict[str, Any]):
    """Gelişmiş maç kartı görünümü"""
    with st.expander(f"🏟️ {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}", expanded=False):
        
        # Temel maç bilgileri
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"### {fixture['teams']['home']['name']}")
            if fixture['teams']['home'].get('logo'):
                st.image(fixture['teams']['home']['logo'], width=80)
                
        with col2:
            match_time = datetime.fromisoformat(fixture['fixture']['date'].replace('Z', '+00:00'))
            st.markdown(f"**{match_time.strftime('%H:%M')}**")
            st.markdown(f"{fixture['league']['name']}")
            
        with col3:
            st.markdown(f"### {fixture['teams']['away']['name']}")
            if fixture['teams']['away'].get('logo'):
                st.image(fixture['teams']['away']['logo'], width=80)
        
        # Detaylı analiz butonları
        tab1, tab2, tab3, tab4 = st.tabs(["🔮 API Tahmini", "💰 Bahis Oranları", "👥 Kadro", "📊 İstatistikler"])
        
        with tab1:
            display_api_predictions(api_key, base_url, fixture['fixture']['id'])
            
        with tab2:
            display_betting_odds(api_key, base_url, fixture['fixture']['id'])
            
        with tab3:
            display_lineups(api_key, base_url, fixture['fixture']['id'])
            
        with tab4:
            display_match_statistics(api_key, base_url, fixture['fixture']['id'])

def display_api_predictions(api_key: str, base_url: str, fixture_id: int):
    """API tahminlerini göster"""
    predictions, error = get_api_predictions(api_key, base_url, fixture_id)
    
    if error:
        st.info("API tahmini henüz mevcut değil.")
        return
        
    if predictions:
        pred = predictions['predictions']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Kazanan Tahmini", pred.get('winner', {}).get('name', 'Belirsiz'))
            
        with col2:
            st.metric("Forma Durumu", f"{pred.get('percent', {}).get('home', 'N/A')}% - {pred.get('percent', {}).get('away', 'N/A')}%")
            
        with col3:
            advice = pred.get('advice', 'Veri yok')
            st.metric("Tavsiye", advice if len(advice) < 20 else advice[:20] + "...")

def display_betting_odds(api_key: str, base_url: str, fixture_id: int):
    """Bahis oranlarını göster"""
    odds, error = get_betting_odds(api_key, base_url, fixture_id)
    
    if error or not odds:
        st.info("Bahis oranları henüz mevcut değil.")
        return
        
    for bookmaker in odds[:3]:  # İlk 3 bahis sitesini göster
        st.markdown(f"**{bookmaker['bookmaker']['name']}**")
        
        for bet in bookmaker['bets']:
            if bet['name'] == 'Match Winner':
                col1, col2, col3 = st.columns(3)
                
                for value in bet['values']:
                    if value['value'] == 'Home':
                        with col1:
                            st.metric("Ev Sahibi", value['odd'])
                    elif value['value'] == 'Draw':
                        with col2:
                            st.metric("Beraberlik", value['odd'])
                    elif value['value'] == 'Away':
                        with col3:
                            st.metric("Deplasman", value['odd'])
                break

def display_lineups(api_key: str, base_url: str, fixture_id: int):
    """Maç kadrolarını göster"""
    lineups, error = get_fixtures_lineups(api_key, base_url, fixture_id)
    
    if error or not lineups:
        st.info("Kadro bilgisi henüz mevcut değil.")
        return
        
    for team_lineup in lineups:
        st.markdown(f"### {team_lineup['team']['name']}")
        st.markdown(f"**Forma:** {team_lineup['formation']}")
        
        if team_lineup.get('startXI'):
            st.markdown("**İlk 11:**")
            for player in team_lineup['startXI']:
                st.write(f"{player['player']['number']}. {player['player']['name']} - {player['player']['pos']}")

def display_match_statistics(api_key: str, base_url: str, fixture_id: int):
    """Maç istatistiklerini göster"""
    stats, error = get_fixture_players_stats(api_key, base_url, fixture_id)
    
    if error or not stats:
        st.info("Oyuncu istatistikleri henüz mevcut değil.")
        return
        
    for team_stats in stats:
        st.markdown(f"### {team_stats['team']['name']}")
        
        if team_stats.get('players'):
            best_players = sorted(team_stats['players'], 
                                key=lambda x: x['statistics'][0].get('games', {}).get('rating', 0) or 0, 
                                reverse=True)[:5]
            
            for player in best_players:
                stat = player['statistics'][0]
                rating = stat.get('games', {}).get('rating')
                if rating:
                    st.write(f"⭐ {player['player']['name']}: {rating}/10")

def display_team_players_analysis(api_key: str, base_url: str, team_id: int, season: int):
    """Takım oyuncuları analizi"""
    st.markdown("### 👥 Takım Oyuncuları")
    
    players, error = get_team_top_players(api_key, base_url, team_id, season)
    
    if error or not players:
        st.info("Oyuncu bilgileri alınamadı.")
        return
        
    # En iyi oyuncuları göster
    best_players = sorted(players, 
                         key=lambda x: x['statistics'][0].get('games', {}).get('rating', 0) or 0, 
                         reverse=True)[:10]
    
    for i, player in enumerate(best_players, 1):
        stat = player['statistics'][0]
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        
        with col1:
            st.write(f"**{i}.**")
        with col2:
            st.write(f"{player['player']['name']}")
            st.caption(f"{stat.get('games', {}).get('position', 'N/A')}")
        with col3:
            rating = stat.get('games', {}).get('rating', 0)
            st.write(f"⭐ {rating if rating else 'N/A'}")
        with col4:
            goals = stat.get('goals', {}).get('total', 0)
            assists = stat.get('goals', {}).get('assists', 0)
            st.write(f"⚽ {goals} 🎯 {assists}")