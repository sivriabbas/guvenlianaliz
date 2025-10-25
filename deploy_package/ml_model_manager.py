"""
MACHINE LEARNING MODEL MANAGER
17 faktör ile maç tahmini - XGBoost/LightGBM
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
import json
import os
from pathlib import Path
from datetime import datetime
import pickle

# ML kütüphanelerini kontrol et
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost bulunamadı. pip install xgboost ile yükleyin.")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️ LightGBM bulunamadı. pip install lightgbm ile yükleyin.")

try:
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn bulunamadı. pip install scikit-learn ile yükleyin.")


class MLModelManager:
    """
    Machine Learning model yöneticisi
    17 faktör ile maç sonucu tahmini
    """
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.models = {}
        self.feature_names = [
            # BASE FACTORS (8)
            'elo_diff', 'league_position', 'form', 'h2h',
            'home_advantage', 'motivation', 'fatigue', 'recent_performance',
            # PHASE 1 (3)
            'injuries', 'match_importance', 'xg_performance',
            # PHASE 2 (3)
            'weather', 'referee', 'betting_odds',
            # PHASE 3 (3)
            'tactical_matchup', 'transfer_impact', 'squad_experience'
        ]
        
        self.target_names = ['home_win', 'draw', 'away_win']
        self.model_metadata = {}
    
    def prepare_features(self, team1_factors: Dict[str, float],
                        team2_factors: Dict[str, float]) -> np.ndarray:
        """
        İki takımın faktörlerinden ML feature vektörü oluştur
        """
        features = []
        
        for factor in self.feature_names:
            team1_val = team1_factors.get(factor, 0.5)
            team2_val = team2_factors.get(factor, 0.5)
            
            # Fark özelliği (team1 - team2)
            diff = team1_val - team2_val
            features.append(diff)
        
        return np.array(features).reshape(1, -1)
    
    def create_xgboost_model(self, params: Dict = None) -> 'xgb.XGBClassifier':
        """
        XGBoost modeli oluştur
        """
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost yüklü değil!")
        
        default_params = {
            'objective': 'multi:softprob',
            'num_class': 3,
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42
        }
        
        if params:
            default_params.update(params)
        
        model = xgb.XGBClassifier(**default_params)
        return model
    
    def create_lightgbm_model(self, params: Dict = None) -> 'lgb.LGBMClassifier':
        """
        LightGBM modeli oluştur
        """
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("LightGBM yüklü değil!")
        
        default_params = {
            'objective': 'multiclass',
            'num_class': 3,
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'verbose': -1
        }
        
        if params:
            default_params.update(params)
        
        model = lgb.LGBMClassifier(**default_params)
        return model
    
    def train_model(self, X: np.ndarray, y: np.ndarray,
                   model_type: str = 'xgboost',
                   model_name: str = 'default',
                   test_size: float = 0.2) -> Dict:
        """
        Modeli eğit ve değerlendir
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn yüklü değil!")
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Model oluştur
        if model_type == 'xgboost':
            model = self.create_xgboost_model()
        elif model_type == 'lightgbm':
            model = self.create_lightgbm_model()
        else:
            raise ValueError(f"Bilinmeyen model tipi: {model_type}")
        
        # Eğit
        print(f"🎓 {model_type.upper()} modeli eğitiliyor...")
        model.fit(X_train, y_train)
        
        # Değerlendir
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        logloss = log_loss(y_test, y_pred_proba)
        
        # Modeli kaydet
        self.models[model_name] = model
        self.model_metadata[model_name] = {
            'type': model_type,
            'accuracy': float(accuracy),
            'log_loss': float(logloss),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'trained_at': datetime.now().isoformat(),
            'features': self.feature_names
        }
        
        print(f"✅ Model eğitildi: {model_name}")
        print(f"   📊 Accuracy: {accuracy:.4f}")
        print(f"   📉 Log Loss: {logloss:.4f}")
        
        return {
            'model': model,
            'accuracy': accuracy,
            'log_loss': logloss,
            'y_test': y_test,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
    
    def predict(self, team1_factors: Dict[str, float],
               team2_factors: Dict[str, float],
               model_name: str = 'default') -> Dict:
        """
        Maç sonucu tahmin et
        """
        if model_name not in self.models:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        # Feature hazırla
        X = self.prepare_features(team1_factors, team2_factors)
        
        # Tahmin
        model = self.models[model_name]
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # Sonuç mapping
        result_map = {0: 'home_win', 1: 'draw', 2: 'away_win'}
        predicted_result = result_map[prediction]
        
        return {
            'prediction': predicted_result,
            'probabilities': {
                'home_win': float(probabilities[0]),
                'draw': float(probabilities[1]),
                'away_win': float(probabilities[2])
            },
            'confidence': float(max(probabilities)),
            'model_name': model_name,
            'model_type': self.model_metadata[model_name]['type']
        }
    
    def get_feature_importance(self, model_name: str = 'default') -> List[Tuple[str, float]]:
        """
        Faktör önem sıralaması
        """
        if model_name not in self.models:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        model = self.models[model_name]
        
        # Feature importance al
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            raise ValueError("Model feature importance desteklemiyor")
        
        # Sırala
        feature_importance = list(zip(self.feature_names, importances))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        return feature_importance
    
    def save_model(self, model_name: str = 'default'):
        """
        Modeli diske kaydet
        """
        if model_name not in self.models:
            raise ValueError(f"Model bulunamadı: {model_name}")
        
        model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
        metadata_path = os.path.join(self.model_dir, f"{model_name}_metadata.json")
        
        # Model kaydet
        with open(model_path, 'wb') as f:
            pickle.dump(self.models[model_name], f)
        
        # Metadata kaydet
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.model_metadata[model_name], f, indent=2, ensure_ascii=False)
        
        print(f"✅ Model kaydedildi: {model_path}")
    
    def load_model(self, model_name: str = 'default'):
        """
        Modeli diskten yükle
        """
        model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
        metadata_path = os.path.join(self.model_dir, f"{model_name}_metadata.json")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model bulunamadı: {model_path}")
        
        # Model yükle
        with open(model_path, 'rb') as f:
            self.models[model_name] = pickle.load(f)
        
        # Metadata yükle
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.model_metadata[model_name] = json.load(f)
        
        print(f"✅ Model yüklendi: {model_path}")
        return True


# Singleton instance
_ml_manager = None

def get_ml_manager() -> MLModelManager:
    """Global ML manager instance"""
    global _ml_manager
    if _ml_manager is None:
        _ml_manager = MLModelManager()
        
        # Mevcut modelleri yükle
        model_dir = Path("models")
        if model_dir.exists():
            for model_file in model_dir.glob("*.pkl"):
                model_name = model_file.stem  # xgb_v1, lgb_v1 gibi
                try:
                    loaded_data = _ml_manager.load_model(model_name)
                    if loaded_data:
                        print(f"✅ Model yüklendi: {model_name}")
                except Exception as e:
                    print(f"⚠️ Model yüklenemedi ({model_name}): {e}")
    
    return _ml_manager


# Demo veri oluşturucu
def generate_demo_data(n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Demo eğitim verisi oluştur (gerçek veriye ihtiyaç var!)
    """
    np.random.seed(42)
    
    # 17 faktör için rastgele değerler (team1 - team2 farkı)
    X = np.random.randn(n_samples, 17) * 0.3
    
    # Basit kural tabanlı label oluştur
    y = []
    for i in range(n_samples):
        # İlk 5 faktörün ortalamasına göre karar
        avg = np.mean(X[i, :5])
        
        if avg > 0.15:
            y.append(0)  # Home win
        elif avg < -0.15:
            y.append(2)  # Away win
        else:
            y.append(1)  # Draw
    
    return X, np.array(y)


# Test
if __name__ == "__main__":
    print("="*70)
    print("🧪 ML MODEL MANAGER TEST")
    print("="*70)
    
    # Kütüphane kontrolü
    print("\n📦 Kütüphane Durumu:")
    print(f"   XGBoost: {'✅' if XGBOOST_AVAILABLE else '❌'}")
    print(f"   LightGBM: {'✅' if LIGHTGBM_AVAILABLE else '❌'}")
    print(f"   scikit-learn: {'✅' if SKLEARN_AVAILABLE else '❌'}")
    
    if not (XGBOOST_AVAILABLE or LIGHTGBM_AVAILABLE) or not SKLEARN_AVAILABLE:
        print("\n⚠️ Gerekli kütüphaneler yüklü değil!")
        print("   pip install xgboost lightgbm scikit-learn")
        exit(1)
    
    # ML manager oluştur
    manager = get_ml_manager()
    
    # Demo veri oluştur
    print("\n1️⃣ DEMO VERİ OLUŞTURMA")
    print("-"*70)
    X, y = generate_demo_data(n_samples=1000)
    print(f"✅ {X.shape[0]} örnek oluşturuldu")
    print(f"   Features: {X.shape[1]}")
    print(f"   Sınıf dağılımı:")
    print(f"      Home Win: {(y == 0).sum()}")
    print(f"      Draw: {(y == 1).sum()}")
    print(f"      Away Win: {(y == 2).sum()}")
    
    # XGBoost eğit
    print("\n2️⃣ XGBOOST MODELİ EĞİTİMİ")
    print("-"*70)
    if XGBOOST_AVAILABLE:
        result_xgb = manager.train_model(X, y, model_type='xgboost', model_name='xgb_v1')
        manager.save_model('xgb_v1')
    
    # LightGBM eğit
    print("\n3️⃣ LIGHTGBM MODELİ EĞİTİMİ")
    print("-"*70)
    if LIGHTGBM_AVAILABLE:
        result_lgb = manager.train_model(X, y, model_type='lightgbm', model_name='lgb_v1')
        manager.save_model('lgb_v1')
    
    # Tahmin testi
    print("\n4️⃣ TAHMİN TESTİ")
    print("-"*70)
    
    # Örnek faktörler
    team1_factors = {
        'elo_diff': 0.3, 'league_position': 0.8, 'form': 0.7,
        'h2h': 0.6, 'home_advantage': 1.0, 'motivation': 0.8,
        'fatigue': 0.7, 'recent_performance': 0.8,
        'injuries': 0.9, 'match_importance': 0.7, 'xg_performance': 0.75,
        'weather': 0.5, 'referee': 0.5, 'betting_odds': 0.65,
        'tactical_matchup': 0.7, 'transfer_impact': 0.75, 'squad_experience': 0.8
    }
    
    team2_factors = {
        'elo_diff': -0.3, 'league_position': 0.5, 'form': 0.6,
        'h2h': 0.4, 'home_advantage': 0.0, 'motivation': 0.7,
        'fatigue': 0.6, 'recent_performance': 0.7,
        'injuries': 0.7, 'match_importance': 0.7, 'xg_performance': 0.65,
        'weather': 0.5, 'referee': 0.5, 'betting_odds': 0.35,
        'tactical_matchup': 0.65, 'transfer_impact': 0.7, 'squad_experience': 0.75
    }
    
    if XGBOOST_AVAILABLE:
        pred_xgb = manager.predict(team1_factors, team2_factors, 'xgb_v1')
        print(f"XGBoost Tahmini:")
        print(f"   Sonuç: {pred_xgb['prediction']}")
        print(f"   Güven: {pred_xgb['confidence']:.2%}")
        print(f"   Olasılıklar:")
        for outcome, prob in pred_xgb['probabilities'].items():
            print(f"      {outcome}: {prob:.2%}")
    
    # Feature importance
    print("\n5️⃣ FAKTÖR ÖNEMİ")
    print("-"*70)
    if XGBOOST_AVAILABLE:
        importance = manager.get_feature_importance('xgb_v1')
        print("En önemli 10 faktör:")
        for i, (feature, score) in enumerate(importance[:10], 1):
            bar = "█" * int(score * 50)
            print(f"   {i:2d}. {feature:20s} {score:6.4f} {bar}")
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI!")
    print("="*70)
