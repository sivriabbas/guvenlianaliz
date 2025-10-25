"""
API Metrics System - Phase 8.C
Gelişmiş API performans metrikleri, izleme ve analitik sistemi

Özellikler:
- API yanıt süreleri tracking
- Endpoint bazlı istatistikler
- Başarı/hata oranları
- Performans analizleri
- Real-time metrikler
"""

import time
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Any
import threading
import json
from pathlib import Path


class MetricsCollector:
    """API metriklerini toplayan ve saklayan sistem"""
    
    def __init__(self, db_path: str = "api_metrics.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        
        # In-memory metrikler (hızlı erişim için)
        self.request_times = defaultdict(list)  # endpoint -> [süreler]
        self.request_counts = Counter()  # endpoint -> sayı
        self.error_counts = Counter()  # endpoint -> hata sayısı
        self.status_codes = Counter()  # status_code -> sayı
        self.last_reset = time.time()
        
    def _init_database(self):
        """Metrics veritabanını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Request logs tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                response_time REAL NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                error_message TEXT
            )
        """)
        
        # Daily metrics tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_requests INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                success_rate REAL DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                unique_ips INTEGER DEFAULT 0,
                metrics_json TEXT
            )
        """)
        
        # Endpoint statistics tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS endpoint_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                date DATE NOT NULL,
                request_count INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                min_response_time REAL,
                max_response_time REAL,
                error_count INTEGER DEFAULT 0,
                UNIQUE(endpoint, date)
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ API Metrics Database initialized")
    
    def record_request(self, 
                      endpoint: str, 
                      method: str,
                      status_code: int, 
                      response_time: float,
                      ip_address: str = None,
                      user_agent: str = None,
                      error_message: str = None):
        """Bir API isteğini kaydet"""
        
        with self.lock:
            # In-memory güncelle
            self.request_times[endpoint].append(response_time)
            self.request_counts[endpoint] += 1
            self.status_codes[status_code] += 1
            
            if status_code >= 400:
                self.error_counts[endpoint] += 1
            
            # Database'e kaydet (async olabilir)
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO request_logs 
                    (endpoint, method, status_code, response_time, ip_address, user_agent, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (endpoint, method, status_code, response_time, ip_address, user_agent, error_message))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"⚠️ Metrics logging error: {e}")
    
    def get_endpoint_metrics(self, endpoint: str) -> Dict[str, Any]:
        """Belirli bir endpoint için metrikleri getir"""
        
        with self.lock:
            times = self.request_times.get(endpoint, [])
            count = self.request_counts.get(endpoint, 0)
            errors = self.error_counts.get(endpoint, 0)
            
            if not times:
                return {
                    "endpoint": endpoint,
                    "request_count": 0,
                    "avg_response_time": 0,
                    "min_response_time": 0,
                    "max_response_time": 0,
                    "error_count": 0,
                    "success_rate": 0
                }
            
            return {
                "endpoint": endpoint,
                "request_count": count,
                "avg_response_time": sum(times) / len(times),
                "min_response_time": min(times),
                "max_response_time": max(times),
                "error_count": errors,
                "success_rate": ((count - errors) / count * 100) if count > 0 else 0
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Tüm API metriklerini getir"""
        
        with self.lock:
            total_requests = sum(self.request_counts.values())
            total_errors = sum(self.error_counts.values())
            
            # Tüm endpoint'lerin metriklerini topla
            endpoint_metrics = {}
            for endpoint in self.request_counts.keys():
                endpoint_metrics[endpoint] = self.get_endpoint_metrics(endpoint)
            
            # Tüm yanıt sürelerini topla
            all_times = []
            for times in self.request_times.values():
                all_times.extend(times)
            
            return {
                "summary": {
                    "total_requests": total_requests,
                    "total_errors": total_errors,
                    "success_rate": ((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 0,
                    "avg_response_time": sum(all_times) / len(all_times) if all_times else 0,
                    "uptime_seconds": time.time() - self.last_reset
                },
                "endpoints": endpoint_metrics,
                "status_codes": dict(self.status_codes),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_historical_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Geçmiş metrikleri getir"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Son N günün verilerini getir
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as request_count,
                    AVG(response_time) as avg_time,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
                FROM request_logs
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (days,))
            
            daily_data = []
            for row in cursor.fetchall():
                daily_data.append({
                    "date": row[0],
                    "requests": row[1],
                    "avg_response_time": round(row[2], 3) if row[2] else 0,
                    "errors": row[3]
                })
            
            # En popüler endpoint'ler
            cursor.execute("""
                SELECT endpoint, COUNT(*) as count, AVG(response_time) as avg_time
                FROM request_logs
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY endpoint
                ORDER BY count DESC
                LIMIT 10
            """, (days,))
            
            popular_endpoints = []
            for row in cursor.fetchall():
                popular_endpoints.append({
                    "endpoint": row[0],
                    "requests": row[1],
                    "avg_time": round(row[2], 3) if row[2] else 0
                })
            
            conn.close()
            
            return {
                "period_days": days,
                "daily_stats": daily_data,
                "popular_endpoints": popular_endpoints
            }
            
        except Exception as e:
            print(f"⚠️ Historical metrics error: {e}")
            return {"error": str(e)}
    
    def get_slow_endpoints(self, threshold_ms: float = 1000, limit: int = 10) -> List[Dict]:
        """Yavaş endpoint'leri tespit et"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    endpoint,
                    COUNT(*) as count,
                    AVG(response_time) as avg_time,
                    MAX(response_time) as max_time
                FROM request_logs
                WHERE timestamp >= datetime('now', '-1 day')
                GROUP BY endpoint
                HAVING avg_time > ?
                ORDER BY avg_time DESC
                LIMIT ?
            """, (threshold_ms / 1000, limit))
            
            slow_endpoints = []
            for row in cursor.fetchall():
                slow_endpoints.append({
                    "endpoint": row[0],
                    "request_count": row[1],
                    "avg_time_ms": round(row[2] * 1000, 2),
                    "max_time_ms": round(row[3] * 1000, 2)
                })
            
            conn.close()
            return slow_endpoints
            
        except Exception as e:
            print(f"⚠️ Slow endpoints error: {e}")
            return []
    
    def get_error_analysis(self, limit: int = 20) -> List[Dict]:
        """Hata analizi yap"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    endpoint,
                    status_code,
                    COUNT(*) as count,
                    error_message,
                    MAX(timestamp) as last_occurrence
                FROM request_logs
                WHERE status_code >= 400
                    AND timestamp >= datetime('now', '-1 day')
                GROUP BY endpoint, status_code, error_message
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            
            errors = []
            for row in cursor.fetchall():
                errors.append({
                    "endpoint": row[0],
                    "status_code": row[1],
                    "count": row[2],
                    "error_message": row[3],
                    "last_seen": row[4]
                })
            
            conn.close()
            return errors
            
        except Exception as e:
            print(f"⚠️ Error analysis error: {e}")
            return []
    
    def reset_metrics(self):
        """In-memory metrikleri sıfırla (database'i etkilemez)"""
        
        with self.lock:
            self.request_times.clear()
            self.request_counts.clear()
            self.error_counts.clear()
            self.status_codes.clear()
            self.last_reset = time.time()
            print("✅ Metrics reset")
    
    def export_metrics(self, output_file: str = "metrics_export.json"):
        """Metrikleri JSON dosyasına export et"""
        
        metrics = self.get_all_metrics()
        historical = self.get_historical_metrics(days=30)
        
        export_data = {
            "export_time": datetime.now().isoformat(),
            "current_metrics": metrics,
            "historical_metrics": historical,
            "slow_endpoints": self.get_slow_endpoints(),
            "error_analysis": self.get_error_analysis()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metrics exported to {output_file}")
        return output_file


class MetricsMiddleware:
    """FastAPI middleware - otomatik metrics toplama"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    async def __call__(self, request, call_next):
        """Her request için metrics topla"""
        
        start_time = time.time()
        
        # Request işle
        response = await call_next(request)
        
        # Süreyi hesapla
        response_time = time.time() - start_time
        
        # Metrikleri kaydet
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        
        # IP ve User-Agent al
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Hata mesajı varsa al (response body'den)
        error_message = None
        if status_code >= 400:
            # Burada response body'yi okuyamayız, middleware'de
            error_message = f"HTTP {status_code}"
        
        # Kaydet
        self.collector.record_request(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message
        )
        
        # Response'a metrics header'ları ekle
        response.headers["X-Response-Time"] = f"{response_time:.3f}s"
        
        return response


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Metrics collector instance'ı getir"""
    return metrics_collector


# Test fonksiyonu
if __name__ == "__main__":
    print("🔧 API Metrics System Test\n")
    
    # Collector oluştur
    collector = MetricsCollector(db_path="test_metrics.db")
    
    # Test verileri ekle
    print("📊 Test verileri ekleniyor...")
    
    endpoints = ["/api/predict", "/api/ml-predict", "/api/ensemble-predict", "/api/optimize-weights"]
    
    for i in range(100):
        endpoint = endpoints[i % len(endpoints)]
        response_time = 0.1 + (i % 10) * 0.05
        status_code = 200 if i % 20 != 0 else 500
        
        collector.record_request(
            endpoint=endpoint,
            method="POST",
            status_code=status_code,
            response_time=response_time,
            ip_address=f"192.168.1.{i % 50}",
            user_agent="TestAgent/1.0"
        )
    
    time.sleep(0.5)
    
    # Metrikleri göster
    print("\n📈 Genel Metrikler:")
    metrics = collector.get_all_metrics()
    print(json.dumps(metrics["summary"], indent=2))
    
    print("\n🎯 Endpoint Metrikleri:")
    for endpoint, stats in metrics["endpoints"].items():
        print(f"  {endpoint}:")
        print(f"    İstekler: {stats['request_count']}")
        print(f"    Ort. Süre: {stats['avg_response_time']:.3f}s")
        print(f"    Başarı: %{stats['success_rate']:.1f}")
    
    print("\n⚠️ Hata Analizi:")
    errors = collector.get_error_analysis()
    for error in errors[:5]:
        print(f"  {error['endpoint']} - {error['status_code']}: {error['count']} kez")
    
    print("\n🐌 Yavaş Endpoint'ler (>200ms):")
    slow = collector.get_slow_endpoints(threshold_ms=200)
    for endpoint in slow[:5]:
        print(f"  {endpoint['endpoint']}: {endpoint['avg_time_ms']:.2f}ms")
    
    # Export et
    print("\n💾 Metrikleri export ediliyor...")
    collector.export_metrics("test_metrics_export.json")
    
    print("\n✅ API Metrics System - Ready!")
    print("   - Request tracking: ✅")
    print("   - Performance metrics: ✅")
    print("   - Error analysis: ✅")
    print("   - Historical data: ✅")
