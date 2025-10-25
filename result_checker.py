"""
Phase 7.D2: Sonuç Kontrol Sistemi
==================================
Gerçek maç sonuçlarını API'den çeker ve tahminlerle karşılaştırır.

Özellikler:
- API-Football'dan gerçek sonuçları çekme
- Tahminlerle otomatik eşleştirme
- Doğruluk oranı hesaplama
- Model performans tracking
- Detaylı analiz raporları
- Email/webhook bildirimleri (opsiyonel)

Kullanım:
    python result_checker.py
    
    # Belirli bir tarih aralığı
    python result_checker.py --start-date 2024-01-01 --end-date 2024-01-31
    
    # Sadece belirli bir model
    python result_checker.py --model "Ensemble_Weighted"
    
    # Otomatik mod (günlük)
    python result_checker.py --auto

Database Updates:
    - Predictions tablosundaki actual_result sütunu güncellenir
    - is_correct sütunu hesaplanır
    - Model performance tablosu güncellenir
"""

import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from prediction_logger import PredictionLogger
import pandas as pd
import numpy as np


class ResultChecker:
    """Gerçek sonuçları kontrol eder ve tahminleri günceller."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        db_path: str = "predictions.db",
        config_path: str = "config.yaml"
    ):
        """
        Args:
            api_key: API-Football API key
            db_path: Predictions veritabanı yolu
            config_path: Config dosyası yolu
        """
        self.db_path = db_path
        self.logger = PredictionLogger(db_path)
        
        # API key
        self.api_key = api_key
        if not api_key:
            self.api_key = self._load_api_key_from_config(config_path)
        
        # API settings
        self.api_base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": self.api_key
        }
        
        self.results = []
        self.stats = {
            'total_checked': 0,
            'total_updated': 0,
            'total_correct': 0,
            'total_incorrect': 0,
            'api_calls': 0
        }
        
        print("🔍 ResultChecker başlatıldı")
    
    def _load_api_key_from_config(self, config_path: str) -> Optional[str]:
        """Config'den API key yükle."""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            api_key = config.get('api_football', {}).get('api_key')
            if api_key:
                print(f"   ✅ API key config'den yüklendi")
                return api_key
                
        except Exception as e:
            print(f"   ⚠️ Config yükleme hatası: {e}")
        
        print(f"   ⚠️ API key bulunamadı!")
        return None
    
    def get_fixture_result(self, home_team: str, away_team: str, date: str) -> Optional[Dict]:
        """
        API'den maç sonucunu getir.
        
        Args:
            home_team: Ev sahibi takım
            away_team: Deplasman takımı
            date: Maç tarihi (YYYY-MM-DD)
        
        Returns:
            Maç sonucu bilgisi veya None
        """
        if not self.api_key:
            print("   ❌ API key bulunamadı!")
            return None
        
        try:
            # Fixture ara
            endpoint = f"{self.api_base_url}/fixtures"
            params = {
                "date": date,
                "status": "FT"  # Finished (tamamlanmış)
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            self.stats['api_calls'] += 1
            
            if response.status_code != 200:
                print(f"   ❌ API hatası: {response.status_code}")
                return None
            
            data = response.json()
            fixtures = data.get('response', [])
            
            # Takım isimlerini eşleştir
            for fixture in fixtures:
                teams = fixture.get('teams', {})
                home = teams.get('home', {}).get('name', '')
                away = teams.get('away', {}).get('name', '')
                
                # Basit eşleştirme (iyileştirilebilir)
                if (home_team.lower() in home.lower() or home.lower() in home_team.lower()) and \
                   (away_team.lower() in away.lower() or away.lower() in away_team.lower()):
                    
                    goals = fixture.get('goals', {})
                    home_goals = goals.get('home', 0)
                    away_goals = goals.get('away', 0)
                    
                    # Sonucu belirle
                    if home_goals > away_goals:
                        result = 2  # Home win
                    elif home_goals < away_goals:
                        result = 0  # Away win
                    else:
                        result = 1  # Draw
                    
                    return {
                        'fixture_id': fixture.get('fixture', {}).get('id'),
                        'home_team': home,
                        'away_team': away,
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'result': result,
                        'status': fixture.get('fixture', {}).get('status', {}).get('short'),
                        'date': fixture.get('fixture', {}).get('date')
                    }
            
            return None
            
        except Exception as e:
            print(f"   ❌ API çağrısı hatası: {e}")
            return None
    
    def check_pending_predictions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Sonucu güncellenmemiş tahminleri kontrol et.
        
        Args:
            start_date: Başlangıç tarihi (YYYY-MM-DD)
            end_date: Bitiş tarihi (YYYY-MM-DD)
            model_name: Sadece belirli model
        """
        print("\n" + "="*80)
        print("🔍 SONUÇ KONTROLÜ BAŞLIYOR")
        print("="*80)
        
        # Pending predictions getir
        query = '''
            SELECT id, home_team, away_team, prediction, confidence, 
                   model_name, timestamp, league
            FROM predictions
            WHERE actual_result IS NULL
        '''
        
        params = []
        
        if start_date:
            query += ' AND DATE(timestamp) >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND DATE(timestamp) <= ?'
            params.append(end_date)
        
        if model_name:
            query += ' AND model_name = ?'
            params.append(model_name)
        
        query += ' ORDER BY timestamp DESC'
        
        # Execute
        self.logger.cursor.execute(query, params)
        pending = self.logger.cursor.fetchall()
        
        print(f"\n📊 Kontrol edilecek tahmin: {len(pending)}")
        
        if not pending:
            print("   ℹ️ Güncellenecek tahmin bulunamadı")
            return
        
        # Her tahmin için kontrol
        for pred in pending:
            pred_id, home_team, away_team, prediction, confidence, \
                model_name_pred, timestamp, league = pred
            
            self.stats['total_checked'] += 1
            
            # Tarih parse
            pred_date = datetime.fromisoformat(timestamp).date()
            date_str = pred_date.strftime('%Y-%m-%d')
            
            print(f"\n{'='*60}")
            print(f"🔍 Kontrol: {home_team} vs {away_team}")
            print(f"   Tarih: {date_str}")
            print(f"   Tahmin: {self._prediction_to_text(prediction)} ({confidence:.2%})")
            
            # API'den sonucu getir
            result = self.get_fixture_result(home_team, away_team, date_str)
            
            if result:
                actual = result['result']
                
                print(f"   Gerçek: {self._prediction_to_text(actual)}")
                print(f"   Skor: {result['home_goals']}-{result['away_goals']}")
                
                # Güncelle
                self.logger.update_actual_result(pred_id, actual)
                
                self.stats['total_updated'] += 1
                
                if prediction == actual:
                    self.stats['total_correct'] += 1
                    print(f"   ✅ DOĞRU TAHMİN!")
                else:
                    self.stats['total_incorrect'] += 1
                    print(f"   ❌ YANLIŞ TAHMİN")
                
                # Sonucu kaydet
                self.results.append({
                    'prediction_id': pred_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': date_str,
                    'prediction': prediction,
                    'actual': actual,
                    'is_correct': (prediction == actual),
                    'confidence': confidence,
                    'model': model_name_pred
                })
                
            else:
                print(f"   ⚠️ Sonuç bulunamadı (henüz oynanmamış veya API'de yok)")
            
            # Rate limiting
            time.sleep(0.5)
        
        # Özet
        self._print_summary()
    
    def check_date_range(
        self,
        start_date: str,
        end_date: str,
        model_name: Optional[str] = None
    ):
        """Belirli tarih aralığındaki tahminleri kontrol et."""
        print(f"\n📅 Tarih aralığı kontrolü: {start_date} - {end_date}")
        self.check_pending_predictions(start_date, end_date, model_name)
    
    def check_yesterday(self, model_name: Optional[str] = None):
        """Dünkü tahminleri kontrol et."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"\n📅 Dünkü tahminler kontrol ediliyor: {yesterday}")
        self.check_pending_predictions(yesterday, yesterday, model_name)
    
    def check_last_n_days(self, days: int = 7, model_name: Optional[str] = None):
        """Son N günün tahminlerini kontrol et."""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"\n📅 Son {days} günün tahminleri kontrol ediliyor")
        self.check_pending_predictions(start_date, end_date, model_name)
    
    def update_model_performance(self):
        """Model performance tablosunu güncelle."""
        print("\n📊 Model performansları güncelleniyor...")
        
        # Tüm modellerin günlük istatistiklerini al
        query = '''
            SELECT 
                model_name,
                DATE(timestamp) as date,
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                AVG(confidence) as avg_confidence
            FROM predictions
            WHERE actual_result IS NOT NULL
            GROUP BY model_name, DATE(timestamp)
        '''
        
        df = pd.read_sql_query(query, self.logger.conn)
        
        # Her satır için performance tablosunu güncelle
        for _, row in df.iterrows():
            accuracy = row['correct'] / row['total'] if row['total'] > 0 else 0
            
            self.logger.cursor.execute('''
                INSERT OR REPLACE INTO model_performance 
                (model_name, date, total_predictions, correct_predictions, accuracy, avg_confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row['model_name'],
                row['date'],
                int(row['total']),
                int(row['correct']),
                accuracy,
                row['avg_confidence']
            ))
        
        self.logger.conn.commit()
        print(f"   ✅ {len(df)} günlük performans kaydı güncellendi")
    
    def generate_report(self, output_path: str = "result_check_report.json"):
        """Kontrol raporu oluştur."""
        print(f"\n📄 Rapor oluşturuluyor: {output_path}")
        
        # Model bazlı istatistikler
        model_stats = self.logger.get_all_models_statistics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'check_stats': self.stats,
            'results': self.results,
            'model_statistics': model_stats,
            'accuracy_by_model': {
                stat['model_name']: {
                    'accuracy': stat['accuracy'],
                    'total': stat['total_predictions'],
                    'correct': stat['correct_predictions']
                }
                for stat in model_stats
            }
        }
        
        # JSON kaydet
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Rapor kaydedildi")
    
    def _print_summary(self):
        """Özet istatistikleri yazdır."""
        print("\n" + "="*80)
        print("📊 ÖZET İSTATİSTİKLER")
        print("="*80)
        
        print(f"\n🔍 Kontrol Edilen: {self.stats['total_checked']}")
        print(f"✅ Güncellenen: {self.stats['total_updated']}")
        print(f"✅ Doğru Tahmin: {self.stats['total_correct']}")
        print(f"❌ Yanlış Tahmin: {self.stats['total_incorrect']}")
        print(f"🌐 API Çağrısı: {self.stats['api_calls']}")
        
        if self.stats['total_updated'] > 0:
            accuracy = self.stats['total_correct'] / self.stats['total_updated']
            print(f"\n📈 Genel Doğruluk: {accuracy:.2%}")
    
    def _prediction_to_text(self, prediction: int) -> str:
        """Tahmin kodunu metne çevir."""
        mapping = {0: "Away Win", 1: "Draw", 2: "Home Win"}
        return mapping.get(prediction, "Unknown")


def main():
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(
        description='Tahmin sonuçlarını kontrol et ve güncelle'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='Başlangıç tarihi (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        help='Bitiş tarihi (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--yesterday',
        action='store_true',
        help='Sadece dünkü tahminleri kontrol et'
    )
    parser.add_argument(
        '--last-days',
        type=int,
        help='Son N günü kontrol et'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Sadece belirli bir modeli kontrol et'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Otomatik mod (dünkü tahminleri kontrol et)'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='predictions.db',
        help='Veritabanı yolu (default: predictions.db)'
    )
    parser.add_argument(
        '--report',
        type=str,
        default='result_check_report.json',
        help='Rapor dosya yolu'
    )
    
    args = parser.parse_args()
    
    # Checker oluştur
    checker = ResultChecker(db_path=args.db_path)
    
    # Mod seçimi
    if args.auto or args.yesterday:
        checker.check_yesterday(model_name=args.model)
    elif args.last_days:
        checker.check_last_n_days(days=args.last_days, model_name=args.model)
    elif args.start_date and args.end_date:
        checker.check_date_range(args.start_date, args.end_date, model_name=args.model)
    else:
        # Default: Son 7 gün
        checker.check_last_n_days(days=7, model_name=args.model)
    
    # Performance güncelle
    checker.update_model_performance()
    
    # Rapor oluştur
    checker.generate_report(output_path=args.report)
    
    # Kapat
    checker.logger.close()
    
    print("\n" + "="*80)
    print("✅ SONUÇ KONTROLÜ TAMAMLANDI")
    print("="*80)


if __name__ == "__main__":
    main()
