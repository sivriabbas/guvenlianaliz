"""
Phase 7.D1: Tahmin Kayıt Sistemi
=================================
Yapılan tahminleri SQLite veritabanına kaydeder ve yönetir.

Özellikler:
- SQLite database ile tahmin saklama
- Timestamp ve model bilgisi
- Güven skorları ve olasılık dağılımları
- Maç detayları ve lig bilgisi
- Tahmin geçmişi sorgulama
- CSV/JSON export

Kullanım:
    from prediction_logger import PredictionLogger
    
    logger = PredictionLogger()
    logger.log_prediction(
        home_team="Galatasaray",
        away_team="Fenerbahçe",
        prediction=1,
        confidence=0.85,
        model_name="Ensemble_Weighted"
    )

Database Schema:
    predictions (
        id INTEGER PRIMARY KEY,
        timestamp DATETIME,
        home_team TEXT,
        away_team TEXT,
        league TEXT,
        prediction INTEGER,
        confidence REAL,
        probabilities TEXT,
        model_name TEXT,
        model_version TEXT,
        features TEXT,
        actual_result INTEGER,
        is_correct BOOLEAN,
        created_at DATETIME
    )
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class PredictionLogger:
    """Tahminleri veritabanına kaydeder ve yönetir."""
    
    def __init__(self, db_path: str = "predictions.db"):
        """
        Args:
            db_path: SQLite veritabanı dosya yolu
        """
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        
        # Veritabanını başlat
        self._initialize_database()
        
        print(f"📊 PredictionLogger başlatıldı: {self.db_path}")
    
    def _initialize_database(self):
        """Veritabanını ve tabloları oluştur."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Predictions tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                league TEXT,
                prediction INTEGER NOT NULL,
                confidence REAL,
                probabilities TEXT,
                model_name TEXT NOT NULL,
                model_version TEXT,
                features TEXT,
                actual_result INTEGER,
                is_correct BOOLEAN,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Model performance tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                date DATE NOT NULL,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy REAL,
                avg_confidence REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(model_name, date)
            )
        ''')
        
        # İndeksler
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON predictions(timestamp)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_model_name 
            ON predictions(model_name)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_actual_result 
            ON predictions(actual_result)
        ''')
        
        self.conn.commit()
        print("   ✅ Veritabanı hazır")
    
    def log_prediction(
        self,
        home_team: str,
        away_team: str,
        prediction: int,
        confidence: float,
        model_name: str,
        league: Optional[str] = None,
        probabilities: Optional[List[float]] = None,
        model_version: Optional[str] = None,
        features: Optional[Dict] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Tahmin kaydı oluştur.
        
        Args:
            home_team: Ev sahibi takım
            away_team: Deplasman takımı
            prediction: Tahmin (0: Away, 1: Draw, 2: Home)
            confidence: Güven skoru (0-1)
            model_name: Model adı
            league: Lig adı
            probabilities: Olasılık dağılımı [away, draw, home]
            model_version: Model versiyonu
            features: Feature değerleri
            notes: Notlar
        
        Returns:
            Prediction ID
        """
        timestamp = datetime.now()
        
        # Probabilities JSON'a çevir
        proba_json = json.dumps(probabilities) if probabilities else None
        
        # Features JSON'a çevir
        features_json = json.dumps(features) if features else None
        
        # Insert
        self.cursor.execute('''
            INSERT INTO predictions (
                timestamp, home_team, away_team, league,
                prediction, confidence, probabilities,
                model_name, model_version, features, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, home_team, away_team, league,
            prediction, confidence, proba_json,
            model_name, model_version, features_json, notes
        ))
        
        self.conn.commit()
        prediction_id = self.cursor.lastrowid
        
        print(f"   ✅ Tahmin kaydedildi (ID: {prediction_id})")
        print(f"      {home_team} vs {away_team}")
        print(f"      Tahmin: {self._prediction_to_text(prediction)}")
        print(f"      Güven: {confidence:.2%}")
        
        return prediction_id
    
    def update_actual_result(
        self,
        prediction_id: int,
        actual_result: int
    ) -> bool:
        """
        Gerçek sonucu güncelle.
        
        Args:
            prediction_id: Tahmin ID
            actual_result: Gerçek sonuç (0: Away, 1: Draw, 2: Home)
        
        Returns:
            Başarılı mı
        """
        # Tahmin bilgisini al
        self.cursor.execute('''
            SELECT prediction FROM predictions WHERE id = ?
        ''', (prediction_id,))
        
        result = self.cursor.fetchone()
        if not result:
            print(f"   ❌ Tahmin bulunamadı (ID: {prediction_id})")
            return False
        
        prediction = result[0]
        is_correct = (prediction == actual_result)
        
        # Güncelle
        self.cursor.execute('''
            UPDATE predictions 
            SET actual_result = ?, is_correct = ?
            WHERE id = ?
        ''', (actual_result, is_correct, prediction_id))
        
        self.conn.commit()
        
        status = "✅ Doğru" if is_correct else "❌ Yanlış"
        print(f"   {status} - Gerçek sonuç güncellendi (ID: {prediction_id})")
        
        return True
    
    def get_prediction(self, prediction_id: int) -> Optional[Dict]:
        """Tahmin detaylarını getir."""
        self.cursor.execute('''
            SELECT * FROM predictions WHERE id = ?
        ''', (prediction_id,))
        
        row = self.cursor.fetchone()
        if not row:
            return None
        
        columns = [desc[0] for desc in self.cursor.description]
        prediction = dict(zip(columns, row))
        
        # JSON alanları parse et
        if prediction['probabilities']:
            prediction['probabilities'] = json.loads(prediction['probabilities'])
        if prediction['features']:
            prediction['features'] = json.loads(prediction['features'])
        
        return prediction
    
    def get_recent_predictions(
        self,
        limit: int = 10,
        model_name: Optional[str] = None
    ) -> List[Dict]:
        """Son tahminleri getir."""
        query = 'SELECT * FROM predictions'
        params = []
        
        if model_name:
            query += ' WHERE model_name = ?'
            params.append(model_name)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        self.cursor.execute(query, params)
        
        columns = [desc[0] for desc in self.cursor.description]
        predictions = []
        
        for row in self.cursor.fetchall():
            pred = dict(zip(columns, row))
            
            # JSON parse
            if pred['probabilities']:
                pred['probabilities'] = json.loads(pred['probabilities'])
            if pred['features']:
                pred['features'] = json.loads(pred['features'])
            
            predictions.append(pred)
        
        return predictions
    
    def get_model_statistics(self, model_name: str) -> Dict:
        """Model istatistiklerini getir."""
        # Toplam tahmin sayısı
        self.cursor.execute('''
            SELECT COUNT(*) FROM predictions WHERE model_name = ?
        ''', (model_name,))
        total = self.cursor.fetchone()[0]
        
        # Doğru tahmin sayısı
        self.cursor.execute('''
            SELECT COUNT(*) FROM predictions 
            WHERE model_name = ? AND is_correct = 1
        ''', (model_name,))
        correct = self.cursor.fetchone()[0]
        
        # Ortalama güven
        self.cursor.execute('''
            SELECT AVG(confidence) FROM predictions WHERE model_name = ?
        ''', (model_name,))
        avg_confidence = self.cursor.fetchone()[0] or 0.0
        
        # Sınıf bazlı doğruluk
        class_accuracy = {}
        for pred_class in [0, 1, 2]:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM predictions 
                WHERE model_name = ? AND prediction = ? AND actual_result IS NOT NULL
            ''', (model_name, pred_class))
            
            total_class, correct_class = self.cursor.fetchone()
            if total_class > 0:
                class_accuracy[pred_class] = correct_class / total_class
        
        accuracy = correct / total if total > 0 else 0.0
        
        stats = {
            'model_name': model_name,
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'class_accuracy': class_accuracy
        }
        
        return stats
    
    def get_all_models_statistics(self) -> List[Dict]:
        """Tüm modellerin istatistiklerini getir."""
        # Tüm model isimlerini al
        self.cursor.execute('''
            SELECT DISTINCT model_name FROM predictions
        ''')
        
        models = [row[0] for row in self.cursor.fetchall()]
        
        all_stats = []
        for model in models:
            stats = self.get_model_statistics(model)
            all_stats.append(stats)
        
        # Accuracy'ye göre sırala
        all_stats.sort(key=lambda x: x['accuracy'], reverse=True)
        
        return all_stats
    
    def export_to_csv(self, filepath: str, model_name: Optional[str] = None):
        """Tahminleri CSV'ye export et."""
        query = 'SELECT * FROM predictions'
        
        if model_name:
            df = pd.read_sql_query(
                query + ' WHERE model_name = ?',
                self.conn,
                params=[model_name]
            )
        else:
            df = pd.read_sql_query(query, self.conn)
        
        df.to_csv(filepath, index=False)
        print(f"   ✅ CSV export: {filepath} ({len(df)} kayıt)")
    
    def export_to_json(self, filepath: str, model_name: Optional[str] = None):
        """Tahminleri JSON'a export et."""
        if model_name:
            predictions = self.get_recent_predictions(limit=999999, model_name=model_name)
        else:
            predictions = self.get_recent_predictions(limit=999999)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(predictions, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   ✅ JSON export: {filepath} ({len(predictions)} kayıt)")
    
    def get_daily_accuracy(self, days: int = 7) -> pd.DataFrame:
        """Günlük doğruluk oranlarını getir."""
        query = '''
            SELECT 
                DATE(timestamp) as date,
                model_name,
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                CAST(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as accuracy
            FROM predictions
            WHERE actual_result IS NOT NULL
                AND timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp), model_name
            ORDER BY date DESC, accuracy DESC
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[days])
        return df
    
    def cleanup_old_predictions(self, days: int = 90):
        """Eski tahminleri temizle."""
        self.cursor.execute('''
            DELETE FROM predictions 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        deleted = self.cursor.rowcount
        self.conn.commit()
        
        print(f"   ✅ {deleted} eski tahmin silindi ({days} günden eski)")
    
    def _prediction_to_text(self, prediction: int) -> str:
        """Tahmin kodunu metne çevir."""
        mapping = {0: "Away Win", 1: "Draw", 2: "Home Win"}
        return mapping.get(prediction, "Unknown")
    
    def close(self):
        """Veritabanı bağlantısını kapat."""
        if self.conn:
            self.conn.close()
            print("   ✅ Veritabanı bağlantısı kapatıldı")
    
    def __enter__(self):
        """Context manager girişi."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager çıkışı."""
        self.close()


def main():
    """Test ve örnek kullanım."""
    print("\n" + "="*80)
    print("📊 PREDICTION LOGGER - TEST")
    print("="*80)
    
    # Logger oluştur
    logger = PredictionLogger("test_predictions.db")
    
    # Örnek tahminler
    print("\n1️⃣ Tahmin kaydetme:")
    
    pred_id = logger.log_prediction(
        home_team="Galatasaray",
        away_team="Fenerbahçe",
        prediction=2,
        confidence=0.85,
        probabilities=[0.05, 0.10, 0.85],
        model_name="Ensemble_Weighted",
        league="Süper Lig",
        model_version="v2.0"
    )
    
    logger.log_prediction(
        home_team="Beşiktaş",
        away_team="Trabzonspor",
        prediction=1,
        confidence=0.65,
        probabilities=[0.20, 0.65, 0.15],
        model_name="XGBoost_v2",
        league="Süper Lig"
    )
    
    # Gerçek sonucu güncelle
    print("\n2️⃣ Gerçek sonuç güncelleme:")
    logger.update_actual_result(pred_id, actual_result=2)  # Doğru tahmin
    
    # Son tahminler
    print("\n3️⃣ Son tahminler:")
    recent = logger.get_recent_predictions(limit=5)
    for pred in recent:
        print(f"   • {pred['home_team']} vs {pred['away_team']}")
        print(f"     Model: {pred['model_name']}")
        print(f"     Tahmin: {logger._prediction_to_text(pred['prediction'])}")
        print(f"     Güven: {pred['confidence']:.2%}")
        if pred['is_correct'] is not None:
            status = "✅" if pred['is_correct'] else "❌"
            print(f"     Sonuç: {status}")
        print()
    
    # Model istatistikleri
    print("\n4️⃣ Model istatistikleri:")
    all_stats = logger.get_all_models_statistics()
    for stats in all_stats:
        print(f"\n   📊 {stats['model_name']}:")
        print(f"      Toplam: {stats['total_predictions']}")
        print(f"      Doğru: {stats['correct_predictions']}")
        print(f"      Accuracy: {stats['accuracy']:.2%}")
        print(f"      Avg Confidence: {stats['avg_confidence']:.2%}")
    
    # Export
    print("\n5️⃣ Export:")
    logger.export_to_csv("predictions_export.csv")
    logger.export_to_json("predictions_export.json")
    
    # Günlük accuracy
    print("\n6️⃣ Günlük accuracy:")
    daily_acc = logger.get_daily_accuracy(days=7)
    if not daily_acc.empty:
        print(daily_acc.to_string(index=False))
    
    # Kapat
    logger.close()
    
    print("\n" + "="*80)
    print("✅ TEST TAMAMLANDI")
    print("="*80)


if __name__ == "__main__":
    main()
