"""
⚙️ GEÇMİŞ MAÇLAR İÇİN 17 FAKTÖR HESAPLAMA - PHASE 7.A2
======================================================
historical_matches.db'deki maçlar için tüm faktörleri hesapla
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from tqdm import tqdm


class HistoricalFactorCalculator:
    """Geçmiş maçlar için 17 faktör hesaplayıcı"""
    
    def __init__(self, db_path='historical_matches.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # ELO başlangıç değerleri
        self.elo_ratings = {}  # {team_id: elo_rating}
        self.K_FACTOR = 32
        self.HOME_ADVANTAGE = 100
        
        print(f"✅ Bağlantı kuruldu: {db_path}")
    
    def initialize_elo_ratings(self):
        """Tüm takımlar için başlangıç ELO değerleri (1500)"""
        self.cursor.execute('''
            SELECT DISTINCT home_team_id, home_team_name FROM matches
            UNION
            SELECT DISTINCT away_team_id, away_team_name FROM matches
        ''')
        
        for team_id, team_name in self.cursor.fetchall():
            if team_id not in self.elo_ratings:
                self.elo_ratings[team_id] = 1500
        
        print(f"✅ {len(self.elo_ratings)} takım için ELO başlatıldı")
    
    def calculate_elo_change(self, team1_elo: float, team2_elo: float, 
                            result: str, is_home: bool) -> tuple:
        """
        ELO rating değişimini hesapla
        
        Args:
            team1_elo: Takım 1'in mevcut ELO'su
            team2_elo: Takım 2'nin mevcut ELO'su
            result: 'H' (home win), 'A' (away win), 'D' (draw)
            is_home: Takım 1 ev sahibi mi?
            
        Returns:
            (team1_new_elo, team2_new_elo)
        """
        # Ev avantajı ekle
        if is_home:
            team1_elo_adjusted = team1_elo + self.HOME_ADVANTAGE
            team2_elo_adjusted = team2_elo
        else:
            team1_elo_adjusted = team1_elo
            team2_elo_adjusted = team2_elo + self.HOME_ADVANTAGE
        
        # Beklenen skor
        expected_team1 = 1 / (1 + 10 ** ((team2_elo_adjusted - team1_elo_adjusted) / 400))
        expected_team2 = 1 - expected_team1
        
        # Gerçek skor
        if result == 'H':
            actual_team1, actual_team2 = 1, 0
        elif result == 'A':
            actual_team1, actual_team2 = 0, 1
        else:  # Draw
            actual_team1, actual_team2 = 0.5, 0.5
        
        # Yeni ELO hesapla
        new_team1_elo = team1_elo + self.K_FACTOR * (actual_team1 - expected_team1)
        new_team2_elo = team2_elo + self.K_FACTOR * (actual_team2 - expected_team2)
        
        return new_team1_elo, new_team2_elo
    
    def get_team_form(self, team_id: int, before_date: str, n_matches: int = 5) -> float:
        """
        Takımın son N maçtaki formu
        
        Returns:
            Form skoru (0-100 arası)
        """
        self.cursor.execute('''
            SELECT result, home_team_id, away_team_id
            FROM matches
            WHERE (home_team_id = ? OR away_team_id = ?)
                AND match_date < ?
                AND status = 'FT'
            ORDER BY match_date DESC
            LIMIT ?
        ''', (team_id, team_id, before_date, n_matches))
        
        results = self.cursor.fetchall()
        
        if not results:
            return 50.0  # Varsayılan
        
        points = 0
        for result, home_id, away_id in results:
            if result == 'H' and home_id == team_id:
                points += 3  # Galibiyet
            elif result == 'A' and away_id == team_id:
                points += 3  # Galibiyet
            elif result == 'D':
                points += 1  # Beraberlik
        
        max_points = len(results) * 3
        form_score = (points / max_points) * 100 if max_points > 0 else 50.0
        
        return round(form_score, 2)
    
    def get_h2h_stats(self, team1_id: int, team2_id: int, 
                     before_date: str, n_matches: int = 10) -> Dict:
        """
        İki takım arasındaki kafa kafaya istatistikler
        """
        self.cursor.execute('''
            SELECT result, home_team_id, home_goals, away_goals
            FROM matches
            WHERE ((home_team_id = ? AND away_team_id = ?) 
                OR (home_team_id = ? AND away_team_id = ?))
                AND match_date < ?
                AND status = 'FT'
            ORDER BY match_date DESC
            LIMIT ?
        ''', (team1_id, team2_id, team2_id, team1_id, before_date, n_matches))
        
        results = self.cursor.fetchall()
        
        if not results:
            return {
                'total_matches': 0,
                'team1_wins': 0,
                'team2_wins': 0,
                'draws': 0,
                'team1_win_rate': 0.5,
                'team1_goals_avg': 0,
                'team2_goals_avg': 0
            }
        
        team1_wins = 0
        team2_wins = 0
        draws = 0
        team1_goals_total = 0
        team2_goals_total = 0
        
        for result, home_id, home_goals, away_goals in results:
            if home_id == team1_id:
                team1_goals_total += home_goals
                team2_goals_total += away_goals
                if result == 'H':
                    team1_wins += 1
                elif result == 'A':
                    team2_wins += 1
                else:
                    draws += 1
            else:
                team1_goals_total += away_goals
                team2_goals_total += home_goals
                if result == 'A':
                    team1_wins += 1
                elif result == 'H':
                    team2_wins += 1
                else:
                    draws += 1
        
        total = len(results)
        
        return {
            'total_matches': total,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'team1_win_rate': team1_wins / total if total > 0 else 0.5,
            'team1_goals_avg': team1_goals_total / total if total > 0 else 0,
            'team2_goals_avg': team2_goals_total / total if total > 0 else 0
        }
    
    def get_league_position(self, team_id: int, league_id: int, 
                           season: int, before_date: str) -> int:
        """
        Maç tarihindeki lig pozisyonu (simüle edilmiş)
        """
        # Basitleştirilmiş: Sezon içindeki performansa göre tahmin
        self.cursor.execute('''
            SELECT 
                SUM(CASE 
                    WHEN home_team_id = ? AND result = 'H' THEN 3
                    WHEN away_team_id = ? AND result = 'A' THEN 3
                    WHEN (home_team_id = ? OR away_team_id = ?) AND result = 'D' THEN 1
                    ELSE 0
                END) as points
            FROM matches
            WHERE (home_team_id = ? OR away_team_id = ?)
                AND league_id = ?
                AND season = ?
                AND match_date < ?
                AND status = 'FT'
        ''', (team_id, team_id, team_id, team_id, team_id, team_id, 
              league_id, season, before_date))
        
        points = self.cursor.fetchone()[0] or 0
        
        # Tüm takımların puanlarını al ve sırala
        self.cursor.execute('''
            SELECT home_team_id as team_id,
                SUM(CASE 
                    WHEN result = 'H' THEN 3
                    WHEN result = 'D' THEN 1
                    ELSE 0
                END) as points
            FROM matches
            WHERE league_id = ?
                AND season = ?
                AND match_date < ?
                AND status = 'FT'
            GROUP BY team_id
            ORDER BY points DESC
        ''', (league_id, season, before_date))
        
        positions = self.cursor.fetchall()
        
        for idx, (tid, pts) in enumerate(positions, 1):
            if tid == team_id:
                return idx
        
        return 10  # Varsayılan orta sıra
    
    def get_home_away_stats(self, team_id: int, before_date: str, 
                           is_home: bool, n_matches: int = 10) -> Dict:
        """Ev/Deplasman performans istatistikleri"""
        if is_home:
            where_clause = 'home_team_id = ?'
            result_win = 'H'
        else:
            where_clause = 'away_team_id = ?'
            result_win = 'A'
        
        self.cursor.execute(f'''
            SELECT result
            FROM matches
            WHERE {where_clause}
                AND match_date < ?
                AND status = 'FT'
            ORDER BY match_date DESC
            LIMIT ?
        ''', (team_id, before_date, n_matches))
        
        results = [r[0] for r in self.cursor.fetchall()]
        
        if not results:
            return {'win_rate': 50.0, 'matches_played': 0}
        
        wins = sum(1 for r in results if r == result_win)
        
        return {
            'win_rate': (wins / len(results)) * 100,
            'matches_played': len(results)
        }
    
    def calculate_match_factors(self, match_row: tuple) -> Dict:
        """
        Bir maç için 17 faktörü hesapla
        """
        (match_id, league_id, league_name, season, match_date,
         home_team_id, home_team_name, away_team_id, away_team_name,
         home_goals, away_goals, result, status) = match_row
        
        # 1. ELO Ratings (maç öncesi)
        home_elo = self.elo_ratings.get(home_team_id, 1500)
        away_elo = self.elo_ratings.get(away_team_id, 1500)
        elo_diff = home_elo - away_elo
        
        # 2. Form
        home_form = self.get_team_form(home_team_id, match_date)
        away_form = self.get_team_form(away_team_id, match_date)
        form_diff = home_form - away_form
        
        # 3. H2H
        h2h = self.get_h2h_stats(home_team_id, away_team_id, match_date)
        
        # 4. League Position
        home_position = self.get_league_position(home_team_id, league_id, season, match_date)
        away_position = self.get_league_position(away_team_id, league_id, season, match_date)
        position_diff = away_position - home_position  # Düşük daha iyi
        
        # 5. Home/Away Performance
        home_stats = self.get_home_away_stats(home_team_id, match_date, is_home=True)
        away_stats = self.get_home_away_stats(away_team_id, match_date, is_home=False)
        
        # 6-17. Diğer faktörler (basitleştirilmiş)
        # Gerçek implementasyonda bu faktörler API'den çekilmeli
        
        factors = {
            # Temel Faktörler
            'elo_diff': elo_diff,
            'home_elo': home_elo,
            'away_elo': away_elo,
            
            'form_diff': form_diff,
            'home_form': home_form,
            'away_form': away_form,
            
            'h2h_win_rate': h2h['team1_win_rate'],
            'h2h_total': h2h['total_matches'],
            
            'position_diff': position_diff,
            'home_position': home_position,
            'away_position': away_position,
            
            'home_advantage': home_stats['win_rate'],
            'away_disadvantage': 100 - away_stats['win_rate'],
            
            # Ek Faktörler (varsayılan değerler)
            'goals_for_ratio': 1.0,
            'goals_against_ratio': 1.0,
            'motivation_score': 50.0,
            'rest_days': 3,
            
            # Hedef değişken
            'result': result,
            'home_goals': home_goals,
            'away_goals': away_goals
        }
        
        # ELO güncelle (maçtan sonra)
        new_home_elo, new_away_elo = self.calculate_elo_change(
            home_elo, away_elo, result, is_home=True
        )
        self.elo_ratings[home_team_id] = new_home_elo
        self.elo_ratings[away_team_id] = new_away_elo
        
        return factors
    
    def process_all_matches(self, output_csv='training_dataset.csv'):
        """Tüm maçları işle ve CSV'ye kaydet"""
        print("\n" + "="*80)
        print("⚙️ 17 FAKTÖR HESAPLAMA BAŞLADI")
        print("="*80)
        
        # ELO başlat
        self.initialize_elo_ratings()
        
        # Tüm maçları tarih sırasına göre al (kronolojik)
        self.cursor.execute('''
            SELECT id, league_id, league_name, season, match_date,
                   home_team_id, home_team_name, away_team_id, away_team_name,
                   home_goals, away_goals, result, status
            FROM matches
            WHERE status = 'FT'
            ORDER BY match_date ASC
        ''')
        
        matches = self.cursor.fetchall()
        total = len(matches)
        
        print(f"\n📊 Toplam {total} maç işlenecek")
        print("-" * 80)
        
        # Her maç için faktörleri hesapla
        all_factors = []
        
        for match in tqdm(matches, desc="Faktörler hesaplanıyor"):
            try:
                factors = self.calculate_match_factors(match)
                factors['match_id'] = match[0]
                factors['league'] = match[2]
                factors['season'] = match[3]
                factors['date'] = match[4]
                factors['home_team'] = match[6]
                factors['away_team'] = match[8]
                
                all_factors.append(factors)
                
            except Exception as e:
                print(f"\n⚠️ Hata (Match {match[0]}): {str(e)}")
                continue
        
        # DataFrame oluştur
        df = pd.DataFrame(all_factors)
        
        # CSV'ye kaydet
        df.to_csv(output_csv, index=False)
        
        print(f"\n✅ {len(all_factors)} maç işlendi")
        print(f"📁 Kaydedildi: {output_csv}")
        
        self.print_dataset_summary(df)
        
        return df
    
    def print_dataset_summary(self, df: pd.DataFrame):
        """Dataset özetini göster"""
        print("\n" + "="*80)
        print("📊 DATASET ÖZETİ")
        print("="*80)
        
        print(f"\n   Toplam Maç: {len(df)}")
        print(f"   Özellik Sayısı: {len(df.columns)}")
        
        # Sonuç dağılımı
        print("\n   Sonuç Dağılımı:")
        result_counts = df['result'].value_counts()
        for result, count in result_counts.items():
            label = {'H': 'Ev Sahibi', 'A': 'Deplasman', 'D': 'Beraberlik'}[result]
            print(f"      {label:15}: {count:4} ({count/len(df)*100:.1f}%)")
        
        # Lig dağılımı
        print("\n   Lig Dağılımı:")
        league_counts = df['league'].value_counts()
        for league, count in league_counts.items():
            print(f"      {league:20}: {count:4} maç")
        
        # Faktör istatistikleri
        print("\n   Faktör Özet İstatistikleri:")
        numeric_cols = ['elo_diff', 'form_diff', 'position_diff', 
                       'home_advantage', 'h2h_win_rate']
        
        stats_df = df[numeric_cols].describe()
        print(stats_df.to_string())
        
        # Korelasyon matrisi
        print("\n   Hedef ile Korelasyon:")
        # Result'u numerik yap (H=1, D=0.5, A=0)
        df['result_numeric'] = df['result'].map({'H': 1, 'D': 0.5, 'A': 0})
        correlations = df[numeric_cols + ['result_numeric']].corr()['result_numeric'].sort_values(ascending=False)
        
        for col, corr in correlations.items():
            if col != 'result_numeric':
                print(f"      {col:20}: {corr:6.3f}")
    
    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.conn:
            self.conn.close()
            print("\n🔒 Bağlantı kapatıldı")


# Test & Run
if __name__ == "__main__":
    print("\n" + "="*80)
    print("⚙️ GEÇMİŞ MAÇLAR İÇİN 17 FAKTÖR HESAPLAMA - PHASE 7.A2")
    print("="*80)
    
    calculator = HistoricalFactorCalculator('historical_matches.db')
    
    # Tüm maçları işle
    df = calculator.process_all_matches('training_dataset.csv')
    
    calculator.close()
    
    print("\n" + "="*80)
    print("✅ FAKTÖR HESAPLAMA TAMAMLANDI!")
    print("="*80)
    print("\n📌 Sonraki Adımlar:")
    print("   1. training_dataset.csv'yi kontrol et")
    print("   2. prepare_training_data.py ile model eğitimi için hazırla")
    print("   3. tune_xgboost.py ile hyperparameter tuning yap")
    print("="*80 + "\n")
