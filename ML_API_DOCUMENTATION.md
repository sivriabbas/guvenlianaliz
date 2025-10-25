# Phase 9: ML & AI API Documentation

## 🚀 Overview

Phase 9 ML API entegrasyonu, gelişmiş makine öğrenmesi ve yapay zeka özelliklerini FastAPI üzerinden sunmaktadır.

**Version:** 9.0.0  
**Base URL:** `http://localhost:8000/api/ml`  
**Documentation:** `http://localhost:8000/docs`

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Models](#models)
5. [Examples](#examples)
6. [Error Handling](#error-handling)

---

## 🚦 Quick Start

### 1. Start the API Server

```bash
# Windows
start_ml_api.bat

# Linux/Mac
uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Test the API

```bash
python test_ml_api.py
```

### 3. Access Documentation

Open: http://localhost:8000/docs

---

## 🔐 Authentication

API uses HTTP Basic Authentication (configured in `main_fastapi.py`).

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    "http://localhost:8000/api/ml/health",
    auth=HTTPBasicAuth('username', 'password')
)
```

---

## 📡 Endpoints

### 1. Health Check

**GET** `/api/ml/health`

Check service health and module availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T12:00:00",
  "modules": {
    "advanced_ml": true,
    "feature_engineering": true,
    "monitoring": true,
    "automl": true,
    "explainability": true
  },
  "cached_models": ["default"],
  "performance_monitoring": true
}
```

---

### 2. Get Capabilities

**GET** `/api/ml/capabilities`

Get available ML capabilities and features.

**Response:**
```json
{
  "version": "9.0.0",
  "phase": "Phase 9: Advanced ML & AI",
  "capabilities": [
    {
      "name": "Neural Network Prediction",
      "available": true,
      "endpoint": "/api/ml/predict",
      "description": "Advanced neural network match prediction"
    }
  ],
  "supported_models": [
    "Neural Network (MLP)",
    "Random Forest",
    "Gradient Boosting",
    "XGBoost",
    "LightGBM"
  ]
}
```

---

### 3. Match Prediction

**POST** `/api/ml/predict`

Predict match outcome using ML models.

**Request Body:**
```json
{
  "home_team_features": [1.2, 0.8, 2.1, ...],
  "away_team_features": [0.9, 1.1, 1.8, ...],
  "feature_names": ["goals", "shots", "possession", ...],
  "model_type": "neural_network",
  "explain": false
}
```

**Response:**
```json
{
  "prediction": 2,
  "probabilities": [0.15, 0.25, 0.60],
  "confidence": 0.60,
  "model_used": "neural_network",
  "explanation": null
}
```

**Prediction Classes:**
- `0` = Away Win
- `1` = Draw
- `2` = Home Win

---

### 4. Feature Engineering

**POST** `/api/ml/feature-engineering`

Apply automated feature engineering.

**Request Body:**
```json
{
  "features": [[1.2, 0.8], [0.9, 1.1], ...],
  "target": [2, 1, 0, ...],
  "feature_names": ["f1", "f2"],
  "create_polynomials": true,
  "select_features": true,
  "n_features": 30
}
```

**Response:**
```json
{
  "success": true,
  "original_features": 2,
  "engineered_features": 30,
  "feature_names": ["f1", "f2", "f1^2", "f1 f2", ...],
  "top_features": {
    "f1 f2": 0.152,
    "f1^2": 0.134,
    ...
  },
  "pipeline_steps": ["polynomial_features", "feature_selection", "scaling"]
}
```

---

### 5. Drift Detection

**POST** `/api/ml/drift-detection`

Detect data drift between datasets.

**Request Body:**
```json
{
  "reference_data": [[1.2, 0.8], [0.9, 1.1], ...],
  "current_data": [[1.5, 0.9], [1.0, 1.2], ...],
  "feature_names": ["f1", "f2"],
  "method": "psi"
}
```

**Methods:**
- `psi` - Population Stability Index
- `ks_test` - Kolmogorov-Smirnov Test

**Response:**
```json
{
  "success": true,
  "drift_detected": true,
  "drift_ratio": 0.40,
  "total_features": 5,
  "drift_features": 2,
  "method": "psi",
  "features": {
    "f1": {
      "drift_detected": true,
      "psi_value": 0.28,
      "severity": "high"
    }
  }
}
```

---

### 6. Train Model

**POST** `/api/ml/train-model`

Train a new ML model.

**Request Body:**
```json
{
  "features": [[1.2, 0.8], [0.9, 1.1], ...],
  "target": [2, 1, 0, ...],
  "model_name": "my_model_v1",
  "optimize_hyperparameters": true,
  "n_trials": 20
}
```

**Response:**
```json
{
  "success": true,
  "model_name": "my_model_v1",
  "accuracy": 0.85,
  "f1_score": 0.83,
  "samples_trained": 1000,
  "hyperparameter_optimized": true
}
```

---

### 7. AutoML Model Selection

**POST** `/api/ml/automl`

Run automated model selection.

**Request Body:**
```json
{
  "features": [[1.2, 0.8], [0.9, 1.1], ...],
  "target": [2, 1, 0, ...],
  "cv_folds": 5,
  "metric": "f1_weighted"
}
```

**Response:**
```json
{
  "success": true,
  "best_model": "Random Forest",
  "best_score": 0.87,
  "all_scores": {
    "Random Forest": 0.87,
    "Gradient Boosting": 0.85,
    "Neural Network": 0.83,
    "XGBoost": 0.86
  },
  "results": [
    {
      "model": "Random Forest",
      "mean_score": 0.87,
      "std_score": 0.02
    }
  ]
}
```

---

### 8. Model Performance

**GET** `/api/ml/model-performance?model_name=my_model&hours=24`

Get model performance metrics.

**Parameters:**
- `model_name` (optional): Filter by model name
- `hours` (default: 24): Time window in hours

**Response:**
```json
{
  "success": true,
  "model_name": "my_model",
  "time_window_hours": 24,
  "total_predictions": 150,
  "recent_performance": [
    {
      "timestamp": "2025-10-24T12:00:00",
      "accuracy": 0.85,
      "f1_score": 0.83
    }
  ],
  "degradation_detected": false,
  "degradation_details": {}
}
```

---

## 📊 Data Models

### MatchPredictionRequest

```python
{
  "home_team_features": List[float],  # Required
  "away_team_features": List[float],  # Required
  "feature_names": List[str],         # Optional
  "model_type": str,                  # Default: "neural_network"
  "explain": bool                     # Default: false
}
```

### FeatureEngineeringRequest

```python
{
  "features": List[List[float]],      # Required
  "target": List[int],                # Required
  "feature_names": List[str],         # Optional
  "create_polynomials": bool,         # Default: true
  "select_features": bool,            # Default: true
  "n_features": int                   # Default: 30
}
```

---

## 💡 Examples

### Python Client Example

```python
import requests
import numpy as np

# API endpoint
BASE_URL = "http://localhost:8000/api/ml"

# 1. Check health
health = requests.get(f"{BASE_URL}/health").json()
print(f"Status: {health['status']}")

# 2. Make prediction
home_features = np.random.randn(10).tolist()
away_features = np.random.randn(10).tolist()

prediction_request = {
    "home_team_features": home_features,
    "away_team_features": away_features,
    "model_type": "neural_network",
    "explain": False
}

response = requests.post(f"{BASE_URL}/predict", json=prediction_request)
result = response.json()

print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.2%}")

# 3. Run AutoML
features = np.random.randn(200, 15).tolist()
target = np.random.randint(0, 3, 200).tolist()

automl_request = {
    "features": features,
    "target": target,
    "cv_folds": 5
}

response = requests.post(f"{BASE_URL}/automl", json=automl_request)
result = response.json()

print(f"Best Model: {result['best_model']}")
print(f"Best Score: {result['best_score']:.4f}")
```

### JavaScript/Fetch Example

```javascript
// Make prediction
const response = await fetch('http://localhost:8000/api/ml/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    home_team_features: [1.2, 0.8, 2.1, ...],
    away_team_features: [0.9, 1.1, 1.8, ...],
    model_type: 'neural_network',
    explain: false
  })
});

const result = await response.json();
console.log('Prediction:', result.prediction);
console.log('Confidence:', result.confidence);
```

### cURL Example

```bash
# Health check
curl http://localhost:8000/api/ml/health

# Get capabilities
curl http://localhost:8000/api/ml/capabilities

# Make prediction
curl -X POST http://localhost:8000/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "home_team_features": [1.2, 0.8, 2.1],
    "away_team_features": [0.9, 1.1, 1.8],
    "model_type": "neural_network"
  }'
```

---

## ⚠️ Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (authentication required)
- `404` - Not Found
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error
- `503` - Service Unavailable (module not loaded)

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Errors

**503 Service Unavailable**
```json
{
  "detail": "Advanced ML models not available"
}
```

**Cause:** Required Python modules not installed.  
**Solution:** Install dependencies: `pip install scikit-learn numpy pandas`

**500 Internal Server Error**
```json
{
  "detail": "Prediction failed: Invalid feature shape"
}
```

**Cause:** Feature dimensions mismatch.  
**Solution:** Ensure features match expected dimensions.

---

## 🔧 Configuration

### Environment Variables

```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Model Settings
ML_MODEL_CACHE=./models
ML_PERFORMANCE_LOG=./api_ml_performance.json
```

### Model Storage

Models are saved in `models/` directory:
- `models/default.pkl` - Default neural network
- `models/my_model_v1.pkl` - Custom trained models

---

## 📈 Performance

### Optimization Tips

1. **Model Caching:** Models are cached in memory for fast predictions
2. **Background Tasks:** Use for long-running training
3. **Batch Predictions:** Send multiple samples in one request
4. **Feature Caching:** Reuse engineered features

### Benchmarks

- **Prediction:** ~10ms per request
- **Feature Engineering:** ~50-200ms for 100 samples
- **Drift Detection:** ~30-100ms for 100 samples
- **AutoML:** ~5-30 seconds (depends on trials)

---

## 🔗 Related Documentation

- [Phase 9 Implementation Report](PHASE_9_REPORT.md)
- [Feature Engineering Guide](feature_engineering.py)
- [AutoML Documentation](automl.py)
- [Model Monitoring](model_monitoring.py)

---

## 🆘 Support

For issues or questions:
1. Check API documentation: `http://localhost:8000/docs`
2. Run health check: `GET /api/ml/health`
3. Review logs in console
4. Test with: `python test_ml_api.py`

---

**Last Updated:** 2025-10-24  
**Version:** 9.0.0  
**Status:** Production Ready ✅
