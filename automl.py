"""
Phase 9.D: AutoML Integration
Automated hyperparameter optimization and model selection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    AdaBoostClassifier, ExtraTreesClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score, make_scorer
import json
import warnings
warnings.filterwarnings('ignore')

# Try to import Optuna (optional)
try:
    import optuna
    from optuna.samplers import TPESampler
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("Warning: Optuna not installed. Using grid search fallback.")


class HyperparameterOptimizer:
    """
    Hyperparameter optimization using Optuna or grid search
    """
    
    def __init__(self, n_trials: int = 50, timeout: Optional[int] = None):
        """
        Args:
            n_trials: Number of optimization trials
            timeout: Maximum optimization time in seconds
        """
        self.n_trials = n_trials
        self.timeout = timeout
        self.best_params = None
        self.best_score = None
        self.study = None
    
    def optimize_random_forest(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        cv: int = 5
    ) -> Dict[str, Any]:
        """
        Optimize Random Forest hyperparameters
        
        Args:
            X: Features
            y: Target
            cv: Cross-validation folds
            
        Returns:
            Best parameters
        """
        print(f"🔍 Optimizing Random Forest hyperparameters...")
        
        if OPTUNA_AVAILABLE:
            return self._optimize_rf_optuna(X, y, cv)
        else:
            return self._optimize_rf_grid(X, y, cv)
    
    def _optimize_rf_optuna(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        cv: int
    ) -> Dict[str, Any]:
        """Optimize using Optuna"""
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
                'random_state': 42,
                'n_jobs': -1
            }
            
            model = RandomForestClassifier(**params)
            scores = cross_val_score(model, X, y, cv=cv, scoring='f1_weighted', n_jobs=-1)
            
            return scores.mean()
        
        self.study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=42)
        )
        
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True
        )
        
        self.best_params = self.study.best_params
        self.best_score = self.study.best_value
        
        print(f"   ✓ Best F1: {self.best_score:.4f}")
        print(f"   ✓ Best params: {self.best_params}")
        
        return self.best_params
    
    def _optimize_rf_grid(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        cv: int
    ) -> Dict[str, Any]:
        """Fallback grid search"""
        
        param_grid = [
            {'n_estimators': 100, 'max_depth': 10, 'min_samples_split': 5},
            {'n_estimators': 200, 'max_depth': 15, 'min_samples_split': 2},
            {'n_estimators': 150, 'max_depth': 20, 'min_samples_split': 10},
        ]
        
        best_score = 0
        best_params = None
        
        for params in param_grid:
            params['random_state'] = 42
            params['n_jobs'] = -1
            
            model = RandomForestClassifier(**params)
            scores = cross_val_score(model, X, y, cv=cv, scoring='f1_weighted', n_jobs=-1)
            score = scores.mean()
            
            if score > best_score:
                best_score = score
                best_params = params
        
        self.best_params = best_params
        self.best_score = best_score
        
        print(f"   ✓ Best F1: {best_score:.4f}")
        
        return best_params
    
    def optimize_xgboost(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        cv: int = 5
    ) -> Dict[str, Any]:
        """
        Optimize XGBoost hyperparameters
        
        Args:
            X: Features
            y: Target
            cv: Cross-validation folds
            
        Returns:
            Best parameters
        """
        print(f"🔍 Optimizing XGBoost hyperparameters...")
        
        try:
            import xgboost as xgb
        except ImportError:
            print("   ⚠️  XGBoost not installed, skipping")
            return {}
        
        if not OPTUNA_AVAILABLE:
            # Default params
            return {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8
            }
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 12),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'gamma': trial.suggest_float('gamma', 0, 5),
                'random_state': 42,
                'n_jobs': -1,
                'eval_metric': 'mlogloss'
            }
            
            model = xgb.XGBClassifier(**params)
            scores = cross_val_score(model, X, y, cv=cv, scoring='f1_weighted', n_jobs=-1)
            
            return scores.mean()
        
        study = optuna.create_study(direction='maximize', sampler=TPESampler(seed=42))
        study.optimize(objective, n_trials=self.n_trials, timeout=self.timeout, show_progress_bar=True)
        
        self.best_params = study.best_params
        self.best_score = study.best_value
        
        print(f"   ✓ Best F1: {self.best_score:.4f}")
        
        return self.best_params
    
    def optimize_neural_network(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        cv: int = 5
    ) -> Dict[str, Any]:
        """
        Optimize Neural Network hyperparameters
        
        Args:
            X: Features
            y: Target
            cv: Cross-validation folds
            
        Returns:
            Best parameters
        """
        print(f"🔍 Optimizing Neural Network hyperparameters...")
        
        if not OPTUNA_AVAILABLE:
            return {
                'hidden_layer_sizes': (128, 64, 32),
                'activation': 'relu',
                'alpha': 0.0001,
                'learning_rate_init': 0.001
            }
        
        def objective(trial):
            # Architecture
            n_layers = trial.suggest_int('n_layers', 1, 4)
            hidden_layers = tuple([
                trial.suggest_int(f'n_units_l{i}', 32, 256)
                for i in range(n_layers)
            ])
            
            params = {
                'hidden_layer_sizes': hidden_layers,
                'activation': trial.suggest_categorical('activation', ['relu', 'tanh']),
                'alpha': trial.suggest_float('alpha', 1e-5, 1e-2, log=True),
                'learning_rate_init': trial.suggest_float('learning_rate_init', 1e-4, 1e-2, log=True),
                'max_iter': 500,
                'random_state': 42,
                'early_stopping': True
            }
            
            model = MLPClassifier(**params)
            scores = cross_val_score(model, X, y, cv=cv, scoring='f1_weighted', n_jobs=-1)
            
            return scores.mean()
        
        study = optuna.create_study(direction='maximize', sampler=TPESampler(seed=42))
        study.optimize(objective, n_trials=min(30, self.n_trials), timeout=self.timeout, show_progress_bar=True)
        
        self.best_params = study.best_params
        self.best_score = study.best_value
        
        # Reconstruct hidden layers
        n_layers = self.best_params['n_layers']
        hidden_layers = tuple([
            self.best_params[f'n_units_l{i}']
            for i in range(n_layers)
        ])
        self.best_params['hidden_layer_sizes'] = hidden_layers
        
        print(f"   ✓ Best F1: {self.best_score:.4f}")
        print(f"   ✓ Architecture: {hidden_layers}")
        
        return self.best_params


class AutoModelSelector:
    """
    Automatically select the best model from multiple candidates
    """
    
    def __init__(self, cv: int = 5, scoring: str = 'f1_weighted'):
        """
        Args:
            cv: Cross-validation folds
            scoring: Scoring metric
        """
        self.cv = cv
        self.scoring = scoring
        self.results = []
        self.best_model = None
        self.best_model_name = None
        self.best_score = 0
    
    def evaluate_models(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        models: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Evaluate multiple models and select the best
        
        Args:
            X: Features
            y: Target
            models: Dictionary of models to evaluate
            
        Returns:
            Dictionary of model scores
        """
        print(f"\n{'='*70}")
        print(f"🤖 Auto Model Selection")
        print(f"{'='*70}\n")
        
        if models is None:
            models = self._get_default_models()
        
        scores = {}
        
        for name, model in models.items():
            print(f"Evaluating {name}...")
            
            try:
                cv_scores = cross_val_score(
                    model, X, y,
                    cv=self.cv,
                    scoring=self.scoring,
                    n_jobs=-1
                )
                
                mean_score = cv_scores.mean()
                std_score = cv_scores.std()
                
                scores[name] = mean_score
                
                self.results.append({
                    'model': name,
                    'mean_score': float(mean_score),
                    'std_score': float(std_score),
                    'cv_scores': cv_scores.tolist()
                })
                
                print(f"   ✓ {name}: {mean_score:.4f} (±{std_score:.4f})")
                
                # Track best
                if mean_score > self.best_score:
                    self.best_score = mean_score
                    self.best_model = model
                    self.best_model_name = name
                
            except Exception as e:
                print(f"   ✗ {name}: Failed - {str(e)}")
                scores[name] = 0.0
        
        print(f"\n{'='*70}")
        print(f"🏆 Best Model: {self.best_model_name}")
        print(f"   Score: {self.best_score:.4f}")
        print(f"{'='*70}\n")
        
        return scores
    
    def _get_default_models(self) -> Dict[str, Any]:
        """Get default model candidates"""
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
            'Extra Trees': ExtraTreesClassifier(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            ),
            'Logistic Regression': LogisticRegression(
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            ),
            'Neural Network': MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                max_iter=500,
                random_state=42,
                early_stopping=True
            )
        }
        
        # Try to add XGBoost
        try:
            import xgboost as xgb
            models['XGBoost'] = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                eval_metric='mlogloss'
            )
        except ImportError:
            pass
        
        # Try to add LightGBM
        try:
            import lightgbm as lgb
            models['LightGBM'] = lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
        except ImportError:
            pass
        
        return models
    
    def get_best_model(self) -> Tuple[str, Any, float]:
        """
        Get the best model
        
        Returns:
            (model_name, model_object, score)
        """
        return self.best_model_name, self.best_model, self.best_score
    
    def get_results_df(self) -> pd.DataFrame:
        """Get results as DataFrame"""
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        df = df.sort_values('mean_score', ascending=False)
        
        return df


class EnsembleOptimizer:
    """
    Optimize ensemble weights for multiple models
    """
    
    def __init__(self):
        self.models = []
        self.weights = None
        self.best_score = 0
    
    def add_model(self, name: str, model: Any):
        """Add a model to the ensemble"""
        self.models.append({'name': name, 'model': model})
    
    def optimize_weights(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        cv: int = 5
    ) -> np.ndarray:
        """
        Optimize ensemble weights
        
        Args:
            X: Features
            y: Target
            cv: Cross-validation folds
            
        Returns:
            Optimal weights
        """
        print(f"🔍 Optimizing ensemble weights for {len(self.models)} models...")
        
        if not OPTUNA_AVAILABLE:
            # Equal weights
            self.weights = np.ones(len(self.models)) / len(self.models)
            print(f"   Using equal weights (Optuna not available)")
            return self.weights
        
        # Get predictions from all models
        predictions = []
        for model_info in self.models:
            model = model_info['model']
            
            # Cross-validation predictions
            from sklearn.model_selection import cross_val_predict
            y_pred_proba = cross_val_predict(
                model, X, y,
                cv=cv,
                method='predict_proba',
                n_jobs=-1
            )
            predictions.append(y_pred_proba)
        
        predictions = np.array(predictions)
        
        def objective(trial):
            # Sample weights (sum to 1)
            weights = np.array([
                trial.suggest_float(f'weight_{i}', 0, 1)
                for i in range(len(self.models))
            ])
            weights = weights / weights.sum()
            
            # Weighted average of predictions
            ensemble_pred_proba = np.zeros_like(predictions[0])
            for i, weight in enumerate(weights):
                ensemble_pred_proba += weight * predictions[i]
            
            # Get class predictions
            ensemble_pred = np.argmax(ensemble_pred_proba, axis=1)
            
            # Calculate score
            score = f1_score(y, ensemble_pred, average='weighted')
            
            return score
        
        study = optuna.create_study(direction='maximize', sampler=TPESampler(seed=42))
        study.optimize(objective, n_trials=100, show_progress_bar=True)
        
        # Get best weights
        self.weights = np.array([
            study.best_params[f'weight_{i}']
            for i in range(len(self.models))
        ])
        self.weights = self.weights / self.weights.sum()
        self.best_score = study.best_value
        
        print(f"   ✓ Best F1: {self.best_score:.4f}")
        print(f"   ✓ Weights: {self.weights}")
        
        return self.weights
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make ensemble predictions"""
        if self.weights is None:
            raise ValueError("Weights not optimized. Call optimize_weights() first.")
        
        predictions = []
        for model_info in self.models:
            pred_proba = model_info['model'].predict_proba(X)
            predictions.append(pred_proba)
        
        predictions = np.array(predictions)
        
        # Weighted average
        ensemble_pred_proba = np.zeros_like(predictions[0])
        for i, weight in enumerate(self.weights):
            ensemble_pred_proba += weight * predictions[i]
        
        return np.argmax(ensemble_pred_proba, axis=1)


# Test code
if __name__ == "__main__":
    print("🤖 Testing AutoML Integration...\n")
    
    # Create synthetic data
    np.random.seed(42)
    n_samples = 500
    n_features = 20
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    y = np.random.randint(0, 3, n_samples)
    
    # Test 1: Hyperparameter Optimization
    print("="*70)
    print("Test 1: Hyperparameter Optimization")
    print("="*70 + "\n")
    
    optimizer = HyperparameterOptimizer(n_trials=10)
    
    # Optimize Random Forest
    rf_params = optimizer.optimize_random_forest(X, y, cv=3)
    print(f"Random Forest params: {rf_params}\n")
    
    # Optimize Neural Network
    nn_params = optimizer.optimize_neural_network(X, y, cv=3)
    print(f"Neural Network params: {nn_params}\n")
    
    # Test 2: Auto Model Selection
    print("\n" + "="*70)
    print("Test 2: Auto Model Selection")
    print("="*70)
    
    selector = AutoModelSelector(cv=3)
    scores = selector.evaluate_models(X, y)
    
    best_name, best_model, best_score = selector.get_best_model()
    print(f"\nSelected: {best_name} with score {best_score:.4f}")
    
    # Results DataFrame
    results_df = selector.get_results_df()
    print(f"\nTop 3 Models:")
    print(results_df.head(3)[['model', 'mean_score', 'std_score']])
    
    # Test 3: Ensemble Optimization
    print("\n" + "="*70)
    print("Test 3: Ensemble Optimization")
    print("="*70 + "\n")
    
    ensemble = EnsembleOptimizer()
    
    # Add top 3 models
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    ensemble.add_model('Random Forest', rf)
    
    gb = GradientBoostingClassifier(n_estimators=50, random_state=42)
    gb.fit(X_train, y_train)
    ensemble.add_model('Gradient Boosting', gb)
    
    et = ExtraTreesClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    et.fit(X_train, y_train)
    ensemble.add_model('Extra Trees', et)
    
    # Optimize weights
    weights = ensemble.optimize_weights(X_train, y_train, cv=3)
    
    # Make predictions
    ensemble_pred = ensemble.predict(X_test)
    ensemble_score = f1_score(y_test, ensemble_pred, average='weighted')
    
    print(f"\nEnsemble F1 Score: {ensemble_score:.4f}")
    
    print(f"\n✅ AutoML integration test complete!")
