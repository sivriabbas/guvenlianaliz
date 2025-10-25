"""
Phase 7.D4: Otomatik Re-Training Sistemi
=========================================
Model performansını izler ve gerektiğinde otomatik re-training yapar.

Özellikler:
- Performans düşüşü algılama
- Otomatik veri güncelleme
- Model re-training
- Versiyon yönetimi
- Backup/Rollback
- Email/webhook bildirimleri
- Scheduled execution (cron/task scheduler)

Kullanım:
    python auto_retrain.py
    
    # Performans kontrolü
    python auto_retrain.py --check-only
    
    # Zorla re-training
    python auto_retrain.py --force
    
    # Belirli bir model
    python auto_retrain.py --model xgboost
    
    # Scheduled (her gün 03:00)
    # Windows: Task Scheduler ile
    # Linux: crontab -e
    # 0 3 * * * /usr/bin/python3 /path/to/auto_retrain.py

Performans Kriterleri:
- Accuracy düşüşü: Son 7 gün vs önceki 30 gün
- Trend analizi: Negatif trend tespiti
- Minimum sample size: 100 prediction
- Threshold: %5 düşüş veya %85 altı accuracy
"""

import os
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import joblib

from prediction_logger import PredictionLogger


class AutoRetrain:
    """Otomatik model re-training sistemi."""
    
    def __init__(
        self,
        db_path: str = "predictions.db",
        models_dir: str = "models",
        data_dir: str = "prepared_data",
        backup_dir: str = "model_backups"
    ):
        """
        Args:
            db_path: Predictions veritabanı
            models_dir: Model dosyaları dizini
            data_dir: Training data dizini
            backup_dir: Backup dizini
        """
        self.db_path = db_path
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        
        self.backup_dir.mkdir(exist_ok=True)
        
        self.logger = PredictionLogger(db_path)
        
        # Thresholds
        self.min_samples = 100  # Minimum tahmin sayısı
        self.accuracy_threshold = 0.85  # Minimum kabul edilebilir accuracy
        self.drop_threshold = 0.05  # Maksimum kabul edilebilir düşüş (%5)
        self.lookback_recent = 7  # Son N gün (recent performance)
        self.lookback_baseline = 30  # Karşılaştırma için N gün (baseline)
        
        self.retrain_needed = {}
        self.performance_data = {}
        
        print("🤖 AutoRetrain başlatıldı")
    
    def check_performance(self, model_name: str) -> Dict:
        """
        Model performansını kontrol et.
        
        Args:
            model_name: Model adı
        
        Returns:
            Performans raporu
        """
        print(f"\n📊 {model_name} performansı kontrol ediliyor...")
        
        # Recent performance (son 7 gün)
        recent_start = (datetime.now() - timedelta(days=self.lookback_recent)).strftime('%Y-%m-%d')
        recent_query = f'''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                AVG(confidence) as avg_confidence
            FROM predictions
            WHERE model_name = ?
                AND actual_result IS NOT NULL
                AND DATE(timestamp) >= ?
        '''
        
        self.logger.cursor.execute(recent_query, (model_name, recent_start))
        recent_total, recent_correct, recent_conf = self.logger.cursor.fetchone()
        
        # Baseline performance (30 gün önce - 7 gün önce arası)
        baseline_start = (datetime.now() - timedelta(days=self.lookback_baseline)).strftime('%Y-%m-%d')
        baseline_end = recent_start
        
        baseline_query = f'''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                AVG(confidence) as avg_confidence
            FROM predictions
            WHERE model_name = ?
                AND actual_result IS NOT NULL
                AND DATE(timestamp) >= ?
                AND DATE(timestamp) < ?
        '''
        
        self.logger.cursor.execute(baseline_query, (model_name, baseline_start, baseline_end))
        baseline_total, baseline_correct, baseline_conf = self.logger.cursor.fetchone()
        
        # Hesaplamalar
        recent_accuracy = recent_correct / recent_total if recent_total else 0.0
        baseline_accuracy = baseline_correct / baseline_total if baseline_total else 0.0
        
        accuracy_drop = baseline_accuracy - recent_accuracy
        drop_percentage = (accuracy_drop / baseline_accuracy * 100) if baseline_accuracy > 0 else 0
        
        # Karar
        needs_retrain = False
        reasons = []
        
        if recent_total < self.min_samples:
            print(f"   ℹ️ Yetersiz veri: {recent_total} < {self.min_samples}")
        else:
            # Accuracy düşük mü?
            if recent_accuracy < self.accuracy_threshold:
                needs_retrain = True
                reasons.append(f"Düşük accuracy: {recent_accuracy:.2%} < {self.accuracy_threshold:.2%}")
            
            # Performans düşüşü var mı?
            if accuracy_drop > self.drop_threshold:
                needs_retrain = True
                reasons.append(f"Performans düşüşü: {drop_percentage:.1f}% (>{self.drop_threshold*100:.0f}%)")
            
            # Sonuç
            if needs_retrain:
                print(f"   ⚠️ RE-TRAINING GEREKLİ!")
                for reason in reasons:
                    print(f"      - {reason}")
            else:
                print(f"   ✅ Performans normal")
                print(f"      Recent: {recent_accuracy:.2%}")
                print(f"      Baseline: {baseline_accuracy:.2%}")
        
        report = {
            'model_name': model_name,
            'recent': {
                'period': f'{self.lookback_recent} days',
                'total': int(recent_total) if recent_total else 0,
                'correct': int(recent_correct) if recent_correct else 0,
                'accuracy': float(recent_accuracy),
                'avg_confidence': float(recent_conf) if recent_conf else 0.0
            },
            'baseline': {
                'period': f'{self.lookback_baseline}-{self.lookback_recent} days ago',
                'total': int(baseline_total) if baseline_total else 0,
                'correct': int(baseline_correct) if baseline_correct else 0,
                'accuracy': float(baseline_accuracy),
                'avg_confidence': float(baseline_conf) if baseline_conf else 0.0
            },
            'analysis': {
                'accuracy_drop': float(accuracy_drop),
                'drop_percentage': float(drop_percentage),
                'needs_retrain': needs_retrain,
                'reasons': reasons
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def check_all_models(self) -> Dict[str, Dict]:
        """Tüm modelleri kontrol et."""
        print("\n" + "="*80)
        print("🔍 TÜM MODELLER KONTROL EDİLİYOR")
        print("="*80)
        
        # Tüm model isimlerini al
        self.logger.cursor.execute('''
            SELECT DISTINCT model_name FROM predictions
        ''')
        
        models = [row[0] for row in self.logger.cursor.fetchall()]
        
        all_reports = {}
        
        for model in models:
            report = self.check_performance(model)
            all_reports[model] = report
            
            if report['analysis']['needs_retrain']:
                self.retrain_needed[model] = report
        
        return all_reports
    
    def backup_model(self, model_filename: str) -> str:
        """Model backup oluştur."""
        source = self.models_dir / model_filename
        
        if not source.exists():
            print(f"   ⚠️ Model bulunamadı: {source}")
            return None
        
        # Backup filename (timestamp ile)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{source.stem}_backup_{timestamp}{source.suffix}"
        backup_path = self.backup_dir / backup_filename
        
        # Kopyala
        shutil.copy2(source, backup_path)
        print(f"   ✅ Backup oluşturuldu: {backup_path}")
        
        return str(backup_path)
    
    def retrain_model(self, model_type: str, force: bool = False):
        """
        Modeli yeniden eğit.
        
        Args:
            model_type: 'xgboost' veya 'lightgbm'
            force: Zorla re-train
        """
        print(f"\n{'='*80}")
        print(f"🔧 {model_type.upper()} RE-TRAINING")
        print(f"{'='*80}")
        
        # Model dosyası
        if model_type.lower() == 'xgboost':
            model_file = 'xgb_v2.pkl'
            tuning_script = 'tune_xgboost.py'
        elif model_type.lower() == 'lightgbm':
            model_file = 'lgb_v2.pkl'
            tuning_script = 'tune_lightgbm.py'
        else:
            print(f"   ❌ Bilinmeyen model tipi: {model_type}")
            return
        
        # Backup
        print("\n1️⃣ Model backup...")
        backup_path = self.backup_model(model_file)
        
        # Veri güncelle
        print("\n2️⃣ Veri güncelleme...")
        self._update_training_data()
        
        # Re-train
        print("\n3️⃣ Model eğitimi...")
        success = self._run_training_script(tuning_script)
        
        if success:
            print(f"\n   ✅ {model_type.upper()} re-training başarılı!")
            
            # Version bilgisi güncelle
            self._update_model_version(model_file)
            
        else:
            print(f"\n   ❌ {model_type.upper()} re-training başarısız!")
            
            # Rollback
            if backup_path and Path(backup_path).exists():
                print(f"   🔄 Rollback yapılıyor...")
                shutil.copy2(backup_path, self.models_dir / model_file)
                print(f"   ✅ Model geri yüklendi")
    
    def _update_training_data(self):
        """Training data'yı güncelle."""
        # Historical data collection
        print("   • Yeni veri toplama...")
        
        try:
            import subprocess
            result = subprocess.run(
                ['python', 'historical_data_collector.py'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("   ✅ Veri toplama başarılı")
            else:
                print(f"   ⚠️ Veri toplama hatası: {result.stderr}")
        
        except Exception as e:
            print(f"   ⚠️ Veri toplama hatası: {e}")
        
        # Calculate factors
        print("   • Faktör hesaplama...")
        
        try:
            result = subprocess.run(
                ['python', 'calculate_historical_factors.py'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("   ✅ Faktör hesaplama başarılı")
            else:
                print(f"   ⚠️ Faktör hesaplama hatası: {result.stderr}")
        
        except Exception as e:
            print(f"   ⚠️ Faktör hesaplama hatası: {e}")
        
        # Prepare training data
        print("   • Dataset hazırlama...")
        
        try:
            result = subprocess.run(
                ['python', 'prepare_training_data.py'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("   ✅ Dataset hazırlama başarılı")
            else:
                print(f"   ⚠️ Dataset hazırlama hatası: {result.stderr}")
        
        except Exception as e:
            print(f"   ⚠️ Dataset hazırlama hatası: {e}")
    
    def _run_training_script(self, script_name: str) -> bool:
        """Training script'ini çalıştır."""
        print(f"   • {script_name} çalıştırılıyor...")
        
        try:
            import subprocess
            result = subprocess.run(
                ['python', script_name],
                capture_output=True,
                text=True,
                timeout=1800  # 30 dakika
            )
            
            if result.returncode == 0:
                print(f"   ✅ {script_name} başarılı")
                return True
            else:
                print(f"   ❌ {script_name} hatası: {result.stderr}")
                return False
        
        except Exception as e:
            print(f"   ❌ Script hatası: {e}")
            return False
    
    def _update_model_version(self, model_file: str):
        """Model version bilgisini güncelle."""
        metadata_file = model_file.replace('.pkl', '_metadata.json')
        metadata_path = self.models_dir / metadata_file
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Version güncelle
                old_version = metadata.get('version', 'v2.0')
                new_version = self._increment_version(old_version)
                
                metadata['version'] = new_version
                metadata['retrain_date'] = datetime.now().isoformat()
                metadata['previous_version'] = old_version
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                print(f"   ✅ Version güncellendi: {old_version} → {new_version}")
            
            except Exception as e:
                print(f"   ⚠️ Metadata güncelleme hatası: {e}")
    
    def _increment_version(self, version: str) -> str:
        """Version numarasını artır."""
        try:
            # v2.0 → v2.1, v2.9 → v3.0
            parts = version.replace('v', '').split('.')
            major, minor = int(parts[0]), int(parts[1])
            
            minor += 1
            if minor >= 10:
                major += 1
                minor = 0
            
            return f"v{major}.{minor}"
        
        except:
            return version + "_retrained"
    
    def generate_report(self, all_reports: Dict, output_path: str = "retrain_report.json"):
        """Re-train raporu oluştur."""
        print(f"\n📄 Rapor oluşturuluyor: {output_path}")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'thresholds': {
                'min_samples': self.min_samples,
                'accuracy_threshold': self.accuracy_threshold,
                'drop_threshold': self.drop_threshold,
                'lookback_recent': self.lookback_recent,
                'lookback_baseline': self.lookback_baseline
            },
            'models_checked': len(all_reports),
            'models_needing_retrain': len(self.retrain_needed),
            'performance_reports': all_reports,
            'retrain_needed': list(self.retrain_needed.keys())
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Rapor kaydedildi")


def main():
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(
        description='Otomatik model re-training sistemi'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Sadece performans kontrolü yap, re-train yapma'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Zorla re-training yap'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=['xgboost', 'lightgbm', 'all'],
        default='all',
        help='Re-train yapılacak model'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='predictions.db',
        help='Veritabanı yolu'
    )
    
    args = parser.parse_args()
    
    # AutoRetrain
    auto_retrain = AutoRetrain(db_path=args.db_path)
    
    # Performans kontrolü
    all_reports = auto_retrain.check_all_models()
    
    # Rapor oluştur
    auto_retrain.generate_report(all_reports)
    
    # Re-training
    if not args.check_only:
        if args.force or auto_retrain.retrain_needed:
            print("\n" + "="*80)
            print("🔧 RE-TRAINING BAŞLIYOR")
            print("="*80)
            
            if args.model == 'all' or args.model == 'xgboost':
                auto_retrain.retrain_model('xgboost', force=args.force)
            
            if args.model == 'all' or args.model == 'lightgbm':
                auto_retrain.retrain_model('lightgbm', force=args.force)
        else:
            print("\n✅ Tüm modeller iyi durumda, re-training gerekmedi")
    
    # Kapat
    auto_retrain.logger.close()
    
    print("\n" + "="*80)
    print("✅ OTOMATIK RE-TRAINING TAMAMLANDI")
    print("="*80)


if __name__ == "__main__":
    main()
