# app.py

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date
<<<<<<< HEAD
from typing import Dict, Any, Optional
=======
from typing import Dict, List
>>>>>>> 022d0ad2125e10a505d9177179a42170fc80c60f

import api_utils
import analysis_logic

# --- KONFİGÜRASYON ---
<<<<<<< HEAD
st.set_page_config(layout="wide", page_title="Futbol Analiz Motoru")
=======
>>>>>>> 022d0ad2125e10a505d9177179a42170fc80c60f
try:
    API_KEY = st.secrets["API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("⚠️ Lütfen `.streamlit/secrets.toml` dosyasını oluşturun ve API_KEY'inizi ekleyin.")
    st.stop()
<<<<<<< HEAD
BASE_URL = "https://v3.football.api-sports.io"

# YENİ: Lig listesi alt liglerle birlikte genişletildi
INTERESTING_LEAGUES = {
    # Popüler Avrupa 1. Ligleri
    39: "🇬🇧 Premier League", 140: "🇪🇸 La Liga", 135: "🇮🇹 Serie A", 
    78: "🇩🇪 Bundesliga", 61: "🇫🇷 Ligue 1", 203: "🇹🇷 Süper Lig",
    88: "🇳🇱 Eredivisie", 94: "🇵🇹 Primeira Liga",
    # Popüler Avrupa 2. Ligleri
    40: "🇬🇧 Championship", 141: "🇪🇸 La Liga 2", 136: "🇮🇹 Serie B", 
    79: "🇩🇪 2. Bundesliga", 62: "🇫🇷 Ligue 2", 204: "🇹🇷 TFF 1. Lig",
    # Dünya Ligleri - 1. Seviye
    253: "🇺🇸 ABD - Major League Soccer",
    71: "🇧🇷 Brezilya - Serie A",
    128: "🇦🇷 Arjantin - Liga Profesional",
    144: "🇧🇪 Belçika - Jupiler Pro League",
    179: "🏴󠁧󠁢󠁳󠁣󠁴󠁿 İskoçya - Premiership",
    98: "🇯🇵 Japonya - J1 League",
    307: "🇸🇦 Suudi Arabistan - Professional League",
    # Dünya Ligleri - 2. Seviye
    255: "🇺🇸 ABD - USL Championship",
    72: "🇧🇷 Brezilya - Serie B",
    129: "🇦🇷 Arjantin - Primera Nacional",
    145: "🇧🇪 Belçika - Challenger Pro League",
    180: "🏴󠁧󠁢󠁳󠁣󠁴󠁿 İskoçya - Championship",
    99: "🇯🇵 Japonya - J2 League",
}

LIG_ORTALAMA_GOL = 1.35
DEFAULT_MAX_GOAL_EXPECTANCY, DEFAULT_KEY_PLAYER_IMPACT_MULTIPLIER, BEST_BET_THRESHOLD, H2H_MATCH_LIMIT = 3.0, 0.80, 30.0, 10

# --- YARDIMCI GÖRÜNÜM FONKSİYONLARII ---
def display_summary_tab(analysis: Dict, team_names: Dict, odds_data: Optional[Dict]):
    name_a, name_b = team_names['a'], team_names['b']
    score_a, score_b, probs, confidence, diff = analysis['score_a'], analysis['score_b'], analysis['probs'], analysis['confidence'], analysis['diff']
    max_prob_key = max(probs, key=lambda k: probs[k] if 'win' in k or 'draw' in k else -1)
    decision = f"{name_a} Kazanır" if max_prob_key == 'win_a' else f"{name_b} Kazanır" if max_prob_key == 'win_b' else "Beraberlik"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ev S. Gol Beklentisi", f"{score_a:.2f}")
    c2.metric("Dep. Gol Beklentisi", f"{score_b:.2f}")
    c3.metric("Olasılık Farkı", f"{diff:.1f}%")
    c4.metric("AI Güven Puanı", f"**{confidence:.1f}**")
    st.info(f"**Ana Karar (1X2):** {decision}")
    if analysis.get('reasons'):
        with st.expander("🕵️‍♂️ Tahminin Arkasındaki Nedenleri Gör"):
            for reason in analysis['reasons']: st.markdown(f"- {reason}")
    st.markdown("---")
    st.subheader("📊 Model Olasılıkları ve Piyasa Karşılaştırması")
    model_probs = [analysis['probs']['win_a'], analysis['probs']['draw'], analysis['probs']['win_b']]
    if odds_data:
        market_odds = [odds_data['home']['odd'], odds_data['draw']['odd'], odds_data['away']['odd']]
        market_probs = [odds_data['home']['prob'], odds_data['draw']['prob'], odds_data['away']['prob']]
        value_tags = ["✅ Değerli Oran!" if model_p > market_p + 5 else "" for model_p, market_p in zip(model_probs, market_probs)]
        comparison_df = pd.DataFrame({'Sonuç': [f"{name_a} Kazanır", "Beraberlik", f"{name_b} Kazanır"], 'Model Olasılığı (%)': model_probs, 'Piyasa Oranı': market_odds, 'Piyasa Olasılığı (%)': market_probs, 'Değer Analizi': value_tags})
        st.dataframe(comparison_df.style.format({'Model Olasılığı (%)': '{:.1f}', 'Piyasa Oranı': '{:.2f}', 'Piyasa Olasılığı (%)': '{:.1f}'}).apply(lambda x: ['background-color: #285238' if 'Değerli' in x.iloc[4] else '' for i in x], axis=1), hide_index=True, use_container_width=True)
    else:
        st.warning("Bu maç için oran verisi bulunamadı.")
        st.markdown("##### 🏆 Maç Sonu (1X2) Model Olasılıkları")
        chart_data = pd.DataFrame({'Olasılık (%)': {f'{name_a} K.': model_probs[0], 'Ber.': model_probs[1], f'{name_b} K.': model_probs[2]}})
        st.bar_chart(chart_data)
    st.markdown("---")
    st.subheader("⚽ Gol Piyasaları (Model Tahmini)")
    gol_data = pd.DataFrame({'Kategori': ['2.5 ÜST', '2.5 ALT', 'KG VAR', 'KG YOK'], 'İhtimal (%)': [analysis['probs']['ust_2.5'], analysis['probs']['alt_2.5'], analysis['probs']['kg_var'], analysis['probs']['kg_yok']]}).set_index('Kategori')
    st.dataframe(gol_data.style.format("{:.1f}"), use_container_width=True)

def display_stats_tab(stats: Dict, team_names: Dict, team_ids: Dict):
    name_a, name_b, id_a, id_b = team_names['a'], team_names['b'], team_ids['a'], team_ids['b']
    st.subheader("📊 İstatistiksel Karşılaştırma Grafiği (Radar)")
    stats_a_home = stats['a'].get('home', {}); stats_b_away = stats['b'].get('away', {})
    categories = ['Atılan Gol', 'Yenen Gol', 'İstikrar']
    values_a = [stats_a_home.get('Ort. Gol ATILAN', 0), stats_a_home.get('Ort. Gol YENEN', 0), stats_a_home.get('Istikrar_Puani', 0)]
    values_b = [stats_b_away.get('Ort. Gol ATILAN', 0), stats_b_away.get('Ort. Gol YENEN', 0), stats_b_away.get('Istikrar_Puani', 0)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values_a, theta=categories, fill='toself', name=f'{name_a} (Ev)'))
    fig.add_trace(go.Scatterpolar(r=values_b, theta=categories, fill='toself', name=f'{name_b} (Dep)'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=350, margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig, use_container_width=True)
    st.info("Not: 'Yenen Gol' metriğinde daha düşük değerler daha iyidir.")
    st.markdown("---")
    st.subheader("📈 Genel Form İstatistikleri ve Son Maçlar")
    col1_form, col2_form = st.columns(2)
    with col1_form:
        st.markdown(f"**{name_a} - Son 10 Maç Formu**")
        form_a = api_utils.get_team_form_sequence(API_KEY, BASE_URL, id_a)
        if form_a:
            results = [r['result'] for r in form_a]; colors = [{'G': 'green', 'B': 'gray', 'M': 'red'}[r] for r in results]
            hover_texts = [f"Rakip: {r['opponent']}<br>Skor: {r['score']}" for r in form_a]
            fig_a = go.Figure(data=go.Scatter(x=list(range(1, len(results) + 1)), y=results, mode='markers', marker=dict(color=colors, size=15), hoverinfo='text', hovertext=hover_texts))
            fig_a.update_layout(yaxis_title=None, xaxis_title="Oynanan Maçlar (Eskiden Yeniye)", height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_a, use_container_width=True)
    with col2_form:
        st.markdown(f"**{name_b} - Son 10 Maç Formu**")
        form_b = api_utils.get_team_form_sequence(API_KEY, BASE_URL, id_b)
        if form_b:
            results = [r['result'] for r in form_b]; colors = [{'G': 'green', 'B': 'gray', 'M': 'red'}[r] for r in results]
            hover_texts = [f"Rakip: {r['opponent']}<br>Skor: {r['score']}" for r in form_b]
            fig_b = go.Figure(data=go.Scatter(x=list(range(1, len(results) + 1)), y=results, mode='markers', marker=dict(color=colors, size=15), hoverinfo='text', hovertext=hover_texts))
            fig_b.update_layout(yaxis_title=None, xaxis_title="Oynanan Maçlar (Eskiden Yeniye)", height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_b, use_container_width=True)
    st.markdown("---")
    def format_stats(stat_dict):
        filtered_dict = {k: v for k, v in stat_dict.items() if k != 'team_specific_home_adv'}
        return {k.replace('_', ' ').title(): f"{v:.2f}" for k, v in filtered_dict.items()} if filtered_dict else {"Veri Yok": "-"}
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{name_a}**"); st.write("**Ev Sahibi Olarak:**"); st.dataframe(pd.Series(format_stats(stats['a'].get('home'))), use_container_width=True)
        st.write("**Deplasmanda Olarak:**"); st.dataframe(pd.Series(format_stats(stats['a'].get('away'))), use_container_width=True)
    with c2:
        st.markdown(f"**{name_b}**"); st.write("**Ev Sahibi Olarak:**"); st.dataframe(pd.Series(format_stats(stats['b'].get('home'))), use_container_width=True)
        st.write("**Deplasmanda Olarak:**"); st.dataframe(pd.Series(format_stats(stats['b'].get('away'))), use_container_width=True)

def display_injuries_tab(fixture_id: int, team_names: Dict, team_ids: Dict, league_info: Dict):
    st.subheader("❗ Maç Öncesi Önemli Eksikler")
    injuries, error = api_utils.get_fixture_injuries(API_KEY, BASE_URL, fixture_id)
    if error: 
        st.warning(f"Sakatlık verisi çekilemedi: {error}")
    elif not injuries: 
        st.success("✅ Takımlarda önemli bir eksik bildirilmedi.")
    else:
        team_a_inj = [p for p in injuries if p['team']['id'] == team_ids['a']]
        team_b_inj = [p for p in injuries if p['team']['id'] == team_ids['b']]
        season = league_info['season']
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{team_names['a']}**")
            if team_a_inj: 
                for p in team_a_inj:
                    player_id = p['player']['id']
                    player_stats_data, _ = api_utils.get_player_stats(API_KEY, BASE_URL, player_id, season)
                    stats_str = analysis_logic.process_player_stats(player_stats_data) or ""
                    st.warning(f"**{p['player']['name']}** - {p['player']['reason']}{stats_str}")
            else: 
                st.write("Eksik yok.")
        with c2:
            st.markdown(f"**{team_names['b']}**")
            if team_b_inj: 
                for p in team_b_inj:
                    player_id = p['player']['id']
                    player_stats_data, _ = api_utils.get_player_stats(API_KEY, BASE_URL, player_id, season)
                    stats_str = analysis_logic.process_player_stats(player_stats_data) or ""
                    st.warning(f"**{p['player']['name']}** - {p['player']['reason']}{stats_str}")
            else: 
                st.write("Eksik yok.")

def display_standings_tab(league_info: Dict, team_names: Dict):
    st.subheader("🏆 Lig Puan Durumu")
    standings_data, error = api_utils.get_league_standings(API_KEY, BASE_URL, league_info['league_id'], league_info['season'])
    if error: st.warning(f"Puan durumu çekilemedi: {error}")
    elif standings_data:
        df = pd.DataFrame(standings_data)[['rank', 'team', 'points', 'goalsDiff', 'form']].rename(columns={'rank':'Sıra', 'team':'Takım', 'points':'Puan', 'goalsDiff':'Averaj', 'form':'Form'})
        df['Takım'] = df['Takım'].apply(lambda x: x['name'])
        def highlight(row):
            if row.Takım == team_names['a']: return ['background-color: lightblue'] * len(row)
            if row.Takım == team_names['b']: return ['background-color: lightcoral'] * len(row)
            return [''] * len(row)
        st.dataframe(df.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
    else: st.warning("Bu lig için puan durumu verisi bulunamadı.")

def display_referee_tab(referee_stats: Optional[Dict]):
    st.subheader("⚖️ Hakem İstatistikleri")
    if referee_stats:
        st.info(f"Maçın hakemi: **{referee_stats['name']}**")
        if referee_stats.get('total_games') != "N/A":
            c1, c2, c3 = st.columns(3)
            c1.metric("Yönettiği Maç Sayısı", referee_stats['total_games'])
            c2.metric("Maç Başına Sarı Kart", f"{referee_stats['yellow_per_game']:.2f}")
            c3.metric("Maç Başına Kırmızı Kart", f"{referee_stats['red_per_game']:.2f}")
        else:
            st.warning("Bu hakemin detaylı istatistikleri bu sezon için bulunamadı.")
    else:
        st.warning("Bu maç için hakem bilgisi atanmamış veya bulunamadı.")

def display_h2h_tab(h2h_stats: Optional[Dict], team_names: Dict):
    st.subheader(f"⚔️ {team_names['a']} vs {team_names['b']}: Kafa Kafaya Analiz")
    if h2h_stats:
        summary = h2h_stats['summary']
        goals = h2h_stats['goals']
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Toplam Maç", summary['total_matches'])
        c2.metric(f"{team_names['a']} Galibiyeti", summary['wins_a'])
        c3.metric(f"{team_names['b']} Galibiyeti", summary['wins_b'])
        c4.metric("Beraberlik", summary['draws'])
        st.markdown("---")
        st.markdown("##### Gol İstatistikleri")
        goal_df = pd.DataFrame({'İstatistik': ['Toplam Gol', 'Maç Başına Gol'], team_names['a']: [goals['goals_a'], f"{goals['avg_goals_a']:.2f}"], team_names['b']: [goals['goals_b'], f"{goals['avg_goals_b']:.2f}"]}).set_index('İstatistik')
        st.table(goal_df)
        st.markdown("---")
        st.markdown("##### Son Karşılaşmalar")
        recent_matches_df = pd.DataFrame(h2h_stats['recent_matches'])
        st.dataframe(recent_matches_df, hide_index=True, use_container_width=True)
    else:
        st.warning("İki takım arasında geçmişe dönük karşılaşma verisi bulunamadı.")
        
def display_parameters_tab(params: Dict, team_names: Dict):
    st.subheader("⚙️ Modelin Kullandığı Parametreler")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**{team_names['a']} (Ev Sahibi)**")
        st.metric("Hibrit Hücum Gücü", f"{params['home_att']:.2f}", help="Takımın sezonluk ve son 10 maçlık formuna göre hesaplanan hücum gücü.")
        st.metric("Hibrit Savunma Gücü", f"{params['home_def']:.2f}", help="Takımın sezonluk ve son 10 maçlık formuna göre hesaplanan savunma gücü.")
    with c2:
        st.markdown(f"**{team_names['b']} (Deplasman)**")
        st.metric("Hibrit Hücum Gücü", f"{params['away_att']:.2f}")
        st.metric("Hibrit Savunma Gücü", f"{params['away_def']:.2f}")
    with c3:
        st.markdown("**Genel Parametreler**")
        st.metric("Lig Ort. Gol Sayısı", f"{params['avg_goals']:.2f}")
        st.metric("Dinamik Ev S. Avantajı", f"x{params['home_advantage']:.2f}", help="Ev sahibi takımın PBM istatistiklerine göre dinamik olarak hesaplanan avantaj katsayısı.")

def analyze_fixture_summary(fixture: Dict, model_params: Dict) -> Optional[Dict]:
    try:
        id_a, name_a, id_b, name_b = fixture['home_id'], fixture['home_name'], fixture['away_id'], fixture['away_name']
        league_info = api_utils.get_team_league_info(API_KEY, BASE_URL, id_a)
        if not league_info: return None
        analysis = analysis_logic.run_core_analysis(API_KEY, BASE_URL, id_a, id_b, name_a, name_b, fixture['match_id'], league_info, model_params, LIG_ORTALAMA_GOL)
        if not analysis: return None
        probs = analysis['probs']
        max_prob_key = max(probs, key=lambda k: probs[k] if 'win' in k or 'draw' in k else -1)
        decision = f"{name_a} K." if max_prob_key == 'win_a' else f"{name_b} K." if max_prob_key == 'win_b' else "Ber."
        result_icon, actual_score_str = "", fixture.get('actual_score', '')
        if actual_score_str:
            is_home_winner = fixture.get('winner_home')
            predicted_home_win = " K." in decision and name_a in decision; predicted_away_win = " K." in decision and name_b in decision; predicted_draw = "Ber." in decision
            actual_winner = 'home' if is_home_winner is True else 'away' if is_home_winner is False else 'draw'
            if (predicted_home_win and actual_winner == 'home') or (predicted_away_win and actual_winner == 'away') or (predicted_draw and actual_winner == 'draw'): result_icon = "✅"
            else: result_icon = "❌"
        return {"Saat": fixture['time'], "Lig": fixture['league_name'], "Ev Sahibi": name_a, "Deplasman": name_b, "Tahmin": decision, "Gerçekleşen Skor": actual_score_str, "Sonuç": result_icon, "AI Güven Puanı": analysis['confidence'], "2.5 ÜST (%)": probs['ust_2.5'], "KG VAR (%)": probs['kg_var'], "home_id": id_a, "away_id": id_b, "fixture_id": fixture['match_id']}
    except Exception: return None

def analyze_and_display(team_a_data: Dict, team_b_data: Dict, fixture_id: int, model_params: Dict):
    id_a, name_a, id_b, name_b = team_a_data['id'], team_a_data['name'], team_b_data['id'], team_b_data['name']
    st.header(f"⚽ {name_a} vs {name_b} Detaylı Analiz")
    league_info = api_utils.get_team_league_info(API_KEY, BASE_URL, id_a)
    if not league_info: st.error("Lig bilgisi alınamadı."); return
    analysis = analysis_logic.run_core_analysis(API_KEY, BASE_URL, id_a, id_b, name_a, name_b, fixture_id, league_info, model_params, LIG_ORTALAMA_GOL)
    if not analysis: st.error("Analiz verisi oluşturulamadı."); return

    with st.spinner("Ek veriler çekiliyor..."):
        odds_response, _ = api_utils.get_fixture_odds(API_KEY, BASE_URL, fixture_id)
        processed_odds = analysis_logic.process_odds_data(odds_response)
        fixture_details, _ = api_utils.get_fixture_details(API_KEY, BASE_URL, fixture_id)
        processed_referee_stats = None
        if fixture_details:
            referee_info = fixture_details.get('fixture', {}).get('referee')
            referee_id, referee_name_only = None, None
            if isinstance(referee_info, dict):
                referee_id = referee_info.get('id')
            elif isinstance(referee_info, str):
                referee_name_only = referee_info
            if referee_id:
                referee_data, _ = api_utils.get_referee_stats(API_KEY, BASE_URL, referee_id, league_info['season'])
                processed_referee_stats = analysis_logic.process_referee_data(referee_data)
            elif referee_name_only:
                processed_referee_stats = {"name": referee_name_only, "total_games": "N/A"}
        h2h_matches, _ = api_utils.get_h2h_matches(API_KEY, BASE_URL, id_a, id_b, H2H_MATCH_LIMIT)
        processed_h2h = analysis_logic.process_h2h_data(h2h_matches, id_a)

    team_names = {'a': name_a, 'b': name_b}; team_ids = {'a': id_a, 'b': id_b}
    tab_list = ["🎯 Tahmin Özeti", "📈 İstatistikler", "🚑 Eksikler", "📊 Puan Durumu", "⚔️ H2H Analizi", "⚖️ Hakem Analizi", "⚙️ Analiz Parametreleri"]
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_list)

    with tab1: display_summary_tab(analysis, team_names, processed_odds)
    with tab2: display_stats_tab(analysis['stats'], team_names, team_ids)
    with tab3: display_injuries_tab(fixture_id, team_names, team_ids, league_info)
    with tab4: display_standings_tab(league_info, team_names)
    with tab5: display_h2h_tab(processed_h2h, team_names)
    with tab6: display_referee_tab(processed_referee_stats)
    with tab7: display_parameters_tab(analysis['params'], team_names)

def build_dashboard_view(model_params: Dict):
    st.title("🗓️ Maç Panosu")
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_date = st.date_input("Tarih Seçin", value=date.today())
    with col2:
        leagues_map = {v: k for k, v in INTERESTING_LEAGUES.items()}
        default_leagues = st.session_state.get('favorite_leagues') or ["🇹🇷 Süper Lig", "🇬🇧 Premier League"]
        selected_names = st.multiselect("Analiz Edilecek Ligleri Seçin", options=list(INTERESTING_LEAGUES.values()), default=default_leagues)
    st.markdown(f"### {selected_date.strftime('%d %B %Y')} Maçları")
    st.markdown("---")
    if not selected_names: 
        st.warning("Lütfen analiz için yukarıdan en az bir lig seçin."); return
    selected_ids = [leagues_map[name] for name in selected_names]
    with st.spinner(f"Maçlar getiriliyor..."):
        fixtures, error = api_utils.get_fixtures_by_date(API_KEY, BASE_URL, selected_ids, selected_date)
    if error: st.error(f"Maçlar çekilirken bir hata oluştu:\n\n{error}"); return
    if not fixtures: st.info(f"Seçtiğiniz tarih ve liglerde maç bulunamadı."); return
    progress_bar = st.progress(0, text="Maçlar analiz ediliyor...")
    analyzed_fixtures = [summary for i, f in enumerate(fixtures) if (summary := analyze_fixture_summary(f, model_params)) and (progress_bar.progress((i + 1) / len(fixtures), f"Analiz: {f['home_name']}", ))]
    progress_bar.empty()
    if not analyzed_fixtures: st.error("Hiçbir maç analiz edilemedi."); return
    df = pd.DataFrame(analyzed_fixtures)
=======

BASE_URL = "https://v3.football.api-sports.io"

INTERESTING_LEAGUES = {
    203: "🇹🇷 Süper Lig", 39: "🇬🇧 Premier League", 140: "🇪🇸 La Liga",
    135: "🇮🇹 Serie A", 78: "🇩🇪 Bundesliga", 61: "🇫🇷 Ligue 1",
    88: "🇳🇱 Eredivisie", 94: "🇵🇹 Primeira Liga",
    204: "🇹🇷 TFF 1. Lig", 40: "🇬🇧 Championship", 141: "🇪🇸 La Liga 2",
    136: "🇮🇹 Serie B", 79: "🇩🇪 2. Bundesliga", 62: "🇫🇷 Ligue 2",
    89: "🇳🇱 Eerste Divisie", 95: "🇵🇹 Liga Portugal 2"
}

FORM_MATCH_LIMIT = 15
H2H_MATCH_LIMIT = 10
LIG_ORTALAMA_GOL = 1.35
DEFAULT_MAX_GOAL_EXPECTANCY = 3.0
DEFAULT_HOME_ADVANTAGE_MULTIPLIER = 1.15
DEFAULT_KEY_PLAYER_IMPACT_MULTIPLIER = 0.80
BEST_BET_THRESHOLD = 30.0

# --- GÖRÜNÜM FONKSİYONLARI ---

def analyze_fixture_summary(fixture, model_params: Dict):
    try:
        id_a, name_a, id_b, name_b = fixture['home_id'],fixture['home_name'],fixture['away_id'],fixture['away_name']
        league_info = api_utils.get_team_league_info(API_KEY, BASE_URL, id_a)
        if not league_info: return None
        analysis = analysis_logic.run_core_analysis(API_KEY, BASE_URL, id_a, id_b, fixture['match_id'], league_info, model_params, FORM_MATCH_LIMIT, LIG_ORTALAMA_GOL)
        if not analysis: return None
        probs, stats = analysis['probs'], analysis['stats']
        max_prob = max(probs, key=lambda k: probs[k] if 'win' in k or 'draw' in k else -1)
        decision = f"{name_a} K." if max_prob=='win_a' else f"{name_b} K." if max_prob=='win_b' else "Ber."
        result_icon, actual_score_str = "", fixture.get('actual_score', '')
        if actual_score_str:
            is_home_winner = fixture.get('winner_home')
            predicted_home_win = " K." in decision and name_a in decision
            predicted_away_win = " K." in decision and name_b in decision
            predicted_draw = "Ber." in decision
            actual_winner = 'home' if is_home_winner is True else 'away' if is_home_winner is False else 'draw'
            if (predicted_home_win and actual_winner == 'home') or \
               (predicted_away_win and actual_winner == 'away') or \
               (predicted_draw and actual_winner == 'draw'): result_icon = "✅"
            else: result_icon = "❌"
        total_corners = stats['a'].get('home', {}).get('Ort. Korner', 0) + stats['b'].get('away', {}).get('Ort. Korner', 0)
        total_cards = stats['a'].get('home', {}).get('Ort. Sarı Kart', 0) + stats['b'].get('away', {}).get('Ort. Sarı Kart', 0)
        return {"Saat":fixture['time'],"Lig":fixture['league_name'],"Ev Sahibi":name_a,"Deplasman":name_b,
                "Tahmin":decision,"Gerçekleşen Skor": actual_score_str, "Sonuç": result_icon,
                "AI Güven Puanı":analysis['confidence'],"2.5 ÜST (%)":probs['ust_2.5'],
                "KG VAR (%)":probs['kg_var'], "Ort. Korner": total_corners, "Ort. Sarı Kart": total_cards,
                "home_id":id_a,"away_id":id_b,"fixture_id":fixture['match_id']}
    except Exception: return None

def analyze_and_display(team_a_data, team_b_data, fixture_id, model_params: Dict):
    id_a,name_a,id_b,name_b = team_a_data['id'],team_a_data['name'],team_b_data['id'],team_b_data['name']
    st.header(f"⚽ {name_a} vs {name_b} Detaylı Analiz")
    league_info = api_utils.get_team_league_info(API_KEY, BASE_URL, id_a)
    if not league_info: st.error("Lig bilgisi alınamadı."); return
    analysis = analysis_logic.run_core_analysis(API_KEY, BASE_URL, id_a, id_b, fixture_id, league_info, model_params, FORM_MATCH_LIMIT, LIG_ORTALAMA_GOL)
    if not analysis: st.error("Analiz verisi oluşturulamadı."); return
    params, stats = analysis['params'], analysis['stats']
    values_list = list(analysis.values())
    score_a, score_b, probs, confidence, diff = values_list[:5]
    max_prob = max(probs, key=lambda k: probs[k] if 'win' in k or 'draw' in k else -1)
    decision = f"{name_a} Kazanır" if max_prob=='win_a' else f"{name_b} Kazanır" if max_prob=='win_b' else "Beraberlik"
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Tahmin Özeti", "📈 Takım İstatistikleri", "🚑 Sakat ve Cezalılar", "⚙️ Analiz Parametreleri", "📊 Puan Durumu", "⚔️ Kafa Kafaya (H2H)"])
    with tab1:
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Ev S. Gol Beklentisi", f"{score_a:.2f}"); c2.metric("Dep. Gol Beklentisi", f"{score_b:.2f}")
        c3.metric("Olasılık Farkı", f"{diff:.1f}%"); c4.metric("AI Güven Puanı", f"**{confidence:.1f}**")
        st.info(f"**Ana Karar (1X2):** {decision}")
        st.markdown("---"); st.subheader("📊 Maç Sonucu Olasılıkları")
        col_1x2, col_gol = st.columns([0.6, 0.4])
        with col_1x2:
            st.markdown("##### 🏆 Maç Sonu (1X2)"); chart_data = pd.DataFrame({'Olasılık (%)': {f'{name_a} K.': probs['win_a'], 'Ber.': probs['draw'], f'{name_b} K.': probs['win_b']}})
            st.bar_chart(chart_data)
        with col_gol:
            st.markdown("##### ⚽ Gol Piyasaları"); gol_data = pd.DataFrame({'Kategori': ['2.5 ÜST', '2.5 ALT', 'KG VAR', 'KG YOK'], 'İhtimal (%)': [probs['ust_2.5'], probs['alt_2.5'], probs['kg_var'], probs['kg_yok']]}).set_index('Kategori')
            st.dataframe(gol_data.T, use_container_width=True)
    with tab2:
        st.subheader("📊 İstatistiksel Karşılaştırma Grafiği (Radar)")
        stats_a_home = stats['a'].get('home', {}); stats_b_away = stats['b'].get('away', {})
        categories = ['Atılan Gol', 'Yenen Gol', 'Korner', 'Sarı Kart', 'İstikrar']
        values_a = [stats_a_home.get('Ort. Gol ATILAN', 0), stats_a_home.get('Ort. Gol YENEN', 0), stats_a_home.get('Ort. Korner', 0), stats_a_home.get('Ort. Sarı Kart', 0), stats_a_home.get('Istikrar_Puani', 0)]
        values_b = [stats_b_away.get('Ort. Gol ATILAN', 0), stats_b_away.get('Ort. Gol YENEN', 0), stats_b_away.get('Ort. Korner', 0), stats_b_away.get('Ort. Sarı Kart', 0), stats_b_away.get('Istikrar_Puani', 0)]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values_a, theta=categories, fill='toself', name=f'{name_a} (Ev)'))
        fig.add_trace(go.Scatterpolar(r=values_b, theta=categories, fill='toself', name=f'{name_b} (Dep)'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        st.info("Not: 'Yenen Gol' ve 'Sarı Kart' metriklerinde daha düşük değerler daha iyidir.")
        st.markdown("---")
        st.subheader("📈 Genel Form İstatistikleri ve Son Maçlar")
        col1_form, col2_form = st.columns(2)
        with col1_form:
            st.markdown(f"**{name_a} - Son 10 Maç Formu**")
            form_a = api_utils.get_team_form_sequence(API_KEY, BASE_URL, id_a)
            if form_a:
                y_values = [r['result'] for r in form_a]; colors = [{'G': 'green', 'B': 'gray', 'M': 'red'}[r] for r in y_values]
                hover_texts = [f"Rakip: {r['opponent']}<br>Skor: {r['score']}" for r in form_a]
                fig_a = go.Figure(data=go.Scatter(x=list(range(1, len(y_values) + 1)), y=y_values, mode='markers', marker=dict(color=colors, size=15), hoverinfo='text', hovertext=hover_texts))
                fig_a.update_layout(yaxis_title=None, xaxis_title="Oynanan Maçlar (Eskiden Yeniye)", height=250, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_a, use_container_width=True)
        with col2_form:
            st.markdown(f"**{name_b} - Son 10 Maç Formu**")
            form_b = api_utils.get_team_form_sequence(API_KEY, BASE_URL, id_b)
            if form_b:
                y_values = [r['result'] for r in form_b]; colors = [{'G': 'green', 'B': 'gray', 'M': 'red'}[r] for r in y_values]
                hover_texts = [f"Rakip: {r['opponent']}<br>Skor: {r['score']}" for r in form_b]
                fig_b = go.Figure(data=go.Scatter(x=list(range(1, len(y_values) + 1)), y=y_values, mode='markers', marker=dict(color=colors, size=15), hoverinfo='text', hovertext=hover_texts))
                fig_b.update_layout(yaxis_title=None, xaxis_title="Oynanan Maçlar (Eskiden Yeniye)", height=250, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_b, use_container_width=True)
        st.markdown("---")
        def format_stats(stat_dict):
            return {k.replace('_', ' ').title(): f"{v:.2f}" for k, v in stat_dict.items()} if stat_dict else {"Veri Yok": "-"}
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{name_a}**"); st.write("**Ev Sahibi Olarak:**"); st.dataframe(pd.Series(format_stats(stats['a'].get('home'))), use_container_width=True)
            st.write("**Deplasmanda Olarak:**"); st.dataframe(pd.Series(format_stats(stats['a'].get('away'))), use_container_width=True)
        with c2:
            st.markdown(f"**{name_b}**"); st.write("**Ev Sahibi Olarak:**"); st.dataframe(pd.Series(format_stats(stats['b'].get('home'))), use_container_width=True)
            st.write("**Deplasmanda Olarak:**"); st.dataframe(pd.Series(format_stats(stats['b'].get('away'))), use_container_width=True)
    with tab3:
        st.subheader("❗ Maç Öncesi Önemli Eksikler"); injuries, error = api_utils.get_fixture_injuries(API_KEY, BASE_URL, fixture_id)
        if error: st.warning(f"Sakatlık verisi çekilemedi: {error}")
        elif not injuries: st.success("✅ Takımlarda önemli bir eksik bildirilmedi.")
        else:
            team_a_inj=[p for p in injuries if p['team']['id']==id_a]; team_b_inj=[p for p in injuries if p['team']['id']==id_b]
            c1,c2=st.columns(2)
            with c1:
                st.markdown(f"**{name_a}**")
                if team_a_inj: 
                    for p in team_a_inj: st.warning(f"**{p['player']['name']}** - {p['player']['reason']}")
                else: st.write("Eksik yok.")
            with c2:
                st.markdown(f"**{name_b}**")
                if team_b_inj: 
                    for p in team_b_inj: st.warning(f"**{p['player']['name']}** - {p['player']['reason']}")
                else: st.write("Eksik yok.")
    with tab4:
        st.subheader("Modelin Kullandığı Parametreler"); c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{name_a} (Ev Sahibi)**"); st.metric("Ham Hücum Gücü", f"{params['home_att']:.2f}"); st.metric("Ham Savunma Gücü", f"{params['home_def']:.2f}")
            st.metric("Hücum Etki Katsayısı", f"{params['att_mult_a']:.2f}"); st.metric("Savunma Etki Katsayısı", f"x{params['def_mult_a']:.2f}")
        with c2:
            st.markdown(f"**{name_b} (Deplasman)**"); st.metric("Ham Hücum Gücü", f"{params['away_att']:.2f}"); st.metric("Ham Savunma Gücü", f"{params['away_def']:.2f}")
            st.metric("Hücum Etki Katsayısı", f"{params['att_mult_b']:.2f}"); st.metric("Savunma Etki Katsayısı", f"x{params['def_mult_b']:.2f}")
        st.metric("Lig Ortalaması", f"{params['avg_goals']:.2f} Gol/Maç")
    with tab5:
        st.subheader("🏆 Lig Puan Durumu"); standings_data, error = api_utils.get_league_standings(API_KEY, BASE_URL, league_info['league_id'], league_info['season'])
        if error: st.warning(f"Puan durumu çekilemedi: {error}")
        elif standings_data:
            df = pd.DataFrame(standings_data)[['rank', 'team', 'points', 'goalsDiff', 'form']].rename(columns={'rank':'Sıra', 'team':'Takım', 'points':'Puan', 'goalsDiff':'Averaj', 'form':'Form'})
            df['Takım'] = df['Takım'].apply(lambda x: x['name'])
            def highlight(row):
                if row.Takım == name_a: return ['background-color: lightblue']*len(row)
                if row.Takım == name_b: return ['background-color: lightcoral']*len(row)
                return ['']*len(row)
            st.dataframe(df.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
        else: st.warning("Bu lig için puan durumu verisi bulunamadı.")
    with tab6:
        st.subheader(f"⚔️ {name_a} vs {name_b}: Geçmiş Karşılaşmalar"); h2h_matches, error = api_utils.get_h2h_matches(API_KEY, BASE_URL, id_a, id_b, H2H_MATCH_LIMIT)
        if error: st.warning(f"H2H verisi çekilemedi: {error}")
        elif h2h_matches:
            w_a,w_b,d,g_a,g_b = 0,0,0,0,0
            for m in h2h_matches:
                s=m['score']['fulltime']
                if s['home'] is None: continue
                winner = m['teams']['home']['winner']
                if winner is True: w_a,w_b = (w_a+1,w_b) if m['teams']['home']['id']==id_a else (w_a,w_b+1)
                elif winner is False: w_b,w_a = (w_b+1,w_a) if m['teams']['home']['id']==id_a else (w_b,w_a+1)
                else: d+=1
                g_a += s['home'] if m['teams']['home']['id']==id_a else s['away']
                g_b += s['away'] if m['teams']['home']['id']==id_a else s['home']
            t=len(h2h_matches); c1,c2,c3,c4=st.columns(4)
            c1.metric("Toplam Maç",t); c2.metric(f"{name_a} G.",w_a); c3.metric(f"{name_b} G.",w_b); c4.metric("Ber.",d)
            df = pd.DataFrame({'İstatistik':['Toplam Gol','Ort. Gol'], name_a:[g_a, f"{g_a/t:.2f}"], name_b:[g_b, f"{g_b/t:.2f}"]}).set_index('İstatistik')
            st.table(df)
        else: st.warning("İki takım arasında geçmişe dönük karşılaşma verisi bulunamadı.")

def build_dashboard_view(model_params: Dict):
    selected_date = st.sidebar.date_input("Analiz için bir tarih seçin", value=date.today())
    st.title(f"🗓️ {selected_date.strftime('%d.%m.%Y')} Maç Panosu")
    leagues_map = {v: k for k, v in INTERESTING_LEAGUES.items()}
    selected_names = st.sidebar.multiselect("Analiz edilecek ligleri seçin:", options=list(INTERESTING_LEAGUES.values()), default=["🇹🇷 Süper Lig", "🇬🇧 Premier League"])
    if not selected_names:
        st.warning("Lütfen analiz için kenar çubuğundan en az bir lig seçin."); return
    selected_ids = [leagues_map[name] for name in selected_names]
    with st.spinner(f"{selected_date.strftime('%d.%m.%Y')} tarihindeki maçlar getiriliyor..."):
        fixtures, error = api_utils.get_fixtures_by_date(API_KEY, BASE_URL, selected_ids, selected_date)
    if error: st.error(f"Maçlar çekilirken bir hata oluştu:\n\n{error}"); return
    if not fixtures: st.warning(f"{selected_date.strftime('%d.%m.%Y')} tarihi için seçtiğiniz liglerde maç bulunamadı."); return
    progress_bar = st.progress(0, text="Maçlar analiz ediliyor...")
    analyzed = [summary for i, f in enumerate(fixtures) if (summary := analyze_fixture_summary(f, model_params)) and (progress_bar.progress((i+1)/len(fixtures), f"Analiz: {f['home_name']}"))]
    progress_bar.empty()
    if not analyzed: st.error("Hiçbir maç analiz edilemedi."); return
    df = pd.DataFrame(analyzed)
>>>>>>> 022d0ad2125e10a505d9177179a42170fc80c60f
    if not df.empty and selected_date >= date.today():
        best_bet = df.loc[df['AI Güven Puanı'].idxmax()]
        if best_bet['AI Güven Puanı'] > BEST_BET_THRESHOLD:
            st.subheader("🏆 Günün Öne Çıkan Tahmini")
            with st.container(border=True):
<<<<<<< HEAD
                c1, c2, c3 = st.columns(3); c1.metric("Maç", f"{best_bet['Ev Sahibi']} vs {best_bet['Deplasman']}"); c2.metric("Tahmin", best_bet['Tahmin']); c3.metric("AI Güven Puanı", f"{best_bet['AI Güven Puanı']:.1f}")
            st.markdown("---")
    if selected_date < date.today() and 'Sonuç' in df.columns and not df.empty:
        success_count = df['Sonuç'].str.contains('✅').sum(); total_matches = len(df)
        accuracy = (success_count / total_matches) * 100 if total_matches > 0 else 0
        st.metric("Günlük Tahmin Başarısı", f"{accuracy:.1f}%", f"{success_count} / {total_matches} doğru tahmin")
=======
                c1, c2, c3 = st.columns(3)
                c1.metric("Maç", f"{best_bet['Ev Sahibi']} vs {best_bet['Deplasman']}")
                c2.metric("Tahmin", best_bet['Tahmin'])
                c3.metric("AI Güven Puanı", f"{best_bet['AI Güven Puanı']:.1f}")
            st.markdown("---")
    if selected_date < date.today():
        if 'Sonuç' in df.columns and not df.empty:
            success_count = df['Sonuç'].str.contains('✅').sum()
            total_matches = len(df)
            accuracy = (success_count / total_matches) * 100 if total_matches > 0 else 0
            st.metric("Günlük Tahmin Başarısı", f"{accuracy:.1f}%", f"{success_count} / {total_matches} doğru tahmin")
>>>>>>> 022d0ad2125e10a505d9177179a42170fc80c60f
        st.markdown("---")
    st.subheader("📋 Analiz Sonuçları")
    cols_to_display = ["Saat", "Lig", "Ev Sahibi", "Deplasman", "Tahmin", "AI Güven Puanı"]
    if 'Gerçekleşen Skor' in df.columns and not df['Gerçekleşen Skor'].eq('').all():
<<<<<<< HEAD
        cols_to_display.insert(5, "Gerçekleşen Skor"); cols_to_display.insert(6, "Sonuç")
    st.dataframe(df.sort_values("AI Güven Puanı", ascending=False)[cols_to_display], use_container_width=True, hide_index=True)
    st.markdown("---")
    st.subheader("🔍 Detaylı Maç Analizi")
    options = [f"{r['Saat']} | {r['Lig']} | {r['Ev Sahibi']} vs {r['Deplasman']}" for _, r in df.iterrows()]
    selected = st.selectbox("Detaylı analiz için maç seçin:", options, index=None, placeholder="Tablodan bir maç seçin...")
    if selected:
        row = df[df.apply(lambda r: f"{r['Saat']} | {r['Lig']} | {r['Ev Sahibi']} vs {r['Deplasman']}" == selected, axis=1)].iloc[0]
        team_a, team_b = {'id': row['home_id'], 'name': row['Ev Sahibi']}, {'id': row['away_id'], 'name': row['Deplasman']}
        with st.spinner(f"**{team_a['name']} vs {team_b['name']}** analizi yapılıyor..."):
            analyze_and_display(team_a, team_b, row['fixture_id'], model_params)
=======
        cols_to_display.insert(5, "Gerçekleşen Skor")
        cols_to_display.insert(6, "Sonuç")
    st.dataframe(df.sort_values("AI Güven Puanı",ascending=False)[cols_to_display], use_container_width=True,hide_index=True)
    st.markdown("---"); st.subheader("🎯 Günün Favorileri")
    c1,c2 = st.columns(2)
    with c1: st.markdown("##### Yüksek 2.5 Üst Olasılıkları"); st.dataframe(df.sort_values("2.5 ÜST (%)",ascending=False).head(5)[['Ev Sahibi','Deplasman','2.5 ÜST (%)']], use_container_width=True,hide_index=True)
    with c2: st.markdown("##### Yüksek KG Var Olasılıkları"); st.dataframe(df.sort_values("KG VAR (%)",ascending=False).head(5)[['Ev Sahibi','Deplasman','KG VAR (%)']], use_container_width=True,hide_index=True)
    c3,c4 = st.columns(2)
    with c3:
        st.markdown("##### En Yüksek Ortalama Korner"); df_corners = df.sort_values("Ort. Korner", ascending=False).head(5)
        st.dataframe(df_corners[['Ev Sahibi', 'Deplasman', 'Ort. Korner']].style.format({"Ort. Korner": "{:.2f}"}), use_container_width=True, hide_index=True)
    with c4:
        st.markdown("##### En Yüksek Ortalama Sarı Kart"); df_cards = df.sort_values("Ort. Sarı Kart", ascending=False).head(5)
        st.dataframe(df_cards[['Ev Sahibi', 'Deplasman', 'Ort. Sarı Kart']].style.format({"Ort. Sarı Kart": "{:.2f}"}), use_container_width=True, hide_index=True)
    st.markdown("---"); st.subheader("🔍 Detaylı Maç Analizi")
    options = [f"{r['Saat']} | {r['Lig']} | {r['Ev Sahibi']} vs {r['Deplasman']}" for _,r in df.iterrows()]
    selected = st.selectbox("Detaylı analiz için maç seçin:", options, index=None, placeholder="Tablodan bir maç seçin...")
    if selected:
        row = df[df.apply(lambda r: f"{r['Saat']} | {r['Lig']} | {r['Ev Sahibi']} vs {r['Deplasman']}" == selected, axis=1)].iloc[0]
        team_a,team_b = {'id':row['home_id'],'name':row['Ev Sahibi']},{'id':row['away_id'],'name':row['Deplasman']}
        with st.spinner(f"**{team_a['name']} vs {team_b['name']}** analizi yapılıyor..."):
            analyze_and_display(team_a,team_b,row['fixture_id'], model_params)
>>>>>>> 022d0ad2125e10a505d9177179a42170fc80c60f

def build_manual_view(model_params: Dict):
    st.title("🔩 Manuel Takım Analizi")
    c1,c2 = st.columns(2)
    t1_in,t2_in = c1.text_input("Ev Sahibi Takım (Ad/ID)"), c2.text_input("Deplasman Takımı (Ad/ID)")
    if st.button("Analizi Başlat", use_container_width=True):
        if not t1_in or not t2_in: st.warning("Lütfen iki takımı da girin."); return
        team_a,team_b = api_utils.get_team_id(API_KEY, BASE_URL, t1_in), api_utils.get_team_id(API_KEY, BASE_URL, t2_in)
        if team_a and team_b:
            with st.spinner('Maç aranıyor...'):
                info = api_utils.get_team_league_info(API_KEY, BASE_URL, team_a['id'])
                if not info: st.error(f"{team_a['name']} için sezon bilgisi yok."); return
                match, error = api_utils.find_upcoming_fixture(API_KEY, BASE_URL, team_a['id'], team_b['id'], info['season'])
            if error: st.error(f"Maç aranırken hata oluştu: {error}")
            elif match:
                st.success(f"✅ Maç bulundu! Tarih: {datetime.fromtimestamp(match['fixture']['timestamp']).strftime('%d.%m.%Y')}")
                with st.spinner('Detaylı analiz yapılıyor...'):
                    analyze_and_display(team_a, team_b, match['fixture']['id'], model_params)
            else: st.error("Bu iki takım arasında yakın zamanda maç bulunamadı.")
        else: st.error("Takımlar bulunamadı.")

<<<<<<< HEAD
def main():
    if 'view' not in st.session_state: st.session_state.view = 'home'
    if 'favorite_leagues' not in st.session_state: st.session_state.favorite_leagues = None

    st.sidebar.title("⚽ Futbol Analiz Motoru"); st.sidebar.markdown("---")
    
    with st.sidebar.expander("⭐ Favori Ligleri Yönet"):
        all_leagues = list(INTERESTING_LEAGUES.values())
        current_favorites = st.session_state.get('favorite_leagues') or []
        new_favorites = st.multiselect("Favori liglerinizi seçin:", options=all_leagues, default=current_favorites)
        if st.button("Favorileri Kaydet", key="save_fav"):
            st.session_state.favorite_leagues = new_favorites
            st.success("Favoriler kaydedildi!")
            st.rerun()

    if st.sidebar.button("Maç Panosu", use_container_width=True): st.session_state.view = 'dashboard'
    if st.sidebar.button("Manuel Analiz", use_container_width=True): st.session_state.view = 'manual'
    
    st.sidebar.markdown("---")
    
    with st.sidebar.expander("⚙️ Model Ayarlarını Değiştir"):
        injury_impact = st.slider("Kilit Oyuncu Etkisi", 0.5, 1.0, DEFAULT_KEY_PLAYER_IMPACT_MULTIPLIER, 0.05, help="Sakat veya cezalı olan kilit oyuncuların (en golcü, en çok süre alan) maça etkisini ayarlar. 1.0 = Etki yok, 0.5 = Maksimum etki.")
        max_goals = st.slider("Maksimum Gol Beklentisi", 2.0, 5.0, DEFAULT_MAX_GOAL_EXPECTANCY, 0.1, help="Tek bir takım için hesaplanabilecek en yüksek gol beklentisi. Aşırı skorları önler.")
    
    model_params = {"injury_impact": injury_impact, "max_goals": max_goals}
    
    st.sidebar.info("Temayı değiştirmek için sağ üstteki menüden (☰) 'Settings' bölümünü kullanabilirsiniz.")
    
    with st.sidebar.expander("🤔 Neden Bize Güvenmelisiniz?"):
        st.markdown("""
        Modelimizin zaman zaman bahis piyasasının favorisiyle aynı fikirde olmaması, aslında "hatalı" olduğu anlamına gelmez. Bu durum, modelimizin en değerli özelliğini ortaya çıkarır: **piyasadan farklı ve veriye dayalı bir bakış açısı sunma potansiyelini.**

        #### Bahis Oranları Neyi Yansıtır?
        Bahis oranları sadece istatistik değil, aynı zamanda şunların bir karışımıdır:
        * **Topluluğun Beklentisi:** Popüler takımlar, form durumlarından bağımsız olarak daha çok bahis alır ve bu da oranlarını düşürür.
        * **Soyut Bilgiler:** Takım içi huzursuzluk, moral durumu gibi modelimizin göremediği haberler.
        * **Risk Yönetimi:** Bahis şirketlerinin kar marjları.

        #### Bizim Modelimiz Neyi Yansıtır?
        Modelimiz bir "matematikçi" gibi davranır; popülerliğe veya duygulara değil, sadece ve sadece sayılara bakar:
        * **Veri Odaklılık:** Ağırlıklı form, PBM'ye dayalı ev sahibi avantajı, gol ortalamaları gibi ölçülebilir verilere dayanır.
        * **Tarafsızlık:** Modelin bir takıma karşı ön yargısı yoktur. İstatistikler ne gösteriyorsa onu sunar.
        * **"Değer" Arayışı:** Modelimizin asıl amacı, piyasanın gözden kaçırdığı veya yanlış fiyatladığı **değerli oranları** tespit etmektir. Bir tahminin oranlara göre "saçma" görünmesi, genellikle istatistiksel bir fırsata işaret eder.
        """)
        st.info("""
        **'Ana Karar' ve 'Değerli Oran' Farkı Nedir?**
        * **Ana Karar**, modelimizin istatistiksel olarak **en olası** gördüğü sonuçtur (en yüksek yüzde).
        * **Değerli Oran**, kazanma ihtimali en yüksek olan değil, **piyasa oranlarına kıyasla en karlı olan** fırsattır. Modelimizin olasılığının, piyasanın ima ettiği olasılıktan anlamlı şekilde yüksek olduğu durumları işaret eder.
        """)
=======
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Futbol Analiz Motoru")
    if 'view' not in st.session_state:
        st.session_state.view = 'home'

    st.sidebar.title("⚽ Futbol Analiz Motoru"); st.sidebar.markdown("---")
    
    if st.sidebar.button("Maç Panosu", use_container_width=True):
        st.session_state.view = 'dashboard'
    
    if st.sidebar.button("Manuel Analiz", use_container_width=True):
        st.session_state.view = 'manual'
    
    with st.sidebar.expander("⚙️ Model Ayarlarını Değiştir"):
        home_adv = st.slider("Ev Sahibi Avantajı", 1.0, 1.5, DEFAULT_HOME_ADVANTAGE_MULTIPLIER, 0.01)
        injury_impact = st.slider("Kilit Oyuncu Etkisi", 0.5, 1.0, DEFAULT_KEY_PLAYER_IMPACT_MULTIPLIER, 0.05)
        max_goals = st.slider("Maksimum Gol Beklentisi", 2.0, 5.0, DEFAULT_MAX_GOAL_EXPECTANCY, 0.1)
    
    model_params = {"home_adv": home_adv, "injury_impact": injury_impact, "max_goals": max_goals}
>>>>>>> 022d0ad2125e10a505d9177179a42170fc80c60f

    if st.session_state.view == 'home':
        st.title(" Futbol Analiz Motoruna Hoş Geldiniz!")
        st.info("Analize başlamak için lütfen kenar çubuğundan bir mod seçin.")
<<<<<<< HEAD
        st.markdown("Kenar çubuğundaki **'🤔 Neden Bize Güvenmelisiniz?'** bölümünü okuyarak modelimizin çalışma felsefesi hakkında bilgi alabilirsiniz.")
    elif st.session_state.view == 'dashboard': 
        build_dashboard_view(model_params)
    elif st.session_state.view == 'manual': 
        build_manual_view(model_params)

if __name__ == "__main__":
    main()
=======
    
    elif st.session_state.view == 'dashboard':
        build_dashboard_view(model_params)

    elif st.session_state.view == 'manual':
        build_manual_view(model_params)
>>>>>>> 022d0ad2125e10a505d9177179a42170fc80c60f
