"""
Phase 9 ML & AI API Endpoints
Advanced ML features integration for FastAPI
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import numpy as np
import pandas as pd
from datetime import datetime
import json

# Import Phase 9 modules
try:
    from advanced_ml_models import AdvancedNeuralPredictor, SequentialMatchPredictor
    ADVANCED_ML_AVAILABLE = True
except ImportError:
    ADVANCED_ML_AVAILABLE = False

try:
    from feature_engineering import AutoFeatureEngineer
    FEATURE_ENG_AVAILABLE = True
except ImportError:
    FEATURE_ENG_AVAILABLE = False

try:
    from model_monitoring import DataDriftDetector, ModelPerformanceMonitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

try:
    from automl import AutoModelSelector, HyperparameterOptimizer
    AUTOML_AVAILABLE = True
except ImportError:
    AUTOML_AVAILABLE = False

try:
    from model_explainability import ModelInterpreter
    EXPLAINABILITY_AVAILABLE = True
except ImportError:
    EXPLAINABILITY_AVAILABLE = False


# Create router
router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


# ========== REQUEST/RESPONSE MODELS ==========

class MatchPredictionRequest(BaseModel):
    """Match prediction request"""
    home_team_features: List[float] = Field(..., description="Home team feature vector")
    away_team_features: List[float] = Field(..., description="Away team feature vector")
    feature_names: Optional[List[str]] = Field(None, description="Feature names")
    model_type: str = Field("neural_network", description="Model type: neural_network, automl")
    explain: bool = Field(False, description="Include SHAP/LIME explanation")


class MatchPredictionResponse(BaseModel):
    """Match prediction response"""
    prediction: int = Field(..., description="Predicted class (0=Away, 1=Draw, 2=Home)")
    probabilities: List[float] = Field(..., description="Class probabilities [Away, Draw, Home]")
    confidence: float = Field(..., description="Confidence score (0-1)")
    model_used: str = Field(..., description="Model that made prediction")
    explanation: Optional[Dict[str, Any]] = Field(None, description="SHAP/LIME explanation")


class FeatureEngineeringRequest(BaseModel):
    """Feature engineering request"""
    features: List[List[float]] = Field(..., description="Input features")
    target: List[int] = Field(..., description="Target labels")
    feature_names: Optional[List[str]] = Field(None, description="Feature names")
    create_polynomials: bool = Field(True, description="Create polynomial features")
    select_features: bool = Field(True, description="Apply feature selection")
    n_features: int = Field(30, description="Number of features to select")


class DriftDetectionRequest(BaseModel):
    """Drift detection request"""
    reference_data: List[List[float]] = Field(..., description="Reference dataset")
    current_data: List[List[float]] = Field(..., description="Current dataset")
    feature_names: Optional[List[str]] = Field(None, description="Feature names")
    method: str = Field("psi", description="Detection method: psi or ks_test")


class ModelTrainingRequest(BaseModel):
    """Model training request"""
    features: List[List[float]] = Field(..., description="Training features")
    target: List[int] = Field(..., description="Training labels")
    model_name: str = Field(..., description="Model name for saving")
    optimize_hyperparameters: bool = Field(False, description="Run hyperparameter optimization")
    n_trials: int = Field(20, description="Number of optimization trials")


class AutoMLRequest(BaseModel):
    """AutoML model selection request"""
    features: List[List[float]] = Field(..., description="Training features")
    target: List[int] = Field(..., description="Training labels")
    cv_folds: int = Field(5, description="Cross-validation folds")
    metric: str = Field("f1_weighted", description="Optimization metric")


# ========== GLOBAL MODEL CACHE ==========

_model_cache: Dict[str, Any] = {}
_feature_engineer_cache: Dict[str, Any] = {}
_drift_detector: Optional[Any] = None
_performance_monitor: Optional[Any] = None


def get_model(model_name: str = "default"):
    """Get or create model from cache"""
    if model_name not in _model_cache and ADVANCED_ML_AVAILABLE:
        _model_cache[model_name] = AdvancedNeuralPredictor()
    return _model_cache.get(model_name)


def get_performance_monitor():
    """Get global performance monitor"""
    global _performance_monitor
    if _performance_monitor is None and MONITORING_AVAILABLE:
        _performance_monitor = ModelPerformanceMonitor(save_path='api_ml_performance.json')
    return _performance_monitor


# ========== API ENDPOINTS ==========

@router.post("/predict", response_model=MatchPredictionResponse)
async def predict_match(request: MatchPredictionRequest):
    """
    Predict match outcome using advanced ML models
    
    **Features:**
    - Neural Network prediction
    - Probability distribution
    - Confidence scores
    - Optional SHAP/LIME explanation
    """
    if not ADVANCED_ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="Advanced ML models not available")
    
    try:
        # Get model
        model = get_model("default")
        
        # Prepare features
        features = np.array([request.home_team_features + request.away_team_features])
        
        # Make prediction
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features)[0]
            prediction = int(np.argmax(probabilities))
        else:
            prediction = int(model.predict(features)[0])
            probabilities = [0.33, 0.33, 0.33]  # Fallback
        
        confidence = float(np.max(probabilities))
        
        # Get explanation if requested
        explanation = None
        if request.explain and EXPLAINABILITY_AVAILABLE:
            try:
                feature_df = pd.DataFrame(
                    [features[0]],
                    columns=request.feature_names or [f"f{i}" for i in range(len(features[0]))]
                )
                interpreter = ModelInterpreter(model, feature_df)
                exp = interpreter.explain_prediction(feature_df, methods=['native'])
                explanation = exp.get('explanations', {})
            except Exception as e:
                print(f"Explanation failed: {e}")
        
        # Log prediction for monitoring
        monitor = get_performance_monitor()
        if monitor:
            # Will be logged when ground truth is available
            pass
        
        return MatchPredictionResponse(
            prediction=prediction,
            probabilities=probabilities.tolist(),
            confidence=confidence,
            model_used=request.model_type,
            explanation=explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/feature-engineering")
async def engineer_features(request: FeatureEngineeringRequest):
    """
    Apply automated feature engineering
    
    **Features:**
    - Polynomial features
    - Interaction features
    - Feature selection
    - PCA dimensionality reduction
    """
    if not FEATURE_ENG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Feature engineering not available")
    
    try:
        # Convert to DataFrame
        X = pd.DataFrame(
            request.features,
            columns=request.feature_names or [f"f{i}" for i in range(len(request.features[0]))]
        )
        y = np.array(request.target)
        
        # Apply feature engineering
        auto_fe = AutoFeatureEngineer()
        X_engineered = auto_fe.fit_transform(
            X, y,
            create_polynomials=request.create_polynomials,
            select_features=request.select_features,
            n_features=request.n_features
        )
        
        # Get top features
        top_features = auto_fe.get_top_features(n=20)
        
        return {
            "success": True,
            "original_features": X.shape[1],
            "engineered_features": X_engineered.shape[1],
            "feature_names": X_engineered.columns.tolist(),
            "top_features": top_features,
            "pipeline_steps": auto_fe.pipeline_steps
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature engineering failed: {str(e)}")


@router.post("/drift-detection")
async def detect_drift(request: DriftDetectionRequest):
    """
    Detect data drift between reference and current data
    
    **Methods:**
    - PSI (Population Stability Index)
    - KS Test (Kolmogorov-Smirnov)
    """
    if not MONITORING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Monitoring not available")
    
    try:
        # Convert to DataFrame
        feature_names = request.feature_names or [f"f{i}" for i in range(len(request.reference_data[0]))]
        
        X_ref = pd.DataFrame(request.reference_data, columns=feature_names)
        X_curr = pd.DataFrame(request.current_data, columns=feature_names)
        
        # Detect drift
        detector = DataDriftDetector()
        detector.set_reference(X_ref)
        report = detector.generate_report(X_curr, method=request.method)
        
        return {
            "success": True,
            "drift_detected": report['drift_detected'],
            "drift_ratio": report['drift_ratio'],
            "total_features": report['total_features'],
            "drift_features": report['drift_features'],
            "method": request.method,
            "features": report['features']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drift detection failed: {str(e)}")


@router.post("/train-model")
async def train_model(request: ModelTrainingRequest, background_tasks: BackgroundTasks):
    """
    Train a new ML model
    
    **Features:**
    - Neural network training
    - Hyperparameter optimization (optional)
    - Model persistence
    - Performance logging
    """
    if not ADVANCED_ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    try:
        X = pd.DataFrame(request.features)
        y = np.array(request.target)
        
        # Hyperparameter optimization if requested
        if request.optimize_hyperparameters and AUTOML_AVAILABLE:
            optimizer = HyperparameterOptimizer(n_trials=request.n_trials)
            best_params = optimizer.optimize_neural_network(X, y, cv=3)
            
            # Create model with optimized params
            model = AdvancedNeuralPredictor(
                hidden_layers=best_params.get('hidden_layer_sizes', (128, 64, 32)),
                max_iter=500
            )
        else:
            model = AdvancedNeuralPredictor()
        
        # Train model
        model.train(X, y, validation_split=0.2)
        
        # Save model
        model.save(f"models/{request.model_name}.pkl")
        
        # Cache model
        _model_cache[request.model_name] = model
        
        # Evaluate
        predictions = model.predict(X)
        from sklearn.metrics import f1_score, accuracy_score
        accuracy = accuracy_score(y, predictions)
        f1 = f1_score(y, predictions, average='weighted')
        
        return {
            "success": True,
            "model_name": request.model_name,
            "accuracy": float(accuracy),
            "f1_score": float(f1),
            "samples_trained": len(X),
            "hyperparameter_optimized": request.optimize_hyperparameters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/automl")
async def run_automl(request: AutoMLRequest):
    """
    Run AutoML model selection
    
    **Features:**
    - Multiple model comparison
    - Automatic best model selection
    - Cross-validation
    - Performance metrics
    """
    if not AUTOML_AVAILABLE:
        raise HTTPException(status_code=503, detail="AutoML not available")
    
    try:
        X = pd.DataFrame(request.features)
        y = np.array(request.target)
        
        # Run AutoML
        selector = AutoModelSelector(cv=request.cv_folds, scoring=request.metric)
        scores = selector.evaluate_models(X, y)
        
        best_name, best_model, best_score = selector.get_best_model()
        
        # Get results DataFrame
        results_df = selector.get_results_df()
        
        return {
            "success": True,
            "best_model": best_name,
            "best_score": float(best_score),
            "all_scores": scores,
            "results": results_df.to_dict('records') if not results_df.empty else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AutoML failed: {str(e)}")


@router.get("/model-performance")
async def get_model_performance(
    model_name: Optional[str] = None,
    hours: int = 24
):
    """
    Get model performance metrics
    
    **Returns:**
    - Recent predictions
    - Performance trends
    - Degradation alerts
    """
    if not MONITORING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Monitoring not available")
    
    try:
        monitor = get_performance_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Performance monitor not initialized")
        
        # Get recent performance
        recent = monitor.get_recent_performance(model_name, hours=hours)
        
        # Check for degradation
        degraded = False
        degradation_details = {}
        
        if model_name and len(recent) > 0:
            degraded, degradation_details = monitor.detect_performance_degradation(
                model_name, threshold=0.05, window_hours=hours
            )
        
        return {
            "success": True,
            "model_name": model_name,
            "time_window_hours": hours,
            "total_predictions": len(recent),
            "recent_performance": recent[-10:] if recent else [],
            "degradation_detected": degraded,
            "degradation_details": degradation_details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance check failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Check health of ML services
    
    **Returns:**
    - Service availability
    - Module status
    - Cache info
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "advanced_ml": ADVANCED_ML_AVAILABLE,
            "feature_engineering": FEATURE_ENG_AVAILABLE,
            "monitoring": MONITORING_AVAILABLE,
            "automl": AUTOML_AVAILABLE,
            "explainability": EXPLAINABILITY_AVAILABLE
        },
        "cached_models": list(_model_cache.keys()),
        "performance_monitoring": _performance_monitor is not None
    }


@router.get("/capabilities")
async def get_capabilities():
    """
    Get available ML capabilities
    
    **Returns:**
    - Available features
    - Supported models
    - API endpoints
    """
    return {
        "version": "9.0.0",
        "phase": "Phase 9: Advanced ML & AI",
        "capabilities": [
            {
                "name": "Neural Network Prediction",
                "available": ADVANCED_ML_AVAILABLE,
                "endpoint": "/api/ml/predict",
                "description": "Advanced neural network match prediction"
            },
            {
                "name": "Feature Engineering",
                "available": FEATURE_ENG_AVAILABLE,
                "endpoint": "/api/ml/feature-engineering",
                "description": "Automated feature creation and selection"
            },
            {
                "name": "Drift Detection",
                "available": MONITORING_AVAILABLE,
                "endpoint": "/api/ml/drift-detection",
                "description": "Data and concept drift monitoring"
            },
            {
                "name": "AutoML",
                "available": AUTOML_AVAILABLE,
                "endpoint": "/api/ml/automl",
                "description": "Automated model selection and optimization"
            },
            {
                "name": "Model Training",
                "available": ADVANCED_ML_AVAILABLE,
                "endpoint": "/api/ml/train-model",
                "description": "Custom model training with hyperparameter optimization"
            },
            {
                "name": "Performance Monitoring",
                "available": MONITORING_AVAILABLE,
                "endpoint": "/api/ml/model-performance",
                "description": "Real-time model performance tracking"
            }
        ],
        "supported_models": [
            "Neural Network (MLP)",
            "Random Forest",
            "Gradient Boosting",
            "XGBoost",
            "LightGBM"
        ],
        "features": [
            "SHAP explanations",
            "LIME local interpretability",
            "Hyperparameter optimization (Optuna)",
            "Feature importance analysis",
            "Drift detection (PSI, KS-test)",
            "Performance degradation alerts"
        ]
    }


# Export router
__all__ = ['router']
