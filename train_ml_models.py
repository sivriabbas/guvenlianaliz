"""
MODEL TRAINER - ML Modellerini Gerçek Veri ile Eğitir
Phase 6: Toplanan gerçek maç verisi ile XGBoost ve LightGBM modellerini eğitir
"""
import pandas as pd
import numpy as np
from pathlib import Path
from ml_model_manager import MLModelManager
from typing import Dict, List
import json
from datetime import datetime

class ModelTrainer:
    """Gerçek veri ile model eğitimi"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.ml_manager = MLModelManager()
        self.results = {}
        
    def load_training_data(self) -> tuple:
        """CSV'den eğitim verisini yükle"""
        print(f"\n{'='*70}")
        print(f"📊 EĞİTİM VERİSİ YÜKLENİYOR")
        print(f"{'='*70}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Veri dosyası bulunamadı: {self.data_path}")
        
        # CSV oku
        df = pd.read_csv(self.data_path)
        print(f"✅ {len(df)} maç verisi yüklendi")
        
        # Feature columns (17 faktör)
        feature_cols = [
            'form', 'elo_diff', 'home_advantage', 'h2h', 'league_position',
            'injuries', 'motivation', 'recent_xg',
            'weather', 'referee', 'betting_odds',
            'tactical_matchup', 'transfer_impact', 'squad_experience',
            'match_importance', 'fatigue', 'recent_performance'
        ]
        
        # Features ve labels ayır
        X = df[feature_cols].values
        y = df['result'].values
        
        print(f"\n📈 Veri İstatistikleri:")
        print(f"  Features shape: {X.shape}")
        print(f"  Labels shape: {y.shape}")
        
        # Sınıf dağılımı
        unique, counts = np.unique(y, return_counts=True)
        class_dist = dict(zip(unique, counts))
        print(f"\n🎯 Sınıf Dağılımı:")
        labels = {0: 'Home Win', 1: 'Draw', 2: 'Away Win'}
        for cls, count in class_dist.items():
            pct = count / len(y) * 100
            print(f"  {labels[cls]}: {count} (%{pct:.1f})")
        
        return X, y, df
    
    def train_all_models(self, X: np.ndarray, y: np.ndarray):
        """Tüm modelleri eğit ve değerlendir"""
        print(f"\n{'='*70}")
        print(f"🎓 MODEL EĞİTİMİ BAŞLIYOR")
        print(f"{'='*70}")
        
        models_to_train = [
            ('xgboost', 'xgb_real_v1'),
            ('lightgbm', 'lgb_real_v1')
        ]
        
        for model_type, model_name in models_to_train:
            print(f"\n{'─'*70}")
            print(f"🤖 {model_type.upper()} Eğitiliyor...")
            print(f"{'─'*70}")
            
            try:
                result = self.ml_manager.train_model(
                    X, y,
                    model_type=model_type,
                    model_name=model_name,
                    test_size=0.2
                )
                
                # Sonuçları kaydet
                self.results[model_name] = {
                    'type': model_type,
                    'accuracy': result['accuracy'],
                    'log_loss': result['log_loss'],
                    'trained_at': datetime.now().isoformat()
                }
                
                # Metrikleri göster
                print(f"\n✅ Eğitim Tamamlandı!")
                print(f"  📊 Accuracy: {result['accuracy']:.4f} (%{result['accuracy']*100:.2f})")
                print(f"  📉 Log Loss: {result['log_loss']:.4f}")
                
                # Modeli kaydet
                self.ml_manager.save_model(model_name)
                
                # Confusion matrix
                self._print_confusion_matrix(result['y_test'], result['y_pred'])
                
                # Feature importance
                self._print_feature_importance(model_name)
                
            except Exception as e:
                print(f"❌ {model_type} eğitim hatası: {e}")
                continue
    
    def _print_confusion_matrix(self, y_test: np.ndarray, y_pred: np.ndarray):
        """Confusion matrix göster"""
        from sklearn.metrics import confusion_matrix
        
        cm = confusion_matrix(y_test, y_pred)
        
        print(f"\n📊 Confusion Matrix:")
        print(f"               Predicted")
        print(f"            Home  Draw  Away")
        print(f"  Actual")
        print(f"  Home     {cm[0][0]:4d}  {cm[0][1]:4d}  {cm[0][2]:4d}")
        print(f"  Draw     {cm[1][0]:4d}  {cm[1][1]:4d}  {cm[1][2]:4d}")
        print(f"  Away     {cm[2][0]:4d}  {cm[2][1]:4d}  {cm[2][2]:4d}")
    
    def _print_feature_importance(self, model_name: str, top_n: int = 10):
        """Feature importance göster"""
        print(f"\n📈 Top {top_n} Önemli Faktörler:")
        
        importance = self.ml_manager.get_feature_importance(model_name)
        
        for i, (feature, score) in enumerate(importance[:top_n], 1):
            bar = "█" * int(score * 50)
            print(f"  {i:2d}. {feature:20s} {score:6.4f} {bar}")
    
    def save_training_report(self, output_path: str = "models/training_report.json"):
        """Eğitim raporunu kaydet"""
        report = {
            'training_date': datetime.now().isoformat(),
            'data_path': str(self.data_path),
            'models': self.results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Eğitim raporu kaydedildi: {output_path}")
    
    def compare_models(self):
        """Modelleri karşılaştır"""
        if len(self.results) < 2:
            return
        
        print(f"\n{'='*70}")
        print(f"⚔️ MODEL KARŞILAŞTIRMA")
        print(f"{'='*70}")
        
        print(f"\n{'Model':<20} {'Accuracy':<12} {'Log Loss':<12}")
        print(f"{'-'*44}")
        
        sorted_models = sorted(
            self.results.items(),
            key=lambda x: x[1]['accuracy'],
            reverse=True
        )
        
        for model_name, metrics in sorted_models:
            acc = metrics['accuracy']
            loss = metrics['log_loss']
            print(f"{model_name:<20} {acc:>10.4f}  {loss:>10.4f}")
        
        # En iyi model
        best_model = sorted_models[0]
        print(f"\n🏆 EN İYİ MODEL: {best_model[0]}")
        print(f"   Accuracy: %{best_model[1]['accuracy']*100:.2f}")
        print(f"   Log Loss: {best_model[1]['log_loss']:.4f}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎯 MODEL EĞİTİM SİSTEMİ - PHASE 6")
    print("="*70)
    
    # Veri dosyasını bul
    data_dir = Path("ml_training_data")
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("\n❌ Eğitim verisi bulunamadı!")
        print("Önce 'python data_collector.py' ile veri toplayın")
        exit(1)
    
    print(f"\n📁 Bulunan veri dosyaları:")
    for i, csv_file in enumerate(csv_files, 1):
        print(f"  {i}. {csv_file.name}")
    
    # İlk dosyayı kullan (veya kullanıcıdan seç)
    data_file = csv_files[0]
    print(f"\n✅ Kullanılacak dosya: {data_file.name}")
    
    response = input("\n❓ Model eğitimine başlamak istiyor musunuz? (e/h): ")
    
    if response.lower() == 'e':
        # Trainer oluştur
        trainer = ModelTrainer(data_file)
        
        # Veriyi yükle
        X, y, df = trainer.load_training_data()
        
        # Modelleri eğit
        trainer.train_all_models(X, y)
        
        # Modelleri karşılaştır
        trainer.compare_models()
        
        # Rapor kaydet
        trainer.save_training_report()
        
        print(f"\n{'='*70}")
        print(f"🎉 EĞİTİM TAMAMLANDI!")
        print(f"{'='*70}")
        print(f"✅ Modeller 'models/' dizinine kaydedildi")
        print(f"🎯 API'yi yeniden başlatarak yeni modelleri kullanabilirsiniz")
        print(f"\n💡 Komut: python simple_fastapi.py")
    else:
        print("\n⏸️ İşlem iptal edildi")
