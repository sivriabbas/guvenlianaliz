# init_all_teams_elo.py
# TÜM DÜNYA TAKIMLARINI API'DEN ÇEK VE ELO EKLE

import json
import toml
import os
from datetime import datetime
import requests
import time

def get_api_credentials():
    """API anahtarını secrets.toml'dan oku"""
    try:
        secrets_path = os.path.join('.streamlit', 'secrets.toml')
        secrets = toml.load(secrets_path)
        return secrets["API_KEY"], "https://v3.football.api-sports.io"
    except Exception as e:
        print(f"❌ Hata: API anahtarı okunamadı: {e}")
        return None, None

def fetch_all_leagues(api_key, base_url):
    """API'den TÜM aktif ligleri çek"""
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    print("📡 API'den tüm ligler çekiliyor...")
    
    try:
        url = f"{base_url}/leagues"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            leagues = []
            
            if data.get('response'):
                for item in data['response']:
                    league = item['league']
                    country = item['country']
                    seasons = item.get('seasons', [])
                    
                    # 2024 sezonuna sahip aktif ligleri seç
                    has_2024 = any(s['year'] == 2024 for s in seasons)
                    if has_2024:
                        leagues.append({
                            'id': league['id'],
                            'name': league['name'],
                            'country': country['name'],
                            'type': league['type']
                        })
            
            print(f"✅ {len(leagues)} aktif lig bulundu!")
            return leagues
        else:
            print(f"❌ HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Hata: {e}")
        return []

def fetch_all_teams_from_leagues(api_key, base_url):
    """TÜM liglerden TÜM takımları çek"""
    
    # Öncelikli ligler (daha yüksek rating)
    PRIORITY_LEAGUES = {
        # Avrupa Top 5
        39: ("Premier League", 1750),
        140: ("La Liga", 1750), 
        78: ("Bundesliga", 1750),
        135: ("Serie A", 1750),
        61: ("Ligue 1", 1750),
        
        # Türkiye
        203: ("Süper Lig", 1600),
        
        # Diğer önemli ligler
        94: ("Primeira Liga", 1650),
        88: ("Eredivisie", 1650),
        144: ("Belgian Pro League", 1600),
        235: ("Premier League (Russia)", 1600),
        
        # Güney Amerika
        71: ("Série A (Brazil)", 1700),
        128: ("Primera División (Argentina)", 1700),
        
        # Diğer
        188: ("Ligue 1 (Algeria)", 1500),
        307: ("Saudi Pro League", 1550),
        113: ("J1 League", 1550),
        253: ("MLS", 1550),
        
        # Avrupa diğer
        103: ("Eliteserien (Norway)", 1500),
        119: ("Superliga (Denmark)", 1500),
        113: ("Allsvenskan (Sweden)", 1500),
        
        # İkinci seviye ligler
        40: ("Championship", 1550),
        141: ("La Liga 2", 1500),
        79: ("2. Bundesliga", 1550),
    }
    
    teams = {}
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    print(f"\n🌍 {len(PRIORITY_LEAGUES)} öncelikli ligden takımlar çekiliyor...\n")
    
    for league_id, (league_name, base_rating) in PRIORITY_LEAGUES.items():
        try:
            print(f"📥 {league_name} (ID: {league_id})...", end=" ", flush=True)
            
            url = f"{base_url}/teams"
            params = {
                'league': league_id,
                'season': 2024
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('response'):
                    league_teams = data['response']
                    for team_data in league_teams:
                        team = team_data['team']
                        team_id = str(team['id'])
                        team_name = team['name']
                        
                        teams[team_id] = {
                            'name': team_name,
                            'rating': base_rating,
                            'league': league_name,
                            'league_id': league_id
                        }
                    
                    print(f"✅ {len(league_teams)} takım")
                else:
                    print("⚠️ Veri yok")
            else:
                print(f"❌ HTTP {response.status_code}")
            
            # Rate limiting için bekleme
            time.sleep(0.4)
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            continue
    
    print(f"\n📊 Öncelikli liglerden toplam {len(teams)} takım çekildi!")
    
    # ŞİMDİ EKRANDA GÖRÜNEN TÜM FİKSTÜRLERDEN TAKIMLARI ÇEK
    print("\n🔍 Bugünün tüm fikstürlerinden takımları çekiyorum...")
    
    try:
        from datetime import date
        today = date.today().isoformat()
        
        url = f"{base_url}/fixtures"
        params = {'date': today}
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get('response', [])
            
            print(f"✅ Bugün {len(fixtures)} maç bulundu!")
            
            new_teams = 0
            for fixture in fixtures:
                home = fixture['teams']['home']
                away = fixture['teams']['away']
                league_id = fixture['league']['id']
                
                # Ev sahibi takım
                home_id = str(home['id'])
                if home_id not in teams:
                    teams[home_id] = {
                        'name': home['name'],
                        'rating': 1500,  # Default rating
                        'league': fixture['league']['name'],
                        'league_id': league_id
                    }
                    new_teams += 1
                
                # Deplasman takımı
                away_id = str(away['id'])
                if away_id not in teams:
                    teams[away_id] = {
                        'name': away['name'],
                        'rating': 1500,  # Default rating
                        'league': fixture['league']['name'],
                        'league_id': league_id
                    }
                    new_teams += 1
            
            print(f"✅ Bugünün maçlarından {new_teams} yeni takım eklendi!")
            
    except Exception as e:
        print(f"⚠️ Fikstür çekme hatası: {e}")
    
    return teams

def calculate_team_ratings(teams):
    """Takım kalitesine göre rating'leri ayarla"""
    
    # Elite takımlar (manuel ayarlama)
    ELITE_TEAMS = {
        '50': 1920,   # Man City
        '33': 1900,   # Man United
        '40': 1890,   # Liverpool
        '42': 1860,   # Arsenal
        '49': 1850,   # Chelsea
        
        '541': 1950,  # Real Madrid
        '529': 1930,  # Barcelona
        '530': 1850,  # Atletico Madrid
        
        '157': 1920,  # Bayern Munich
        '165': 1830,  # Dortmund
        
        '489': 1870,  # AC Milan
        '487': 1880,  # Juventus
        '505': 1870,  # Inter
        '492': 1860,  # Napoli
        
        '85': 1900,   # PSG
        
        '212': 1800,  # Ajax
        '211': 1790,  # PSV
        
        '228': 1800,  # Sporting CP
        '211': 1810,  # Porto
        '210': 1790,  # Benfica
        
        # Türkiye
        '645': 1700,  # Galatasaray
        '643': 1690,  # Fenerbahçe
        '641': 1670,  # Beşiktaş
        '607': 1570,  # Konyaspor (doğru ID)
        '549': 1670,  # Beşiktaş (alternatif ID)
        '644': 1620,  # Trabzonspor
    }
    
    # Elite takımları güncelle
    for team_id, elite_rating in ELITE_TEAMS.items():
        if team_id in teams:
            teams[team_id]['rating'] = elite_rating
    
    return teams

def save_elo_ratings(teams):
    """Elo ratings'i JSON dosyasına kaydet"""
    
    ratings = {}
    timestamp = datetime.utcnow().isoformat()
    
    for team_id, team_info in teams.items():
        ratings[team_id] = {
            'rating': team_info['rating'],
            'last_updated': timestamp
        }
    
    # Dosyaya yaz
    with open('elo_ratings.json', 'w', encoding='utf-8') as f:
        json.dump(ratings, f, indent=4, ensure_ascii=False)
    
    return len(ratings)

def main():
    print("="*70)
    print("🌍 DÜNYA TAKIMLARI ELO RATING İNİSİYALİZASYONU")
    print("="*70)
    print()
    
    # API bilgilerini al
    api_key, base_url = get_api_credentials()
    if not api_key:
        return
    
    # Takımları çek
    print("📡 API'den takımlar çekiliyor...\n")
    teams = fetch_all_teams_from_leagues(api_key, base_url)
    
    if not teams:
        print("❌ Hiç takım çekilemedi!")
        return
    
    print(f"\n✅ Toplam {len(teams)} takım çekildi!")
    
    # Rating'leri ayarla
    print("\n⚙️ Takım kalitelerine göre rating'ler ayarlanıyor...")
    teams = calculate_team_ratings(teams)
    
    # Kaydet
    print("\n💾 Elo ratings dosyasına kaydediliyor...")
    total_saved = save_elo_ratings(teams)
    
    print("\n" + "="*70)
    print(f"✅ BAŞARILI! {total_saved} takım için Elo rating oluşturuldu!")
    print("="*70)
    print()
    
    # Örnek takımları göster
    print("📊 Örnek Rating'ler:")
    print("-" * 70)
    sample_teams = [
        ('50', 'Man City'),
        ('541', 'Real Madrid'),
        ('157', 'Bayern Munich'),
        ('645', 'Galatasaray'),
        ('607', 'Konyaspor'),
        ('549', 'Beşiktaş')
    ]
    
    for team_id, expected_name in sample_teams:
        if team_id in teams:
            team = teams[team_id]
            print(f"  {expected_name:20s} (ID: {team_id:5s}) → {team['rating']} Elo")
    
    print("-" * 70)
    print("\n✨ Şimdi Streamlit uygulamanızı yeniden başlatın!")

if __name__ == '__main__':
    main()
