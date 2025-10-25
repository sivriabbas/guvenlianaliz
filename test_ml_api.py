"""
Phase 9 ML API Test Suite
Test all ML endpoints
"""

import requests
import json
import numpy as np
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"
ML_BASE = f"{BASE_URL}/api/ml"


class MLAPITester:
    """Test ML API endpoints"""
    
    def __init__(self, base_url: str = ML_BASE):
        self.base_url = base_url
        self.results = []
    
    def test_health_check(self):
        """Test health endpoint"""
        print("\n" + "="*70)
        print("Test 1: Health Check")
        print("="*70)
        
        try:
            response = requests.get(f"{self.base_url}/health")
            data = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Service Status: {data.get('status')}")
            print(f"Modules:")
            for module, available in data.get('modules', {}).items():
                status = "✅" if available else "❌"
                print(f"  {status} {module}")
            
            self.results.append({"test": "health_check", "passed": response.status_code == 200})
            return True
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append({"test": "health_check", "passed": False})
            return False
    
    def test_capabilities(self):
        """Test capabilities endpoint"""
        print("\n" + "="*70)
        print("Test 2: Capabilities")
        print("="*70)
        
        try:
            response = requests.get(f"{self.base_url}/capabilities")
            data = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Version: {data.get('version')}")
            print(f"Phase: {data.get('phase')}")
            print(f"\nCapabilities:")
            for cap in data.get('capabilities', []):
                status = "✅" if cap.get('available') else "❌"
                print(f"  {status} {cap.get('name')}")
                print(f"     Endpoint: {cap.get('endpoint')}")
            
            self.results.append({"test": "capabilities", "passed": response.status_code == 200})
            return True
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append({"test": "capabilities", "passed": False})
            return False
    
    def test_prediction(self):
        """Test match prediction"""
        print("\n" + "="*70)
        print("Test 3: Match Prediction")
        print("="*70)
        
        try:
            # Create synthetic match features
            home_features = np.random.randn(10).tolist()
            away_features = np.random.randn(10).tolist()
            
            payload = {
                "home_team_features": home_features,
                "away_team_features": away_features,
                "feature_names": [f"feature_{i}" for i in range(20)],
                "model_type": "neural_network",
                "explain": False
            }
            
            response = requests.post(f"{self.base_url}/predict", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {response.status_code}")
                print(f"Prediction: {data.get('prediction')}")
                print(f"Probabilities: {data.get('probabilities')}")
                print(f"Confidence: {data.get('confidence'):.4f}")
                print(f"Model: {data.get('model_used')}")
                
                self.results.append({"test": "prediction", "passed": True})
                return True
            else:
                print(f"⚠️  Status: {response.status_code}")
                print(f"Response: {response.text}")
                self.results.append({"test": "prediction", "passed": False})
                return False
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append({"test": "prediction", "passed": False})
            return False
    
    def test_feature_engineering(self):
        """Test feature engineering"""
        print("\n" + "="*70)
        print("Test 4: Feature Engineering")
        print("="*70)
        
        try:
            # Create synthetic data
            features = np.random.randn(100, 8).tolist()
            target = np.random.randint(0, 3, 100).tolist()
            
            payload = {
                "features": features,
                "target": target,
                "feature_names": [f"f{i}" for i in range(8)],
                "create_polynomials": True,
                "select_features": True,
                "n_features": 20
            }
            
            response = requests.post(f"{self.base_url}/feature-engineering", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {response.status_code}")
                print(f"Original Features: {data.get('original_features')}")
                print(f"Engineered Features: {data.get('engineered_features')}")
                print(f"Pipeline Steps: {data.get('pipeline_steps')}")
                print(f"Top 5 Features:")
                for feat, imp in list(data.get('top_features', {}).items())[:5]:
                    print(f"  - {feat}: {imp:.6f}")
                
                self.results.append({"test": "feature_engineering", "passed": True})
                return True
            else:
                print(f"⚠️  Status: {response.status_code}")
                print(f"Response: {response.text}")
                self.results.append({"test": "feature_engineering", "passed": False})
                return False
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append({"test": "feature_engineering", "passed": False})
            return False
    
    def test_drift_detection(self):
        """Test drift detection"""
        print("\n" + "="*70)
        print("Test 5: Drift Detection")
        print("="*70)
        
        try:
            # Create reference and drifted data
            reference_data = np.random.randn(100, 5).tolist()
            current_data = (np.random.randn(100, 5) + 0.5).tolist()  # Shifted distribution
            
            payload = {
                "reference_data": reference_data,
                "current_data": current_data,
                "feature_names": [f"f{i}" for i in range(5)],
                "method": "psi"
            }
            
            response = requests.post(f"{self.base_url}/drift-detection", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {response.status_code}")
                print(f"Drift Detected: {data.get('drift_detected')}")
                print(f"Drift Ratio: {data.get('drift_ratio'):.2%}")
                print(f"Total Features: {data.get('total_features')}")
                print(f"Drift Features: {data.get('drift_features')}")
                print(f"Method: {data.get('method')}")
                
                self.results.append({"test": "drift_detection", "passed": True})
                return True
            else:
                print(f"⚠️  Status: {response.status_code}")
                print(f"Response: {response.text}")
                self.results.append({"test": "drift_detection", "passed": False})
                return False
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append({"test": "drift_detection", "passed": False})
            return False
    
    def test_automl(self):
        """Test AutoML"""
        print("\n" + "="*70)
        print("Test 6: AutoML Model Selection")
        print("="*70)
        
        try:
            # Create synthetic data
            features = np.random.randn(100, 10).tolist()
            target = np.random.randint(0, 3, 100).tolist()
            
            payload = {
                "features": features,
                "target": target,
                "cv_folds": 3,
                "metric": "f1_weighted"
            }
            
            response = requests.post(f"{self.base_url}/automl", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {response.status_code}")
                print(f"Best Model: {data.get('best_model')}")
                print(f"Best Score: {data.get('best_score'):.4f}")
                print(f"All Models:")
                for model, score in data.get('all_scores', {}).items():
                    print(f"  - {model}: {score:.4f}")
                
                self.results.append({"test": "automl", "passed": True})
                return True
            else:
                print(f"⚠️  Status: {response.status_code}")
                print(f"Response: {response.text}")
                self.results.append({"test": "automl", "passed": False})
                return False
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.results.append({"test": "automl", "passed": False})
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 Test Summary")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n" + "="*70 + "\n")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 Phase 9 ML API Test Suite")
    print("="*70)
    print(f"Base URL: {ML_BASE}")
    print("="*70)
    
    tester = MLAPITester()
    
    # Run tests
    tester.test_health_check()
    tester.test_capabilities()
    tester.test_prediction()
    tester.test_feature_engineering()
    tester.test_drift_detection()
    tester.test_automl()
    
    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    main()
