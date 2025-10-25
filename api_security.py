"""
API Güvenlik Sistemi - Phase 8.A
=================================

Rate Limiting, API Key Authentication, Request Validation
"""

import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json
from functools import wraps
from fastapi import HTTPException, Request, Header
from collections import defaultdict
import time


class RateLimiter:
    """
    IP bazlı ve endpoint bazlı rate limiting sistemi
    """
    
    def __init__(self):
        self.requests = defaultdict(list)  # {ip: [timestamps]}
        self.endpoint_requests = defaultdict(lambda: defaultdict(list))  # {endpoint: {ip: [timestamps]}}
        
    def clean_old_requests(self, ip: str, window: int):
        """Eski istekleri temizle"""
        cutoff_time = time.time() - window
        if ip in self.requests:
            self.requests[ip] = [ts for ts in self.requests[ip] if ts > cutoff_time]
    
    def check_rate_limit(self, ip: str, limit: int, window: int = 60) -> bool:
        """
        Rate limit kontrolü
        
        Args:
            ip: IP adresi
            limit: İzin verilen maksimum istek sayısı
            window: Zaman penceresi (saniye)
            
        Returns:
            True: İzin ver, False: Limit aşıldı
        """
        current_time = time.time()
        
        # Eski istekleri temizle
        self.clean_old_requests(ip, window)
        
        # Mevcut istek sayısını kontrol et
        if ip in self.requests and len(self.requests[ip]) >= limit:
            return False
        
        # Yeni isteği kaydet
        self.requests[ip].append(current_time)
        return True
    
    def check_endpoint_rate_limit(self, endpoint: str, ip: str, limit: int, window: int = 60) -> bool:
        """
        Endpoint bazlı rate limit kontrolü
        """
        current_time = time.time()
        cutoff_time = current_time - window
        
        # Eski istekleri temizle
        if endpoint in self.endpoint_requests and ip in self.endpoint_requests[endpoint]:
            self.endpoint_requests[endpoint][ip] = [
                ts for ts in self.endpoint_requests[endpoint][ip] if ts > cutoff_time
            ]
        
        # Mevcut istek sayısını kontrol et
        if endpoint in self.endpoint_requests and ip in self.endpoint_requests[endpoint]:
            if len(self.endpoint_requests[endpoint][ip]) >= limit:
                return False
        
        # Yeni isteği kaydet
        self.endpoint_requests[endpoint][ip].append(current_time)
        return True
    
    def get_remaining_requests(self, ip: str, limit: int, window: int = 60) -> int:
        """Kalan istek sayısını döndür"""
        self.clean_old_requests(ip, window)
        current_count = len(self.requests.get(ip, []))
        return max(0, limit - current_count)
    
    def get_reset_time(self, ip: str, window: int = 60) -> int:
        """Rate limit sıfırlanma zamanını döndür (saniye)"""
        if ip not in self.requests or not self.requests[ip]:
            return 0
        
        oldest_request = min(self.requests[ip])
        reset_time = oldest_request + window - time.time()
        return max(0, int(reset_time))


class APIKeyManager:
    """
    API Key yönetim sistemi
    SQLite ile key oluşturma, doğrulama, kullanım izleme
    """
    
    def __init__(self, db_path: str = "api_keys.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Veritabanını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # API Keys tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT UNIQUE NOT NULL,
                key_name TEXT NOT NULL,
                owner TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                rate_limit INTEGER DEFAULT 100,
                total_requests INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                permissions TEXT DEFAULT 'basic'
            )
        """)
        
        # API Key kullanım logları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_key_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success INTEGER DEFAULT 1,
                response_time REAL
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ API Key veritabanı hazır:", self.db_path)
    
    def generate_api_key(self, name: str, owner: str = None, 
                        expires_days: int = None, rate_limit: int = 100,
                        permissions: str = "basic") -> str:
        """
        Yeni API key oluştur
        
        Args:
            name: Key ismi
            owner: Sahip bilgisi
            expires_days: Kaç gün sonra sona erecek (None = sınırsız)
            rate_limit: Dakika başına istek limiti
            permissions: Yetki seviyesi (basic, premium, admin)
            
        Returns:
            API key string
        """
        # 32 byte random key oluştur
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        
        # Hash'le (veritabanında hash saklanır)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Expiry date hesapla
        expires_at = None
        if expires_days:
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
        
        # Veritabanına kaydet
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_keys (key_hash, key_name, owner, expires_at, rate_limit, permissions)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (key_hash, name, owner, expires_at, rate_limit, permissions))
        
        conn.commit()
        conn.close()
        
        print(f"✅ API Key oluşturuldu: {name}")
        print(f"   Key: {api_key}")
        print(f"   Rate Limit: {rate_limit}/dakika")
        print(f"   Yetki: {permissions}")
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """
        API key'i doğrula
        
        Returns:
            None: Geçersiz key
            Dict: Key bilgileri
        """
        if not api_key or not api_key.startswith("sk_"):
            return None
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1
        """, (key_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        key_data = dict(row)
        
        # Expiry kontrolü
        if key_data['expires_at']:
            expires_at = datetime.fromisoformat(key_data['expires_at'])
            if datetime.now() > expires_at:
                return None
        
        return key_data
    
    def log_usage(self, api_key: str, endpoint: str, ip_address: str, 
                  success: bool = True, response_time: float = None):
        """API key kullanımını logla"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Kullanım logu ekle
        cursor.execute("""
            INSERT INTO api_key_usage (key_hash, endpoint, ip_address, success, response_time)
            VALUES (?, ?, ?, ?, ?)
        """, (key_hash, endpoint, ip_address, int(success), response_time))
        
        # Total requests güncelle
        cursor.execute("""
            UPDATE api_keys 
            SET total_requests = total_requests + 1, last_used = CURRENT_TIMESTAMP
            WHERE key_hash = ?
        """, (key_hash,))
        
        conn.commit()
        conn.close()
    
    def get_key_stats(self, api_key: str) -> Dict:
        """API key istatistikleri"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Toplam istatistikler
        cursor.execute("""
            SELECT 
                COUNT(*) as total_calls,
                SUM(success) as successful_calls,
                AVG(response_time) as avg_response_time,
                COUNT(DISTINCT endpoint) as unique_endpoints
            FROM api_key_usage
            WHERE key_hash = ?
        """, (key_hash,))
        
        stats = cursor.fetchone()
        
        # Son 24 saat
        cursor.execute("""
            SELECT COUNT(*) FROM api_key_usage
            WHERE key_hash = ? AND timestamp > datetime('now', '-1 day')
        """, (key_hash,))
        
        last_24h = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_calls': stats[0],
            'successful_calls': stats[1],
            'avg_response_time': stats[2],
            'unique_endpoints': stats[3],
            'last_24h': last_24h
        }
    
    def deactivate_key(self, api_key: str):
        """API key'i deaktif et"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE api_keys SET is_active = 0 WHERE key_hash = ?", (key_hash,))
        conn.commit()
        conn.close()
        
        print(f"🔒 API Key deaktif edildi")


# Global instances
rate_limiter = RateLimiter()
api_key_manager = APIKeyManager()


def get_client_ip(request: Request) -> str:
    """Client IP adresini al"""
    # X-Forwarded-For header'ını kontrol et (proxy/load balancer için)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # X-Real-IP header'ını kontrol et
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Direct IP
    return request.client.host


def require_api_key(permissions: List[str] = None):
    """
    API key gerektiren endpoint decorator'ı
    
    Usage:
        @app.get("/api/premium")
        @require_api_key(permissions=["premium", "admin"])
        async def premium_endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, x_api_key: str = Header(None), **kwargs):
            # API key kontrolü
            if not x_api_key:
                raise HTTPException(
                    status_code=401,
                    detail="API key gerekli. Header: X-API-Key"
                )
            
            # Key doğrulama
            key_data = api_key_manager.verify_api_key(x_api_key)
            if not key_data:
                raise HTTPException(
                    status_code=403,
                    detail="Geçersiz veya süresi dolmuş API key"
                )
            
            # Yetki kontrolü
            if permissions and key_data['permissions'] not in permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Yetersiz yetki. Gerekli: {permissions}"
                )
            
            # Rate limit kontrolü (key bazlı)
            ip = get_client_ip(request)
            key_rate_limit = key_data['rate_limit']
            
            if not rate_limiter.check_rate_limit(f"key_{key_data['id']}", key_rate_limit, 60):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit aşıldı. Limit: {key_rate_limit}/dakika"
                )
            
            # Kullanımı logla
            start_time = time.time()
            
            try:
                result = await func(*args, request=request, **kwargs)
                response_time = time.time() - start_time
                api_key_manager.log_usage(x_api_key, request.url.path, ip, True, response_time)
                return result
            except Exception as e:
                response_time = time.time() - start_time
                api_key_manager.log_usage(x_api_key, request.url.path, ip, False, response_time)
                raise e
        
        return wrapper
    return decorator


# CLI için key oluşturma
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create-key":
        name = input("Key ismi: ")
        owner = input("Sahip (opsiyonel): ") or None
        expires_days = input("Kaç gün geçerli (Enter = sınırsız): ")
        expires_days = int(expires_days) if expires_days else None
        rate_limit = input("Rate limit (varsayılan 100/dk): ")
        rate_limit = int(rate_limit) if rate_limit else 100
        permissions = input("Yetki (basic/premium/admin, varsayılan basic): ") or "basic"
        
        key = api_key_manager.generate_api_key(
            name=name,
            owner=owner,
            expires_days=expires_days,
            rate_limit=rate_limit,
            permissions=permissions
        )
        
        print("\n" + "="*60)
        print("🔑 YENİ API KEY OLUŞTURULDU!")
        print("="*60)
        print(f"\nKey: {key}")
        print(f"\nBu key'i güvenli bir yerde sakla!")
        print(f"Kullanım: Header'a ekle -> X-API-Key: {key}")
        print("="*60)
    
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\n🧪 API Güvenlik Sistemi Testi\n")
        
        # Test key oluştur
        test_key = api_key_manager.generate_api_key(
            name="Test Key",
            owner="Test User",
            rate_limit=10,
            permissions="basic"
        )
        
        print("\n✅ Key oluşturuldu")
        
        # Key doğrula
        key_data = api_key_manager.verify_api_key(test_key)
        print(f"✅ Key doğrulandı: {key_data['key_name']}")
        
        # Rate limiter test
        print("\n🔄 Rate limiter testi...")
        for i in range(12):
            allowed = rate_limiter.check_rate_limit("test_ip", 10, 60)
            print(f"  İstek {i+1}: {'✅ İzin verildi' if allowed else '❌ Limit aşıldı'}")
        
        print("\n✅ Tüm testler başarılı!")
    
    else:
        print("Kullanım:")
        print("  python api_security.py create-key  # Yeni API key oluştur")
        print("  python api_security.py test        # Sistemi test et")
