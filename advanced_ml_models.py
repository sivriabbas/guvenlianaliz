"""
Phase 9.A: Advanced ML Models (Without Deep Learning Dependencies)
Neural Network-style models using scikit-learn MLPClassifier
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import pickle
import json
from pathlib import Path
from datetime import datetime
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')


class AdvancedNeuralPredictor:
    """
    Advanced Neural Network predictor using scikit-learn
    Multi-layer perceptron for match outcome prediction
    """
    
    def __init__(
        self,
        hidden_layers: Tuple[int, ...] = (128, 64, 32),
        activation: str = 'relu',
        solver: str = 'adam',
        learning_rate_init: float = 0.001,
        max_iter: int = 500,
        early_stopping: bool = True
    ):
        self.hidden_layers = hidden_layers
        self.activation = activation
        self.solver = solver
        self.learning_rate_init = learning_rate_init
        self.max_iter = max_iter
        self.early_stopping = early_stopping
        
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.classes_ = ['Home Win', 'Draw', 'Away Win']
        self.model_path = Path("models/advanced_nn_predictor.pkl")
        self.is_trained = False
    
    def build_model(self):
        """Build neural network model"""
        self.model = MLPClassifier(
            hidden_layer_sizes=self.hidden_layers,
            activation=self.activation,
            solver=self.solver,
            learning_rate_init=self.learning_rate_init,
            max_iter=self.max_iter,
            early_stopping=self.early_stopping,
            validation_fraction=0.1,
            n_iter_no_change=15,
            random_state=42,
            verbose=True
        )
        return self.model
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> Dict:
        """
        Train neural network model
        
        Args:
            X: Training features
            y: Training labels (0=Home Win, 1=Draw, 2=Away Win)
            feature_names: Names of features
            
        Returns:
            Training metrics
        """
        if self.model is None:
            self.build_model()
        
        self.feature_names = feature_names
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"🎯 Training Advanced Neural Network...")
        print(f"   Architecture: {self.hidden_layers}")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Validation samples: {len(X_val)}")
        
        # Train
        start_time = datetime.now()
        self.model.fit(X_train, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        val_score = self.model.score(X_val, y_val)
        
        # Predictions for detailed metrics
        y_pred = self.model.predict(X_val)
        
        # Classification report
        report = classification_report(
            y_val, y_pred,
            target_names=self.classes_,
            output_dict=True
        )
        
        cm = confusion_matrix(y_val, y_pred)
        
        self.is_trained = True
        
        metrics = {
            'train_accuracy': float(train_score),
            'val_accuracy': float(val_score),
            'training_time_seconds': training_time,
            'iterations': self.model.n_iter_,
            'loss': float(self.model.loss_),
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'feature_count': X.shape[1]
        }
        
        print(f"\n✅ Training complete!")
        print(f"   Train Accuracy: {train_score:.4f}")
        print(f"   Val Accuracy: {val_score:.4f}")
        print(f"   Training Time: {training_time:.2f}s")
        print(f"   Iterations: {self.model.n_iter_}")
        
        return metrics
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels
        
        Args:
            X: Input features
            
        Returns:
            Predicted class labels
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities
        
        Args:
            X: Input features
            
        Returns:
            Predicted probabilities for each class
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)
    
    def predict_match(self, features: Dict) -> Dict:
        """
        Predict single match outcome
        
        Args:
            features: Dictionary of match features
            
        Returns:
            Prediction with probabilities and confidence
        """
        # Convert features to array
        if self.feature_names:
            X = np.array([[features.get(name, 0) for name in self.feature_names]])
        else:
            X = np.array([list(features.values())])
        
        # Get probabilities
        probs = self.predict_proba(X)[0]
        predicted_class = int(np.argmax(probs))
        
        prediction = {
            'predicted_outcome': predicted_class,
            'outcome_name': self.classes_[predicted_class],
            'home_win_prob': float(probs[0]),
            'draw_prob': float(probs[1]),
            'away_win_prob': float(probs[2]),
            'confidence': float(np.max(probs)),
            'timestamp': datetime.now().isoformat()
        }
        
        return prediction
    
    def get_feature_importance(self) -> Dict:
        """
        Get feature importance based on connection weights
        This is approximate - neural networks don't have direct feature importance
        """
        if not self.is_trained or self.feature_names is None:
            return {}
        
        # Get weights from first layer
        first_layer_weights = self.model.coefs_[0]
        
        # Calculate importance as mean absolute weight
        importance = np.abs(first_layer_weights).mean(axis=1)
        
        # Normalize
        importance = importance / importance.sum()
        
        # Create dict
        feature_importance = {
            name: float(imp)
            for name, imp in zip(self.feature_names, importance)
        }
        
        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return feature_importance
    
    def save(self, path: Optional[str] = None):
        """Save model, scaler, and configuration"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        save_path = Path(path) if path else self.model_path
        save_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Save model and scaler together
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'hidden_layers': self.hidden_layers,
            'classes': self.classes_,
            'created_at': datetime.now().isoformat()
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {save_path}")
    
    def load(self, path: Optional[str] = None):
        """Load model, scaler, and configuration"""
        load_path = Path(path) if path else self.model_path
        
        if not load_path.exists():
            raise FileNotFoundError(f"Model file not found: {load_path}")
        
        with open(load_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.hidden_layers = model_data['hidden_layers']
        self.classes_ = model_data.get('classes', self.classes_)
        self.is_trained = True
        
        print(f"✅ Model loaded from {load_path}")
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        if not self.is_trained:
            return {"status": "not_trained"}
        
        info = {
            'status': 'trained',
            'architecture': {
                'input_features': len(self.feature_names) if self.feature_names else 'unknown',
                'hidden_layers': list(self.hidden_layers),
                'output_classes': len(self.classes_),
                'activation': self.activation,
                'solver': self.solver
            },
            'training': {
                'iterations': self.model.n_iter_,
                'final_loss': float(self.model.loss_),
                'learning_rate': self.learning_rate_init
            },
            'parameters': {
                'total_params': sum(w.size for w in self.model.coefs_) + sum(b.size for b in self.model.intercepts_)
            }
        }
        
        return info


class SequentialMatchPredictor:
    """
    Sequential match predictor that considers team's recent form
    Uses rolling window of recent matches
    """
    
    def __init__(
        self,
        window_size: int = 5,
        hidden_layers: Tuple[int, ...] = (64, 32)
    ):
        self.window_size = window_size
        self.hidden_layers = hidden_layers
        self.model = AdvancedNeuralPredictor(hidden_layers=hidden_layers)
        self.feature_columns = None
    
    def prepare_sequential_features(
        self,
        data: pd.DataFrame,
        team_col: str = 'team',
        features_cols: List[str] = None
    ) -> pd.DataFrame:
        """
        Create sequential features from match history
        
        Args:
            data: Match history data
            team_col: Column containing team names
            features_cols: Columns to use for features
            
        Returns:
            DataFrame with sequential features
        """
        if features_cols is None:
            features_cols = [c for c in data.columns if c not in [team_col, 'date', 'result']]
        
        self.feature_columns = features_cols
        
        # Sort by team and date
        data = data.sort_values([team_col, 'date']).reset_index(drop=True)
        
        # Create rolling features
        sequential_data = []
        
        for team in data[team_col].unique():
            team_data = data[data[team_col] == team].copy()
            
            # Calculate rolling statistics
            for col in features_cols:
                for window in [3, 5, 10]:
                    # Rolling mean
                    team_data[f'{col}_rolling_mean_{window}'] = \
                        team_data[col].rolling(window=window, min_periods=1).mean()
                    
                    # Rolling std
                    team_data[f'{col}_rolling_std_{window}'] = \
                        team_data[col].rolling(window=window, min_periods=1).std().fillna(0)
            
            sequential_data.append(team_data)
        
        result = pd.concat(sequential_data, ignore_index=True)
        return result
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> Dict:
        """Train sequential model"""
        return self.model.train(X, y, feature_names)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities"""
        return self.model.predict_proba(X)
    
    def save(self, path: str = "models/sequential_predictor.pkl"):
        """Save model"""
        self.model.save(path)
    
    def load(self, path: str = "models/sequential_predictor.pkl"):
        """Load model"""
        self.model.load(path)


# Test code
if __name__ == "__main__":
    print("🧠 Testing Advanced ML Models...\n")
    
    # Test Advanced Neural Predictor
    print("="*70)
    print("📊 Testing Advanced Neural Network Predictor")
    print("="*70)
    
    # Create synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    # Generate features
    X = np.random.randn(n_samples, n_features)
    
    # Generate labels (0, 1, 2)
    # Make it somewhat realistic - home advantage
    home_advantage = X[:, 0] * 0.5  # First feature gives home advantage
    form_diff = X[:, 1] * 0.3  # Second feature is form difference
    
    y_prob = home_advantage + form_diff + np.random.randn(n_samples) * 0.5
    y = np.zeros(n_samples, dtype=int)
    y[y_prob > 0.5] = 0  # Home win
    y[y_prob < -0.5] = 2  # Away win
    y[(y_prob >= -0.5) & (y_prob <= 0.5)] = 1  # Draw
    
    feature_names = [f'feature_{i}' for i in range(n_features)]
    
    # Create and train model
    nn_model = AdvancedNeuralPredictor(
        hidden_layers=(128, 64, 32),
        max_iter=200
    )
    
    metrics = nn_model.train(X, y, feature_names)
    
    print(f"\n📈 Training Metrics:")
    print(f"   Accuracy: {metrics['val_accuracy']:.4f}")
    print(f"   Iterations: {metrics['iterations']}")
    print(f"   Training Time: {metrics['training_time_seconds']:.2f}s")
    
    # Test predictions
    print(f"\n🔮 Testing Predictions...")
    X_test = X[:5]
    predictions = nn_model.predict(X_test)
    probabilities = nn_model.predict_proba(X_test)
    
    for i in range(5):
        print(f"\n   Sample {i+1}:")
        print(f"      True: {y[i]} ({nn_model.classes_[y[i]]})")
        print(f"      Predicted: {predictions[i]} ({nn_model.classes_[predictions[i]]})")
        print(f"      Probabilities: H:{probabilities[i][0]:.3f} D:{probabilities[i][1]:.3f} A:{probabilities[i][2]:.3f}")
    
    # Feature importance
    print(f"\n🎯 Top 5 Important Features:")
    importance = nn_model.get_feature_importance()
    for i, (feature, imp) in enumerate(list(importance.items())[:5], 1):
        print(f"   {i}. {feature}: {imp:.4f}")
    
    # Model info
    print(f"\n📋 Model Information:")
    info = nn_model.get_model_info()
    print(f"   Architecture: {info['architecture']['hidden_layers']}")
    print(f"   Total Parameters: {info['parameters']['total_params']:,}")
    print(f"   Final Loss: {info['training']['final_loss']:.6f}")
    
    # Save and load test
    print(f"\n💾 Testing Save/Load...")
    nn_model.save()
    
    nn_model2 = AdvancedNeuralPredictor()
    nn_model2.load()
    
    # Verify loaded model works
    pred2 = nn_model2.predict(X_test[:1])
    print(f"   ✓ Loaded model prediction: {pred2[0]} ({nn_model2.classes_[pred2[0]]})")
    
    print(f"\n✅ Advanced ML Models test complete!")
    print("="*70)
