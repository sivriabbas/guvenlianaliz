"""
PARALEL API ÇAĞRI SİSTEMİ
Asyncio ile birden fazla API'yi aynı anda çağır
"""
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any, Tuple
import json

API_KEY = "6336fb21e17dea87880d3b133132a13f"
BASE_URL = "https://v3.football.api-sports.io"


class ParallelAPIClient:
    """
    Async API client - Paralel çağrılar için
    """
    
    def __init__(self, api_key: str = API_KEY, base_url: str = BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {'x-apisports-key': api_key}
    
    async def fetch(self, session: aiohttp.ClientSession, endpoint: str, 
                   params: Dict = None) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Tek bir API endpoint'ini çağır
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data, None
                else:
                    return None, f"HTTP {response.status}"
        except asyncio.TimeoutError:
            return None, "Timeout"
        except Exception as e:
            return None, str(e)
    
    async def fetch_team_data(self, session: aiohttp.ClientSession, 
                              team_id: int, league_id: int, season: int) -> Dict:
        """
        Bir takım için tüm gerekli verileri paralel çek
        """
        # Tüm endpoint'leri tanımla
        tasks = {
            'team_info': self.fetch(session, f'teams', {'id': team_id}),
            'standings': self.fetch(session, 'standings', {
                'league': league_id, 
                'season': season,
                'team': team_id
            }),
            'fixtures': self.fetch(session, 'fixtures', {
                'team': team_id,
                'last': 10
            }),
            'injuries': self.fetch(session, 'injuries', {'team': team_id}),
            'transfers': self.fetch(session, 'transfers', {'team': team_id})
        }
        
        # Paralel olarak çalıştır
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Sonuçları düzenle
        data = {}
        for i, (key, task) in enumerate(tasks.items()):
            result = results[i]
            if isinstance(result, Exception):
                data[key] = (None, str(result))
            else:
                data[key] = result
        
        return data
    
    async def fetch_match_data(self, session: aiohttp.ClientSession,
                               team1_id: int, team2_id: int,
                               league_id: int, season: int) -> Dict:
        """
        Maç analizi için her iki takımın verilerini paralel çek
        """
        print("🔄 Paralel API çağrıları başlatılıyor...")
        start = time.time()
        
        # Her iki takım için paralel veri çekimi
        tasks = [
            self.fetch_team_data(session, team1_id, league_id, season),
            self.fetch_team_data(session, team2_id, league_id, season),
            # H2H verisi
            self.fetch(session, 'fixtures/headtohead', {
                'h2h': f'{team1_id}-{team2_id}',
                'last': 10
            }),
            # Hakem verileri
            self.fetch(session, 'fixtures', {
                'league': league_id,
                'season': season,
                'last': 50
            })
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start
        print(f"✅ Paralel API çağrıları tamamlandı: {elapsed:.2f}s")
        
        return {
            'team1_data': results[0] if not isinstance(results[0], Exception) else None,
            'team2_data': results[1] if not isinstance(results[1], Exception) else None,
            'h2h_data': results[2] if not isinstance(results[2], Exception) else None,
            'referee_data': results[3] if not isinstance(results[3], Exception) else None,
            'elapsed_time': elapsed
        }


async def parallel_fetch_example(team1_id: int, team2_id: int):
    """
    Örnek kullanım - Paralel veri çekimi
    """
    client = ParallelAPIClient()
    
    async with aiohttp.ClientSession(headers=client.headers) as session:
        result = await client.fetch_match_data(
            session, team1_id, team2_id,
            league_id=203,  # Süper Lig
            season=2025
        )
        
        return result


# Senkron wrapper - normal koddan çağrılabilsin
def fetch_match_data_parallel(team1_id: int, team2_id: int, 
                              league_id: int = 203, season: int = 2025) -> Dict:
    """
    Paralel veri çekimi - Senkron kullanım için wrapper
    """
    try:
        # Cache kontrolü
        from cache_manager import get_cache
        cache = get_cache()
        
        cache_key = f"{team1_id}_{team2_id}_{league_id}_{season}"
        cached = cache.get('parallel_match_data', key=cache_key)
        if cached:
            print(f"🎯 Cache'den alındı: {cache_key}")
            return cached
        
    except:
        pass
    
    # Async fonksiyonu çalıştır
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            parallel_fetch_example(team1_id, team2_id)
        )
        
        # Cache'e kaydet (30 dakika)
        try:
            from cache_manager import get_cache
            cache = get_cache()
            cache.set('parallel_match_data', result, 1800, key=cache_key)
        except:
            pass
        
        return result
    finally:
        loop.close()


# Test
if __name__ == "__main__":
    print("="*70)
    print("🧪 PARALEL API TEST")
    print("="*70)
    
    # Test 1: Sıralı vs Paralel karşılaştırma
    print("\n1️⃣ PERFORMANS KARŞILAŞTIRMASI")
    print("-"*70)
    
    team1_id = 645  # Galatasaray
    team2_id = 611  # Fenerbahce
    
    # Paralel çağrı
    print("\n📊 Paralel API çağrısı:")
    start = time.time()
    result = fetch_match_data_parallel(team1_id, team2_id)
    parallel_time = time.time() - start
    
    print(f"\n✅ Toplam süre: {parallel_time:.2f}s")
    print(f"📦 Veri paketleri:")
    if result:
        if result.get('team1_data'):
            print(f"   ✅ Takım 1: {len(result['team1_data'])} endpoint")
        if result.get('team2_data'):
            print(f"   ✅ Takım 2: {len(result['team2_data'])} endpoint")
        if result.get('h2h_data'):
            print(f"   ✅ H2H: Var")
        if result.get('referee_data'):
            print(f"   ✅ Hakem: Var")
    
    # İkinci çağrı (cache'den)
    print("\n2️⃣ CACHE TESTİ")
    print("-"*70)
    print("\n📊 İkinci çağrı (cache'den):")
    start = time.time()
    result2 = fetch_match_data_parallel(team1_id, team2_id)
    cache_time = time.time() - start
    
    print(f"✅ Cache süresi: {cache_time:.2f}s")
    print(f"⚡ Hız artışı: {(parallel_time/cache_time):.1f}x")
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI!")
    print("="*70)
