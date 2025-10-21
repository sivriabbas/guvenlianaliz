# elo_utils.py

import json
import os
from datetime import datetime

ELO_FILE = 'elo_ratings.json'
DEFAULT_RATING = 1500
K_FACTOR = 30 # Elo'nun ne kadar hızlı değişeceğini belirleyen katsayı

def read_ratings() -> dict:
    """elo_ratings.json dosyasını okur ve içeriğini döndürür."""
    if not os.path.exists(ELO_FILE):
        return {}
    try:
        with open(ELO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def write_ratings(ratings: dict):
    """Verilen reyting sözlüğünü elo_ratings.json dosyasına yazar."""
    with open(ELO_FILE, 'w', encoding='utf-8') as f:
        json.dump(ratings, f, indent=4, ensure_ascii=False)

def get_team_rating(team_id: int, ratings: dict) -> int:
    """Bir takımın reytingini alır. Eğer takım yeni ise varsayılan reytingi atar."""
    team_id_str = str(team_id)
    if team_id_str not in ratings:
        ratings[team_id_str] = {'rating': DEFAULT_RATING, 'last_updated': datetime.utcnow().isoformat()}
    return ratings[team_id_str]['rating']

def calculate_new_ratings(rating_a: int, rating_b: int, score_a: int, score_b: int) -> tuple[int, int]:
    """İki takımın reytingini ve maç skorunu alıp yeni Elo reytinglerini hesaplar."""
    
    # Beklenen sonuçları hesapla (A ve B takımlarının kazanma olasılıkları)
    expected_a = 1 / (1 + 10**((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10**((rating_a - rating_b) / 400))
    
    # Gerçekleşen skoru belirle (1: galibiyet, 0.5: beraberlik, 0: mağlubiyet)
    if score_a > score_b:
        actual_a = 1.0
        actual_b = 0.0
    elif score_b > score_a:
        actual_a = 0.0
        actual_b = 1.0
    else:
        actual_a = 0.5
        actual_b = 0.5
        
    # Gol farkına göre K faktörü için bir çarpan belirle (opsiyonel ama daha isabetli sonuç verir)
    goal_diff = abs(score_a - score_b)
    if goal_diff > 1:
        multiplier = 1 + (goal_diff - 1) * 0.25
    else:
        multiplier = 1
        
    # Yeni reytingleri hesapla
    new_rating_a = rating_a + (K_FACTOR * multiplier) * (actual_a - expected_a)
    new_rating_b = rating_b + (K_FACTOR * multiplier) * (actual_b - expected_b)
    
    return round(new_rating_a), round(new_rating_b)