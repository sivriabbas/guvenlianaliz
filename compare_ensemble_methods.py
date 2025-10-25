"""
Phase 7.C2: Ensemble Metod Karşılaştırması
==========================================
Farklı ensemble yöntemlerini (Voting, Averaging, Weighted) karşılaştırır.

Ensemble Metodları:
1. Hard Voting: Çoğunluk oylaması
2. Soft Voting: Olasılık ortalaması
3. Simple Averaging: Eşit ağırlıklı ortalama
4. Weighted Averaging: Optimize edilmiş ağırlıklı ortalama
5. Stacking: Meta-learner ile kombinasyon

Özellikler:
- Tüm ensemble metodlarını test et
- Performans metriklerini karşılaştır
- Görselleştirme (confusion matrix, ROC curve, metric comparison)
- En iyi metodu belirle
- Detaylı rapor oluştur

Kullanım:
    python compare_ensemble_methods.py
    
    # Sadece temel metodlar
    python compare_ensemble_methods.py --basic-only
    
    # Tüm metodlar + stacking
    python compare_ensemble_methods.py --include-stacking

Çıktılar:
- ensemble_comparison/comparison_report.json
- ensemble_comparison/performance_metrics.png
- ensemble_comparison/confusion_matrices.png
- ensemble_comparison/roc_curves.png
- ensemble_comparison/method_recommendation.json
"""

import numpy as np
import pandas as pd
import json
import joblib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import warnings
warnings.filterwarnings('ignore')

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# ML
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc,
    roc_auc_score, log_loss
)
from sklearn.preprocessing import label_binarize
from sklearn.ensemble import VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold

# ML modelleri
try:
    import xgboost as xgb
    import lightgbm as lgb
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    print("⚠️ XGBoost veya LightGBM bulunamadı!")


class EnsembleMethodComparator:
    """Farklı ensemble metodlarını karşılaştırır."""
    
    def __init__(self, models_dir: str = "models", data_dir: str = "prepared_data",
                 weights_dir: str = "optimized_weights"):
        """
        Args:
            models_dir: Model dosyalarının dizini
            data_dir: Hazırlanmış veri dosyalarının dizini
            weights_dir: Optimize edilmiş ağırlıkların dizini
        """
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.weights_dir = Path(weights_dir)
        self.output_dir = Path("ensemble_comparison")
        self.output_dir.mkdir(exist_ok=True)
        
        self.models = {}
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        self.optimized_weights = None
        
        self.results = {}
        
        # Plot settings
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        print("🔧 EnsembleMethodComparator başlatıldı")
    
    def load_data(self):
        """Hazırlanmış veriyi yükle."""
        print("\n📂 Veri yükleniyor...")
        
        try:
            self.X_train = np.load(self.data_dir / "X_train.npy")
            self.y_train = np.load(self.data_dir / "y_train.npy")
            self.X_test = np.load(self.data_dir / "X_test.npy")
            self.y_test = np.load(self.data_dir / "y_test.npy")
            
            print(f"   ✅ Train: {self.X_train.shape}")
            print(f"   ✅ Test: {self.X_test.shape}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Veri yükleme hatası: {e}")
            return False
    
    def load_models(self):
        """Tüm mevcut modelleri yükle."""
        print("\n🤖 Modeller yükleniyor...")
        
        model_files = {
            'XGBoost_v1': 'xgb_v1.pkl',
            'XGBoost_v2': 'xgb_v2.pkl',
            'LightGBM_v1': 'lgb_v1.pkl',
            'LightGBM_v2': 'lgb_v2.pkl'
        }
        
        for name, filename in model_files.items():
            filepath = self.models_dir / filename
            if filepath.exists():
                try:
                    self.models[name] = joblib.load(filepath)
                    print(f"   ✅ {name} yüklendi")
                except Exception as e:
                    print(f"   ⚠️ {name} yüklenemedi: {e}")
        
        print(f"\n   📊 Toplam {len(self.models)} model yüklendi")
        return len(self.models) >= 2
    
    def load_optimized_weights(self):
        """Optimize edilmiş ağırlıkları yükle."""
        print("\n⚖️ Optimize edilmiş ağırlıklar yükleniyor...")
        
        weights_file = self.weights_dir / "general_weights.json"
        if weights_file.exists():
            try:
                with open(weights_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.optimized_weights = data.get('weights', None)
                
                if self.optimized_weights:
                    print("   ✅ Ağırlıklar yüklendi:")
                    for name, weight in self.optimized_weights.items():
                        print(f"      {name}: {weight:.4f}")
                    return True
                    
            except Exception as e:
                print(f"   ⚠️ Ağırlık yükleme hatası: {e}")
        
        print("   ⚠️ Optimize edilmiş ağırlıklar bulunamadı")
        print("   ℹ️ Eşit ağırlıklar kullanılacak")
        
        # Eşit ağırlıklar oluştur
        n_models = len(self.models)
        self.optimized_weights = {name: 1.0/n_models for name in self.models.keys()}
        return False
    
    def method_hard_voting(self) -> Tuple[np.ndarray, Dict]:
        """Hard Voting: Çoğunluk oylaması."""
        print("\n🗳️ Hard Voting ensemble...")
        
        # Her modelin tahminlerini al
        predictions = []
        for name, model in self.models.items():
            y_pred = model.predict(self.X_test)
            predictions.append(y_pred)
        
        # Çoğunluk oylaması
        predictions = np.array(predictions)
        y_pred_voting = np.apply_along_axis(
            lambda x: np.bincount(x).argmax(), 
            axis=0, 
            arr=predictions
        )
        
        # Metrikleri hesapla
        metrics = self.calculate_metrics(y_pred_voting)
        
        return y_pred_voting, metrics
    
    def method_soft_voting(self) -> Tuple[np.ndarray, Dict]:
        """Soft Voting: Olasılık ortalaması."""
        print("\n🎲 Soft Voting ensemble...")
        
        # Her modelin olasılık tahminlerini al
        probas = []
        for name, model in self.models.items():
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(self.X_test)
            else:
                # One-hot encoding for models without predict_proba
                y_pred = model.predict(self.X_test)
                n_classes = len(np.unique(self.y_train))
                y_proba = np.zeros((len(y_pred), n_classes))
                y_proba[np.arange(len(y_pred)), y_pred] = 1
            
            probas.append(y_proba)
        
        # Ortalama olasılıklar
        avg_proba = np.mean(probas, axis=0)
        y_pred_soft = np.argmax(avg_proba, axis=1)
        
        # Metrikleri hesapla
        metrics = self.calculate_metrics(y_pred_soft, y_proba=avg_proba)
        
        return y_pred_soft, metrics
    
    def method_simple_averaging(self) -> Tuple[np.ndarray, Dict]:
        """Simple Averaging: Eşit ağırlıklı ortalama."""
        print("\n📊 Simple Averaging ensemble...")
        
        # Eşit ağırlıklar
        n_models = len(self.models)
        equal_weights = {name: 1.0/n_models for name in self.models.keys()}
        
        # Ağırlıklı ortalama
        y_pred, y_proba = self.weighted_average(equal_weights)
        
        # Metrikleri hesapla
        metrics = self.calculate_metrics(y_pred, y_proba=y_proba)
        
        return y_pred, metrics
    
    def method_weighted_averaging(self) -> Tuple[np.ndarray, Dict]:
        """Weighted Averaging: Optimize edilmiş ağırlıklı ortalama."""
        print("\n⚖️ Weighted Averaging ensemble...")
        
        # Optimize edilmiş ağırlıkları kullan
        y_pred, y_proba = self.weighted_average(self.optimized_weights)
        
        # Metrikleri hesapla
        metrics = self.calculate_metrics(y_pred, y_proba=y_proba)
        
        return y_pred, metrics
    
    def method_stacking(self) -> Tuple[np.ndarray, Dict]:
        """Stacking: Meta-learner ile kombinasyon."""
        print("\n🏗️ Stacking ensemble...")
        
        try:
            # Estimator listesi oluştur
            estimators = [(name, model) for name, model in self.models.items()]
            
            # Meta-learner: Logistic Regression
            meta_learner = LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='multinomial'
            )
            
            # Stacking classifier
            stacking_clf = StackingClassifier(
                estimators=estimators,
                final_estimator=meta_learner,
                cv=5,
                n_jobs=-1
            )
            
            # Eğit
            print("   Training stacking classifier...")
            stacking_clf.fit(self.X_train, self.y_train)
            
            # Tahmin
            y_pred = stacking_clf.predict(self.X_test)
            y_proba = stacking_clf.predict_proba(self.X_test)
            
            # Metrikleri hesapla
            metrics = self.calculate_metrics(y_pred, y_proba=y_proba)
            
            return y_pred, metrics
            
        except Exception as e:
            print(f"   ❌ Stacking hatası: {e}")
            return None, None
    
    def weighted_average(self, weights: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
        """Ağırlıklı ortalama hesapla."""
        # Her modelin olasılık tahminlerini al
        probas = {}
        for name, model in self.models.items():
            if hasattr(model, 'predict_proba'):
                probas[name] = model.predict_proba(self.X_test)
            else:
                # Fallback
                y_pred = model.predict(self.X_test)
                n_classes = len(np.unique(self.y_train))
                y_proba = np.zeros((len(y_pred), n_classes))
                y_proba[np.arange(len(y_pred)), y_pred] = 1
                probas[name] = y_proba
        
        # Ağırlıklı ortalama
        weighted_proba = np.zeros_like(list(probas.values())[0])
        total_weight = sum(weights.values())
        
        for name, proba in probas.items():
            if name in weights:
                weighted_proba += proba * (weights[name] / total_weight)
        
        # En yüksek olasılığa sahip sınıfı seç
        y_pred = np.argmax(weighted_proba, axis=1)
        
        return y_pred, weighted_proba
    
    def calculate_metrics(self, y_pred: np.ndarray, y_proba: Optional[np.ndarray] = None) -> Dict:
        """Performans metriklerini hesapla."""
        metrics = {
            'accuracy': float(accuracy_score(self.y_test, y_pred)),
            'precision_macro': float(precision_score(self.y_test, y_pred, average='macro')),
            'recall_macro': float(recall_score(self.y_test, y_pred, average='macro')),
            'f1_macro': float(f1_score(self.y_test, y_pred, average='macro')),
            'precision_weighted': float(precision_score(self.y_test, y_pred, average='weighted')),
            'recall_weighted': float(recall_score(self.y_test, y_pred, average='weighted')),
            'f1_weighted': float(f1_score(self.y_test, y_pred, average='weighted'))
        }
        
        # ROC AUC (sadece proba varsa)
        if y_proba is not None:
            try:
                n_classes = len(np.unique(self.y_train))
                if n_classes == 2:
                    metrics['roc_auc'] = float(roc_auc_score(self.y_test, y_proba[:, 1]))
                else:
                    metrics['roc_auc_ovr'] = float(roc_auc_score(
                        self.y_test, y_proba, multi_class='ovr', average='macro'
                    ))
                    metrics['roc_auc_ovo'] = float(roc_auc_score(
                        self.y_test, y_proba, multi_class='ovo', average='macro'
                    ))
                
                # Log loss
                metrics['log_loss'] = float(log_loss(self.y_test, y_proba))
                
            except Exception as e:
                print(f"   ⚠️ ROC AUC hesaplama hatası: {e}")
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # Per-class metrics
        class_report = classification_report(self.y_test, y_pred, output_dict=True)
        metrics['per_class'] = class_report
        
        return metrics
    
    def compare_all_methods(self, include_stacking: bool = False):
        """Tüm metodları karşılaştır."""
        print("\n" + "="*80)
        print("🔍 ENSEMBLE METOD KARŞILAŞTIRMASI")
        print("="*80)
        
        methods = {
            'Hard Voting': self.method_hard_voting,
            'Soft Voting': self.method_soft_voting,
            'Simple Averaging': self.method_simple_averaging,
            'Weighted Averaging': self.method_weighted_averaging
        }
        
        if include_stacking:
            methods['Stacking'] = self.method_stacking
        
        # Her metodu test et
        for method_name, method_func in methods.items():
            print(f"\n{'='*60}")
            print(f"📍 {method_name}")
            print(f"{'='*60}")
            
            y_pred, metrics = method_func()
            
            if metrics is not None:
                self.results[method_name] = {
                    'predictions': y_pred,
                    'metrics': metrics
                }
                
                # Metrikleri yazdır
                print(f"\n   📊 Performans Metrikleri:")
                print(f"      Accuracy:    {metrics['accuracy']:.4f}")
                print(f"      Precision:   {metrics['precision_macro']:.4f}")
                print(f"      Recall:      {metrics['recall_macro']:.4f}")
                print(f"      F1-Score:    {metrics['f1_macro']:.4f}")
                if 'roc_auc_ovr' in metrics:
                    print(f"      ROC AUC:     {metrics['roc_auc_ovr']:.4f}")
                if 'log_loss' in metrics:
                    print(f"      Log Loss:    {metrics['log_loss']:.4f}")
    
    def plot_performance_comparison(self):
        """Performans karşılaştırma grafiği."""
        print("\n📊 Performans karşılaştırma grafiği oluşturuluyor...")
        
        # Metrikleri topla
        methods = list(self.results.keys())
        metrics_names = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Ensemble Metodları - Performans Karşılaştırması', 
                     fontsize=16, fontweight='bold')
        
        for idx, metric in enumerate(metrics_names):
            ax = axes[idx // 2, idx % 2]
            
            values = [self.results[m]['metrics'][metric] for m in methods]
            
            bars = ax.bar(methods, values, color=self.colors[:len(methods)], 
                         alpha=0.7, edgecolor='black')
            
            # Değerleri göster
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.4f}',
                       ha='center', va='bottom', fontweight='bold')
            
            ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
            ax.set_ylim([0, 1.1])
            ax.grid(axis='y', alpha=0.3)
            ax.set_xticklabels(methods, rotation=15, ha='right')
        
        plt.tight_layout()
        
        # Kaydet
        filepath = self.output_dir / 'performance_metrics.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"   ✅ Grafik kaydedildi: {filepath}")
        plt.close()
    
    def plot_confusion_matrices(self):
        """Confusion matrix karşılaştırması."""
        print("\n🎯 Confusion matrix karşılaştırması oluşturuluyor...")
        
        n_methods = len(self.results)
        fig, axes = plt.subplots(1, n_methods, figsize=(5*n_methods, 4))
        
        if n_methods == 1:
            axes = [axes]
        
        fig.suptitle('Ensemble Metodları - Confusion Matrix Karşılaştırması', 
                     fontsize=16, fontweight='bold')
        
        for idx, (method_name, result) in enumerate(self.results.items()):
            cm = np.array(result['metrics']['confusion_matrix'])
            
            # Normalize
            cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            
            # Plot
            ax = axes[idx]
            sns.heatmap(cm_normalized, annot=True, fmt='.2%', cmap='Blues',
                       ax=ax, cbar=True, square=True)
            ax.set_title(method_name, fontsize=12, fontweight='bold')
            ax.set_ylabel('Gerçek', fontsize=10)
            ax.set_xlabel('Tahmin', fontsize=10)
        
        plt.tight_layout()
        
        # Kaydet
        filepath = self.output_dir / 'confusion_matrices.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"   ✅ Grafik kaydedildi: {filepath}")
        plt.close()
    
    def determine_best_method(self) -> Dict:
        """En iyi metodu belirle."""
        print("\n🏆 En iyi metod belirleniyor...")
        
        # Metriklere göre sıralama
        rankings = {
            'accuracy': {},
            'f1_macro': {},
            'precision_macro': {},
            'recall_macro': {}
        }
        
        for metric in rankings.keys():
            for method_name, result in self.results.items():
                score = result['metrics'][metric]
                rankings[metric][method_name] = score
        
        # Her metrik için en iyi metodu bul
        best_by_metric = {}
        for metric, scores in rankings.items():
            best_method = max(scores.items(), key=lambda x: x[1])
            best_by_metric[metric] = {
                'method': best_method[0],
                'score': float(best_method[1])
            }
        
        # Genel en iyi (F1-score bazlı)
        best_overall = max(
            self.results.items(),
            key=lambda x: x[1]['metrics']['f1_macro']
        )
        
        recommendation = {
            'best_overall': {
                'method': best_overall[0],
                'f1_macro': float(best_overall[1]['metrics']['f1_macro']),
                'accuracy': float(best_overall[1]['metrics']['accuracy']),
                'all_metrics': best_overall[1]['metrics']
            },
            'best_by_metric': best_by_metric,
            'all_rankings': {
                metric: sorted(scores.items(), key=lambda x: x[1], reverse=True)
                for metric, scores in rankings.items()
            }
        }
        
        print(f"\n   🥇 EN İYİ METOD: {best_overall[0]}")
        print(f"      F1-Score: {best_overall[1]['metrics']['f1_macro']:.4f}")
        print(f"      Accuracy: {best_overall[1]['metrics']['accuracy']:.4f}")
        
        print(f"\n   📊 Metrik Bazlı En İyiler:")
        for metric, info in best_by_metric.items():
            print(f"      {metric:20s}: {info['method']:20s} ({info['score']:.4f})")
        
        return recommendation
    
    def save_results(self, recommendation: Dict):
        """Sonuçları kaydet."""
        print("\n💾 Sonuçlar kaydediliyor...")
        
        # Comparison report
        comparison_report = {
            'timestamp': datetime.now().isoformat(),
            'n_models': len(self.models),
            'model_names': list(self.models.keys()),
            'methods_compared': list(self.results.keys()),
            'results': {
                method: {
                    'metrics': result['metrics']
                }
                for method, result in self.results.items()
            },
            'recommendation': recommendation
        }
        
        # JSON kaydet
        filepath = self.output_dir / 'comparison_report.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comparison_report, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Karşılaştırma raporu: {filepath}")
        
        # Recommendation kaydet
        filepath = self.output_dir / 'method_recommendation.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recommendation, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Metod önerisi: {filepath}")
    
    def run(self, include_stacking: bool = False):
        """Karşılaştırmayı çalıştır."""
        print("\n" + "="*80)
        print("🎯 ENSEMBLE METOD KARŞILAŞTIRMASI")
        print("="*80)
        
        # Veri ve modelleri yükle
        if not self.load_data():
            return
        
        if not self.load_models():
            print("❌ Yeterli model bulunamadı!")
            return
        
        # Ağırlıkları yükle
        self.load_optimized_weights()
        
        # Tüm metodları karşılaştır
        self.compare_all_methods(include_stacking=include_stacking)
        
        if not self.results:
            print("❌ Sonuç bulunamadı!")
            return
        
        # Görselleştirmeler
        self.plot_performance_comparison()
        self.plot_confusion_matrices()
        
        # En iyi metodu belirle
        recommendation = self.determine_best_method()
        
        # Sonuçları kaydet
        self.save_results(recommendation)
        
        print("\n" + "="*80)
        print("✅ KARŞILAŞTIRMA TAMAMLANDI!")
        print("="*80)
        print(f"\n📁 Çıktılar: {self.output_dir}")
        print(f"   • comparison_report.json")
        print(f"   • method_recommendation.json")
        print(f"   • performance_metrics.png")
        print(f"   • confusion_matrices.png")
        
        return recommendation


def main():
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(
        description='Ensemble metodlarını karşılaştır'
    )
    parser.add_argument(
        '--include-stacking',
        action='store_true',
        help='Stacking metodunu da dahil et (daha yavaş)'
    )
    parser.add_argument(
        '--basic-only',
        action='store_true',
        help='Sadece temel metodları test et'
    )
    parser.add_argument(
        '--models-dir',
        type=str,
        default='models',
        help='Model dizini (default: models)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='prepared_data',
        help='Veri dizini (default: prepared_data)'
    )
    parser.add_argument(
        '--weights-dir',
        type=str,
        default='optimized_weights',
        help='Ağırlık dizini (default: optimized_weights)'
    )
    
    args = parser.parse_args()
    
    # Comparator oluştur
    comparator = EnsembleMethodComparator(
        models_dir=args.models_dir,
        data_dir=args.data_dir,
        weights_dir=args.weights_dir
    )
    
    # Çalıştır
    include_stacking = args.include_stacking and not args.basic_only
    comparator.run(include_stacking=include_stacking)


if __name__ == "__main__":
    main()
