"""
Phase 9.A: Deep Learning Model Integration
LSTM-based time series prediction for match outcomes
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import pickle
import json
from pathlib import Path
from datetime import datetime

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, callbacks
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not available. Install with: pip install tensorflow")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("⚠️ PyTorch not available. Install with: pip install torch")


class LSTMMatchPredictor:
    """
    LSTM model for time series match prediction
    Uses team performance history to predict match outcomes
    """
    
    def __init__(
        self,
        sequence_length: int = 10,
        lstm_units: int = 64,
        dropout_rate: float = 0.2,
        learning_rate: float = 0.001
    ):
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_path = Path("models/lstm_match_predictor.h5")
        self.config_path = Path("models/lstm_config.json")
        
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM model")
    
    def build_model(self, input_features: int):
        """Build LSTM model architecture"""
        model = models.Sequential([
            # First LSTM layer with return sequences
            layers.LSTM(
                self.lstm_units,
                return_sequences=True,
                input_shape=(self.sequence_length, input_features),
                name='lstm_1'
            ),
            layers.Dropout(self.dropout_rate, name='dropout_1'),
            
            # Second LSTM layer
            layers.LSTM(
                self.lstm_units // 2,
                return_sequences=False,
                name='lstm_2'
            ),
            layers.Dropout(self.dropout_rate, name='dropout_2'),
            
            # Dense layers
            layers.Dense(32, activation='relu', name='dense_1'),
            layers.Dropout(self.dropout_rate / 2, name='dropout_3'),
            
            # Output layer (3 classes: home win, draw, away win)
            layers.Dense(3, activation='softmax', name='output')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        self.model = model
        return model
    
    def prepare_sequences(
        self,
        data: pd.DataFrame,
        target_col: str = 'result'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequential data for LSTM training
        
        Args:
            data: DataFrame with team performance history
            target_col: Column name for target variable
            
        Returns:
            X: Sequences of features
            y: Target labels (one-hot encoded)
        """
        # Sort by date
        data = data.sort_values('date').reset_index(drop=True)
        
        # Extract features and target
        feature_cols = [c for c in data.columns if c not in ['date', target_col, 'match_id']]
        self.feature_names = feature_cols
        
        X_sequences = []
        y_labels = []
        
        # Create sequences
        for i in range(len(data) - self.sequence_length):
            # Get sequence of features
            seq = data[feature_cols].iloc[i:i+self.sequence_length].values
            X_sequences.append(seq)
            
            # Get target (next match result)
            target = data[target_col].iloc[i + self.sequence_length]
            y_labels.append(target)
        
        X = np.array(X_sequences)
        y = np.array(y_labels)
        
        # One-hot encode target
        y_onehot = tf.keras.utils.to_categorical(y, num_classes=3)
        
        return X, y_onehot
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 50,
        batch_size: int = 32
    ) -> Dict:
        """
        Train LSTM model
        
        Args:
            X_train: Training sequences
            y_train: Training labels
            X_val: Validation sequences
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size
            
        Returns:
            Training history
        """
        if self.model is None:
            input_features = X_train.shape[2]
            self.build_model(input_features)
        
        # Callbacks
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss' if X_val is not None else 'loss',
            patience=10,
            restore_best_weights=True
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss' if X_val is not None else 'loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7
        )
        
        # Create models directory
        self.model_path.parent.mkdir(exist_ok=True)
        
        model_checkpoint = callbacks.ModelCheckpoint(
            str(self.model_path),
            monitor='val_accuracy' if X_val is not None else 'accuracy',
            save_best_only=True,
            mode='max'
        )
        
        callback_list = [early_stop, reduce_lr, model_checkpoint]
        
        # Train
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callback_list,
            verbose=1
        )
        
        # Save config
        self._save_config()
        
        return history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input sequences
            
        Returns:
            Predicted probabilities for each class
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        return self.model.predict(X)
    
    def predict_match(
        self,
        team_history: pd.DataFrame,
        opponent_history: pd.DataFrame
    ) -> Dict:
        """
        Predict match outcome based on team histories
        
        Args:
            team_history: Recent performance of home team
            opponent_history: Recent performance of away team
            
        Returns:
            Prediction probabilities and confidence
        """
        # Combine histories
        # This is simplified - in practice, you'd engineer features
        combined = pd.concat([team_history, opponent_history], axis=1)
        
        # Get last sequence_length matches
        if len(combined) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} historical matches")
        
        sequence = combined[self.feature_names].iloc[-self.sequence_length:].values
        X = np.expand_dims(sequence, axis=0)
        
        # Predict
        probs = self.predict(X)[0]
        
        prediction = {
            'home_win_prob': float(probs[0]),
            'draw_prob': float(probs[1]),
            'away_win_prob': float(probs[2]),
            'predicted_outcome': int(np.argmax(probs)),
            'confidence': float(np.max(probs)),
            'timestamp': datetime.now().isoformat()
        }
        
        return prediction
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate model performance
        
        Args:
            X_test: Test sequences
            y_test: Test labels
            
        Returns:
            Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        results = self.model.evaluate(X_test, y_test, verbose=0)
        
        # Get predictions
        y_pred = self.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true_classes = np.argmax(y_test, axis=1)
        
        # Calculate accuracy per class
        from sklearn.metrics import classification_report, confusion_matrix
        
        report = classification_report(
            y_true_classes, y_pred_classes,
            target_names=['Home Win', 'Draw', 'Away Win'],
            output_dict=True
        )
        
        cm = confusion_matrix(y_true_classes, y_pred_classes)
        
        metrics = {
            'loss': float(results[0]),
            'accuracy': float(results[1]),
            'auc': float(results[2]),
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'test_samples': len(X_test)
        }
        
        return metrics
    
    def save(self, path: Optional[str] = None):
        """Save model and configuration"""
        if self.model is None:
            raise ValueError("No model to save")
        
        save_path = Path(path) if path else self.model_path
        save_path.parent.mkdir(exist_ok=True, parents=True)
        
        self.model.save(str(save_path))
        self._save_config()
        
        print(f"✅ Model saved to {save_path}")
    
    def load(self, path: Optional[str] = None):
        """Load model and configuration"""
        load_path = Path(path) if path else self.model_path
        
        if not load_path.exists():
            raise FileNotFoundError(f"Model file not found: {load_path}")
        
        self.model = tf.keras.models.load_model(str(load_path))
        self._load_config()
        
        print(f"✅ Model loaded from {load_path}")
    
    def _save_config(self):
        """Save model configuration"""
        config = {
            'sequence_length': self.sequence_length,
            'lstm_units': self.lstm_units,
            'dropout_rate': self.dropout_rate,
            'learning_rate': self.learning_rate,
            'feature_names': self.feature_names,
            'created_at': datetime.now().isoformat()
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _load_config(self):
        """Load model configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self.sequence_length = config['sequence_length']
            self.lstm_units = config['lstm_units']
            self.dropout_rate = config['dropout_rate']
            self.learning_rate = config['learning_rate']
            self.feature_names = config.get('feature_names')
    
    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        if self.model is None:
            return "Model not built yet"
        
        from io import StringIO
        stream = StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
        return stream.getvalue()


class DenseNeuralNetwork:
    """
    Dense Neural Network for match prediction
    Uses engineered features for prediction
    """
    
    def __init__(
        self,
        hidden_layers: List[int] = [128, 64, 32],
        dropout_rate: float = 0.3,
        learning_rate: float = 0.001
    ):
        self.hidden_layers = hidden_layers
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.model = None
        self.model_path = Path("models/dnn_match_predictor.h5")
        
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for DNN model")
    
    def build_model(self, input_features: int):
        """Build Dense Neural Network architecture"""
        model = models.Sequential()
        
        # Input layer
        model.add(layers.Input(shape=(input_features,), name='input'))
        
        # Hidden layers
        for i, units in enumerate(self.hidden_layers):
            model.add(layers.Dense(
                units,
                activation='relu',
                name=f'dense_{i+1}'
            ))
            model.add(layers.BatchNormalization(name=f'bn_{i+1}'))
            model.add(layers.Dropout(self.dropout_rate, name=f'dropout_{i+1}'))
        
        # Output layer (3 classes)
        model.add(layers.Dense(3, activation='softmax', name='output'))
        
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        self.model = model
        return model
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 100,
        batch_size: int = 32
    ) -> Dict:
        """Train DNN model"""
        if self.model is None:
            self.build_model(X_train.shape[1])
        
        # Callbacks
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss' if X_val is not None else 'loss',
            patience=15,
            restore_best_weights=True
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss' if X_val is not None else 'loss',
            factor=0.5,
            patience=7,
            min_lr=1e-7
        )
        
        self.model_path.parent.mkdir(exist_ok=True)
        
        model_checkpoint = callbacks.ModelCheckpoint(
            str(self.model_path),
            monitor='val_accuracy' if X_val is not None else 'accuracy',
            save_best_only=True
        )
        
        callback_list = [early_stop, reduce_lr, model_checkpoint]
        
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callback_list,
            verbose=1
        )
        
        return history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        return self.model.predict(X)
    
    def save(self, path: Optional[str] = None):
        """Save model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        save_path = Path(path) if path else self.model_path
        save_path.parent.mkdir(exist_ok=True, parents=True)
        self.model.save(str(save_path))
        print(f"✅ DNN Model saved to {save_path}")
    
    def load(self, path: Optional[str] = None):
        """Load model"""
        load_path = Path(path) if path else self.model_path
        
        if not load_path.exists():
            raise FileNotFoundError(f"Model file not found: {load_path}")
        
        self.model = tf.keras.models.load_model(str(load_path))
        print(f"✅ DNN Model loaded from {load_path}")


# Test code
if __name__ == "__main__":
    print("🧠 Testing Deep Learning Models...\n")
    
    if not TENSORFLOW_AVAILABLE:
        print("❌ TensorFlow not available. Please install: pip install tensorflow")
        exit(1)
    
    # Test LSTM Model
    print("📊 Testing LSTM Match Predictor...")
    lstm_model = LSTMMatchPredictor(
        sequence_length=5,
        lstm_units=32,
        dropout_rate=0.2
    )
    
    # Create dummy data
    n_samples = 100
    sequence_length = 5
    n_features = 10
    
    X_dummy = np.random.randn(n_samples, sequence_length, n_features)
    y_dummy = tf.keras.utils.to_categorical(
        np.random.randint(0, 3, n_samples),
        num_classes=3
    )
    
    # Build model
    lstm_model.build_model(input_features=n_features)
    print("   ✓ LSTM model built")
    print(f"   ✓ Parameters: {lstm_model.model.count_params():,}")
    
    # Train (just 2 epochs for testing)
    print("\n   Training LSTM (2 epochs)...")
    history = lstm_model.train(
        X_dummy[:80], y_dummy[:80],
        X_dummy[80:], y_dummy[80:],
        epochs=2,
        batch_size=16
    )
    print(f"   ✓ Training complete: Accuracy={history['accuracy'][-1]:.3f}")
    
    # Predict
    predictions = lstm_model.predict(X_dummy[:5])
    print(f"   ✓ Predictions shape: {predictions.shape}")
    print(f"   ✓ Sample prediction: {predictions[0]}")
    
    # Test DNN Model
    print("\n📊 Testing Dense Neural Network...")
    dnn_model = DenseNeuralNetwork(
        hidden_layers=[64, 32],
        dropout_rate=0.3
    )
    
    # Create dummy flat data
    X_flat = np.random.randn(n_samples, n_features)
    
    dnn_model.build_model(input_features=n_features)
    print("   ✓ DNN model built")
    print(f"   ✓ Parameters: {dnn_model.model.count_params():,}")
    
    # Train
    print("\n   Training DNN (2 epochs)...")
    history = dnn_model.train(
        X_flat[:80], y_dummy[:80],
        X_flat[80:], y_dummy[80:],
        epochs=2,
        batch_size=16
    )
    print(f"   ✓ Training complete: Accuracy={history['accuracy'][-1]:.3f}")
    
    print("\n✅ Deep Learning models test complete!")
