"""
Phase 9.E: Model Explainability (XAI)
SHAP values, LIME, and model interpretation tools
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Try to import SHAP (optional)
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("Warning: SHAP not installed. Using fallback methods.")

# Try to import LIME (optional)
try:
    from lime import lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    print("Warning: LIME not installed. Using fallback methods.")


class SHAPExplainer:
    """
    SHAP-based model explanation
    """
    
    def __init__(self, model: Any, X_background: Optional[pd.DataFrame] = None):
        """
        Args:
            model: Trained model
            X_background: Background data for SHAP
        """
        self.model = model
        self.X_background = X_background
        self.explainer = None
        self.shap_values = None
        
        if SHAP_AVAILABLE and X_background is not None:
            self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer"""
        try:
            # Try TreeExplainer first (faster for tree models)
            self.explainer = shap.TreeExplainer(self.model)
            print("✓ Using SHAP TreeExplainer")
        except:
            try:
                # Fallback to KernelExplainer
                self.explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    shap.sample(self.X_background, 100)
                )
                print("✓ Using SHAP KernelExplainer")
            except Exception as e:
                print(f"Warning: Could not initialize SHAP explainer: {e}")
                self.explainer = None
    
    def explain_prediction(
        self,
        X: pd.DataFrame,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Explain a single prediction using SHAP
        
        Args:
            X: Single sample to explain
            feature_names: Feature names
            
        Returns:
            Explanation dictionary
        """
        if not SHAP_AVAILABLE or self.explainer is None:
            return self._fallback_explanation(X, feature_names)
        
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(X)
            
            if isinstance(shap_values, list):
                # Multi-class: use values for predicted class
                prediction = self.model.predict(X)[0]
                shap_vals = shap_values[prediction][0]
            else:
                shap_vals = shap_values[0]
            
            # Get feature names
            if feature_names is None:
                feature_names = X.columns.tolist() if isinstance(X, pd.DataFrame) else \
                               [f'feature_{i}' for i in range(X.shape[1])]
            
            # Sort by absolute importance
            importance_dict = dict(zip(feature_names, shap_vals))
            sorted_features = sorted(
                importance_dict.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            return {
                'method': 'shap',
                'feature_importance': dict(sorted_features),
                'top_features': sorted_features[:10],
                'shap_values': shap_vals.tolist()
            }
            
        except Exception as e:
            print(f"SHAP explanation failed: {e}")
            return self._fallback_explanation(X, feature_names)
    
    def get_global_importance(
        self,
        X: pd.DataFrame,
        max_samples: int = 100
    ) -> Dict[str, float]:
        """
        Get global feature importance using SHAP
        
        Args:
            X: Dataset
            max_samples: Maximum samples to use
            
        Returns:
            Feature importance dictionary
        """
        if not SHAP_AVAILABLE or self.explainer is None:
            return self._fallback_global_importance(X)
        
        try:
            # Sample data if too large
            if len(X) > max_samples:
                X_sample = X.sample(n=max_samples, random_state=42)
            else:
                X_sample = X
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(X_sample)
            
            if isinstance(shap_values, list):
                # Multi-class: average across classes
                shap_values = np.abs(shap_values).mean(axis=0)
            
            # Mean absolute SHAP value per feature
            mean_shap = np.abs(shap_values).mean(axis=0)
            
            feature_names = X.columns.tolist() if isinstance(X, pd.DataFrame) else \
                           [f'feature_{i}' for i in range(X.shape[1])]
            
            importance = dict(zip(feature_names, mean_shap))
            
            # Sort by importance
            importance = dict(
                sorted(importance.items(), key=lambda x: x[1], reverse=True)
            )
            
            return importance
            
        except Exception as e:
            print(f"Global SHAP failed: {e}")
            return self._fallback_global_importance(X)
    
    def _fallback_explanation(
        self,
        X: pd.DataFrame,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Fallback explanation using feature values"""
        if feature_names is None:
            feature_names = X.columns.tolist() if isinstance(X, pd.DataFrame) else \
                           [f'feature_{i}' for i in range(X.shape[1])]
        
        # Use feature importance from model if available
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            elif hasattr(self.model, 'coef_'):
                importances = np.abs(self.model.coef_[0])
            else:
                importances = np.abs(X.values[0])
            
            importance_dict = dict(zip(feature_names, importances))
            sorted_features = sorted(
                importance_dict.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            return {
                'method': 'fallback',
                'feature_importance': dict(sorted_features),
                'top_features': sorted_features[:10]
            }
        except:
            return {'method': 'fallback', 'error': 'Could not generate explanation'}
    
    def _fallback_global_importance(self, X: pd.DataFrame) -> Dict[str, float]:
        """Fallback global importance"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            elif hasattr(self.model, 'coef_'):
                importances = np.abs(self.model.coef_).mean(axis=0)
            else:
                return {}
            
            feature_names = X.columns.tolist() if isinstance(X, pd.DataFrame) else \
                           [f'feature_{i}' for i in range(X.shape[1])]
            
            importance = dict(zip(feature_names, importances))
            return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        except:
            return {}


class LIMEExplainer:
    """
    LIME-based local explanation
    """
    
    def __init__(
        self,
        model: Any,
        X_train: pd.DataFrame,
        mode: str = 'classification'
    ):
        """
        Args:
            model: Trained model
            X_train: Training data
            mode: 'classification' or 'regression'
        """
        self.model = model
        self.X_train = X_train
        self.mode = mode
        self.explainer = None
        
        if LIME_AVAILABLE:
            self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize LIME explainer"""
        try:
            feature_names = self.X_train.columns.tolist() if isinstance(self.X_train, pd.DataFrame) \
                           else [f'feature_{i}' for i in range(self.X_train.shape[1])]
            
            self.explainer = lime_tabular.LimeTabularExplainer(
                self.X_train.values,
                feature_names=feature_names,
                mode=self.mode,
                random_state=42
            )
            print("✓ LIME explainer initialized")
        except Exception as e:
            print(f"Warning: Could not initialize LIME: {e}")
            self.explainer = None
    
    def explain_prediction(
        self,
        X: np.ndarray,
        num_features: int = 10
    ) -> Dict[str, Any]:
        """
        Explain a single prediction using LIME
        
        Args:
            X: Single sample
            num_features: Number of features to include
            
        Returns:
            Explanation dictionary
        """
        if not LIME_AVAILABLE or self.explainer is None:
            return {'method': 'lime', 'error': 'LIME not available'}
        
        try:
            # Get prediction function
            if self.mode == 'classification':
                predict_fn = self.model.predict_proba
            else:
                predict_fn = self.model.predict
            
            # Explain
            exp = self.explainer.explain_instance(
                X.flatten(),
                predict_fn,
                num_features=num_features
            )
            
            # Extract feature importance
            feature_importance = dict(exp.as_list())
            
            return {
                'method': 'lime',
                'feature_importance': feature_importance,
                'top_features': list(feature_importance.items())[:num_features]
            }
            
        except Exception as e:
            return {'method': 'lime', 'error': str(e)}


class ModelInterpreter:
    """
    Comprehensive model interpretation
    """
    
    def __init__(
        self,
        model: Any,
        X_train: pd.DataFrame,
        feature_names: Optional[List[str]] = None
    ):
        """
        Args:
            model: Trained model
            X_train: Training data
            feature_names: Feature names
        """
        self.model = model
        self.X_train = X_train
        self.feature_names = feature_names or \
                            (X_train.columns.tolist() if isinstance(X_train, pd.DataFrame) 
                             else [f'feature_{i}' for i in range(X_train.shape[1])])
        
        # Initialize explainers
        self.shap_explainer = SHAPExplainer(model, X_train)
        self.lime_explainer = LIMEExplainer(model, X_train)
    
    def explain_prediction(
        self,
        X: pd.DataFrame,
        methods: List[str] = ['shap', 'lime', 'native']
    ) -> Dict[str, Any]:
        """
        Explain a prediction using multiple methods
        
        Args:
            X: Single sample
            methods: Explanation methods to use
            
        Returns:
            Combined explanation
        """
        print(f"\n{'='*70}")
        print(f"🔍 Explaining Prediction")
        print(f"{'='*70}\n")
        
        explanations = {}
        
        # Get prediction
        prediction = self.model.predict(X)[0]
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(X)[0]
        else:
            probabilities = None
        
        print(f"Prediction: {prediction}")
        if probabilities is not None:
            print(f"Probabilities: {probabilities}")
        print()
        
        # SHAP explanation
        if 'shap' in methods:
            print("Getting SHAP explanation...")
            shap_exp = self.shap_explainer.explain_prediction(X, self.feature_names)
            explanations['shap'] = shap_exp
            
            if 'top_features' in shap_exp:
                print("Top SHAP features:")
                for feat, val in shap_exp['top_features'][:5]:
                    print(f"   {feat}: {val:.4f}")
            print()
        
        # LIME explanation
        if 'lime' in methods and LIME_AVAILABLE:
            print("Getting LIME explanation...")
            lime_exp = self.lime_explainer.explain_prediction(X.values[0])
            explanations['lime'] = lime_exp
            
            if 'top_features' in lime_exp:
                print("Top LIME features:")
                for feat, val in lime_exp['top_features'][:5]:
                    print(f"   {feat}: {val:.4f}")
            print()
        
        # Native model explanation
        if 'native' in methods:
            print("Getting native feature importance...")
            native_exp = self._get_native_importance()
            explanations['native'] = native_exp
            
            if native_exp:
                print("Top features:")
                for feat, val in list(native_exp.items())[:5]:
                    print(f"   {feat}: {val:.4f}")
            print()
        
        print(f"{'='*70}\n")
        
        return {
            'prediction': int(prediction),
            'probabilities': probabilities.tolist() if probabilities is not None else None,
            'explanations': explanations
        }
    
    def _get_native_importance(self) -> Dict[str, float]:
        """Get native feature importance from model"""
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            elif hasattr(self.model, 'coef_'):
                importances = np.abs(self.model.coef_).mean(axis=0)
            else:
                return {}
            
            importance = dict(zip(self.feature_names, importances))
            return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        except:
            return {}
    
    def get_feature_importance_summary(self) -> pd.DataFrame:
        """
        Get feature importance summary from all methods
        
        Returns:
            DataFrame with feature importance
        """
        print(f"📊 Generating feature importance summary...\n")
        
        importance_data = []
        
        # SHAP global importance
        if SHAP_AVAILABLE:
            shap_importance = self.shap_explainer.get_global_importance(self.X_train)
            for feat, val in shap_importance.items():
                importance_data.append({
                    'feature': feat,
                    'method': 'shap',
                    'importance': val
                })
        
        # Native importance
        native_importance = self._get_native_importance()
        for feat, val in native_importance.items():
            importance_data.append({
                'feature': feat,
                'method': 'native',
                'importance': val
            })
        
        if not importance_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(importance_data)
        
        # Pivot to compare methods
        summary = df.pivot_table(
            index='feature',
            columns='method',
            values='importance',
            fill_value=0
        )
        
        # Add average
        summary['average'] = summary.mean(axis=1)
        summary = summary.sort_values('average', ascending=False)
        
        return summary


# Test code
if __name__ == "__main__":
    print("🔍 Testing Model Explainability...\n")
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    
    # Create synthetic data
    np.random.seed(42)
    n_samples = 500
    n_features = 10
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    y = np.random.randint(0, 3, n_samples)
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    print(f"Model trained. Accuracy: {model.score(X_test, y_test):.4f}\n")
    
    # Test Model Interpreter
    interpreter = ModelInterpreter(model, X_train)
    
    # Explain a single prediction
    X_sample = X_test.iloc[[0]]
    explanation = interpreter.explain_prediction(X_sample)
    
    # Get feature importance summary
    print("="*70)
    print("Feature Importance Summary")
    print("="*70)
    
    summary = interpreter.get_feature_importance_summary()
    if not summary.empty:
        print(summary.head(10))
    else:
        print("No importance data available")
    
    print(f"\n✅ Model explainability test complete!")
