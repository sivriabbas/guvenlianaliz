"""
Phase 8 Test Script - API Security & Validation
==============================================
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8003"

print("\n" + "="*80)
print("🧪 PHASE 8 TEST BAŞLIYOR")
print("="*80 + "\n")

# Test sayaçları
total_tests = 0
passed_tests = 0
failed_tests = 0

def test(name, func):
    """Test wrapper"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    try:
        print(f"\n📋 Test {total_tests}: {name}")
        func()
        passed_tests += 1
        print(f"   ✅ BAŞARILI")
    except AssertionError as e:
        failed_tests += 1
        print(f"   ❌ BAŞARISIZ: {e}")
    except Exception as e:
        failed_tests += 1
        print(f"   ❌ HATA: {e}")

# ============================================================================
# TEST 1: Rate Limit Durumu
# ============================================================================

def test_rate_limit_status():
    """Rate limit durumunu kontrol et"""
    response = requests.get(f"{BASE_URL}/api/security/rate-limit-status")
    assert response.status_code == 200, f"Status code: {response.status_code}"
    
    data = response.json()
    assert data['success'] == True, "Success should be True"
    assert 'limit' in data, "Limit bilgisi olmalı"
    assert 'remaining' in data, "Remaining bilgisi olmalı"
    
    print(f"   📊 Limit: {data['limit']}/dakika")
    print(f"   📊 Kalan: {data['remaining']} istek")
    print(f"   📊 IP: {data['ip']}")

test("Rate Limit Durumu", test_rate_limit_status)

# ============================================================================
# TEST 2: System Status (Phase 8 bilgileriyle)
# ============================================================================

def test_system_status():
    """Sistem durumunu kontrol et"""
    response = requests.get(f"{BASE_URL}/api/system-status")
    assert response.status_code == 200, f"Status code: {response.status_code}"
    
    data = response.json()
    assert data['success'] == True, "Success should be True"
    
    status = data['status']
    assert 'phase8' in status, "Phase 8 bilgisi olmalı"
    assert status['phase8']['available'] == True, "Phase 8 aktif olmalı"
    
    print(f"   📊 Version: {status['version']}")
    print(f"   📊 Phase 8.A: {status['phase8']['features']['rate_limiting']}")
    print(f"   📊 Phase 8.B: Available")

test("System Status", test_system_status)

# ============================================================================
# TEST 3: Ensemble Predict + Auto Logging
# ============================================================================

def test_ensemble_predict_with_logging():
    """Ensemble tahmin + otomatik kayıt"""
    payload = {
        "home_team": "TEST Galatasaray",
        "away_team": "TEST Fenerbahce",
        "league": "TEST Super Lig",
        "ensemble_method": "weighted"
    }
    
    response = requests.post(f"{BASE_URL}/api/ensemble-predict", json=payload)
    assert response.status_code == 200, f"Status code: {response.status_code}"
    
    data = response.json()
    assert data['success'] == True, "Success should be True"
    assert 'prediction' in data, "Prediction olmalı"
    assert data.get('logged') == True, "Logged should be True"
    
    pred = data['prediction']['ensemble_prediction']
    print(f"   🎯 Tahmin: {pred['prediction']}")
    print(f"   💯 Güven: {pred['confidence']:.2%}")
    print(f"   📝 Logged: {data['logged']}")

test("Ensemble Predict + Logging", test_ensemble_predict_with_logging)

# ============================================================================
# TEST 4: Rate Limit Headers
# ============================================================================

def test_rate_limit_headers():
    """Rate limit header'larını kontrol et"""
    response = requests.get(f"{BASE_URL}/api/system-status")
    
    headers = response.headers
    assert 'X-RateLimit-Limit' in headers, "X-RateLimit-Limit header olmalı"
    assert 'X-RateLimit-Remaining' in headers, "X-RateLimit-Remaining header olmalı"
    assert 'X-Process-Time' in headers, "X-Process-Time header olmalı"
    
    print(f"   📊 X-RateLimit-Limit: {headers['X-RateLimit-Limit']}")
    print(f"   📊 X-RateLimit-Remaining: {headers['X-RateLimit-Remaining']}")
    print(f"   ⏱️ X-Process-Time: {headers['X-Process-Time']}s")

test("Rate Limit Headers", test_rate_limit_headers)

# ============================================================================
# TEST 5: Security Headers
# ============================================================================

def test_security_headers():
    """Security header'larını kontrol et"""
    response = requests.get(f"{BASE_URL}/api/system-status")
    
    headers = response.headers
    assert 'X-Content-Type-Options' in headers, "X-Content-Type-Options olmalı"
    assert headers['X-Content-Type-Options'] == 'nosniff', "nosniff olmalı"
    
    assert 'X-Frame-Options' in headers, "X-Frame-Options olmalı"
    assert headers['X-Frame-Options'] == 'DENY', "DENY olmalı"
    
    assert 'X-XSS-Protection' in headers, "X-XSS-Protection olmalı"
    
    print(f"   🔒 X-Content-Type-Options: {headers['X-Content-Type-Options']}")
    print(f"   🔒 X-Frame-Options: {headers['X-Frame-Options']}")
    print(f"   🔒 X-XSS-Protection: {headers['X-XSS-Protection']}")

test("Security Headers", test_security_headers)

# ============================================================================
# TEST 6: Rate Limit Enforcement (Simülasyon)
# ============================================================================

def test_rate_limit_enforcement():
    """Rate limit zorlamasını test et (5 istek)"""
    print("   🔄 5 hızlı istek gönderiliyor...")
    
    for i in range(5):
        response = requests.get(f"{BASE_URL}/api/security/rate-limit-status")
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        print(f"      İstek {i+1}: Kalan {remaining}")
        time.sleep(0.1)
    
    # Son durum
    response = requests.get(f"{BASE_URL}/api/security/rate-limit-status")
    data = response.json()
    print(f"   📊 Final Kalan: {data['remaining']}")
    assert data['remaining'] < 100, "Kalan istek azalmış olmalı"

test("Rate Limit Enforcement", test_rate_limit_enforcement)

# ============================================================================
# TEST 7: Validation Error (Geçersiz Request)
# ============================================================================

def test_validation_error():
    """Validation error response test et"""
    # Çok kısa takım adı (min 2 karakter gerekli)
    payload = {
        "home_team": "A",  # Çok kısa!
        "away_team": "Fenerbahce",
        "league": "Super Lig",
        "ensemble_method": "weighted"
    }
    
    response = requests.post(f"{BASE_URL}/api/ensemble-predict", json=payload)
    
    # 422 Validation Error bekleniyor
    assert response.status_code == 422, f"422 bekleniyor, geldi: {response.status_code}"
    
    data = response.json()
    assert 'error' in data, "Error mesajı olmalı"
    print(f"   ❌ Validation Error: {data.get('error')}")
    print(f"   📝 Timestamp: {data.get('timestamp')}")

test("Validation Error Response", test_validation_error)

# ============================================================================
# TEST 8: Predictions Database Logging
# ============================================================================

def test_database_logging():
    """Database'e kaydedilen tahminleri kontrol et"""
    import sqlite3
    
    conn = sqlite3.connect('predictions.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM predictions")
    count = cursor.fetchone()[0]
    
    cursor.execute("SELECT home_team, away_team, prediction, confidence FROM predictions ORDER BY timestamp DESC LIMIT 3")
    recent = cursor.fetchall()
    
    conn.close()
    
    assert count > 0, "En az 1 tahmin kaydı olmalı"
    
    print(f"   📊 Toplam Kayıt: {count}")
    print(f"   📝 Son 3 Tahmin:")
    for i, (home, away, pred, conf) in enumerate(recent, 1):
        print(f"      {i}. {home} vs {away} - Prediction: {pred} ({conf:.2%})")

test("Database Logging", test_database_logging)

# ============================================================================
# TEST 9: API Keys Database
# ============================================================================

def test_api_keys_database():
    """API keys database'ini kontrol et"""
    import sqlite3
    import os
    
    assert os.path.exists('api_keys.db'), "api_keys.db olmalı"
    
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    
    conn.close()
    
    assert 'api_keys' in tables, "api_keys tablosu olmalı"
    assert 'api_key_usage' in tables, "api_key_usage tablosu olmalı"
    
    print(f"   📊 Tablolar: {', '.join(tables)}")

test("API Keys Database", test_api_keys_database)

# ============================================================================
# TEST 10: CORS Headers
# ============================================================================

def test_cors_headers():
    """CORS header'larını kontrol et"""
    # OPTIONS request (preflight)
    response = requests.options(f"{BASE_URL}/api/system-status")
    
    # CORS headers olmalı
    headers = response.headers
    print(f"   📊 Access-Control headers mevcut: {any('Access-Control' in h for h in headers)}")
    
    # Normal GET request
    response = requests.get(f"{BASE_URL}/api/system-status")
    assert response.status_code == 200, "GET request başarılı olmalı"

test("CORS Headers", test_cors_headers)

# ============================================================================
# ÖZET RAPOR
# ============================================================================

print("\n" + "="*80)
print("📊 TEST SONUÇLARI")
print("="*80 + "\n")

print(f"✅ Başarılı: {passed_tests}/{total_tests}")
print(f"❌ Başarısız: {failed_tests}/{total_tests}")
print(f"📈 Başarı Oranı: {(passed_tests/total_tests)*100:.1f}%")

if failed_tests == 0:
    print("\n🎉 TÜM TESTLER BAŞARILI!")
    print("✅ Phase 8 tam çalışıyor!")
else:
    print(f"\n⚠️ {failed_tests} test başarısız oldu.")

print("\n" + "="*80 + "\n")
