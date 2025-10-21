# init_complete_elo.py
# API'DEKİ TÜM TAKIMLARI ÇEK VE ELO EKLE - TAM KAPSAM

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

def fetch_all_countries(api_key, base_url):
    """API'den tüm ülkeleri çek"""
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    print("🌍 API'den tüm ülkeler çekiliyor...")
    
    try:
        url = f"{base_url}/countries"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            countries = []
            
            if data.get('response'):
                for country in data['response']:
                    if country.get('name'):
                        countries.append(country['name'])
            
            print(f"✅ {len(countries)} ülke bulundu!")
            return countries
        else:
            print(f"❌ HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Hata: {e}")
        return []

def fetch_all_teams_from_country(api_key, base_url, country):
    """Bir ülkedeki TÜM takımları çek"""
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    teams = []
    
    try:
        url = f"{base_url}/teams"
        params = {'country': country}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('response'):
                for team_data in data['response']:
                    team = team_data['team']
                    teams.append({
                        'id': str(team['id']),
                        'name': team['name'],
                        'country': country
                    })
        
        return teams
        
    except Exception as e:
        return []

def determine_base_rating(country):
    """Ülkeye göre temel rating belirle"""
    
    # Elite ülkeler
    if country in ['England', 'Spain', 'Germany', 'Italy', 'France']:
        return 1700
    
    # Üst seviye
    elif country in ['Turkey', 'Portugal', 'Netherlands', 'Belgium', 'Brazil', 'Argentina']:
        return 1600
    
    # Orta-üst seviye
    elif country in ['Russia', 'Scotland', 'Austria', 'Switzerland', 'Denmark', 
                     'Norway', 'Sweden', 'Greece', 'Poland', 'Czech-Republic',
                     'Mexico', 'USA', 'Uruguay', 'Colombia', 'Chile']:
        return 1550
    
    # Orta seviye
    elif country in ['Croatia', 'Serbia', 'Ukraine', 'Romania', 'Bulgaria',
                     'Hungary', 'Israel', 'Japan', 'South-Korea', 'Australia',
                     'Saudi-Arabia', 'UAE', 'Qatar', 'Egypt', 'Morocco', 
                     'Algeria', 'Tunisia', 'South-Africa']:
        return 1500
    
    # Alt seviye
    else:
        return 1450

def main():
    print("="*70)
    print("🌍 KAPSAMLI ELO RATING İNİSİYALİZASYONU")
    print("="*70)
    print()
    
    # API bilgilerini al
    api_key, base_url = get_api_credentials()
    if not api_key:
        return
    
    # Tüm ülkeleri çek
    countries = fetch_all_countries(api_key, base_url)
    if not countries:
        print("❌ Ülkeler çekilemedi!")
        return
    
    print(f"\n📡 {len(countries)} ülkeden takımlar çekiliyor...")
    print("⚠️ Bu işlem 10-15 dakika sürebilir!\n")
    
    all_teams = {}
    country_count = 0
    
    for i, country in enumerate(countries, 1):
        try:
            print(f"[{i}/{len(countries)}] {country:30s}", end=" ", flush=True)
            
            teams = fetch_all_teams_from_country(api_key, base_url, country)
            
            if teams:
                base_rating = determine_base_rating(country)
                
                for team in teams:
                    team_id = team['id']
                    all_teams[team_id] = {
                        'name': team['name'],
                        'rating': base_rating,
                        'country': country
                    }
                
                print(f"✅ {len(teams)} takım")
                country_count += 1
            else:
                print("⚠️ Takım yok")
            
            # Rate limiting
            time.sleep(0.3)
            
            # Her 50 ülkede bir durum raporu
            if i % 50 == 0:
                print(f"\n📊 İlerleme: {len(all_teams)} takım toplandı\n")
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            continue
    
    print("\n" + "="*70)
    print(f"✅ {country_count} ülkeden toplam {len(all_teams)} takım çekildi!")
    print("="*70)
    
    # Elite takımları güncelle
    print("\n⚙️ Elite takım rating'leri güncelleniyor...")
    
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
        '210': 1810,  # Porto
        '645': 1700,  # Galatasaray
        '643': 1690,  # Fenerbahçe
        '641': 1670,  # Beşiktaş (ID 641)
        '607': 1570,  # Konyaspor
        '549': 1670,  # Beşiktaş (ID 549)
        '644': 1620,  # Trabzonspor
    }
    
    for team_id, elite_rating in ELITE_TEAMS.items():
        if team_id in all_teams:
            all_teams[team_id]['rating'] = elite_rating
    
    # Kaydet
    print("\n💾 Elo ratings dosyasına kaydediliyor...")
    
    ratings = {}
    timestamp = datetime.utcnow().isoformat()
    
    for team_id, team_info in all_teams.items():
        ratings[team_id] = {
            'rating': team_info['rating'],
            'last_updated': timestamp
        }
    
    with open('elo_ratings.json', 'w', encoding='utf-8') as f:
        json.dump(ratings, f, indent=4, ensure_ascii=False)
    
    print("\n" + "="*70)
    print(f"✅ BAŞARILI! {len(ratings)} takım için Elo rating oluşturuldu!")
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
        if team_id in all_teams:
            team = all_teams[team_id]
            print(f"  {expected_name:20s} (ID: {team_id:5s}) → {team['rating']} Elo")
    
    print("-" * 70)
    
    # İstatistikler
    print("\n📈 Ülke Bazında İstatistikler:")
    country_stats = {}
    for team_id, team_info in all_teams.items():
        country = team_info['country']
        country_stats[country] = country_stats.get(country, 0) + 1
    
    top_countries = sorted(country_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for country, count in top_countries:
        print(f"  {country:30s} → {count} takım")
    
    print("\n✨ Şimdi Streamlit uygulamanızı yeniden başlatın!")

if __name__ == '__main__':
    main()
