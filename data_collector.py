"""
DATA COLLECTOR - Gerçek Maç Verisi Toplama Sistemi
Phase 6: ML modellerini eğitmek için tarihsel maç verisi toplar
"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import api_utils
from elo_utils import EloManager
from analysis_logic import (
    calculate_form, calculate_h2h, calculate_home_advantage,
    calculate_league_position_factor, calculate_fatigue
)
from pathlib import Path
import pandas as pd

class MatchDataCollector:
    """Gerçek maç verilerini toplar ve ML formatına çevirir"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.elo_manager = EloManager()
        self.data_dir = Path("ml_training_data")
        self.data_dir.mkdir(exist_ok=True)
        
    def collect_league_matches(self, league_id: int, season: int, 
                               max_matches: int = 200) -> List[Dict]:
        """Bir lig sezonunun tüm maçlarını topla"""
        print(f"\n{'='*70}")
        print(f"📊 Lig {league_id} - Sezon {season} Verisi Toplanıyor...")
        print(f"{'='*70}")
        
        collected_data = []
        
        # Sezon maçlarını çek
        print("🔍 Maçlar çekiliyor...")
        fixtures, error = api_utils.get_fixtures_by_league(
            self.api_key, self.base_url, league_id, season
        )
        
        if error or not fixtures:
            print(f"❌ Hata: {error}")
            return collected_data
        
        # Sadece tamamlanmış maçları al
        finished_matches = [f for f in fixtures if f.get('status') == 'Match Finished'][:max_matches]
        print(f"✅ {len(finished_matches)} tamamlanmış maç bulundu")
        
        # Her maç için veri topla
        for i, match in enumerate(finished_matches, 1):
            try:
                print(f"\n[{i}/{len(finished_matches)}] {match['home_name']} vs {match['away_name']}")
                
                match_data = self.extract_match_features(match, league_id, season)
                if match_data:
                    collected_data.append(match_data)
                    print(f"  ✅ Veri toplandı")
                
                # Rate limiting (API limiti için)
                if i % 10 == 0:
                    print(f"\n⏸️ API rate limit - 3 saniye bekleniyor...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"  ❌ Hata: {e}")
                continue
        
        print(f"\n{'='*70}")
        print(f"✅ Toplam {len(collected_data)} maç verisi toplandı")
        print(f"{'='*70}")
        
        return collected_data
    
    def extract_match_features(self, match: Dict, league_id: int, season: int) -> Optional[Dict]:
        """Bir maçtan 17 faktörü çıkar"""
        home_id = match.get('home_id')
        away_id = match.get('away_id')
        
        if not home_id or not away_id:
            return None
        
        # Maç sonucunu belirle (label)
        home_goals = match.get('home_goals', 0)
        away_goals = match.get('away_goals', 0)
        
        if home_goals > away_goals:
            result = 0  # home_win
        elif home_goals < away_goals:
            result = 2  # away_win
        else:
            result = 1  # draw
        
        # API'den ek veriler çek
        try:
            # Form verisi
            home_form = self._get_team_form(home_id, league_id, season)
            away_form = self._get_team_form(away_id, league_id, season)
            
            # H2H verisi
            h2h_data = self._get_h2h(home_id, away_id)
            
            # Lig sıralaması
            standings = self._get_standings(league_id, season)
            home_position = self._find_team_position(standings, home_id)
            away_position = self._find_team_position(standings, away_id)
            
        except Exception as e:
            print(f"  ⚠️ Ek veri çekme hatası: {e}")
            # Default değerler
            home_form = away_form = 0.5
            h2h_data = 0.5
            home_position = away_position = 10
        
        # ELO ratings
        home_elo = self.elo_manager.get_rating(home_id)
        away_elo = self.elo_manager.get_rating(away_id)
        elo_diff = home_elo - away_elo
        
        # 17 faktörü hesapla
        features = {
            # Temel metrikler
            'form': home_form - away_form,
            'elo_diff': elo_diff / 400.0,  # Normalize
            'home_advantage': 0.6,  # Ev sahibi her zaman avantajlı
            'h2h': h2h_data,
            'league_position': (away_position - home_position) / 20.0,  # Normalize
            
            # Phase 1 faktörleri
            'injuries': 0.5,  # Varsayılan (API'de sakatlık verisi limitli)
            'motivation': self._estimate_motivation(home_position, away_position),
            'recent_xg': 0.5,  # Varsayılan (xG verisi için ek API gerekli)
            
            # Phase 2 faktörleri
            'weather': 0.5,  # Varsayılan (weather API ayrı)
            'referee': 0.5,  # Varsayılan (hakem verisi limitli)
            'betting_odds': 0.5,  # Varsayılan (odds API ayrı)
            
            # Phase 3 faktörleri
            'tactical_matchup': 0.5,  # Varsayılan
            'transfer_impact': 0.5,  # Varsayılan
            'squad_experience': 0.5,  # Varsayılan
            
            # Ek metrikler
            'match_importance': self._estimate_importance(home_position, away_position),
            'fatigue': 0.5,  # Varsayılan
            'recent_performance': home_form,
        }
        
        return {
            'features': features,
            'result': result,
            'metadata': {
                'match_id': match.get('match_id'),
                'home_team': match.get('home_name'),
                'away_team': match.get('away_name'),
                'home_goals': home_goals,
                'away_goals': away_goals,
                'date': match.get('date'),
                'league_id': league_id,
                'season': season
            }
        }
    
    def _get_team_form(self, team_id: int, league_id: int, season: int) -> float:
        """Takımın son 5 maçtaki formunu hesapla"""
        try:
            fixtures, _ = api_utils.get_team_last_matches(
                self.api_key, self.base_url, team_id, 5
            )
            
            if not fixtures:
                return 0.5
            
            points = 0
            for match in fixtures:
                if match.get('home_id') == team_id:
                    # Ev sahibi
                    if match.get('home_goals', 0) > match.get('away_goals', 0):
                        points += 3
                    elif match.get('home_goals', 0) == match.get('away_goals', 0):
                        points += 1
                else:
                    # Deplasman
                    if match.get('away_goals', 0) > match.get('home_goals', 0):
                        points += 3
                    elif match.get('away_goals', 0) == match.get('home_goals', 0):
                        points += 1
            
            # Normalize: 0-15 puan -> 0-1
            return points / 15.0
            
        except Exception:
            return 0.5
    
    def _get_h2h(self, home_id: int, away_id: int) -> float:
        """H2H üstünlüğünü hesapla"""
        try:
            h2h_data, _ = api_utils.get_h2h(
                self.api_key, self.base_url, home_id, away_id
            )
            
            if not h2h_data:
                return 0.5
            
            home_wins = sum(1 for m in h2h_data if m.get('winner') == 'home')
            away_wins = sum(1 for m in h2h_data if m.get('winner') == 'away')
            
            total = home_wins + away_wins
            if total == 0:
                return 0.5
            
            return home_wins / total
            
        except Exception:
            return 0.5
    
    def _get_standings(self, league_id: int, season: int) -> List[Dict]:
        """Lig sıralamasını çek"""
        try:
            standings, _ = api_utils.get_standings(
                self.api_key, self.base_url, league_id, season
            )
            return standings or []
        except Exception:
            return []
    
    def _find_team_position(self, standings: List[Dict], team_id: int) -> int:
        """Takımın lig sıralamasını bul"""
        for team in standings:
            if team.get('team_id') == team_id:
                return team.get('position', 10)
        return 10  # Varsayılan orta sıra
    
    def _estimate_motivation(self, home_pos: int, away_pos: int) -> float:
        """Motivasyon tahmini (sıralamaya göre)"""
        # Üst sıradaki takımlar daha motive
        avg_position = (home_pos + away_pos) / 2
        return 1.0 - (avg_position / 20.0)  # 0-1 arası
    
    def _estimate_importance(self, home_pos: int, away_pos: int) -> float:
        """Maç önemi tahmini"""
        # Derby veya kritik maçlar daha önemli
        if abs(home_pos - away_pos) <= 2:
            return 0.8  # Yakın sıralamada olanlar
        elif home_pos <= 3 or away_pos <= 3:
            return 0.9  # Şampiyonluk yarışı
        elif home_pos >= 16 or away_pos >= 16:
            return 0.85  # Düşme hattı
        return 0.5
    
    def save_dataset(self, data: List[Dict], filename: str):
        """Veriyi JSON ve CSV olarak kaydet"""
        if not data:
            print("⚠️ Kaydedilecek veri yok!")
            return
        
        # JSON formatında kaydet
        json_path = self.data_dir / f"{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON kaydedildi: {json_path}")
        
        # CSV formatında kaydet (ML için daha kullanışlı)
        csv_path = self.data_dir / f"{filename}.csv"
        
        # DataFrame oluştur
        rows = []
        for match in data:
            row = match['features'].copy()
            row['result'] = match['result']
            row['match_id'] = match['metadata']['match_id']
            row['home_team'] = match['metadata']['home_team']
            row['away_team'] = match['metadata']['away_team']
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ CSV kaydedildi: {csv_path}")
        
        # İstatistikler
        result_counts = df['result'].value_counts()
        print(f"\n📊 Veri İstatistikleri:")
        print(f"  Toplam maç: {len(df)}")
        print(f"  Ev sahibi galibiyet: {result_counts.get(0, 0)} (%{result_counts.get(0, 0)/len(df)*100:.1f})")
        print(f"  Beraberlik: {result_counts.get(1, 0)} (%{result_counts.get(1, 0)/len(df)*100:.1f})")
        print(f"  Deplasman galibiyet: {result_counts.get(2, 0)} (%{result_counts.get(2, 0)/len(df)*100:.1f})")
    
    def collect_multiple_leagues(self, league_configs: List[Tuple[int, int, int]], 
                                 output_filename: str = "training_data"):
        """Birden fazla lig/sezondan veri topla"""
        all_data = []
        
        print(f"\n{'='*70}")
        print(f"🚀 TOPLU VERİ TOPLAMA BAŞLIYOR")
        print(f"{'='*70}")
        print(f"📋 Hedef: {len(league_configs)} lig/sezon")
        
        for i, (league_id, season, max_matches) in enumerate(league_configs, 1):
            print(f"\n\n[{i}/{len(league_configs)}] İşlem başlıyor...")
            
            league_data = self.collect_league_matches(league_id, season, max_matches)
            all_data.extend(league_data)
            
            print(f"✅ Toplam toplanan: {len(all_data)} maç")
            
            # Rate limiting
            if i < len(league_configs):
                print(f"\n⏸️ Sonraki lige geçmeden önce 5 saniye bekleniyor...")
                time.sleep(5)
        
        # Veriyi kaydet
        print(f"\n{'='*70}")
        print(f"💾 VERİ KAYDEDİLİYOR")
        print(f"{'='*70}")
        self.save_dataset(all_data, output_filename)
        
        return all_data


def load_api_config():
    """API config yükle"""
    import os
    import toml
    
    # Environment variable'dan dene
    api_key = os.environ.get('API_KEY')
    if api_key:
        return api_key, "https://v3.football.api-sports.io"
    
    # Secrets.toml'dan dene
    try:
        secrets_path = ".streamlit/secrets.toml"
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r', encoding='utf-8') as file:
                secrets_data = toml.load(file)
                api_key = secrets_data.get('API_KEY')
                if api_key:
                    return api_key, "https://v3.football.api-sports.io"
    except Exception as e:
        print(f"⚠️ Secrets yüklenirken hata: {e}")
    
    return None, None


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎯 GERÇEK VERİ TOPLAMA SİSTEMİ - PHASE 6")
    print("="*70)
    
    # API config
    api_key, base_url = load_api_config()
    
    if not api_key:
        print("\n❌ API key bulunamadı!")
        print("Lütfen .streamlit/secrets.toml dosyasına API_KEY ekleyin")
        exit(1)
    
    # Collector oluştur
    collector = MatchDataCollector(api_key, base_url)
    
    # Veri toplama planı
    # Format: (league_id, season, max_matches)
    league_configs = [
        (203, 2024, 100),  # Süper Lig 2024 - 100 maç
        (39, 2024, 100),   # Premier League 2024 - 100 maç
        (140, 2024, 100),  # La Liga 2024 - 100 maç
        (78, 2024, 50),    # Bundesliga 2024 - 50 maç
        (135, 2024, 50),   # Serie A 2024 - 50 maç
    ]
    
    print(f"\n📋 Planlanan veri toplama:")
    print(f"  5 lig × ~400 maç = ~400 veri noktası")
    print(f"  Tahmini süre: ~30-45 dakika")
    print(f"  API kullanımı: ~500-600 request")
    
    response = input("\n❓ Devam etmek istiyor musunuz? (e/h): ")
    
    if response.lower() == 'e':
        all_data = collector.collect_multiple_leagues(
            league_configs, 
            output_filename="football_training_data_2024"
        )
        
        print(f"\n{'='*70}")
        print(f"🎉 VERİ TOPLAMA TAMAMLANDI!")
        print(f"{'='*70}")
        print(f"✅ Toplam: {len(all_data)} maç")
        print(f"📁 Dosyalar: ml_training_data/ dizininde")
        print(f"🎯 Sonraki adım: Model eğitimi (python train_ml_models.py)")
    else:
        print("\n⏸️ İşlem iptal edildi")
