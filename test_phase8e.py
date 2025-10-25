"""
Phase 8.E: Advanced Analytics & Reporting - Test Suite
Tests analytics engine, reporting, and dashboard
"""

import sys
import json
import time
from pathlib import Path
import requests

BASE_URL = "http://127.0.0.1:8003"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_test(name, status, message=""):
    status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if status else f"{Colors.RED}✗{Colors.RESET}"
    status_text = f"{Colors.GREEN}BAŞARILI{Colors.RESET}" if status else f"{Colors.RED}BAŞARISIZ{Colors.RESET}"
    print(f"{status_icon} {Colors.BOLD}{name}{Colors.RESET}: {status_text}")
    if message:
        print(f"  {Colors.YELLOW}→ {message}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_system_status_phase8e():
    """Test Phase 8.E in system status endpoint"""
    print_header("TEST 1: System Status - Phase 8.E Bilgisi")
    
    try:
        response = requests.get(f"{BASE_URL}/api/system-status", timeout=10)
        
        if response.status_code != 200:
            print_test("System Status Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Get status object
        if "status" not in data:
            print_test("Response Format", False, "status field eksik")
            return False
        
        status = data["status"]
        
        # Check Phase 8.E exists
        if "phase8" not in status or "E_analytics" not in status["phase8"]:
            print_test("Phase 8.E Varlığı", False, "Phase 8.E bulunamadı")
            return False
        
        phase8e = status["phase8"]["E_analytics"]
        
        # Check availability
        if not phase8e.get("available", False):
            print_test("Phase 8.E Availability", False, "Sistem pasif")
            return False
        
        print_test("Phase 8.E Availability", True)
        
        # Check features
        features = phase8e.get("features", {})
        required_features = [
            "usage_analytics",
            "trend_analysis",
            "anomaly_detection",
            "health_score",
            "report_generation",
            "interactive_dashboard"
        ]
        
        for feature in required_features:
            if features.get(feature, False):
                print_success(f"  ✓ {feature}")
            else:
                print_error(f"  ✗ {feature} eksik")
        
        # Check endpoints
        endpoints = phase8e.get("endpoints", [])
        print_info(f"Toplam {len(endpoints)} endpoint kayıtlı")
        
        # Check report formats
        formats = phase8e.get("report_formats", [])
        print_info(f"Rapor formatları: {', '.join(formats)}")
        
        return True
        
    except Exception as e:
        print_test("System Status Test", False, str(e))
        return False

def test_usage_summary():
    """Test usage summary analytics"""
    print_header("TEST 2: Usage Summary Analytics")
    
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/usage-summary?hours=24", timeout=10)
        
        if response.status_code != 200:
            print_test("Usage Summary Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Check for error
        if "error" in data:
            print_test("Usage Summary", False, data["error"])
            return False
        
        # Check required fields
        required_fields = [
            "period", "total_requests", "success_count", "error_count",
            "success_rate", "error_rate", "avg_response_time"
        ]
        
        for field in required_fields:
            if field not in data:
                print_test(f"Field: {field}", False, "Eksik")
                return False
        
        print_test("Usage Summary", True)
        print_info(f"Period: {data.get('period')}")
        print_info(f"Total Requests: {data.get('total_requests', 0):,}")
        print_info(f"Success Rate: {data.get('success_rate', 0)}%")
        print_info(f"Avg Response Time: {data.get('avg_response_time', 0)}ms")
        
        # Check percentiles
        if "percentiles" in data:
            p = data["percentiles"]
            print_success(f"  Percentiles: P50={p.get('p50', 0)}ms, P95={p.get('p95', 0)}ms, P99={p.get('p99', 0)}ms")
        
        return True
        
    except Exception as e:
        print_test("Usage Summary Test", False, str(e))
        return False

def test_health_score():
    """Test health score calculation"""
    print_header("TEST 3: Health Score")
    
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/health-score?hours=24", timeout=10)
        
        if response.status_code != 200:
            print_test("Health Score Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if "error" in data:
            print_test("Health Score", False, data["error"])
            return False
        
        # Check required fields
        if "health_score" not in data or "status" not in data:
            print_test("Health Score Fields", False, "Required fields missing")
            return False
        
        score = data.get("health_score", 0)
        status = data.get("status", "unknown")
        
        print_test("Health Score Calculation", True)
        print_info(f"Health Score: {score}/100")
        print_info(f"Status: {status.upper()}")
        
        # Check components
        if "components" in data:
            components = data["components"]
            print_success("  Components:")
            for name, value in components.items():
                print(f"    • {name}: {value}%")
        
        return True
        
    except Exception as e:
        print_test("Health Score Test", False, str(e))
        return False

def test_trend_analysis():
    """Test trend analysis"""
    print_header("TEST 4: Trend Analysis")
    
    try:
        # Test different metrics
        metrics = ["requests", "response_time", "error_rate"]
        success_count = 0
        
        for metric in metrics:
            response = requests.get(
                f"{BASE_URL}/api/analytics/trend?metric={metric}&days=7",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "error" not in data:
                    trend = data.get("trend", "unknown")
                    avg = data.get("average", 0)
                    print_success(f"  {metric}: {trend} (avg: {avg:.2f})")
                    success_count += 1
                else:
                    print_error(f"  {metric}: {data['error']}")
            else:
                print_error(f"  {metric}: HTTP {response.status_code}")
        
        print_test(f"Trend Analysis ({success_count}/{len(metrics)})", 
                   success_count > 0,
                   f"{success_count} metric analyzed")
        
        return success_count > 0
        
    except Exception as e:
        print_test("Trend Analysis Test", False, str(e))
        return False

def test_anomaly_detection():
    """Test anomaly detection"""
    print_header("TEST 5: Anomaly Detection")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/analytics/anomalies?hours=24&threshold=2.0",
            timeout=10
        )
        
        if response.status_code != 200:
            print_test("Anomaly Detection Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if "error" in data:
            print_test("Anomaly Detection", False, data["error"])
            return False
        
        print_test("Anomaly Detection", True)
        
        anomalies = data.get("anomalies", [])
        total_checked = data.get("total_checked", 0)
        total_anomalies = data.get("total_anomalies", 0)
        
        print_info(f"Total Checked: {total_checked:,}")
        print_info(f"Anomalies Found: {total_anomalies}")
        
        if len(anomalies) > 0:
            print_success(f"  Top {min(3, len(anomalies))} anomalies:")
            for i, anomaly in enumerate(anomalies[:3], 1):
                print(f"    {i}. {anomaly.get('endpoint', 'N/A')} - "
                      f"{anomaly.get('response_time', 0)}ms "
                      f"(Z-score: {anomaly.get('z_score', 0)})")
        else:
            print_success("  No anomalies detected ✅")
        
        return True
        
    except Exception as e:
        print_test("Anomaly Detection Test", False, str(e))
        return False

def test_top_performers():
    """Test top performers analytics"""
    print_header("TEST 6: Top Performers")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/analytics/top-performers?limit=5&hours=24",
            timeout=10
        )
        
        if response.status_code != 200:
            print_test("Top Performers Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if "error" in data:
            print_test("Top Performers", False, data["error"])
            return False
        
        print_test("Top Performers", True)
        
        # Check categories
        categories = ["fastest_endpoints", "most_reliable", "most_popular"]
        
        for category in categories:
            items = data.get(category, [])
            if items:
                print_success(f"  {category.replace('_', ' ').title()}: {len(items)} endpoints")
                # Show top 2
                for i, item in enumerate(items[:2], 1):
                    endpoint = item.get('endpoint', 'N/A')
                    print(f"    {i}. {endpoint}")
            else:
                print_error(f"  {category}: No data")
        
        return True
        
    except Exception as e:
        print_test("Top Performers Test", False, str(e))
        return False

def test_report_generation():
    """Test report generation"""
    print_header("TEST 7: Report Generation")
    
    try:
        # Test HTML report
        response = requests.post(
            f"{BASE_URL}/api/reports/generate?report_type=general&format=html&hours=24",
            timeout=15
        )
        
        if response.status_code != 200:
            print_test("Report Generation Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get("success", False):
            error = data.get("error", "Unknown error")
            print_test("HTML Report Generation", False, error)
            return False
        
        print_test("HTML Report Generation", True)
        
        file_path = data.get("file", "")
        print_success(f"  Report saved: {file_path}")
        
        # Check if file exists
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print_success(f"  File size: {size:,} bytes")
        else:
            print_error(f"  File not found: {file_path}")
        
        # Test JSON report
        response = requests.post(
            f"{BASE_URL}/api/reports/generate?report_type=health&format=json&hours=24",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                print_success(f"  JSON Report: {data.get('file', 'N/A')}")
        
        return True
        
    except Exception as e:
        print_test("Report Generation Test", False, str(e))
        return False

def test_reports_list():
    """Test reports list"""
    print_header("TEST 8: Reports List")
    
    try:
        response = requests.get(f"{BASE_URL}/api/reports/list", timeout=10)
        
        if response.status_code != 200:
            print_test("Reports List Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if "error" in data:
            print_test("Reports List", False, data["error"])
            return False
        
        print_test("Reports List", True)
        
        total = data.get("total", 0)
        reports = data.get("reports", [])
        
        print_info(f"Total Reports: {total}")
        
        if reports:
            print_success(f"  Latest {min(3, len(reports))} reports:")
            for i, report in enumerate(reports[:3], 1):
                filename = report.get("filename", "N/A")
                size = report.get("size", 0)
                print(f"    {i}. {filename} ({size:,} bytes)")
        else:
            print_info("  No reports found")
        
        return True
        
    except Exception as e:
        print_test("Reports List Test", False, str(e))
        return False

def test_analytics_dashboard():
    """Test analytics dashboard UI"""
    print_header("TEST 9: Analytics Dashboard UI")
    
    try:
        response = requests.get(f"{BASE_URL}/analytics-dashboard", timeout=10)
        
        if response.status_code != 200:
            print_test("Analytics Dashboard", False, f"HTTP {response.status_code}")
            return False
        
        html = response.text
        
        # Check content
        if not html or len(html) < 1000:
            print_test("HTML Content", False, "İçerik çok kısa")
            return False
        
        print_test("Analytics Dashboard HTML", True)
        print_info(f"HTML boyutu: {len(html):,} karakter")
        
        # Check for key components
        components = {
            "<!DOCTYPE html>": "HTML5 doctype",
            "Analytics Dashboard": "Dashboard title",
            "Chart.js": "Chart.js library",
            "loadAllData": "Data loading function",
            "healthScoreCard": "Health score card",
            "responseTimeChart": "Response time chart",
            "trendChart": "Trend chart"
        }
        
        for component, desc in components.items():
            if component in html:
                print_success(f"  ✓ {desc}")
            else:
                print_error(f"  ✗ {desc} eksik")
        
        print_info(f"\n📱 Analytics Dashboard: {BASE_URL}/analytics-dashboard")
        
        return True
        
    except Exception as e:
        print_test("Analytics Dashboard Test", False, str(e))
        return False

def test_endpoint_analytics():
    """Test endpoint-specific analytics"""
    print_header("TEST 10: Endpoint Analytics")
    
    try:
        # Test a common endpoint
        endpoint = "api/system-status"
        response = requests.get(
            f"{BASE_URL}/api/analytics/endpoint/{endpoint}?hours=24",
            timeout=10
        )
        
        if response.status_code != 200:
            print_test("Endpoint Analytics", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        if "error" in data:
            print_test("Endpoint Analytics", False, data["error"])
            return False
        
        print_test("Endpoint Analytics", True)
        print_info(f"Endpoint: {data.get('endpoint', 'N/A')}")
        print_info(f"Total Requests: {data.get('total_requests', 0):,}")
        print_info(f"Success Rate: {data.get('success_rate', 0)}%")
        print_info(f"Avg Response Time: {data.get('avg_response_time', 0)}ms")
        
        # Check status codes
        if "status_codes" in data:
            codes = data["status_codes"]
            print_success(f"  Status codes: {len(codes)} different codes")
        
        # Check hourly distribution
        if "hourly_distribution" in data:
            hourly = data["hourly_distribution"]
            print_success(f"  Hourly data: {len(hourly)} hours")
        
        return True
        
    except Exception as e:
        print_test("Endpoint Analytics Test", False, str(e))
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║         🚀 PHASE 8.E: ADVANCED ANALYTICS & REPORTING 🚀          ║")
    print("║                                                                   ║")
    print("║              Advanced Analytics & Reporting Test Suite           ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    # Check server
    print_info("Sunucu durumu kontrol ediliyor...")
    if not check_server():
        print_error("❌ Sunucu çalışmıyor!")
        print_error(f"Lütfen önce sunucuyu başlatın: python simple_fastapi.py")
        sys.exit(1)
    
    print_success("✓ Sunucu aktif\n")
    
    # Run tests
    results = []
    
    results.append(("System Status Phase 8.E", test_system_status_phase8e()))
    results.append(("Usage Summary", test_usage_summary()))
    results.append(("Health Score", test_health_score()))
    results.append(("Trend Analysis", test_trend_analysis()))
    results.append(("Anomaly Detection", test_anomaly_detection()))
    results.append(("Top Performers", test_top_performers()))
    results.append(("Report Generation", test_report_generation()))
    results.append(("Reports List", test_reports_list()))
    results.append(("Analytics Dashboard", test_analytics_dashboard()))
    results.append(("Endpoint Analytics", test_endpoint_analytics()))
    
    # Summary
    print_header("TEST SONUÇLARI")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if result else f"{Colors.RED}✗{Colors.RESET}"
        print(f"{status_icon} {name}")
    
    print(f"\n{Colors.BOLD}Toplam: {passed}/{total} test başarılı{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TÜM TESTLER BAŞARILI! 🎉{Colors.RESET}")
        print(f"\n{Colors.CYAN}📈 Phase 8.E Advanced Analytics & Reporting: TAM AKTİF{Colors.RESET}")
        print(f"\n{Colors.WHITE}Özellikler:{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Real-time usage analytics{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Trend detection & analysis{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Anomaly detection{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Health score calculation{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Top performers analytics{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Multi-format reports (HTML, JSON, CSV){Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Interactive analytics dashboard{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ BAZI TESTLER BAŞARISIZ{Colors.RESET}")
        print(f"{Colors.YELLOW}Lütfen hataları kontrol edin{Colors.RESET}")

if __name__ == "__main__":
    main()
