"""
Phase 9.C: Model Monitoring & Drift Detection
Real-time performance tracking and data/concept drift detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')


class DataDriftDetector:
    """
    Detect data drift using statistical tests
    """
    
    def __init__(self, significance_level: float = 0.05):
        """
        Args:
            significance_level: p-value threshold for drift detection
        """
        self.significance_level = significance_level
        self.reference_stats = {}
        self.drift_history = []
    
    def set_reference(self, X: pd.DataFrame):
        """
        Set reference data distribution
        
        Args:
            X: Reference data
        """
        print(f"📊 Setting reference distribution ({X.shape[0]} samples)...")
        
        self.reference_stats = {}
        
        for col in X.columns:
            self.reference_stats[col] = {
                'mean': X[col].mean(),
                'std': X[col].std(),
                'min': X[col].min(),
                'max': X[col].max(),
                'q25': X[col].quantile(0.25),
                'q50': X[col].quantile(0.50),
                'q75': X[col].quantile(0.75),
                'data': X[col].values  # Store for KS test
            }
        
        print(f"   ✓ Reference set for {len(self.reference_stats)} features")
    
    def detect_drift_ks_test(
        self,
        X: pd.DataFrame,
        features: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Detect drift using Kolmogorov-Smirnov test
        
        Args:
            X: Current data
            features: Features to check, None = all
            
        Returns:
            Drift detection results
        """
        if not self.reference_stats:
            raise ValueError("Reference distribution not set. Call set_reference() first.")
        
        if features is None:
            features = list(self.reference_stats.keys())
        
        results = {}
        
        for feature in features:
            if feature not in self.reference_stats or feature not in X.columns:
                continue
            
            # KS test
            statistic, p_value = stats.ks_2samp(
                self.reference_stats[feature]['data'],
                X[feature].values
            )
            
            is_drift = p_value < self.significance_level
            
            results[feature] = {
                'test': 'ks_test',
                'statistic': float(statistic),
                'p_value': float(p_value),
                'drift_detected': bool(is_drift),
                'severity': self._calculate_severity(statistic)
            }
        
        return results
    
    def detect_drift_psi(
        self,
        X: pd.DataFrame,
        features: Optional[List[str]] = None,
        bins: int = 10
    ) -> Dict[str, Dict]:
        """
        Detect drift using Population Stability Index (PSI)
        
        Args:
            X: Current data
            features: Features to check
            bins: Number of bins for PSI calculation
            
        Returns:
            PSI results
        """
        if not self.reference_stats:
            raise ValueError("Reference distribution not set.")
        
        if features is None:
            features = list(self.reference_stats.keys())
        
        results = {}
        
        for feature in features:
            if feature not in self.reference_stats or feature not in X.columns:
                continue
            
            # Calculate PSI
            psi = self._calculate_psi(
                self.reference_stats[feature]['data'],
                X[feature].values,
                bins
            )
            
            # PSI thresholds: <0.1 = no drift, 0.1-0.25 = moderate, >0.25 = significant
            drift_detected = psi > 0.1
            
            results[feature] = {
                'test': 'psi',
                'psi_value': float(psi),
                'drift_detected': bool(drift_detected),
                'severity': 'high' if psi > 0.25 else 'moderate' if psi > 0.1 else 'low'
            }
        
        return results
    
    def _calculate_psi(
        self,
        expected: np.ndarray,
        actual: np.ndarray,
        bins: int
    ) -> float:
        """
        Calculate Population Stability Index
        
        Args:
            expected: Expected distribution
            actual: Actual distribution
            bins: Number of bins
            
        Returns:
            PSI value
        """
        # Create bins based on expected distribution
        breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1))
        breakpoints = np.unique(breakpoints)  # Remove duplicates
        
        if len(breakpoints) < 2:
            return 0.0
        
        # Calculate distribution
        expected_percents = np.histogram(expected, bins=breakpoints)[0] / len(expected)
        actual_percents = np.histogram(actual, bins=breakpoints)[0] / len(actual)
        
        # Avoid division by zero
        expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
        actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
        
        # Calculate PSI
        psi = np.sum((actual_percents - expected_percents) * 
                     np.log(actual_percents / expected_percents))
        
        return psi
    
    def _calculate_severity(self, statistic: float) -> str:
        """Calculate drift severity from KS statistic"""
        if statistic > 0.3:
            return 'high'
        elif statistic > 0.15:
            return 'moderate'
        else:
            return 'low'
    
    def generate_report(
        self,
        X: pd.DataFrame,
        method: str = 'ks_test'
    ) -> Dict:
        """
        Generate comprehensive drift report
        
        Args:
            X: Current data
            method: Detection method ('ks_test' or 'psi')
            
        Returns:
            Drift report
        """
        print(f"\n{'='*70}")
        print(f"📊 Data Drift Detection Report ({method})")
        print(f"{'='*70}")
        
        if method == 'ks_test':
            results = self.detect_drift_ks_test(X)
        elif method == 'psi':
            results = self.detect_drift_psi(X)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Count drift
        drift_features = [f for f, r in results.items() if r['drift_detected']]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'total_features': len(results),
            'drift_features': len(drift_features),
            'drift_ratio': len(drift_features) / len(results) if results else 0,
            'drift_detected': len(drift_features) > 0,
            'features': results
        }
        
        print(f"\nTotal features checked: {report['total_features']}")
        print(f"Features with drift: {report['drift_features']} ({report['drift_ratio']*100:.1f}%)")
        
        if drift_features:
            print(f"\n⚠️  Drift detected in features:")
            for feature in drift_features[:10]:  # Show top 10
                severity = results[feature].get('severity', 'unknown')
                print(f"   - {feature} (severity: {severity})")
        else:
            print(f"\n✅ No significant drift detected")
        
        print(f"{'='*70}\n")
        
        # Store in history
        self.drift_history.append(report)
        
        return report


class ConceptDriftDetector:
    """
    Detect concept drift (changes in P(Y|X))
    """
    
    def __init__(self, window_size: int = 100):
        """
        Args:
            window_size: Size of sliding window for drift detection
        """
        self.window_size = window_size
        self.performance_history = []
        self.drift_points = []
    
    def add_prediction(
        self,
        y_true: int,
        y_pred: int,
        y_proba: Optional[np.ndarray] = None
    ):
        """
        Add a prediction to history
        
        Args:
            y_true: True label
            y_pred: Predicted label
            y_proba: Prediction probabilities
        """
        self.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'y_true': y_true,
            'y_pred': y_pred,
            'correct': y_true == y_pred,
            'y_proba': y_proba.tolist() if y_proba is not None else None
        })
        
        # Keep only recent history
        if len(self.performance_history) > self.window_size * 2:
            self.performance_history = self.performance_history[-self.window_size * 2:]
    
    def detect_drift_adwin(self, threshold: float = 0.1) -> bool:
        """
        Detect concept drift using ADWIN-like approach
        
        Args:
            threshold: Performance drop threshold
            
        Returns:
            True if drift detected
        """
        if len(self.performance_history) < self.window_size * 2:
            return False
        
        # Split into two windows
        recent = self.performance_history[-self.window_size:]
        older = self.performance_history[-self.window_size*2:-self.window_size]
        
        # Calculate accuracy in each window
        recent_acc = np.mean([p['correct'] for p in recent])
        older_acc = np.mean([p['correct'] for p in older])
        
        # Detect significant drop
        drift_detected = (older_acc - recent_acc) > threshold
        
        if drift_detected:
            self.drift_points.append({
                'timestamp': datetime.now().isoformat(),
                'older_accuracy': float(older_acc),
                'recent_accuracy': float(recent_acc),
                'drop': float(older_acc - recent_acc)
            })
        
        return drift_detected
    
    def get_current_performance(self) -> Dict:
        """Get current performance metrics"""
        if len(self.performance_history) < 10:
            return {}
        
        recent = self.performance_history[-min(len(self.performance_history), self.window_size):]
        
        y_true = [p['y_true'] for p in recent]
        y_pred = [p['y_pred'] for p in recent]
        
        return {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'samples': len(recent),
            'window_size': self.window_size
        }


class ModelPerformanceMonitor:
    """
    Monitor model performance over time
    """
    
    def __init__(self, save_path: str = 'model_performance.json'):
        """
        Args:
            save_path: Path to save performance history
        """
        self.save_path = save_path
        self.metrics_history = []
        self.load_history()
    
    def log_prediction(
        self,
        model_name: str,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Log prediction results
        
        Args:
            model_name: Name of the model
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities
            metadata: Additional metadata
        """
        # Calculate metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'n_samples': len(y_true),
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
        }
        
        if metadata:
            metrics['metadata'] = metadata
        
        self.metrics_history.append(metrics)
        
        # Auto-save
        self.save_history()
    
    def get_recent_performance(
        self,
        model_name: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict]:
        """
        Get recent performance metrics
        
        Args:
            model_name: Filter by model name
            hours: Last N hours
            
        Returns:
            Recent metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if model_name:
            recent = [m for m in recent if m['model_name'] == model_name]
        
        return recent
    
    def detect_performance_degradation(
        self,
        model_name: str,
        metric: str = 'accuracy',
        threshold: float = 0.05,
        window_hours: int = 24
    ) -> Tuple[bool, Dict]:
        """
        Detect if model performance is degrading
        
        Args:
            model_name: Model to check
            metric: Metric to monitor
            threshold: Degradation threshold
            window_hours: Time window
            
        Returns:
            (degradation_detected, details)
        """
        recent = self.get_recent_performance(model_name, window_hours)
        
        if len(recent) < 2:
            return False, {'reason': 'insufficient_data'}
        
        # Compare first half vs second half
        mid = len(recent) // 2
        older_metrics = [m[metric] for m in recent[:mid]]
        newer_metrics = [m[metric] for m in recent[mid:]]
        
        older_avg = np.mean(older_metrics)
        newer_avg = np.mean(newer_metrics)
        
        degradation = older_avg - newer_avg
        degradation_detected = degradation > threshold
        
        details = {
            'older_performance': float(older_avg),
            'newer_performance': float(newer_avg),
            'degradation': float(degradation),
            'threshold': threshold,
            'samples_checked': len(recent)
        }
        
        return degradation_detected, details
    
    def generate_performance_report(self, model_name: Optional[str] = None) -> Dict:
        """Generate comprehensive performance report"""
        print(f"\n{'='*70}")
        print(f"📊 Model Performance Report")
        print(f"{'='*70}")
        
        recent_24h = self.get_recent_performance(model_name, hours=24)
        recent_7d = self.get_recent_performance(model_name, hours=24*7)
        
        if not recent_24h:
            print("No recent data available")
            return {}
        
        # Calculate averages
        avg_24h = {
            'accuracy': np.mean([m['accuracy'] for m in recent_24h]),
            'f1_score': np.mean([m['f1_score'] for m in recent_24h]),
            'samples': sum([m['n_samples'] for m in recent_24h])
        }
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'last_24h': avg_24h,
            'total_predictions_24h': len(recent_24h),
            'total_predictions_7d': len(recent_7d)
        }
        
        print(f"\nLast 24 hours:")
        print(f"   Predictions: {report['total_predictions_24h']}")
        print(f"   Samples: {avg_24h['samples']}")
        print(f"   Accuracy: {avg_24h['accuracy']:.4f}")
        print(f"   F1 Score: {avg_24h['f1_score']:.4f}")
        print(f"\n{'='*70}\n")
        
        return report
    
    def save_history(self):
        """Save metrics history to file"""
        try:
            with open(self.save_path, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def load_history(self):
        """Load metrics history from file"""
        try:
            with open(self.save_path, 'r') as f:
                self.metrics_history = json.load(f)
        except FileNotFoundError:
            self.metrics_history = []
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
            self.metrics_history = []


# Test code
if __name__ == "__main__":
    print("🔍 Testing Model Monitoring & Drift Detection...\n")
    
    # Test Data Drift Detection
    print("="*70)
    print("Test 1: Data Drift Detection")
    print("="*70)
    
    # Create reference data
    np.random.seed(42)
    X_reference = pd.DataFrame(
        np.random.randn(500, 5),
        columns=[f'feature_{i}' for i in range(5)]
    )
    
    # Create drifted data (shift in mean)
    X_current = pd.DataFrame(
        np.random.randn(500, 5) + np.array([0, 0.5, 0, 1.0, 0]),
        columns=[f'feature_{i}' for i in range(5)]
    )
    
    drift_detector = DataDriftDetector(significance_level=0.05)
    drift_detector.set_reference(X_reference)
    
    # Detect drift with KS test
    drift_report = drift_detector.generate_report(X_current, method='ks_test')
    
    # Detect drift with PSI
    psi_report = drift_detector.generate_report(X_current, method='psi')
    
    # Test Concept Drift Detection
    print("\n" + "="*70)
    print("Test 2: Concept Drift Detection")
    print("="*70)
    
    concept_detector = ConceptDriftDetector(window_size=50)
    
    # Simulate predictions with gradual degradation
    for i in range(200):
        # Accuracy degrades from 90% to 60%
        accuracy = 0.9 - (i / 200) * 0.3
        y_true = 1
        y_pred = 1 if np.random.random() < accuracy else 0
        
        concept_detector.add_prediction(y_true, y_pred)
    
    # Check for drift
    drift_detected = concept_detector.detect_drift_adwin(threshold=0.1)
    current_perf = concept_detector.get_current_performance()
    
    print(f"\nConcept drift detected: {drift_detected}")
    print(f"Current performance: {current_perf}")
    print(f"Drift points detected: {len(concept_detector.drift_points)}")
    
    # Test Performance Monitor
    print("\n" + "="*70)
    print("Test 3: Performance Monitoring")
    print("="*70)
    
    monitor = ModelPerformanceMonitor(save_path='test_performance.json')
    
    # Log some predictions
    for i in range(5):
        y_true = np.random.randint(0, 3, 100)
        y_pred = np.random.randint(0, 3, 100)
        
        monitor.log_prediction(
            model_name='test_model',
            y_true=y_true,
            y_pred=y_pred,
            metadata={'batch': i}
        )
    
    # Generate report
    report = monitor.generate_performance_report('test_model')
    
    # Check for degradation
    degraded, details = monitor.detect_performance_degradation('test_model')
    print(f"Performance degradation detected: {degraded}")
    print(f"Details: {details}")
    
    print(f"\n✅ All monitoring tests complete!")
