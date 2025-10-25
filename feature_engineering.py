"""
Phase 9.B: Advanced Feature Engineering
Automated feature extraction, transformation, and selection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
from sklearn.preprocessing import (
    PolynomialFeatures, StandardScaler, MinMaxScaler,
    RobustScaler, PowerTransformer
)
from sklearn.feature_selection import (
    SelectKBest, f_classif, mutual_info_classif,
    RFE, SelectFromModel
)
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """
    Advanced feature engineering with automated transformations
    """
    
    def __init__(self):
        self.polynomial_features = None
        self.scaler = None
        self.feature_selector = None
        self.pca = None
        self.original_features = None
        self.engineered_features = None
        self.feature_importance = {}
    
    def create_polynomial_features(
        self,
        X: pd.DataFrame,
        degree: int = 2,
        interaction_only: bool = False,
        include_bias: bool = False
    ) -> pd.DataFrame:
        """
        Create polynomial and interaction features
        
        Args:
            X: Input features
            degree: Polynomial degree
            interaction_only: Only create interaction features
            include_bias: Include bias column
            
        Returns:
            DataFrame with polynomial features
        """
        print(f"🔧 Creating polynomial features (degree={degree})...")
        
        self.polynomial_features = PolynomialFeatures(
            degree=degree,
            interaction_only=interaction_only,
            include_bias=include_bias
        )
        
        X_poly = self.polynomial_features.fit_transform(X)
        
        # Get feature names
        feature_names = self.polynomial_features.get_feature_names_out(X.columns)
        
        X_poly_df = pd.DataFrame(X_poly, columns=feature_names, index=X.index)
        
        print(f"   ✓ Created {X_poly_df.shape[1]} features from {X.shape[1]} original features")
        
        return X_poly_df
    
    def create_interaction_features(
        self,
        X: pd.DataFrame,
        feature_pairs: Optional[List[Tuple[str, str]]] = None
    ) -> pd.DataFrame:
        """
        Create custom interaction features
        
        Args:
            X: Input features
            feature_pairs: List of feature pairs to interact, None = all pairs
            
        Returns:
            DataFrame with interaction features
        """
        print(f"🔧 Creating interaction features...")
        
        X_interactions = X.copy()
        
        if feature_pairs is None:
            # Create all pairs
            columns = X.columns.tolist()
            feature_pairs = []
            for i, col1 in enumerate(columns):
                for col2 in columns[i+1:]:
                    feature_pairs.append((col1, col2))
        
        for col1, col2 in feature_pairs:
            if col1 in X.columns and col2 in X.columns:
                # Multiplication
                X_interactions[f'{col1}_x_{col2}'] = X[col1] * X[col2]
                
                # Division (avoid divide by zero)
                X_interactions[f'{col1}_div_{col2}'] = X[col1] / (X[col2] + 1e-8)
                
                # Difference
                X_interactions[f'{col1}_minus_{col2}'] = X[col1] - X[col2]
        
        print(f"   ✓ Created {X_interactions.shape[1] - X.shape[1]} interaction features")
        
        return X_interactions
    
    def create_statistical_features(
        self,
        X: pd.DataFrame,
        window_sizes: List[int] = [3, 5, 10]
    ) -> pd.DataFrame:
        """
        Create statistical features (rolling mean, std, min, max)
        
        Args:
            X: Input features (should be time-ordered)
            window_sizes: Rolling window sizes
            
        Returns:
            DataFrame with statistical features
        """
        print(f"🔧 Creating statistical features...")
        
        X_stats = X.copy()
        
        for col in X.columns:
            for window in window_sizes:
                # Rolling mean
                X_stats[f'{col}_rolling_mean_{window}'] = \
                    X[col].rolling(window=window, min_periods=1).mean()
                
                # Rolling std
                X_stats[f'{col}_rolling_std_{window}'] = \
                    X[col].rolling(window=window, min_periods=1).std().fillna(0)
                
                # Rolling min
                X_stats[f'{col}_rolling_min_{window}'] = \
                    X[col].rolling(window=window, min_periods=1).min()
                
                # Rolling max
                X_stats[f'{col}_rolling_max_{window}'] = \
                    X[col].rolling(window=window, min_periods=1).max()
        
        print(f"   ✓ Created {X_stats.shape[1] - X.shape[1]} statistical features")
        
        return X_stats
    
    def create_ratio_features(
        self,
        X: pd.DataFrame,
        numerators: List[str],
        denominators: List[str]
    ) -> pd.DataFrame:
        """
        Create ratio features
        
        Args:
            X: Input features
            numerators: List of numerator columns
            denominators: List of denominator columns
            
        Returns:
            DataFrame with ratio features
        """
        print(f"🔧 Creating ratio features...")
        
        X_ratios = X.copy()
        
        for num_col in numerators:
            for den_col in denominators:
                if num_col in X.columns and den_col in X.columns:
                    X_ratios[f'{num_col}_per_{den_col}'] = \
                        X[num_col] / (X[den_col] + 1e-8)
        
        print(f"   ✓ Created {X_ratios.shape[1] - X.shape[1]} ratio features")
        
        return X_ratios
    
    def select_features_univariate(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        k: int = 50,
        score_func: Callable = f_classif
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Select top k features using univariate statistical tests
        
        Args:
            X: Input features
            y: Target variable
            k: Number of features to select
            score_func: Scoring function
            
        Returns:
            Selected features and feature names
        """
        print(f"📊 Selecting {k} best features (univariate)...")
        
        self.feature_selector = SelectKBest(score_func=score_func, k=min(k, X.shape[1]))
        X_selected = self.feature_selector.fit_transform(X, y)
        
        # Get selected feature names
        selected_indices = self.feature_selector.get_support(indices=True)
        selected_features = X.columns[selected_indices].tolist()
        
        # Get scores
        scores = self.feature_selector.scores_[selected_indices]
        self.feature_importance = dict(zip(selected_features, scores))
        
        print(f"   ✓ Selected {len(selected_features)} features")
        
        return pd.DataFrame(X_selected, columns=selected_features, index=X.index), selected_features
    
    def select_features_recursive(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        n_features: int = 50,
        estimator = None
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Select features using Recursive Feature Elimination
        
        Args:
            X: Input features
            y: Target variable
            n_features: Number of features to select
            estimator: Model to use for feature selection
            
        Returns:
            Selected features and feature names
        """
        print(f"📊 Selecting {n_features} features (RFE)...")
        
        if estimator is None:
            estimator = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
        
        rfe = RFE(estimator=estimator, n_features_to_select=min(n_features, X.shape[1]))
        X_selected = rfe.fit_transform(X, y)
        
        # Get selected feature names
        selected_indices = rfe.get_support(indices=True)
        selected_features = X.columns[selected_indices].tolist()
        
        # Get feature rankings
        rankings = rfe.ranking_[selected_indices]
        self.feature_importance = dict(zip(selected_features, 1.0 / rankings))
        
        print(f"   ✓ Selected {len(selected_features)} features using RFE")
        
        return pd.DataFrame(X_selected, columns=selected_features, index=X.index), selected_features
    
    def select_features_model_based(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        threshold: str = 'median',
        estimator = None
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Select features based on model importance
        
        Args:
            X: Input features
            y: Target variable
            threshold: Importance threshold
            estimator: Model to use
            
        Returns:
            Selected features and feature names
        """
        print(f"📊 Selecting features (model-based, threshold={threshold})...")
        
        if estimator is None:
            estimator = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            estimator.fit(X, y)
        
        selector = SelectFromModel(estimator=estimator, threshold=threshold, prefit=True)
        X_selected = selector.transform(X)
        
        # Get selected feature names
        selected_indices = selector.get_support(indices=True)
        selected_features = X.columns[selected_indices].tolist()
        
        # Get feature importances
        importances = estimator.feature_importances_[selected_indices]
        self.feature_importance = dict(zip(selected_features, importances))
        
        print(f"   ✓ Selected {len(selected_features)} features based on importance")
        
        return pd.DataFrame(X_selected, columns=selected_features, index=X.index), selected_features
    
    def apply_pca(
        self,
        X: pd.DataFrame,
        n_components: Optional[int] = None,
        variance_threshold: float = 0.95
    ) -> Tuple[pd.DataFrame, PCA]:
        """
        Apply PCA for dimensionality reduction
        
        Args:
            X: Input features
            n_components: Number of components, None = auto based on variance
            variance_threshold: Cumulative variance threshold
            
        Returns:
            Transformed features and PCA object
        """
        print(f"📊 Applying PCA...")
        
        if n_components is None:
            # Determine n_components based on variance threshold
            pca_temp = PCA().fit(X)
            cumsum_var = np.cumsum(pca_temp.explained_variance_ratio_)
            n_components = np.argmax(cumsum_var >= variance_threshold) + 1
        
        self.pca = PCA(n_components=n_components)
        X_pca = self.pca.fit_transform(X)
        
        # Create column names
        columns = [f'PC{i+1}' for i in range(n_components)]
        
        print(f"   ✓ Reduced to {n_components} components")
        print(f"   ✓ Explained variance: {self.pca.explained_variance_ratio_.sum():.4f}")
        
        return pd.DataFrame(X_pca, columns=columns, index=X.index), self.pca
    
    def transform_features(
        self,
        X: pd.DataFrame,
        method: str = 'standard'
    ) -> pd.DataFrame:
        """
        Transform features using various scalers
        
        Args:
            X: Input features
            method: Transformation method ('standard', 'minmax', 'robust', 'power')
            
        Returns:
            Transformed features
        """
        print(f"🔧 Transforming features ({method})...")
        
        if method == 'standard':
            self.scaler = StandardScaler()
        elif method == 'minmax':
            self.scaler = MinMaxScaler()
        elif method == 'robust':
            self.scaler = RobustScaler()
        elif method == 'power':
            self.scaler = PowerTransformer()
        else:
            raise ValueError(f"Unknown method: {method}")
        
        X_transformed = self.scaler.fit_transform(X)
        
        print(f"   ✓ Features transformed")
        
        return pd.DataFrame(X_transformed, columns=X.columns, index=X.index)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        return self.feature_importance


class AutoFeatureEngineer:
    """
    Automated feature engineering pipeline
    """
    
    def __init__(self):
        self.engineer = FeatureEngineer()
        self.pipeline_steps = []
        self.final_features = None
    
    def fit_transform(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        create_polynomials: bool = True,
        create_interactions: bool = True,
        create_statistics: bool = False,
        select_features: bool = True,
        n_features: int = 50,
        apply_pca: bool = False,
        pca_variance: float = 0.95
    ) -> pd.DataFrame:
        """
        Automated feature engineering pipeline
        
        Args:
            X: Input features
            y: Target variable
            create_polynomials: Create polynomial features
            create_interactions: Create interaction features
            create_statistics: Create statistical features
            select_features: Apply feature selection
            n_features: Number of features to select
            apply_pca: Apply PCA
            pca_variance: PCA variance threshold
            
        Returns:
            Engineered features
        """
        print(f"\n{'='*70}")
        print(f"🤖 Automated Feature Engineering Pipeline")
        print(f"{'='*70}")
        print(f"Input: {X.shape[0]} samples, {X.shape[1]} features\n")
        
        X_engineered = X.copy()
        self.pipeline_steps = []
        
        # Step 1: Polynomial features
        if create_polynomials:
            X_engineered = self.engineer.create_polynomial_features(
                X_engineered, degree=2, interaction_only=False
            )
            self.pipeline_steps.append('polynomial_features')
        
        # Step 2: Interaction features
        if create_interactions and not create_polynomials:
            # Only if not already created by polynomial
            X_engineered = self.engineer.create_interaction_features(X_engineered)
            self.pipeline_steps.append('interaction_features')
        
        # Step 3: Statistical features
        if create_statistics:
            X_engineered = self.engineer.create_statistical_features(X_engineered)
            self.pipeline_steps.append('statistical_features')
        
        print(f"\n📊 After feature creation: {X_engineered.shape[1]} features")
        
        # Step 4: Feature selection
        if select_features and X_engineered.shape[1] > n_features:
            X_engineered, selected_features = self.engineer.select_features_model_based(
                X_engineered, y, threshold='median'
            )
            self.pipeline_steps.append('feature_selection')
            self.final_features = selected_features
        
        # Step 5: PCA
        if apply_pca:
            X_engineered, pca_obj = self.engineer.apply_pca(
                X_engineered, variance_threshold=pca_variance
            )
            self.pipeline_steps.append('pca')
        
        # Step 6: Scaling
        X_engineered = self.engineer.transform_features(X_engineered, method='standard')
        self.pipeline_steps.append('scaling')
        
        print(f"\n{'='*70}")
        print(f"✅ Feature Engineering Complete")
        print(f"   Final features: {X_engineered.shape[1]}")
        print(f"   Pipeline steps: {' → '.join(self.pipeline_steps)}")
        print(f"{'='*70}\n")
        
        return X_engineered
    
    def get_top_features(self, n: int = 20) -> Dict[str, float]:
        """Get top n important features"""
        importance = self.engineer.get_feature_importance()
        
        # Sort by importance
        sorted_features = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)[:n]
        )
        
        return sorted_features


# Test code
if __name__ == "__main__":
    print("🔧 Testing Advanced Feature Engineering...\n")
    
    # Create synthetic data
    np.random.seed(42)
    n_samples = 500
    n_features = 10
    
    # Generate features
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    # Generate target
    y = np.random.randint(0, 3, n_samples)
    
    # Test Auto Feature Engineer
    auto_fe = AutoFeatureEngineer()
    
    X_engineered = auto_fe.fit_transform(
        X, y,
        create_polynomials=True,
        create_interactions=False,
        create_statistics=False,
        select_features=True,
        n_features=30,
        apply_pca=False
    )
    
    print(f"📈 Results:")
    print(f"   Original features: {X.shape[1]}")
    print(f"   Engineered features: {X_engineered.shape[1]}")
    print(f"   Pipeline: {' → '.join(auto_fe.pipeline_steps)}")
    
    # Top features
    print(f"\n🏆 Top 10 Important Features:")
    top_features = auto_fe.get_top_features(n=10)
    for i, (feature, importance) in enumerate(top_features.items(), 1):
        print(f"   {i}. {feature}: {importance:.6f}")
    
    print(f"\n✅ Feature Engineering test complete!")
