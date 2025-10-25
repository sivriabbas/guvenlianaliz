"""
🎯 PHASE 7.B4: MODEL EVALUATION & COMPARISON
v1 (baseline) ve v2 (tuned) modellerini karşılaştırır
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_curve, auc,
    roc_auc_score
)
from sklearn.preprocessing import label_binarize
import json
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Matplotlib backend ayarı
import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışmak için

class ModelEvaluator:
    """Model değerlendirme ve karşılaştırma sınıfı"""
    
    def __init__(self, data_dir='prepared_data', model_dir='models', output_dir='evaluation_results'):
        """
        Args:
            data_dir: Hazırlanmış veri dizini
            model_dir: Model dizini
            output_dir: Çıktı dizini
        """
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.output_dir = output_dir
        
        # Çıktı dizinini oluştur
        os.makedirs(output_dir, exist_ok=True)
        
        # Sınıf isimleri
        self.class_names = ['Deplasman', 'Beraberlik', 'Ev Sahibi']
        
        print("="*80)
        print("🎯 MODEL EVALUATION & COMPARISON")
        print("="*80)
    
    def load_data(self):
        """Test verilerini yükle"""
        print("\n📥 Test verileri yükleniyor...")
        
        try:
            self.X_test = np.load(f'{self.data_dir}/X_test.npy')
            self.y_test = np.load(f'{self.data_dir}/y_test.npy')
            
            with open(f'{self.data_dir}/feature_names.json', 'r') as f:
                self.feature_names = json.load(f)
            
            print(f"✅ Veri yüklendi:")
            print(f"   Test samples: {self.X_test.shape[0]}")
            print(f"   Features: {len(self.feature_names)}")
            
            return True
        except Exception as e:
            print(f"❌ Veri yükleme hatası: {e}")
            return False
    
    def load_models(self):
        """Tüm modelleri yükle"""
        print("\n📦 Modeller yükleniyor...")
        
        self.models = {}
        model_files = {
            'XGBoost_v1': 'xgb_v1.pkl',
            'XGBoost_v2': 'xgb_v2.pkl',
            'LightGBM_v1': 'lgb_v1.pkl',
            'LightGBM_v2': 'lgb_v2.pkl'
        }
        
        for model_name, filename in model_files.items():
            filepath = f'{self.model_dir}/{filename}'
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    self.models[model_name] = pickle.load(f)
                print(f"   ✅ {model_name:15s} yüklendi")
            else:
                print(f"   ⏳ {model_name:15s} bulunamadı (henüz eğitilmemiş)")
        
        if len(self.models) == 0:
            print("❌ Hiç model bulunamadı!")
            return False
        
        print(f"\n✅ Toplam {len(self.models)} model yüklendi")
        return True
    
    def evaluate_model(self, model_name, model):
        """Tek bir modeli değerlendir"""
        print(f"\n📊 {model_name} değerlendiriliyor...")
        
        # Tahminler
        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)
        
        # Temel metrikler
        metrics = {
            'accuracy': accuracy_score(self.y_test, y_pred),
            'precision_weighted': precision_score(self.y_test, y_pred, average='weighted'),
            'recall_weighted': recall_score(self.y_test, y_pred, average='weighted'),
            'f1_weighted': f1_score(self.y_test, y_pred, average='weighted'),
            'precision_macro': precision_score(self.y_test, y_pred, average='macro'),
            'recall_macro': recall_score(self.y_test, y_pred, average='macro'),
            'f1_macro': f1_score(self.y_test, y_pred, average='macro')
        }
        
        # Sınıf bazlı metrikler
        precision_per_class = precision_score(self.y_test, y_pred, average=None)
        recall_per_class = recall_score(self.y_test, y_pred, average=None)
        f1_per_class = f1_score(self.y_test, y_pred, average=None)
        
        metrics['per_class'] = {
            self.class_names[i]: {
                'precision': float(precision_per_class[i]),
                'recall': float(recall_per_class[i]),
                'f1': float(f1_per_class[i])
            }
            for i in range(len(self.class_names))
        }
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # ROC AUC (multi-class için one-vs-rest)
        try:
            y_test_bin = label_binarize(self.y_test, classes=[0, 1, 2])
            roc_auc_ovr = roc_auc_score(y_test_bin, y_pred_proba, average='weighted', multi_class='ovr')
            metrics['roc_auc_ovr'] = roc_auc_ovr
        except:
            metrics['roc_auc_ovr'] = None
        
        print(f"   Accuracy:  {metrics['accuracy']:.4f}")
        print(f"   Precision: {metrics['precision_weighted']:.4f}")
        print(f"   Recall:    {metrics['recall_weighted']:.4f}")
        print(f"   F1-Score:  {metrics['f1_weighted']:.4f}")
        if metrics['roc_auc_ovr']:
            print(f"   ROC AUC:   {metrics['roc_auc_ovr']:.4f}")
        
        return metrics, y_pred, y_pred_proba
    
    def compare_models(self):
        """Tüm modelleri karşılaştır"""
        print("\n" + "="*80)
        print("📊 MODEL KARŞILAŞTIRMASI")
        print("="*80)
        
        self.results = {}
        self.predictions = {}
        
        for model_name, model in self.models.items():
            metrics, y_pred, y_pred_proba = self.evaluate_model(model_name, model)
            self.results[model_name] = metrics
            self.predictions[model_name] = {
                'y_pred': y_pred,
                'y_pred_proba': y_pred_proba
            }
        
        # Karşılaştırma tablosu
        self.create_comparison_table()
    
    def create_comparison_table(self):
        """Karşılaştırma tablosu oluştur"""
        print("\n" + "="*80)
        print("📋 PERFORMANS KARŞILAŞTIRMA TABLOSU")
        print("="*80)
        
        # Metrik başlıkları
        metrics_to_compare = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted', 'roc_auc_ovr']
        metric_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC AUC']
        
        # Başlık
        header = f"{'Model':<20}"
        for name in metric_names:
            header += f"{name:>12}"
        print("\n" + header)
        print("-" * 80)
        
        # Her model için satır
        for model_name in sorted(self.results.keys()):
            row = f"{model_name:<20}"
            for metric in metrics_to_compare:
                value = self.results[model_name].get(metric)
                if value is not None:
                    row += f"{value:>12.4f}"
                else:
                    row += f"{'N/A':>12}"
            print(row)
        
        # En iyi modeli bul
        print("\n" + "="*80)
        print("🏆 EN İYİ MODELLER")
        print("="*80)
        
        for i, metric in enumerate(metrics_to_compare):
            if metric == 'roc_auc_ovr':
                continue  # ROC AUC bazı modellerde None olabilir
            
            best_model = max(self.results.keys(), 
                           key=lambda x: self.results[x].get(metric, 0))
            best_value = self.results[best_model][metric]
            
            print(f"   {metric_names[i]:<12}: {best_model} ({best_value:.4f})")
    
    def plot_confusion_matrices(self):
        """Tüm modeller için confusion matrix görselleştir"""
        print("\n📊 Confusion matrix grafikleri oluşturuluyor...")
        
        n_models = len(self.models)
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        axes = axes.ravel()
        
        for i, (model_name, metrics) in enumerate(self.results.items()):
            cm = np.array(metrics['confusion_matrix'])
            
            # Normalize
            cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            
            # Plot
            sns.heatmap(cm_normalized, annot=True, fmt='.2%', cmap='Blues',
                       xticklabels=self.class_names,
                       yticklabels=self.class_names,
                       ax=axes[i], cbar_kws={'label': 'Oran'})
            
            axes[i].set_title(f'{model_name}\nAccuracy: {metrics["accuracy"]:.4f}', 
                            fontsize=12, fontweight='bold')
            axes[i].set_ylabel('Gerçek Sınıf')
            axes[i].set_xlabel('Tahmin')
        
        # Boş subplot'ları gizle
        for i in range(len(self.models), 4):
            axes[i].axis('off')
        
        plt.tight_layout()
        output_path = f'{self.output_dir}/confusion_matrices.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Kaydedildi: {output_path}")
    
    def plot_roc_curves(self):
        """ROC eğrilerini çiz"""
        print("\n📈 ROC eğrileri oluşturuluyor...")
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Her sınıf için ayrı subplot
        for class_idx, class_name in enumerate(self.class_names):
            ax = axes[class_idx]
            
            for model_name, model in self.models.items():
                y_pred_proba = self.predictions[model_name]['y_pred_proba']
                
                # Binary sınıf için ROC
                y_true_binary = (self.y_test == class_idx).astype(int)
                
                fpr, tpr, _ = roc_curve(y_true_binary, y_pred_proba[:, class_idx])
                roc_auc = auc(fpr, tpr)
                
                ax.plot(fpr, tpr, lw=2, label=f'{model_name} (AUC={roc_auc:.3f})')
            
            ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random')
            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_xlabel('False Positive Rate', fontsize=10)
            ax.set_ylabel('True Positive Rate', fontsize=10)
            ax.set_title(f'ROC Curve - {class_name}', fontsize=12, fontweight='bold')
            ax.legend(loc='lower right', fontsize=8)
            ax.grid(alpha=0.3)
        
        plt.tight_layout()
        output_path = f'{self.output_dir}/roc_curves.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Kaydedildi: {output_path}")
    
    def plot_metric_comparison(self):
        """Metrik karşılaştırma bar chart"""
        print("\n📊 Metrik karşılaştırma grafiği oluşturuluyor...")
        
        metrics = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
        metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        
        # Veri hazırla
        data = []
        for model_name in sorted(self.results.keys()):
            row = [self.results[model_name][m] for m in metrics]
            data.append(row)
        
        # Plot
        x = np.arange(len(metric_labels))
        width = 0.2
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for i, model_name in enumerate(sorted(self.results.keys())):
            offset = width * (i - len(self.models)/2 + 0.5)
            bars = ax.bar(x + offset, data[i], width, label=model_name)
            
            # Bar üzerine değer yaz
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=8)
        
        ax.set_ylabel('Skor', fontsize=12)
        ax.set_title('Model Performans Karşılaştırması', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_labels, fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim([0, 1.0])
        
        plt.tight_layout()
        output_path = f'{self.output_dir}/metric_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Kaydedildi: {output_path}")
    
    def compare_feature_importance(self):
        """Feature importance karşılaştırması"""
        print("\n📊 Feature importance karşılaştırması...")
        
        # v2 modellerinin feature importance'ını al
        importances = {}
        
        for model_name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importances[model_name] = model.feature_importances_
        
        if len(importances) == 0:
            print("   ⚠️ Feature importance bilgisi yok")
            return
        
        # DataFrame oluştur
        df = pd.DataFrame(importances, index=self.feature_names)
        
        # En önemli 15 feature'ı al (herhangi bir modelde)
        top_features = df.sum(axis=1).nlargest(15).index
        df_top = df.loc[top_features]
        
        # Plot
        fig, ax = plt.subplots(figsize=(14, 10))
        df_top.plot(kind='barh', ax=ax, width=0.8)
        ax.set_xlabel('Importance', fontsize=12)
        ax.set_ylabel('Features', fontsize=12)
        ax.set_title('Top 15 Feature Importance Karşılaştırması', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        output_path = f'{self.output_dir}/feature_importance_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Kaydedildi: {output_path}")
    
    def analyze_improvements(self):
        """v1 → v2 iyileştirmelerini analiz et"""
        print("\n📈 v1 → v2 iyileştirme analizi...")
        
        improvements = {}
        
        # XGBoost karşılaştırması
        if 'XGBoost_v1' in self.results and 'XGBoost_v2' in self.results:
            improvements['XGBoost'] = self._calculate_improvement(
                self.results['XGBoost_v1'],
                self.results['XGBoost_v2']
            )
        
        # LightGBM karşılaştırması
        if 'LightGBM_v1' in self.results and 'LightGBM_v2' in self.results:
            improvements['LightGBM'] = self._calculate_improvement(
                self.results['LightGBM_v1'],
                self.results['LightGBM_v2']
            )
        
        if len(improvements) == 0:
            print("   ⚠️ v1 ve v2 modelleri karşılaştırılamadı")
            return improvements
        
        # Sonuçları yazdır
        print("\n" + "="*80)
        print("📊 v1 → v2 İYİLEŞTİRMELER")
        print("="*80)
        
        for model_type, impr in improvements.items():
            print(f"\n{model_type}:")
            for metric, values in impr.items():
                if metric == 'per_class':
                    continue
                print(f"   {metric:20s}: {values['v1']:.4f} → {values['v2']:.4f} "
                     f"({values['improvement']:+.2f}%)")
        
        return improvements
    
    def _calculate_improvement(self, v1_metrics, v2_metrics):
        """İyileştirme yüzdesini hesapla"""
        improvement = {}
        
        metrics_to_compare = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
        
        for metric in metrics_to_compare:
            v1_val = v1_metrics.get(metric, 0)
            v2_val = v2_metrics.get(metric, 0)
            
            if v1_val > 0:
                impr_pct = ((v2_val - v1_val) / v1_val) * 100
            else:
                impr_pct = 0
            
            improvement[metric] = {
                'v1': v1_val,
                'v2': v2_val,
                'improvement': impr_pct
            }
        
        return improvement
    
    def generate_report(self):
        """Detaylı değerlendirme raporu oluştur"""
        print("\n📄 Değerlendirme raporu oluşturuluyor...")
        
        # İyileştirmeleri hesapla
        improvements = self.analyze_improvements()
        
        report = {
            'evaluation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'n_test_samples': int(self.X_test.shape[0]),
            'n_features': len(self.feature_names),
            'models_evaluated': list(self.models.keys()),
            'results': {
                model_name: {
                    k: float(v) if isinstance(v, (int, float, np.number)) else v
                    for k, v in metrics.items()
                    if k not in ['confusion_matrix', 'per_class']
                }
                for model_name, metrics in self.results.items()
            },
            'best_models': {
                'accuracy': max(self.results.keys(), key=lambda x: self.results[x]['accuracy']),
                'precision': max(self.results.keys(), key=lambda x: self.results[x]['precision_weighted']),
                'recall': max(self.results.keys(), key=lambda x: self.results[x]['recall_weighted']),
                'f1_score': max(self.results.keys(), key=lambda x: self.results[x]['f1_weighted'])
            },
            'improvements': improvements,
            'recommendation': self._generate_recommendation()
        }
        
        # JSON olarak kaydet
        report_path = f'{self.output_dir}/evaluation_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Kaydedildi: {report_path}")
        
        return report
    
    def _generate_recommendation(self):
        """En iyi model önerisi oluştur"""
        # F1-score'a göre en iyi modeli seç
        best_model = max(self.results.keys(), 
                        key=lambda x: self.results[x]['f1_weighted'])
        best_f1 = self.results[best_model]['f1_weighted']
        
        recommendation = {
            'recommended_model': best_model,
            'reason': f'En yüksek F1-Score: {best_f1:.4f}',
            'confidence': 'High' if best_f1 > 0.90 else 'Medium' if best_f1 > 0.85 else 'Low'
        }
        
        return recommendation
    
    def print_final_summary(self, report):
        """Final özet yazdır"""
        print("\n" + "="*80)
        print("✅ MODEL DEĞERLENDİRME TAMAMLANDI!")
        print("="*80)
        
        print(f"\n📊 Değerlendirilen Modeller: {len(self.models)}")
        print(f"📁 Test Örnekleri: {self.X_test.shape[0]}")
        
        print(f"\n🏆 ÖNERİLEN MODEL:")
        rec = report['recommendation']
        print(f"   Model: {rec['recommended_model']}")
        print(f"   Sebep: {rec['reason']}")
        print(f"   Güven: {rec['confidence']}")
        
        print(f"\n💾 Oluşturulan Dosyalar:")
        print(f"   • {self.output_dir}/evaluation_report.json")
        print(f"   • {self.output_dir}/confusion_matrices.png")
        print(f"   • {self.output_dir}/roc_curves.png")
        print(f"   • {self.output_dir}/metric_comparison.png")
        print(f"   • {self.output_dir}/feature_importance_comparison.png")
        
        print(f"\n🎯 Sıradaki Adım: Phase 7.C - Ensemble Optimization")
        print("="*80 + "\n")
    
    def run_full_evaluation(self):
        """Tam değerlendirme pipeline'ı"""
        print("\n" + "🚀"*40)
        print("MODEL EVALUATION & COMPARISON BAŞLATILIYOR")
        print("🚀"*40 + "\n")
        
        # 1. Veri yükle
        if not self.load_data():
            return False
        
        # 2. Modelleri yükle
        if not self.load_models():
            return False
        
        # 3. Modelleri değerlendir ve karşılaştır
        self.compare_models()
        
        # 4. Görselleştirmeler
        self.plot_confusion_matrices()
        self.plot_roc_curves()
        self.plot_metric_comparison()
        self.compare_feature_importance()
        
        # 5. İyileştirme analizi
        improvements = self.analyze_improvements()
        
        # 6. Rapor oluştur
        report = self.generate_report()
        
        # 7. Final özet
        self.print_final_summary(report)
        
        return True

def main():
    """Ana fonksiyon"""
    evaluator = ModelEvaluator()
    
    success = evaluator.run_full_evaluation()
    
    if success:
        print("✅ Tüm işlemler başarıyla tamamlandı!")
    else:
        print("❌ Değerlendirme başarısız oldu. Lütfen hataları kontrol edin.")

if __name__ == "__main__":
    main()
