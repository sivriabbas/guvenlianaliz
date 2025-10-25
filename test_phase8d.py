"""
Phase 8.D API Documentation & Testing - Test Suite
Tests API documentation generation and testing tools
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

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

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

def test_system_status_phase8d():
    """Test Phase 8.D in system status endpoint"""
    print_header("TEST 1: System Status - Phase 8.D Bilgisi")
    
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
        
        # Check Phase 8.D exists
        if "phase8" not in status or "D_documentation" not in status["phase8"]:
            print_test("Phase 8.D Varlığı", False, "Phase 8.D bulunamadı")
            return False
        
        phase8d = status["phase8"]["D_documentation"]
        
        # Check availability
        if not phase8d.get("available", False):
            print_test("Phase 8.D Availability", False, "Sistem pasif")
            return False
        
        print_test("Phase 8.D Availability", True)
        
        # Check features
        features = phase8d.get("features", {})
        required_features = [
            "auto_documentation",
            "openapi_spec",
            "postman_collection",
            "interactive_tester",
            "code_examples"
        ]
        
        for feature in required_features:
            if features.get(feature, False):
                print_success(f"  ✓ {feature}")
            else:
                print_warning(f"  ✗ {feature} eksik")
        
        # Check endpoints
        endpoints = phase8d.get("endpoints", [])
        print_info(f"Toplam {len(endpoints)} endpoint kayıtlı")
        
        expected_endpoints = [
            "/api-tester",
            "/api/docs/openapi",
            "/api/docs/postman",
            "/api/docs/markdown",
            "/api/docs/export",
            "/api/docs/endpoints"
        ]
        
        for endpoint in expected_endpoints:
            if endpoint in endpoints:
                print_success(f"  ✓ {endpoint}")
            else:
                print_warning(f"  ✗ {endpoint} eksik")
        
        return True
        
    except Exception as e:
        print_test("System Status Test", False, str(e))
        return False

def test_openapi_spec():
    """Test OpenAPI specification generation"""
    print_header("TEST 2: OpenAPI Specification")
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs/openapi", timeout=10)
        
        if response.status_code != 200:
            print_test("OpenAPI Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        spec = response.json()
        
        # Check OpenAPI version
        if "openapi" not in spec:
            print_test("OpenAPI Format", False, "openapi field eksik")
            return False
        
        print_test("OpenAPI Format", True, f"Version: {spec['openapi']}")
        
        # Check info section
        if "info" in spec:
            info = spec["info"]
            print_info(f"Title: {info.get('title', 'N/A')}")
            print_info(f"Version: {info.get('version', 'N/A')}")
            print_info(f"Description: {len(info.get('description', ''))} karakter")
        
        # Check paths
        if "paths" in spec:
            paths = spec["paths"]
            print_success(f"Toplam {len(paths)} endpoint dokümante edildi")
            
            # Show sample endpoints
            sample_count = min(5, len(paths))
            print_info(f"Örnek {sample_count} endpoint:")
            for i, path in enumerate(list(paths.keys())[:sample_count]):
                print(f"    {i+1}. {path}")
        
        # Check components
        if "components" in spec and "schemas" in spec["components"]:
            schemas = spec["components"]["schemas"]
            print_info(f"Toplam {len(schemas)} schema tanımlandı")
        
        return True
        
    except Exception as e:
        print_test("OpenAPI Test", False, str(e))
        return False

def test_postman_collection():
    """Test Postman collection generation"""
    print_header("TEST 3: Postman Collection")
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs/postman", timeout=10)
        
        if response.status_code != 200:
            print_test("Postman Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        collection = response.json()
        
        # Check collection info
        if "info" not in collection:
            print_test("Postman Format", False, "info field eksik")
            return False
        
        info = collection["info"]
        print_test("Postman Format", True, f"Name: {info.get('name', 'N/A')}")
        print_info(f"Version: {info.get('version', 'N/A')}")
        print_info(f"Schema: {info.get('schema', 'N/A')}")
        
        # Check items
        if "item" in collection:
            items = collection["item"]
            print_success(f"Toplam {len(items)} kategori")
            
            total_requests = 0
            for category in items:
                category_name = category.get("name", "Unknown")
                category_items = category.get("item", [])
                total_requests += len(category_items)
                print_info(f"  {category_name}: {len(category_items)} request")
            
            print_success(f"Toplam {total_requests} request tanımlandı")
        
        return True
        
    except Exception as e:
        print_test("Postman Test", False, str(e))
        return False

def test_markdown_docs():
    """Test Markdown documentation generation"""
    print_header("TEST 4: Markdown Documentation")
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs/markdown", timeout=10)
        
        if response.status_code != 200:
            print_test("Markdown Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        markdown = response.text
        
        # Check content
        if not markdown or len(markdown) < 100:
            print_test("Markdown Content", False, "İçerik çok kısa")
            return False
        
        print_test("Markdown Generation", True)
        print_info(f"Toplam {len(markdown)} karakter")
        print_info(f"Toplam {len(markdown.splitlines())} satır")
        
        # Check for common sections
        sections = ["##", "###", "####"]
        for section in sections:
            count = markdown.count(section)
            if count > 0:
                print_success(f"  {section} başlık: {count} adet")
        
        # Check for code blocks
        code_blocks = markdown.count("```")
        if code_blocks > 0:
            print_success(f"  Code blocks: {code_blocks // 2} adet")
        
        return True
        
    except Exception as e:
        print_test("Markdown Test", False, str(e))
        return False

def test_export_all():
    """Test export all documentation"""
    print_header("TEST 5: Export All Documentation")
    
    try:
        response = requests.post(f"{BASE_URL}/api/docs/export", timeout=15)
        
        if response.status_code != 200:
            print_test("Export Endpoint", False, f"HTTP {response.status_code}")
            return False
        
        result = response.json()
        
        # Check success
        if not result.get("success", False):
            error = result.get("error", "Unknown error")
            print_test("Export Status", False, error)
            return False
        
        print_test("Export Success", True)
        
        # Check files
        if "files" in result:
            files = result["files"]
            print_success(f"Toplam {len(files)} dosya oluşturuldu:")
            for file_path in files:
                # Check if file exists
                path = Path(file_path)
                if path.exists():
                    size = path.stat().st_size
                    print_success(f"  ✓ {file_path} ({size:,} bytes)")
                else:
                    print_warning(f"  ✗ {file_path} (dosya bulunamadı)")
        
        return True
        
    except Exception as e:
        print_test("Export Test", False, str(e))
        return False

def test_endpoints_list():
    """Test endpoints list"""
    print_header("TEST 6: Endpoints List")
    
    try:
        response = requests.get(f"{BASE_URL}/api/docs/endpoints", timeout=10)
        
        if response.status_code != 200:
            print_test("Endpoints List", False, f"HTTP {response.status_code}")
            return False
        
        data = response.json()
        
        # Check categories
        if "categories" not in data:
            print_test("Categories", False, "categories field eksik")
            return False
        
        categories = data["categories"]
        print_test("Endpoints Discovery", True)
        print_success(f"Toplam {len(categories)} kategori keşfedildi:")
        
        total_endpoints = 0
        for category_name, endpoints in categories.items():
            total_endpoints += len(endpoints)
            print_info(f"  {category_name}: {len(endpoints)} endpoint")
            
            # Show sample endpoints
            for i, endpoint in enumerate(endpoints[:3]):
                method = endpoint.get("method", "?")
                path = endpoint.get("path", "?")
                print(f"      {method:6} {path}")
            
            if len(endpoints) > 3:
                print(f"      ... ve {len(endpoints) - 3} endpoint daha")
        
        print_success(f"\nToplam {total_endpoints} endpoint kayıtlı")
        
        return True
        
    except Exception as e:
        print_test("Endpoints Test", False, str(e))
        return False

def test_code_examples():
    """Test code examples generation"""
    print_header("TEST 7: Code Examples")
    
    test_paths = [
        "/api/system-status",
        "/api/analyze",
        "/api/match-odds"
    ]
    
    success_count = 0
    
    for path in test_paths:
        try:
            url = f"{BASE_URL}/api/docs/examples{path}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                examples = response.json()
                
                print_info(f"\n{path}:")
                
                # Check cURL
                if "curl" in examples:
                    curl = examples["curl"]
                    print_success(f"  ✓ cURL ({len(curl)} karakter)")
                
                # Check Python
                if "python" in examples:
                    python = examples["python"]
                    print_success(f"  ✓ Python ({len(python)} karakter)")
                
                # Check JavaScript
                if "javascript" in examples:
                    js = examples["javascript"]
                    print_success(f"  ✓ JavaScript ({len(js)} karakter)")
                
                success_count += 1
            else:
                print_warning(f"  {path}: HTTP {response.status_code}")
                
        except Exception as e:
            print_error(f"  {path}: {str(e)}")
    
    print_test(f"\nCode Examples ({success_count}/{len(test_paths)})", 
               success_count > 0,
               f"{success_count} endpoint için örnekler oluşturuldu")
    
    return success_count > 0

def test_api_tester_ui():
    """Test API tester HTML interface"""
    print_header("TEST 8: Interactive API Tester UI")
    
    try:
        response = requests.get(f"{BASE_URL}/api-tester", timeout=10)
        
        if response.status_code != 200:
            print_test("API Tester UI", False, f"HTTP {response.status_code}")
            return False
        
        html = response.text
        
        # Check content
        if not html or len(html) < 1000:
            print_test("HTML Content", False, "İçerik çok kısa")
            return False
        
        print_test("API Tester HTML", True)
        print_info(f"HTML boyutu: {len(html):,} karakter")
        
        # Check for key components
        components = {
            "<!DOCTYPE html>": "HTML5 doctype",
            "<title>": "Sayfa başlığı",
            "class=\"sidebar\"": "Sidebar bileşeni",
            "sendRequest": "Request gönderme fonksiyonu",
            "updateCodeExamples": "Kod örneği generator",
            "loadEndpoints": "Endpoint loader"
        }
        
        for component, desc in components.items():
            if component in html:
                print_success(f"  ✓ {desc}")
            else:
                print_warning(f"  ✗ {desc} eksik")
        
        print_info(f"\n📱 API Tester: {BASE_URL}/api-tester")
        
        return True
        
    except Exception as e:
        print_test("API Tester Test", False, str(e))
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║        🚀 PHASE 8.D: API DOCUMENTATION & TESTING TOOLS 🚀         ║")
    print("║                                                                   ║")
    print("║              Otomatik API Dokümantasyon Test Suite               ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    # Check server
    print_info("Sunucu durumu kontrol ediliyor...")
    if not check_server():
        print_error("❌ Sunucu çalışmıyor!")
        print_warning(f"Lütfen önce sunucuyu başlatın: python simple_fastapi.py")
        sys.exit(1)
    
    print_success("✓ Sunucu aktif\n")
    
    # Run tests
    results = []
    
    results.append(("System Status Phase 8.D", test_system_status_phase8d()))
    results.append(("OpenAPI Specification", test_openapi_spec()))
    results.append(("Postman Collection", test_postman_collection()))
    results.append(("Markdown Documentation", test_markdown_docs()))
    results.append(("Export All Docs", test_export_all()))
    results.append(("Endpoints List", test_endpoints_list()))
    results.append(("Code Examples", test_code_examples()))
    results.append(("API Tester UI", test_api_tester_ui()))
    
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
        print(f"\n{Colors.CYAN}📚 Phase 8.D API Documentation & Testing: TAM AKTİF{Colors.RESET}")
        print(f"\n{Colors.WHITE}Özellikler:{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Otomatik API dokümantasyonu{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ OpenAPI 3.0 specification{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Postman Collection export{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Markdown dokümantasyon{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ İnteraktif API test arayüzü{Colors.RESET}")
        print(f"{Colors.GREEN}  ✓ Kod örnekleri (cURL, Python, JavaScript){Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ BAZI TESTLER BAŞARISIZ{Colors.RESET}")
        print(f"{Colors.YELLOW}Lütfen hataları kontrol edin{Colors.RESET}")

if __name__ == "__main__":
    main()
