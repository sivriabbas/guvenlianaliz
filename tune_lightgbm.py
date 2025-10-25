"""
🎯 PHASE 7.B3: LIGHTGBM HYPERPARAMETER TUNING
Optuna ile LightGBM modelini optimize eder
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
import optuna
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report, confusion_matrix
import json
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Optuna loglarını sessizleştir
optuna.logging.set_verbosity(optuna.logging.WARNING)

class LightGBMTuner:
    """LightGBM model tuning ve değerlendirme sınıfı"""
    
    def __init__(self, data_dir='prepared_data', model_dir='models', n_trials=100):
        """
        Args:
            data_dir: Hazırlanmış veri dizini
            model_dir: Model kayıt dizini
            n_trials: Optuna trial sayısı
        """
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.n_trials = n_trials
        
        # Dizinleri oluştur
        os.makedirs(model_dir, exist_ok=True)
        
        print("="*80)
        print("🎯 LIGHTGBM HYPERPARAMETER TUNING (OPTUNA)")
        print("="*80)
    
    def load_data(self):
        """Hazırlanmış veriyi yükle"""
        print("\n📥 Veri yükleniyor...")
        
        try:
            # NumPy dizilerini yükle
            self.X_train = np.load(f'{self.data_dir}/X_train.npy')
            self.X_test = np.load(f'{self.data_dir}/X_test.npy')
            self.y_train = np.load(f'{self.data_dir}/y_train.npy')
            self.y_test = np.load(f'{self.data_dir}/y_test.npy')
            
            # Metadata yükle
            with open(f'{self.data_dir}/metadata.json', 'r') as f:
                self.metadata = json.load(f)
            
            # Feature isimleri yükle
            with open(f'{self.data_dir}/feature_names.json', 'r') as f:
                self.feature_names = json.load(f)
            
            print(f"✅ Veri yüklendi:")
            print(f"   Train: {self.X_train.shape[0]} samples, {self.X_train.shape[1]} features")
            print(f"   Test: {self.X_test.shape[0]} samples")
            print(f"   Features: {len(self.feature_names)}")
            
            # Sınıf dağılımı
            unique, counts = np.unique(self.y_train, return_counts=True)
            print(f"\n📊 Sınıf Dağılımı (Train):")
            for label, count in zip(unique, counts):
                label_name = {0: 'Deplasman', 1: 'Beraberlik', 2: 'Ev Sahibi'}[label]
                print(f"   {label_name}: {count} ({count/len(self.y_train)*100:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ Veri yükleme hatası: {e}")
            print(f"⚠️ Lütfen önce prepare_training_data.py çalıştırın!")
            return False
    
    def baseline_performance(self):
        """Baseline model performansını ölç"""
        print("\n📊 Baseline model performansı ölçülüyor...")
        
        # Varsayılan parametrelerle model
        baseline_model = lgb.LGBMClassifier(
            objective='multiclass',
            num_class=3,
            random_state=42,
            verbose=-1
        )
        
        # Eğit
        baseline_model.fit(self.X_train, self.y_train)
        
        # Tahmin
        y_pred = baseline_model.predict(self.X_test)
        
        # Metrikler
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, average='weighted')
        recall = recall_score(self.y_test, y_pred, average='weighted')
        f1 = f1_score(self.y_test, y_pred, average='weighted')
        
        self.baseline_metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
        
        print(f"✅ Baseline Performans:")
        print(f"   Accuracy:  {accuracy:.4f}")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   F1-Score:  {f1:.4f}")
        
        return baseline_model
    
    def objective(self, trial):
        """Optuna objective fonksiyonu"""
        # Hyperparameter önerileri
        params = {
            'objective': 'multiclass',
            'num_class': 3,
            'metric': 'multi_logloss',
            'verbosity': -1,
            'random_state': 42,
            
            # Tuning parametreleri
            'num_leaves': trial.suggest_int('num_leaves', 20, 150),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 50, 500),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
            'min_split_gain': trial.suggest_float('min_split_gain', 0.0, 1.0),
        }
        
        # Model oluştur
        model = lgb.LGBMClassifier(**params)
        
        # 5-fold cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_val_score(model, self.X_train, self.y_train, 
                                 cv=cv, scoring='accuracy', n_jobs=-1)
        
        return scores.mean()
    
    def optuna_tuning(self):
        """Optuna ile hyperparameter tuning"""
        print(f"\n🔍 Optuna optimization başlatılıyor...")
        print(f"🎯 Trial sayısı: {self.n_trials}")
        print(f"⏳ Bu işlem 10-20 dakika sürebilir...\n")
        
        # Optuna study oluştur
        self.study = optuna.create_study(
            direction='maximize',
            study_name='lightgbm_tuning',
            sampler=optuna.samplers.TPESampler(seed=42)
        )
        
        # Optimize et
        start_time = datetime.now()
        self.study.optimize(
            self.objective, 
            n_trials=self.n_trials,
            show_progress_bar=True,
            n_jobs=1  # LightGBM zaten paralel çalışıyor
        )
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✅ Optuna optimization tamamlandı!")
        print(f"⏱️ Süre: {duration/60:.1f} dakika")
        print(f"\n🏆 En İyi Parametreler:")
        for param, value in self.study.best_params.items():
            print(f"   • {param}: {value}")
        print(f"\n📊 En İyi CV Skoru: {self.study.best_value:.4f}")
        
        # Trial istatistikleri
        print(f"\n📈 Trial İstatistikleri:")
        print(f"   • Toplam trial: {len(self.study.trials)}")
        print(f"   • Tamamlanan: {len([t for t in self.study.trials if t.state == optuna.trial.TrialState.COMPLETE])}")
        print(f"   • Başarısız: {len([t for t in self.study.trials if t.state == optuna.trial.TrialState.FAIL])}")
        
        # En iyi 5 trial
        print(f"\n🔝 En İyi 5 Trial:")
        for i, trial in enumerate(sorted(self.study.trials, key=lambda t: t.value if t.value else 0, reverse=True)[:5], 1):
            if trial.value:
                print(f"   {i}. Trial #{trial.number}: {trial.value:.4f}")
    
    def train_best_model(self):
        """En iyi parametrelerle final model eğit"""
        print("\n🎯 En iyi parametrelerle final model eğitiliyor...")
        
        # En iyi parametreleri al
        best_params = self.study.best_params.copy()
        best_params.update({
            'objective': 'multiclass',
            'num_class': 3,
            'metric': 'multi_logloss',
            'verbosity': -1,
            'random_state': 42
        })
        
        # Final model
        self.best_model = lgb.LGBMClassifier(**best_params)
        
        # Tam train set ile eğit
        self.best_model.fit(
            self.X_train, 
            self.y_train,
            eval_set=[(self.X_test, self.y_test)],
            eval_metric='multi_logloss',
            callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
        )
        
        print(f"✅ Final model eğitildi!")
    
    def evaluate_best_model(self):
        """En iyi modeli test setinde değerlendir"""
        print("\n📊 Test seti performansı değerlendiriliyor...")
        
        # Test seti tahminleri
        y_pred = self.best_model.predict(self.X_test)
        y_pred_proba = self.best_model.predict_proba(self.X_test)
        
        # Metrikler
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, average='weighted')
        recall = recall_score(self.y_test, y_pred, average='weighted')
        f1 = f1_score(self.y_test, y_pred, average='weighted')
        
        self.tuned_metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
        
        print(f"\n✅ Tuned Model Performansı:")
        print(f"   Accuracy:  {accuracy:.4f}")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   F1-Score:  {f1:.4f}")
        
        # Baseline ile karşılaştırma
        print(f"\n📈 İyileşme (Baseline → Tuned):")
        for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
            baseline = self.baseline_metrics[metric]
            tuned = self.tuned_metrics[metric]
            improvement = ((tuned - baseline) / baseline) * 100
            print(f"   {metric.capitalize():12s}: {baseline:.4f} → {tuned:.4f} ({improvement:+.2f}%)")
        
        # Confusion Matrix
        cm = confusion_matrix(self.y_test, y_pred)
        print(f"\n📊 Confusion Matrix:")
        print(f"   Tahmin →  Deplasman  Beraberlik  Ev Sahibi")
        labels = ['Deplasman', 'Beraberlik', 'Ev Sahibi']
        for i, label in enumerate(labels):
            print(f"   {label:12s}  {cm[i][0]:6d}     {cm[i][1]:6d}     {cm[i][2]:6d}")
        
        # Classification Report
        print(f"\n📋 Sınıf Bazlı Performans:")
        report = classification_report(self.y_test, y_pred, 
                                      target_names=labels, 
                                      digits=4)
        print(report)
        
        return y_pred, y_pred_proba
    
    def analyze_feature_importance(self):
        """Feature importance analizi"""
        print("\n📊 Feature Importance analizi...")
        
        # Feature importances
        importances = self.best_model.feature_importances_
        
        # Sırala
        indices = np.argsort(importances)[::-1]
        
        # En önemli 15 feature
        print(f"\n🔝 En Önemli 15 Feature:")
        for i in range(min(15, len(indices))):
            idx = indices[i]
            print(f"   {i+1:2d}. {self.feature_names[idx]:30s} {importances[idx]:.4f}")
        
        # Feature importance dictionary
        self.feature_importance = {
            self.feature_names[i]: float(importances[i]) 
            for i in range(len(importances))
        }
    
    def save_model(self):
        """Tuned modeli kaydet"""
        print(f"\n💾 Model kaydediliyor...")
        
        # Model dosya yolu
        model_path = f'{self.model_dir}/lgb_v2.pkl'
        
        # Model kaydet
        with open(model_path, 'wb') as f:
            pickle.dump(self.best_model, f)
        
        print(f"✅ Model kaydedildi: {model_path}")
        
        # Metadata oluştur
        metadata = {
            'model_name': 'LightGBM v2 (Tuned)',
            'model_type': 'LGBMClassifier',
            'version': '2.0',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'training_samples': int(self.X_train.shape[0]),
            'test_samples': int(self.X_test.shape[0]),
            'n_features': int(self.X_train.shape[1]),
            'feature_names': self.feature_names,
            'best_params': self.study.best_params,
            'cv_score': float(self.study.best_value),
            'n_trials': self.n_trials,
            'baseline_metrics': {k: float(v) for k, v in self.baseline_metrics.items()},
            'tuned_metrics': {k: float(v) for k, v in self.tuned_metrics.items()},
            'feature_importance': self.feature_importance,
            'improvement': {
                metric: float(((self.tuned_metrics[metric] - self.baseline_metrics[metric]) 
                              / self.baseline_metrics[metric]) * 100)
                for metric in ['accuracy', 'precision', 'recall', 'f1_score']
            }
        }
        
        # Metadata kaydet
        metadata_path = f'{self.model_dir}/lgb_v2_metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadata kaydedildi: {metadata_path}")
        
        return model_path, metadata_path
    
    def generate_report(self):
        """Tuning raporu oluştur"""
        print(f"\n📄 Rapor oluşturuluyor...")
        
        report = {
            'tuning_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model': 'LightGBM v2',
            'method': 'Optuna (TPE Sampler)',
            'cv_folds': 5,
            'n_trials': self.n_trials,
            'best_params': self.study.best_params,
            'best_cv_score': float(self.study.best_value),
            'baseline_performance': {k: float(v) for k, v in self.baseline_metrics.items()},
            'tuned_performance': {k: float(v) for k, v in self.tuned_metrics.items()},
            'improvement': {
                metric: float(((self.tuned_metrics[metric] - self.baseline_metrics[metric]) 
                              / self.baseline_metrics[metric]) * 100)
                for metric in ['accuracy', 'precision', 'recall', 'f1_score']
            },
            'top_features': [
                {
                    'name': name,
                    'importance': float(importance)
                }
                for name, importance in sorted(
                    self.feature_importance.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:15]
            ],
            'trial_stats': {
                'total': len(self.study.trials),
                'completed': len([t for t in self.study.trials if t.state == optuna.trial.TrialState.COMPLETE]),
                'failed': len([t for t in self.study.trials if t.state == optuna.trial.TrialState.FAIL])
            }
        }
        
        # Rapor kaydet
        report_path = 'lightgbm_tuning_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Rapor kaydedildi: {report_path}")
        
        return report
    
    def run_full_tuning(self):
        """Tam tuning pipeline'ını çalıştır"""
        print("\n" + "🚀"*40)
        print("LIGHTGBM HYPERPARAMETER TUNING BAŞLATILIYOR")
        print("🚀"*40 + "\n")
        
        # 1. Veri yükle
        if not self.load_data():
            return False
        
        # 2. Baseline performans
        self.baseline_performance()
        
        # 3. Optuna tuning
        self.optuna_tuning()
        
        # 4. En iyi modeli eğit
        self.train_best_model()
        
        # 5. En iyi modeli değerlendir
        self.evaluate_best_model()
        
        # 6. Feature importance
        self.analyze_feature_importance()
        
        # 7. Model kaydet
        model_path, metadata_path = self.save_model()
        
        # 8. Rapor oluştur
        report = self.generate_report()
        
        # Final özet
        print("\n" + "="*80)
        print("✅ LIGHTGBM TUNING TAMAMLANDI!")
        print("="*80)
        print(f"\n📊 Final Sonuçlar:")
        print(f"   Baseline Accuracy: {self.baseline_metrics['accuracy']:.4f}")
        print(f"   Tuned Accuracy:    {self.tuned_metrics['accuracy']:.4f}")
        print(f"   İyileşme:          {report['improvement']['accuracy']:+.2f}%")
        print(f"\n💾 Kaydedilen Dosyalar:")
        print(f"   • {model_path}")
        print(f"   • {metadata_path}")
        print(f"   • lightgbm_tuning_report.json")
        print(f"\n🎯 Sıradaki Adım: evaluate_models.py (Phase 7.B4)")
        print("="*80 + "\n")
        
        return True

def main():
    """Ana fonksiyon"""
    # Tuner oluştur (100 trial - hızlı test için azaltılabilir)
    tuner = LightGBMTuner(n_trials=100)
    
    # Tuning çalıştır
    success = tuner.run_full_tuning()
    
    if success:
        print("✅ Tüm işlemler başarıyla tamamlandı!")
    else:
        print("❌ Tuning başarısız oldu. Lütfen hataları kontrol edin.")

if __name__ == "__main__":
    main()
