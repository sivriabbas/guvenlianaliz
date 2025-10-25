"""
Phase 8.C Test Suite
Monitoring & Analytics sistemlerini test eder

Test Kapsamı:
- API Metrics Collector
- Advanced Logging
- Monitoring Dashboard
- Performance tracking
- Error analysis
"""

import requests
import time
import json


def print_test(title: str, passed: bool, message: str = ""):
    """Test sonucunu formatla ve yazdır"""
    status = "✅ BAŞARILI" if passed else "❌ BAŞARISIZ"
    print(f"\n{status}: {title}")
    if message:
        print(f"  → {message}")


def test_1_metrics_endpoint():
    """Test 1: /api/metrics endpoint'i çalışıyor mu?"""
    try:
        response = requests.get("http://127.0.0.1:8003/api/metrics")
        
        if response.status_code == 200:
            data = response.json()
            
            # Summary kontrolü
            if "summary" in data:
                summary = data["summary"]
                print_test(
                    "Metrics Endpoint",
                    True,
                    f"İstekler: {summary.get('total_requests', 0)}, "
                    f"Başarı: %{summary.get('success_rate', 0):.1f}, "
                    f"Ort. Süre: {summary.get('avg_response_time', 0):.3f}s"
                )
                return True
            else:
                print_test("Metrics Endpoint", False, "Summary verisi yok")
                return False
        else:
            print_test("Metrics Endpoint", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Metrics Endpoint", False, str(e))
        return False


def test_2_endpoint_specific_metrics():
    """Test 2: Endpoint-specific metrics çalışıyor mu?"""
    try:
        # Önce bir istek yap
        requests.get("http://127.0.0.1:8003/api/system-status")
        time.sleep(0.5)
        
        # Metrics'i kontrol et
        response = requests.get("http://127.0.0.1:8003/api/metrics/endpoint/api/system-status")
        
        if response.status_code == 200:
            data = response.json()
            
            if "request_count" in data:
                print_test(
                    "Endpoint Specific Metrics",
                    True,
                    f"İstekler: {data['request_count']}, "
                    f"Ort. Süre: {data.get('avg_response_time', 0):.3f}s"
                )
                return True
            else:
                print_test("Endpoint Specific Metrics", False, "Veri eksik")
                return False
        else:
            print_test("Endpoint Specific Metrics", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Endpoint Specific Metrics", False, str(e))
        return False


def test_3_historical_metrics():
    """Test 3: Historical metrics çalışıyor mu?"""
    try:
        response = requests.get("http://127.0.0.1:8003/api/metrics/historical?days=7")
        
        if response.status_code == 200:
            data = response.json()
            
            if "period_days" in data:
                print_test(
                    "Historical Metrics",
                    True,
                    f"Dönem: {data['period_days']} gün, "
                    f"Günlük veriler: {len(data.get('daily_stats', []))}"
                )
                return True
            else:
                print_test("Historical Metrics", False, "Veri formatı hatalı")
                return False
        else:
            print_test("Historical Metrics", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Historical Metrics", False, str(e))
        return False


def test_4_slow_endpoints():
    """Test 4: Slow endpoints tespiti çalışıyor mu?"""
    try:
        response = requests.get("http://127.0.0.1:8003/api/metrics/slow?threshold_ms=100&limit=10")
        
        if response.status_code == 200:
            data = response.json()
            
            if "slow_endpoints" in data:
                slow_count = len(data["slow_endpoints"])
                print_test(
                    "Slow Endpoints Detection",
                    True,
                    f"Yavaş endpoint sayısı: {slow_count} (threshold: {data.get('threshold_ms')}ms)"
                )
                return True
            else:
                print_test("Slow Endpoints Detection", False, "Veri formatı hatalı")
                return False
        else:
            print_test("Slow Endpoints Detection", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Slow Endpoints Detection", False, str(e))
        return False


def test_5_error_analysis():
    """Test 5: Error analysis çalışıyor mu?"""
    try:
        response = requests.get("http://127.0.0.1:8003/api/metrics/errors?limit=20")
        
        if response.status_code == 200:
            data = response.json()
            
            if "errors" in data:
                error_count = data.get("count", 0)
                print_test(
                    "Error Analysis",
                    True,
                    f"Hata sayısı: {error_count}"
                )
                return True
            else:
                print_test("Error Analysis", False, "Veri formatı hatalı")
                return False
        else:
            print_test("Error Analysis", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Error Analysis", False, str(e))
        return False


def test_6_response_time_header():
    """Test 6: Response time header ekleniyor mu?"""
    try:
        response = requests.get("http://127.0.0.1:8003/api/system-status")
        
        if "X-Response-Time" in response.headers:
            response_time = response.headers["X-Response-Time"]
            print_test(
                "Response Time Header",
                True,
                f"X-Response-Time: {response_time}"
            )
            return True
        else:
            print_test("Response Time Header", False, "Header bulunamadı")
            return False
    except Exception as e:
        print_test("Response Time Header", False, str(e))
        return False


def test_7_monitoring_dashboard():
    """Test 7: Monitoring dashboard sayfası erişilebilir mi?"""
    try:
        response = requests.get("http://127.0.0.1:8003/monitoring-dashboard")
        
        if response.status_code == 200:
            html_content = response.text
            
            # HTML içerik kontrolü
            if "API Monitoring Dashboard" in html_content:
                print_test(
                    "Monitoring Dashboard",
                    True,
                    "HTML sayfası yüklendi"
                )
                return True
            else:
                print_test("Monitoring Dashboard", False, "HTML içeriği hatalı")
                return False
        else:
            print_test("Monitoring Dashboard", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Monitoring Dashboard", False, str(e))
        return False


def test_8_system_status_phase8c():
    """Test 8: System status Phase 8.C bilgilerini içeriyor mu?"""
    try:
        response = requests.get("http://127.0.0.1:8003/api/system-status")
        
        if response.status_code == 200:
            data = response.json()
            
            if "status" in data:
                status = data["status"]
                phase8 = status.get("phase8", {})
                phase8c = phase8.get("C_monitoring", {})
                
                if phase8c.get("available"):
                    features = phase8c.get("features", {})
                    print_test(
                        "System Status Phase 8.C",
                        True,
                        f"Metrics: {features.get('metrics_collector')}, "
                        f"Logging: {features.get('structured_logging')}, "
                        f"Metrics DB: {phase8c.get('metrics_db', 'N/A')}"
                    )
                    return True
                else:
                    print_test("System Status Phase 8.C", False, "Phase 8.C bilgisi yok")
                    return False
            else:
                print_test("System Status Phase 8.C", False, "Status verisi yok")
                return False
        else:
            print_test("System Status Phase 8.C", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("System Status Phase 8.C", False, str(e))
        return False


def test_9_metrics_database():
    """Test 9: Metrics database oluşturulmuş mu?"""
    try:
        import os
        
        db_path = "api_metrics.db"
        
        if os.path.exists(db_path):
            # Database'i aç ve tabloları kontrol et
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Tabloları listele
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ["request_logs", "daily_metrics", "endpoint_stats"]
            has_all_tables = all(table in tables for table in required_tables)
            
            # Kayıt sayısı
            cursor.execute("SELECT COUNT(*) FROM request_logs")
            log_count = cursor.fetchone()[0]
            
            conn.close()
            
            if has_all_tables:
                print_test(
                    "Metrics Database",
                    True,
                    f"Tablolar: {', '.join(tables)}, Kayıtlar: {log_count}"
                )
                return True
            else:
                print_test("Metrics Database", False, f"Eksik tablolar var: {tables}")
                return False
        else:
            print_test("Metrics Database", False, "Database dosyası bulunamadı")
            return False
    except Exception as e:
        print_test("Metrics Database", False, str(e))
        return False


def test_10_log_files():
    """Test 10: Log dosyaları oluşturulmuş mu?"""
    try:
        import os
        from pathlib import Path
        
        log_dir = Path("logs")
        
        if not log_dir.exists():
            print_test("Log Files", False, "logs/ dizini bulunamadı")
            return False
        
        expected_logs = ["api.log", "api_errors.log", "api_daily.log"]
        existing_logs = []
        
        for log_file in expected_logs:
            log_path = log_dir / log_file
            if log_path.exists():
                existing_logs.append(log_file)
        
        if len(existing_logs) >= 2:  # En az 2 log dosyası olmalı
            print_test(
                "Log Files",
                True,
                f"Oluşturulan: {', '.join(existing_logs)}"
            )
            return True
        else:
            print_test("Log Files", False, f"Yeterli log dosyası yok: {existing_logs}")
            return False
    except Exception as e:
        print_test("Log Files", False, str(e))
        return False


def test_11_performance_tracking():
    """Test 11: Performance tracking çalışıyor mu? (10 istek gönder ve ölç)"""
    try:
        print("\n⏱️  Performance Test: 10 ardışık istek gönderiliyor...")
        
        response_times = []
        
        for i in range(10):
            start = time.time()
            response = requests.get("http://127.0.0.1:8003/api/system-status")
            end = time.time()
            
            response_times.append(end - start)
            
            if response.status_code != 200:
                print_test("Performance Tracking", False, f"İstek {i+1} başarısız")
                return False
        
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        # Metrics'ten veriyi kontrol et
        time.sleep(1)
        metrics_response = requests.get("http://127.0.0.1:8003/api/metrics")
        
        if metrics_response.status_code == 200:
            data = metrics_response.json()
            summary = data.get("summary", {})
            
            print_test(
                "Performance Tracking",
                True,
                f"Ort: {avg_time*1000:.2f}ms, Min: {min_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms | "
                f"Toplam İstek: {summary.get('total_requests', 0)}"
            )
            return True
        else:
            print_test("Performance Tracking", False, "Metrics alınamadı")
            return False
            
    except Exception as e:
        print_test("Performance Tracking", False, str(e))
        return False


# ========================================================================
# ANA TEST RUNNER
# ========================================================================

def run_all_tests():
    """Tüm testleri çalıştır"""
    print("\n" + "="*80)
    print("🧪 PHASE 8.C TEST SUITE - MONITORING & ANALYTICS")
    print("="*80)
    
    tests = [
        test_1_metrics_endpoint,
        test_2_endpoint_specific_metrics,
        test_3_historical_metrics,
        test_4_slow_endpoints,
        test_5_error_analysis,
        test_6_response_time_header,
        test_7_monitoring_dashboard,
        test_8_system_status_phase8c,
        test_9_metrics_database,
        test_10_log_files,
        test_11_performance_tracking
    ]
    
    results = []
    
    for i, test_func in enumerate(tests, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}/{len(tests)}: {test_func.__doc__.strip()}")
        print(f"{'─'*80}")
        
        result = test_func()
        results.append(result)
        
        time.sleep(0.5)  # Test'ler arası kısa bekleme
    
    # Özet
    print("\n" + "="*80)
    print("📊 TEST SONUÇLARI")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n✅ Başarılı: {passed}/{total} ({percentage:.1f}%)")
    print(f"❌ Başarısız: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 TÜM TESTLER BAŞARILI! Phase 8.C tam olarak çalışıyor.")
    elif passed >= total * 0.8:
        print("\n✅ Testlerin çoğu başarılı. Sistem kullanılabilir.")
    else:
        print("\n⚠️ Birçok test başarısız. Kontrol gerekiyor.")
    
    print("="*80 + "\n")
    
    return passed, total


if __name__ == "__main__":
    passed, total = run_all_tests()
    
    # Exit code
    import sys
    sys.exit(0 if passed == total else 1)
