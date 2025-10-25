"""
🎯 PHASE 7.B2: XGBOOST HYPERPARAMETER TUNING
GridSearchCV ile XGBoost modelini optimize eder
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report, confusion_matrix
import json
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class XGBoostTuner:
    """XGBoost model tuning ve değerlendirme sınıfı"""
    
    def __init__(self, data_dir='prepared_data', model_dir='models'):
        """
        Args:
            data_dir: Hazırlanmış veri dizini
            model_dir: Model kayıt dizini
        """
        self.data_dir = data_dir
        self.model_dir = model_dir
        
        # Dizinleri oluştur
        os.makedirs(model_dir, exist_ok=True)
        
        print("="*80)
        print("🎯 XGBOOST HYPERPARAMETER TUNING")
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
    
    def define_param_grid(self):
        """Hyperparameter arama uzayını tanımla"""
        print("\n🔍 Hyperparameter arama uzayı tanımlanıyor...")
        
        # XGBoost için parametre grid'i
        self.param_grid = {
            'max_depth': [3, 4, 5, 6],              # Ağaç derinliği
            'learning_rate': [0.01, 0.05, 0.1],     # Öğrenme oranı
            'n_estimators': [100, 200, 300],        # Ağaç sayısı
            'subsample': [0.7, 0.8, 0.9],           # Veri alt örnekleme
            'colsample_bytree': [0.7, 0.8, 0.9],    # Özellik alt örnekleme
            'min_child_weight': [1, 3, 5],          # Minimum leaf weight
            'gamma': [0, 0.1, 0.2],                 # Minimum loss reduction
            'reg_alpha': [0, 0.01, 0.1],            # L1 regularization
            'reg_lambda': [1, 1.5, 2]               # L2 regularization
        }
        
        # Toplam kombinasyon sayısı
        total_combinations = 1
        for values in self.param_grid.values():
            total_combinations *= len(values)
        
        print(f"✅ Parametre grid tanımlandı:")
        for param, values in self.param_grid.items():
            print(f"   • {param}: {values}")
        print(f"\n📊 Toplam kombinasyon: {total_combinations:,}")
        print(f"⏱️ Tahmini süre: ~{total_combinations * 0.5 / 60:.0f} dakika (CV=5)")
    
    def baseline_performance(self):
        """Baseline model performansını ölç"""
        print("\n📊 Baseline model performansı ölçülüyor...")
        
        # Varsayılan parametrelerle model
        baseline_model = xgb.XGBClassifier(
            objective='multi:softmax',
            num_class=3,
            random_state=42,
            eval_metric='mlogloss'
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
    
    def grid_search_tuning(self):
        """GridSearchCV ile hyperparameter tuning"""
        print("\n🔍 GridSearchCV başlatılıyor...")
        print("⏳ Bu işlem uzun sürebilir (15-30 dakika)...\n")
        
        # Base model
        base_model = xgb.XGBClassifier(
            objective='multi:softmax',
            num_class=3,
            random_state=42,
            eval_metric='mlogloss',
            use_label_encoder=False
        )
        
        # Stratified K-Fold cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        # GridSearchCV
        self.grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=self.param_grid,
            cv=cv,
            scoring='accuracy',
            n_jobs=-1,  # Tüm CPU'ları kullan
            verbose=2,
            return_train_score=True
        )
        
        # Fit
        start_time = datetime.now()
        self.grid_search.fit(self.X_train, self.y_train)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✅ GridSearchCV tamamlandı!")
        print(f"⏱️ Süre: {duration/60:.1f} dakika")
        print(f"\n🏆 En İyi Parametreler:")
        for param, value in self.grid_search.best_params_.items():
            print(f"   • {param}: {value}")
        print(f"\n📊 En İyi CV Skoru: {self.grid_search.best_score_:.4f}")
    
    def evaluate_best_model(self):
        """En iyi modeli test setinde değerlendir"""
        print("\n📊 Test seti performansı değerlendiriliyor...")
        
        # En iyi model
        self.best_model = self.grid_search.best_estimator_
        
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
        model_path = f'{self.model_dir}/xgb_v2.pkl'
        
        # Model kaydet
        with open(model_path, 'wb') as f:
            pickle.dump(self.best_model, f)
        
        print(f"✅ Model kaydedildi: {model_path}")
        
        # Metadata oluştur
        metadata = {
            'model_name': 'XGBoost v2 (Tuned)',
            'model_type': 'XGBClassifier',
            'version': '2.0',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'training_samples': int(self.X_train.shape[0]),
            'test_samples': int(self.X_test.shape[0]),
            'n_features': int(self.X_train.shape[1]),
            'feature_names': self.feature_names,
            'best_params': self.grid_search.best_params_,
            'cv_score': float(self.grid_search.best_score_),
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
        metadata_path = f'{self.model_dir}/xgb_v2_metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metadata kaydedildi: {metadata_path}")
        
        return model_path, metadata_path
    
    def generate_report(self):
        """Tuning raporu oluştur"""
        print(f"\n📄 Rapor oluşturuluyor...")
        
        report = {
            'tuning_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model': 'XGBoost v2',
            'method': 'GridSearchCV',
            'cv_folds': 5,
            'total_combinations': len(self.grid_search.cv_results_['params']),
            'best_params': self.grid_search.best_params_,
            'best_cv_score': float(self.grid_search.best_score_),
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
            ]
        }
        
        # Rapor kaydet
        report_path = 'xgboost_tuning_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Rapor kaydedildi: {report_path}")
        
        return report
    
    def run_full_tuning(self):
        """Tam tuning pipeline'ını çalıştır"""
        print("\n" + "🚀"*40)
        print("XGBOOST HYPERPARAMETER TUNING BAŞLATILIYOR")
        print("🚀"*40 + "\n")
        
        # 1. Veri yükle
        if not self.load_data():
            return False
        
        # 2. Parametre grid tanımla
        self.define_param_grid()
        
        # 3. Baseline performans
        self.baseline_performance()
        
        # 4. Grid search tuning
        self.grid_search_tuning()
        
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
        print("✅ XGBOOST TUNING TAMAMLANDI!")
        print("="*80)
        print(f"\n📊 Final Sonuçlar:")
        print(f"   Baseline Accuracy: {self.baseline_metrics['accuracy']:.4f}")
        print(f"   Tuned Accuracy:    {self.tuned_metrics['accuracy']:.4f}")
        print(f"   İyileşme:          {report['improvement']['accuracy']:+.2f}%")
        print(f"\n💾 Kaydedilen Dosyalar:")
        print(f"   • {model_path}")
        print(f"   • {metadata_path}")
        print(f"   • xgboost_tuning_report.json")
        print(f"\n🎯 Sıradaki Adım: tune_lightgbm.py (Phase 7.B3)")
        print("="*80 + "\n")
        
        return True

def main():
    """Ana fonksiyon"""
    # Tuner oluştur
    tuner = XGBoostTuner()
    
    # Tuning çalıştır
    success = tuner.run_full_tuning()
    
    if success:
        print("✅ Tüm işlemler başarıyla tamamlandı!")
    else:
        print("❌ Tuning başarısız oldu. Lütfen hataları kontrol edin.")

if __name__ == "__main__":
    main()
