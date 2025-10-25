"""
📊 GEÇMİŞ MAÇ VERİSİ TOPLAYICI - PHASE 7.A1
==========================================
API-Football'dan geçmiş maç verilerini toplar ve veritabanına kaydeder
"""

import requests
import sqlite3
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import os

# API Configuration
API_KEY = os.getenv('RAPIDAPI_KEY', 'your_api_key_here')
API_HOST = 'api-football-v1.p.rapidapi.com'
API_URL = f'https://{API_HOST}/v3'

HEADERS = {
    'x-rapidapi-host': API_HOST,
    'x-rapidapi-key': API_KEY
}

# Lig konfigürasyonu
LEAGUES = {
    'Premier League': {'id': 39, 'country': 'England'},
    'La Liga': {'id': 140, 'country': 'Spain'},
    'Bundesliga': {'id': 78, 'country': 'Germany'},
    'Serie A': {'id': 135, 'country': 'Italy'},
    'Süper Lig': {'id': 203, 'country': 'Turkey'},
    'Ligue 1': {'id': 61, 'country': 'France'}
}

# Sezonlar
SEASONS = [2023, 2024, 2025]


class HistoricalDataCollector:
    """Geçmiş maç verilerini topla ve kaydet"""
    
    def __init__(self, db_path='historical_matches.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._init_database()
    
    def _init_database(self):
        """Veritabanı tablolarını oluştur"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Maçlar tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                league_id INTEGER,
                league_name TEXT,
                season INTEGER,
                match_date TEXT,
                home_team_id INTEGER,
                home_team_name TEXT,
                away_team_id INTEGER,
                away_team_name TEXT,
                home_goals INTEGER,
                away_goals INTEGER,
                result TEXT,
                status TEXT,
                raw_data TEXT,
                collected_at TEXT
            )
        ''')
        
        # İstatistikler tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_statistics (
                match_id INTEGER PRIMARY KEY,
                home_shots INTEGER,
                away_shots INTEGER,
                home_shots_on_target INTEGER,
                away_shots_on_target INTEGER,
                home_possession INTEGER,
                away_possession INTEGER,
                home_corners INTEGER,
                away_corners INTEGER,
                home_fouls INTEGER,
                away_fouls INTEGER,
                home_yellow_cards INTEGER,
                away_yellow_cards INTEGER,
                home_red_cards INTEGER,
                away_red_cards INTEGER,
                raw_stats TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        ''')
        
        # Puan durumu snapshot'ları
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS standings_snapshot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                team_id INTEGER,
                team_name TEXT,
                is_home BOOLEAN,
                position INTEGER,
                points INTEGER,
                played INTEGER,
                wins INTEGER,
                draws INTEGER,
                losses INTEGER,
                goals_for INTEGER,
                goals_against INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        ''')
        
        self.conn.commit()
        print(f"✅ Veritabanı hazır: {self.db_path}")
    
    def fetch_league_fixtures(self, league_id: int, season: int) -> List[Dict]:
        """Bir ligdeki tüm maçları çek"""
        print(f"\n📡 Maçlar çekiliyor: League {league_id}, Season {season}")
        
        url = f"{API_URL}/fixtures"
        params = {
            'league': league_id,
            'season': season
        }
        
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                fixtures = data.get('response', [])
                print(f"   ✅ {len(fixtures)} maç bulundu")
                return fixtures
            else:
                print(f"   ❌ Hata: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ İstek hatası: {str(e)}")
            return []
    
    def fetch_match_statistics(self, fixture_id: int) -> Optional[Dict]:
        """Bir maçın istatistiklerini çek"""
        url = f"{API_URL}/fixtures/statistics"
        params = {'fixture': fixture_id}
        
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            else:
                return None
                
        except Exception as e:
            print(f"      ⚠️ İstatistik hatası (fixture {fixture_id}): {str(e)}")
            return None
    
    def parse_statistics(self, stats_data: List[Dict]) -> Dict:
        """İstatistik verisini parse et"""
        if not stats_data or len(stats_data) < 2:
            return {}
        
        home_stats = stats_data[0].get('statistics', [])
        away_stats = stats_data[1].get('statistics', [])
        
        def get_stat(stats_list, stat_type):
            for stat in stats_list:
                if stat.get('type') == stat_type:
                    value = stat.get('value')
                    if isinstance(value, str) and '%' in value:
                        return int(value.replace('%', ''))
                    return value if value is not None else 0
            return 0
        
        return {
            'home_shots': get_stat(home_stats, 'Total Shots'),
            'away_shots': get_stat(away_stats, 'Total Shots'),
            'home_shots_on_target': get_stat(home_stats, 'Shots on Goal'),
            'away_shots_on_target': get_stat(away_stats, 'Shots on Goal'),
            'home_possession': get_stat(home_stats, 'Ball Possession'),
            'away_possession': get_stat(away_stats, 'Ball Possession'),
            'home_corners': get_stat(home_stats, 'Corner Kicks'),
            'away_corners': get_stat(away_stats, 'Corner Kicks'),
            'home_fouls': get_stat(home_stats, 'Fouls'),
            'away_fouls': get_stat(away_stats, 'Fouls'),
            'home_yellow_cards': get_stat(home_stats, 'Yellow Cards'),
            'away_yellow_cards': get_stat(away_stats, 'Yellow Cards'),
            'home_red_cards': get_stat(home_stats, 'Red Cards'),
            'away_red_cards': get_stat(away_stats, 'Red Cards')
        }
    
    def save_match(self, fixture: Dict, league_name: str):
        """Maç verisini veritabanına kaydet"""
        fixture_data = fixture.get('fixture', {})
        teams = fixture.get('teams', {})
        goals = fixture.get('goals', {})
        league = fixture.get('league', {})
        
        match_id = fixture_data.get('id')
        home_goals = goals.get('home', 0)
        away_goals = goals.get('away', 0)
        
        # Sonucu belirle
        if home_goals > away_goals:
            result = 'H'  # Home win
        elif away_goals > home_goals:
            result = 'A'  # Away win
        else:
            result = 'D'  # Draw
        
        # Maç kaydı
        self.cursor.execute('''
            INSERT OR REPLACE INTO matches 
            (id, league_id, league_name, season, match_date, 
             home_team_id, home_team_name, away_team_id, away_team_name,
             home_goals, away_goals, result, status, raw_data, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            league.get('id'),
            league_name,
            league.get('season'),
            fixture_data.get('date'),
            teams.get('home', {}).get('id'),
            teams.get('home', {}).get('name'),
            teams.get('away', {}).get('id'),
            teams.get('away', {}).get('name'),
            home_goals,
            away_goals,
            result,
            fixture_data.get('status', {}).get('short'),
            json.dumps(fixture),
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
    
    def save_statistics(self, match_id: int, stats: Dict):
        """Maç istatistiklerini kaydet"""
        if not stats:
            return
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO match_statistics
            (match_id, home_shots, away_shots, home_shots_on_target, away_shots_on_target,
             home_possession, away_possession, home_corners, away_corners,
             home_fouls, away_fouls, home_yellow_cards, away_yellow_cards,
             home_red_cards, away_red_cards, raw_stats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            stats.get('home_shots', 0),
            stats.get('away_shots', 0),
            stats.get('home_shots_on_target', 0),
            stats.get('away_shots_on_target', 0),
            stats.get('home_possession', 0),
            stats.get('away_possession', 0),
            stats.get('home_corners', 0),
            stats.get('away_corners', 0),
            stats.get('home_fouls', 0),
            stats.get('away_fouls', 0),
            stats.get('home_yellow_cards', 0),
            stats.get('away_yellow_cards', 0),
            stats.get('home_red_cards', 0),
            stats.get('away_red_cards', 0),
            json.dumps(stats)
        ))
        
        self.conn.commit()
    
    def collect_league_season(self, league_id: int, league_name: str, season: int, 
                             fetch_stats: bool = True):
        """Bir lig sezonunun tüm verilerini topla"""
        print(f"\n{'='*80}")
        print(f"🏆 {league_name} - {season}/{season+1} Sezonu")
        print(f"{'='*80}")
        
        # Maçları çek
        fixtures = self.fetch_league_fixtures(league_id, season)
        
        if not fixtures:
            print("   ⚠️ Maç bulunamadı")
            return
        
        # Sadece tamamlanmış maçları al
        finished_matches = [
            f for f in fixtures 
            if f.get('fixture', {}).get('status', {}).get('short') == 'FT'
        ]
        
        print(f"\n📊 Tamamlanmış maçlar: {len(finished_matches)}/{len(fixtures)}")
        
        # Her maçı kaydet
        for i, fixture in enumerate(finished_matches, 1):
            match_id = fixture.get('fixture', {}).get('id')
            home_team = fixture.get('teams', {}).get('home', {}).get('name')
            away_team = fixture.get('teams', {}).get('away', {}).get('name')
            
            print(f"\n   [{i}/{len(finished_matches)}] {home_team} vs {away_team}")
            
            # Maç kaydı
            self.save_match(fixture, league_name)
            print(f"      ✅ Maç kaydedildi (ID: {match_id})")
            
            # İstatistikleri çek (opsiyonel)
            if fetch_stats:
                stats_data = self.fetch_match_statistics(match_id)
                if stats_data:
                    stats = self.parse_statistics(stats_data)
                    self.save_statistics(match_id, stats)
                    print(f"      ✅ İstatistikler kaydedildi")
                    
                # Rate limiting (API limitleri için)
                time.sleep(0.5)
        
        print(f"\n✅ {league_name} - {season} tamamlandı!")
    
    def collect_all_data(self, fetch_stats: bool = True):
        """Tüm ligler ve sezonlar için veri topla"""
        print("\n" + "="*80)
        print("🚀 GEÇMİŞ VERİ TOPLAMA BAŞLADI")
        print("="*80)
        
        start_time = time.time()
        
        for league_name, league_info in LEAGUES.items():
            for season in SEASONS:
                self.collect_league_season(
                    league_info['id'],
                    league_name,
                    season,
                    fetch_stats
                )
                
                # Liglerden sonra kısa ara (rate limiting)
                time.sleep(2)
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*80)
        print("✅ VERİ TOPLAMA TAMAMLANDI!")
        print(f"⏱️  Toplam Süre: {elapsed/60:.1f} dakika")
        print("="*80)
        
        self.print_summary()
    
    def print_summary(self):
        """Toplanan veri özetini göster"""
        print("\n📊 VERİ ÖZETİ:")
        print("-" * 80)
        
        # Toplam maç sayısı
        self.cursor.execute("SELECT COUNT(*) FROM matches")
        total_matches = self.cursor.fetchone()[0]
        print(f"   Toplam Maç: {total_matches}")
        
        # Lig bazında
        self.cursor.execute('''
            SELECT league_name, season, COUNT(*) as count
            FROM matches
            GROUP BY league_name, season
            ORDER BY league_name, season
        ''')
        
        print("\n   Lig Bazında:")
        for row in self.cursor.fetchall():
            print(f"      {row[0]:20} {row[1]}: {row[2]:4} maç")
        
        # İstatistik durumu
        self.cursor.execute("SELECT COUNT(*) FROM match_statistics")
        total_stats = self.cursor.fetchone()[0]
        print(f"\n   İstatistik Kaydı: {total_stats}/{total_matches} maç")
        
        # Sonuç dağılımı
        self.cursor.execute('''
            SELECT result, COUNT(*) as count
            FROM matches
            GROUP BY result
        ''')
        
        print("\n   Sonuç Dağılımı:")
        for row in self.cursor.fetchall():
            result_label = {'H': 'Ev Sahibi', 'A': 'Deplasman', 'D': 'Beraberlik'}.get(row[0], row[0])
            print(f"      {result_label:15}: {row[1]:4} maç ({row[1]/total_matches*100:.1f}%)")
    
    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.conn:
            self.conn.close()
            print("\n🔒 Veritabanı bağlantısı kapatıldı")


# Test & Run
if __name__ == "__main__":
    print("\n" + "="*80)
    print("📊 GEÇMİŞ MAÇ VERİSİ TOPLAYICI - PHASE 7.A1")
    print("="*80)
    
    collector = HistoricalDataCollector()
    
    # Küçük test: Sadece 1 lig, 1 sezon
    print("\n🧪 TEST MODU: Sadece Süper Lig 2024 sezonu")
    collector.collect_league_season(
        league_id=LEAGUES['Süper Lig']['id'],
        league_name='Süper Lig',
        season=2024,
        fetch_stats=True
    )
    
    # Tam toplama için bu satırı aç:
    # collector.collect_all_data(fetch_stats=True)
    
    collector.close()
    
    print("\n✅ TAMAMLANDI!")
    print("📁 Veritabanı: historical_matches.db")
