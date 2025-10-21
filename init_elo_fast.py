# init_elo_fast.py
# Hızlı Elo başlatma - Büyük takımlara manuel rating atama

import json
from datetime import datetime
import os

print("Script başlatıldı...")
print(f"Çalışma dizini: {os.getcwd()}")

# Büyük takımlar ve tahmini Elo rating'leri
INITIAL_RATINGS = {
    # Premier League
    "33": {"rating": 1850, "name": "Manchester United"},  # Man United
    "50": {"rating": 1900, "name": "Manchester City"},    # Man City
    "40": {"rating": 1820, "name": "Liverpool"},          # Liverpool
    "42": {"rating": 1780, "name": "Arsenal"},            # Arsenal
    "49": {"rating": 1770, "name": "Chelsea"},            # Chelsea
    
    # La Liga
    "529": {"rating": 1900, "name": "Barcelona"},         # Barcelona
    "541": {"rating": 1920, "name": "Real Madrid"},       # Real Madrid
    "530": {"rating": 1780, "name": "Atletico Madrid"},   # Atletico
    
    # Bundesliga
    "157": {"rating": 1880, "name": "Bayern Munich"},     # Bayern
    "165": {"rating": 1750, "name": "Borussia Dortmund"}, # Dortmund
    
    # Serie A
    "489": {"rating": 1800, "name": "AC Milan"},          # AC Milan
    "487": {"rating": 1820, "name": "Juventus"},          # Juventus
    "505": {"rating": 1810, "name": "Inter"},             # Inter
    
    # Ligue 1
    "85": {"rating": 1850, "name": "Paris Saint Germain"}, # PSG
    
    # Süper Lig
    "645": {"rating": 1650, "name": "Galatasaray"},       # Galatasaray
    "643": {"rating": 1640, "name": "Fenerbahçe"},        # Fenerbahçe
    "641": {"rating": 1620, "name": "Beşiktaş"},          # Beşiktaş
    "644": {"rating": 1580, "name": "Trabzonspor"},       # Trabzonspor
    
    # Diğer önemli takımlar
    "229": {"rating": 1750, "name": "Ajax"},              # Ajax
    "211": {"rating": 1740, "name": "PSV"},               # PSV
    "228": {"rating": 1720, "name": "Sporting CP"},       # Sporting
    "210": {"rating": 1720, "name": "Porto"},             # Porto
    "211": {"rating": 1700, "name": "Benfica"},           # Benfica
}

def init_elo_ratings():
    """Başlangıç Elo rating'lerini oluşturur"""
    try:
        print("Hızlı Elo başlatma başlıyor...")
        
        ratings = {}
        timestamp = datetime.utcnow().isoformat()
        
        for team_id, data in INITIAL_RATINGS.items():
            ratings[team_id] = {
                "rating": data["rating"],
                "last_updated": timestamp
            }
            print(f"✅ {data['name']}: {data['rating']}")
        
        # Dosyaya yaz
        file_path = 'elo_ratings.json'
        print(f"\nDosyaya yazılıyor: {file_path}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ratings, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Toplam {len(ratings)} takım için Elo rating'i oluşturuldu!")
        print(f"📁 Dosya başarıyla kaydedildi: {file_path}")
        
        # Doğrulama
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            print(f"✅ Doğrulama: {len(saved_data)} kayıt okundu")
        
    except Exception as e:
        print(f"❌ HATA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_elo_ratings()
    print("\nScript tamamlandı.")
