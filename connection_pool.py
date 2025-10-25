"""
Phase 8.G: Performance Optimization - Connection Pool Manager
Database and API connection pooling with health checks
"""

import sqlite3
import time
from typing import Optional, Dict, List, Any
from threading import Lock, Thread
from queue import Queue, Empty
from datetime import datetime, timedelta
import requests
from contextlib import contextmanager


class Connection:
    """Wrapper for a connection with metadata"""
    
    def __init__(self, conn, conn_type: str):
        self.conn = conn
        self.conn_type = conn_type
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.use_count = 0
        self.is_healthy = True
    
    def mark_used(self):
        """Mark connection as used"""
        self.last_used = datetime.now()
        self.use_count += 1
    
    def age(self) -> float:
        """Connection age in seconds"""
        return (datetime.now() - self.created_at).total_seconds()
    
    def idle_time(self) -> float:
        """Time since last use in seconds"""
        return (datetime.now() - self.last_used).total_seconds()


class DatabaseConnectionPool:
    """Connection pool for SQLite databases"""
    
    def __init__(
        self,
        database: str,
        min_size: int = 2,
        max_size: int = 10,
        max_idle_time: int = 300,  # 5 minutes
        max_lifetime: int = 3600,  # 1 hour
        check_interval: int = 60  # Health check every 60s
    ):
        self.database = database
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.max_lifetime = max_lifetime
        self.check_interval = check_interval
        
        self.pool: Queue = Queue(maxsize=max_size)
        self.active_connections: List[Connection] = []
        self.lock = Lock()
        
        self.stats = {
            "created": 0,
            "destroyed": 0,
            "reused": 0,
            "health_checks": 0,
            "health_failures": 0
        }
        
        # Initialize pool
        self._initialize_pool()
        
        # Start health check thread
        self.health_check_thread = Thread(target=self._health_check_loop, daemon=True)
        self.health_check_thread.start()
    
    def _initialize_pool(self):
        """Create minimum number of connections"""
        for _ in range(self.min_size):
            conn = self._create_connection()
            if conn:
                self.pool.put(conn)
    
    def _create_connection(self) -> Optional[Connection]:
        """Create a new database connection"""
        try:
            db_conn = sqlite3.connect(self.database, check_same_thread=False)
            db_conn.row_factory = sqlite3.Row
            
            conn = Connection(db_conn, "sqlite")
            
            with self.lock:
                self.active_connections.append(conn)
                self.stats["created"] += 1
            
            return conn
        except Exception as e:
            print(f"Failed to create connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get a connection from pool (context manager)"""
        conn = None
        try:
            # Try to get from pool
            try:
                conn = self.pool.get(timeout=5)
                conn.mark_used()
                self.stats["reused"] += 1
            except Empty:
                # Pool is empty, create new if under max_size
                if len(self.active_connections) < self.max_size:
                    conn = self._create_connection()
                else:
                    raise Exception("Connection pool exhausted")
            
            yield conn.conn
        
        finally:
            # Return to pool
            if conn:
                try:
                    self.pool.put(conn, timeout=1)
                except:
                    # Pool is full, close connection
                    self._destroy_connection(conn)
    
    def _destroy_connection(self, conn: Connection):
        """Close and remove connection"""
        try:
            conn.conn.close()
            
            with self.lock:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)
                self.stats["destroyed"] += 1
        except Exception as e:
            print(f"Error destroying connection: {e}")
    
    def _health_check_loop(self):
        """Periodic health check for connections"""
        while True:
            time.sleep(self.check_interval)
            self._perform_health_checks()
    
    def _perform_health_checks(self):
        """Check all connections for health and age"""
        with self.lock:
            connections_to_remove = []
            
            for conn in self.active_connections:
                self.stats["health_checks"] += 1
                
                # Check lifetime
                if conn.age() > self.max_lifetime:
                    connections_to_remove.append(conn)
                    continue
                
                # Check idle time
                if conn.idle_time() > self.max_idle_time:
                    connections_to_remove.append(conn)
                    continue
                
                # Test connection
                try:
                    conn.conn.execute("SELECT 1")
                    conn.is_healthy = True
                except Exception:
                    conn.is_healthy = False
                    connections_to_remove.append(conn)
                    self.stats["health_failures"] += 1
            
            # Remove unhealthy connections
            for conn in connections_to_remove:
                self._destroy_connection(conn)
            
            # Ensure minimum pool size
            while len(self.active_connections) < self.min_size:
                new_conn = self._create_connection()
                if new_conn:
                    self.pool.put(new_conn)
    
    def get_stats(self) -> Dict:
        """Get pool statistics"""
        with self.lock:
            active = len(self.active_connections)
            idle = self.pool.qsize()
            in_use = active - idle
            
            return {
                "active_connections": active,
                "idle_connections": idle,
                "in_use_connections": in_use,
                "min_size": self.min_size,
                "max_size": self.max_size,
                "stats": self.stats.copy()
            }
    
    def close_all(self):
        """Close all connections"""
        with self.lock:
            for conn in list(self.active_connections):
                self._destroy_connection(conn)


class HTTPConnectionPool:
    """Connection pool for HTTP requests"""
    
    def __init__(
        self,
        pool_connections: int = 10,
        pool_maxsize: int = 20,
        max_retries: int = 3
    ):
        self.session = requests.Session()
        
        # Configure adapter with connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries
        )
        
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.stats = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "total_time": 0.0
        }
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request using pooled connection"""
        return self._request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request using pooled connection"""
        return self._request('POST', url, **kwargs)
    
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Execute request with statistics tracking"""
        self.stats["requests"] += 1
        start = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            self.stats["successes"] += 1
            return response
        except Exception as e:
            self.stats["failures"] += 1
            raise e
        finally:
            duration = time.time() - start
            self.stats["total_time"] += duration
    
    def get_stats(self) -> Dict:
        """Get request statistics"""
        avg_time = (self.stats["total_time"] / self.stats["requests"] 
                   if self.stats["requests"] > 0 else 0)
        success_rate = (self.stats["successes"] / self.stats["requests"] * 100 
                       if self.stats["requests"] > 0 else 0)
        
        return {
            "total_requests": self.stats["requests"],
            "successful": self.stats["successes"],
            "failed": self.stats["failures"],
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(avg_time, 3)
        }
    
    def close(self):
        """Close session"""
        self.session.close()


class ConnectionPoolManager:
    """Centralized manager for all connection pools"""
    
    def __init__(self):
        self.db_pools: Dict[str, DatabaseConnectionPool] = {}
        self.http_pool = HTTPConnectionPool()
        self.lock = Lock()
    
    def get_db_pool(
        self,
        database: str,
        **kwargs
    ) -> DatabaseConnectionPool:
        """Get or create database connection pool"""
        with self.lock:
            if database not in self.db_pools:
                self.db_pools[database] = DatabaseConnectionPool(database, **kwargs)
            return self.db_pools[database]
    
    def get_http_pool(self) -> HTTPConnectionPool:
        """Get HTTP connection pool"""
        return self.http_pool
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all pools"""
        stats = {
            "database_pools": {},
            "http_pool": self.http_pool.get_stats()
        }
        
        with self.lock:
            for db_name, pool in self.db_pools.items():
                stats["database_pools"][db_name] = pool.get_stats()
        
        return stats
    
    def close_all(self):
        """Close all connection pools"""
        with self.lock:
            for pool in self.db_pools.values():
                pool.close_all()
            self.http_pool.close()


# Test code
if __name__ == "__main__":
    print("🔌 Testing Connection Pool Manager...")
    
    # Test database connection pool
    print("\n📊 Testing Database Connection Pool...")
    
    # Create test database
    test_db = "test_pool.db"
    with sqlite3.connect(test_db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'test')")
        conn.commit()
    
    # Create pool
    db_pool = DatabaseConnectionPool(
        database=test_db,
        min_size=2,
        max_size=5,
        check_interval=10
    )
    
    print(f"   Pool created with min={db_pool.min_size}, max={db_pool.max_size}")
    
    # Test getting connections
    print("\n   Testing connection reuse...")
    for i in range(10):
        with db_pool.get_connection() as conn:
            result = conn.execute("SELECT * FROM test").fetchone()
            # print(f"      Query {i+1}: {dict(result)}")
    
    stats = db_pool.get_stats()
    print(f"   Connections created: {stats['stats']['created']}")
    print(f"   Connections reused: {stats['stats']['reused']}")
    print(f"   Active: {stats['active_connections']}")
    print(f"   Idle: {stats['idle_connections']}")
    print(f"   In-use: {stats['in_use_connections']}")
    
    # Test HTTP connection pool
    print("\n🌐 Testing HTTP Connection Pool...")
    
    http_pool = HTTPConnectionPool(pool_connections=5, pool_maxsize=10)
    
    # Make test requests
    print("   Making 5 test requests...")
    for i in range(5):
        try:
            response = http_pool.get("https://httpbin.org/delay/0")
            print(f"      Request {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"      Request {i+1}: Failed ({e})")
    
    http_stats = http_pool.get_stats()
    print(f"\n   Total requests: {http_stats['total_requests']}")
    print(f"   Success rate: {http_stats['success_rate']}%")
    print(f"   Avg response time: {http_stats['avg_response_time']}s")
    
    # Test ConnectionPoolManager
    print("\n⚙️ Testing Connection Pool Manager...")
    
    manager = ConnectionPoolManager()
    
    # Get database pool
    pool1 = manager.get_db_pool(test_db, min_size=2, max_size=5)
    
    with pool1.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) as cnt FROM test").fetchone()
        print(f"   Database query result: {dict(result)}")
    
    # Get all stats
    all_stats = manager.get_all_stats()
    print(f"\n   Database Pools: {len(all_stats['database_pools'])}")
    print(f"   HTTP Pool Requests: {all_stats['http_pool']['total_requests']}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    db_pool.close_all()
    manager.close_all()
    
    import os
    if os.path.exists(test_db):
        os.remove(test_db)
    
    print("\n✅ Connection Pool test complete!")
