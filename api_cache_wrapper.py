"""
API UTILS İÇİN CACHE WRAPPER
Mevcut API fonksiyonlarını cache ile sarmalayarak hızlandırır
"""
from cache_manager import get_cache, cached
import api_utils
from typing import Optional, Dict, Any, List

# Cache TTL ayarları (saniye cinsinden)
TTL_TEAM_DATA = 1800  # 30 dakika
TTL_TRANSFERS = 86400  # 24 saat
TTL_INJURIES = 3600  # 1 saat
TTL_XG = 7200  # 2 saat
TTL_SQUAD = 43200  # 12 saat
TTL_H2H = 604800  # 7 gün
TTL_REFEREE = 2592000  # 30 gün

cache = get_cache()


def get_team_id_cached(api_key: str, base_url: str, team_name: str) -> Optional[Dict]:
    """
    Takım ID'sini cache ile getir
    """
    # Cache'e bak
    cached_data = cache.get('team_id', team_name=team_name)
    if cached_data:
        return cached_data
    
    # API'den çek
    result = api_utils.get_team_id(api_key, base_url, team_name)
    
    # Cache'e kaydet
    if result:
        cache.set('team_id', result, TTL_TEAM_DATA, team_name=team_name)
    
    return result


def get_team_transfers_cached(api_key: str, base_url: str, team_id: int) -> Optional[List]:
    """
    Transfer verilerini cache ile getir
    """
    cached_data = cache.get('transfers', team_id=team_id)
    if cached_data:
        return cached_data
    
    # API'den çek
    result, error = api_utils.get_team_transfers(api_key, base_url, team_id)
    
    # Cache'e kaydet
    if result:
        cache.set('transfers', result, TTL_TRANSFERS, team_id=team_id)
    
    return result


def get_team_injuries_cached(api_key: str, base_url: str, team_id: int) -> Optional[List]:
    """
    Sakatlık verilerini cache ile getir
    """
    cached_data = cache.get('injuries', team_id=team_id)
    if cached_data:
        return cached_data
    
    # API'den çek
    result, error = api_utils.get_team_injuries(api_key, base_url, team_id)
    
    # Cache'e kaydet
    if result:
        cache.set('injuries', result, TTL_INJURIES, team_id=team_id)
    
    return result


def get_squad_statistics_cached(api_key: str, base_url: str, team_id: int) -> Optional[List]:
    """
    Kadro istatistiklerini cache ile getir
    """
    cached_data = cache.get('squad', team_id=team_id)
    if cached_data:
        return cached_data
    
    # API'den çek
    result, error = api_utils.get_squad_statistics(api_key, base_url, team_id)
    
    # Cache'e kaydet
    if result:
        cache.set('squad', result, TTL_SQUAD, team_id=team_id)
    
    return result


def get_team_xg_cached(api_key: str, base_url: str, team_id: int, league_id: int, season: int) -> Optional[List]:
    """
    xG verilerini cache ile getir
    """
    cached_data = cache.get('xg', team_id=team_id, league_id=league_id, season=season)
    if cached_data:
        return cached_data
    
    # API'den çek
    result, error = api_utils.get_team_xg_data(api_key, base_url, team_id, league_id, season)
    
    # Cache'e kaydet
    if result:
        cache.set('xg', result, TTL_XG, team_id=team_id, league_id=league_id, season=season)
    
    return result


def get_h2h_matches_cached(api_key: str, base_url: str, team1_id: int, team2_id: int, last: int = 10) -> Optional[List]:
    """
    H2H verilerini cache ile getir
    """
    cached_data = cache.get('h2h', team1_id=team1_id, team2_id=team2_id, last=last)
    if cached_data:
        return cached_data
    
    # API'den çek
    result, error = api_utils.get_h2h_matches(api_key, base_url, team1_id, team2_id, last)
    
    # Cache'e kaydet
    if result:
        cache.set('h2h', result, TTL_H2H, team1_id=team1_id, team2_id=team2_id, last=last)
    
    return result


def get_referee_stats_cached(api_key: str, base_url: str, league_id: int, season: int) -> Optional[List]:
    """
    Hakem verilerini cache ile getir
    """
    cached_data = cache.get('referee', league_id=league_id, season=season)
    if cached_data:
        return cached_data
    
    # API'den çek
    result, error = api_utils.get_league_referees(api_key, base_url, league_id, season)
    
    # Cache'e kaydet
    if result:
        cache.set('referee', result, TTL_REFEREE, league_id=league_id, season=season)
    
    return result


# Test
if __name__ == "__main__":
    print("🧪 CACHE WRAPPER TEST")
    print("="*60)
    
    # Test için API key
    import toml
    try:
        config = toml.load('.streamlit/secrets.toml')
        API_KEY = config['API_FOOTBALL_KEY']
    except:
        API_KEY = "6336fb21e17dea87880d3b133132a13f"
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    # 1. Takım ID testi
    print("\n1. Takım ID (ilk çağrı - API):")
    team = get_team_id_cached(API_KEY, BASE_URL, "Galatasaray")
    print(f"   {team['name'] if team else 'Bulunamadı'}")
    
    print("\n2. Takım ID (ikinci çağrı - CACHE):")
    team = get_team_id_cached(API_KEY, BASE_URL, "Galatasaray")
    print(f"   {team['name'] if team else 'Bulunamadı'}")
    
    # İstatistikler
    print("\n3. Cache istatistikleri:")
    cache.print_stats()
    
    print("\n✅ Test tamamlandı!")
