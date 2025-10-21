# update_elo.py

from datetime import date, timedelta
import api_utils
import elo_utils
import os
import toml
from datetime import datetime

# GitHub Actions için app.py bağımlılığını kaldır
INTERESTING_LEAGUES = {
    # Popüler Avrupa 1. Ligleri
    39: "🇬🇧 Premier League", 140: "🇪🇸 La Liga", 135: "🇮🇹 Serie A", 
    78: "🇩🇪 Bundesliga", 61: "🇫🇷 Ligue 1", 203: "🇹🇷 Süper Lig",
    88: "🇳🇱 Eredivisie", 94: "🇵🇹 Primeira Liga", 144: "🇧🇪 Pro League",
    106: "🇷🇺 Premier League", 197: "🇬🇷 Super League", 169: "🇵🇱 Ekstraklasa",
    # Diğer ligler...
    2: "🏆 UEFA Champions League", 3: "🏆 UEFA Europa League", 848: "🏆 UEFA Conference League",
}

def run_elo_update():
    """Elo reytinglerini güncelleyen ana fonksiyon."""
    print("Elo reyting güncelleme betiği başlatıldı...")
    
    # API anahtarını ve URL'yi al (secrets.toml dosyasını manuel okuyarak)
    try:
        # Betiğin çalıştığı dizine göre secrets.toml dosyasının yolunu bul
        secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
        secrets = toml.load(secrets_path)
        API_KEY = secrets["API_KEY"]
        BASE_URL = "https://v3.football.api-sports.io"
    except (FileNotFoundError, KeyError) as e:
        print(f"Hata: API anahtarı '.streamlit/secrets.toml' dosyasından okunamadı. Dosyanın varlığından ve içinde API_KEY olduğundan emin olun. Hata: {e}")
        return

    # 🔒 Mevcut rating'leri yükle - üzerine yazma, sadece güncelle!
    ratings = elo_utils.read_ratings()
    print(f"📊 Mevcut Elo veritabanı yüklendi: {len(ratings)} takım")
    
    # Dünün tarihini al
    yesterday = date.today() - timedelta(days=1)
    
    # İlgilendiğimiz liglerin ID'lerini al
    leagues_map = {v: k for k, v in INTERESTING_LEAGUES.items()}
    league_ids = list(leagues_map.values())
    
    print(f"{yesterday} tarihindeki maçlar için Elo reytingleri güncelleniyor...")
    
    # Dünün bitmiş maçlarını API'den çek (limit kontrolünü atlayarak)
    fixtures, error = api_utils.get_fixtures_by_date(API_KEY, BASE_URL, league_ids, yesterday, bypass_limit_check=True)
    
    if error:
        print(f"API'den maçlar çekilirken hata oluştu: {error}")
        return
        
    if not fixtures:
        print("Dün için güncellenecek maç bulunamadı.")
        return

    updated_count = 0
    for match in fixtures:
        try:
            # Sadece bitmiş ve skoru belli maçları işle
            if 'actual_score' not in match:
                continue

            home_id = match['home_id']
            away_id = match['away_id']
            score_str = match['actual_score'].split(' - ')
            score_home = int(score_str[0])
            score_away = int(score_str[1])

            # Takımların mevcut reytinglerini al (yoksa varsayılan atanır)
            rating_home = elo_utils.get_team_rating(home_id, ratings)
            rating_away = elo_utils.get_team_rating(away_id, ratings)

            # Yeni reytingleri hesapla
            new_rating_home, new_rating_away = elo_utils.calculate_new_ratings(rating_home, rating_away, score_home, score_away)
            
            # Reytingleri güncelle
            ratings[str(home_id)] = {'rating': new_rating_home, 'last_updated': datetime.utcnow().isoformat()}
            ratings[str(away_id)] = {'rating': new_rating_away, 'last_updated': datetime.utcnow().isoformat()}
            
            updated_count += 1
            print(f"Güncellendi: {match['home_name']} ({rating_home} -> {new_rating_home}) vs {match['away_name']} ({rating_away} -> {new_rating_away})")

        except (KeyError, ValueError, TypeError) as e:
            print(f"Bir maç işlenirken hata oluştu: {match.get('home_name')} vs {match.get('away_name')}. Hata: {e}")
            continue

    if updated_count > 0:
        elo_utils.write_ratings(ratings)
        print(f"\nToplam {updated_count} takımın Elo reytingi güncellendi.")
    else:
        print("\nGüncellenecek uygun maç bulunamadı.")
        
    print("İşlem tamamlandı.")

if __name__ == '__main__':
    # Bu dosya doğrudan çalıştırıldığında, ana fonksiyonu çağır.
    run_elo_update()