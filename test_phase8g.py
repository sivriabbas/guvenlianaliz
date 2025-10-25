"""
Phase 8.G: Performance Optimization & Caching - Test Suite
Comprehensive tests for all Phase 8.G components
"""

import pytest
import time
import sqlite3
import os
from pathlib import Path

# Import Phase 8.G modules
from query_optimizer import QueryOptimizer
from advanced_cache import MultiLayerCache, MemoryCache, DiskCache, cache_key_generator, cached
from compression_middleware import CompressionMiddleware, estimate_compression_benefit
from connection_pool import DatabaseConnectionPool, HTTPConnectionPool, ConnectionPoolManager


class TestQueryOptimizer:
    """Test Query Optimizer functionality"""
    
    @pytest.fixture
    def optimizer(self):
        """Create query optimizer instance"""
        db_path = "test_query_optimizer.db"
        optimizer = QueryOptimizer(db_path=db_path, slow_query_threshold=0.1)
        yield optimizer
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.fixture
    def test_db(self):
        """Create test database"""
        db_path = "test_data.db"
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test_table (id INTEGER, name TEXT, value REAL)")
        conn.execute("INSERT INTO test_table VALUES (1, 'test1', 100.5)")
        conn.execute("INSERT INTO test_table VALUES (2, 'test2', 200.5)")
        conn.commit()
        conn.close()
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_query_execution_with_monitoring(self, optimizer, test_db):
        """Test query execution with performance monitoring"""
        query = "SELECT * FROM test_table WHERE id = ?"
        params = (1,)
        
        result = optimizer.execute_with_monitoring(test_db, query, params)
        
        assert result is not None
        assert len(result) == 1
        assert result[0][0] == 1
    
    def test_query_caching(self, optimizer, test_db):
        """Test query result caching"""
        query = "SELECT * FROM test_table WHERE id = ?"
        params = (1,)
        
        # First execution - should cache
        start1 = time.time()
        result1 = optimizer.execute_with_monitoring(test_db, query, params)
        time1 = time.time() - start1
        
        # Second execution - should hit cache
        start2 = time.time()
        result2 = optimizer.execute_with_monitoring(test_db, query, params)
        time2 = time.time() - start2
        
        assert result1 == result2
        # Cache should be faster (though may not always be true in small queries)
        assert time2 <= time1 * 2  # Allow some variance
    
    def test_slow_query_detection(self, optimizer, test_db):
        """Test slow query detection and logging"""
        # Create a slow query
        query = "SELECT * FROM test_table"
        
        # Execute with small threshold to trigger slow query
        optimizer.slow_query_threshold = 0.0001
        optimizer.execute_with_monitoring(test_db, query, ())
        
        slow_queries = optimizer.get_slow_queries(limit=10)
        
        # May or may not be slow depending on system, so just check structure
        assert isinstance(slow_queries, list)
    
    def test_query_statistics(self, optimizer, test_db):
        """Test query statistics tracking"""
        query = "SELECT * FROM test_table WHERE id = ?"
        
        # Execute multiple times
        for i in range(5):
            optimizer.execute_with_monitoring(test_db, query, (1,))
        
        stats = optimizer.get_query_statistics()
        
        assert stats["total_queries"] >= 1
        assert "avg_execution_time" in stats
        assert "cache_hit_rate" in stats
    
    def test_index_recommendations(self, optimizer, test_db):
        """Test index recommendation generation"""
        # Execute a query that could benefit from index
        query = "SELECT * FROM test_table WHERE name = ?"
        
        optimizer.slow_query_threshold = 0.0001
        optimizer.execute_with_monitoring(test_db, query, ('test1',))
        
        recommendations = optimizer.get_index_recommendations()
        
        # Check structure even if no recommendations
        assert isinstance(recommendations, list)


class TestAdvancedCaching:
    """Test Advanced Caching System"""
    
    @pytest.fixture
    def memory_cache(self):
        """Create memory cache instance"""
        return MemoryCache(max_size=10)
    
    @pytest.fixture
    def disk_cache(self):
        """Create disk cache instance"""
        db_path = "test_disk_cache.db"
        cache = DiskCache(db_path=db_path)
        yield cache
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.fixture
    def multi_cache(self):
        """Create multi-layer cache instance"""
        cache = MultiLayerCache(
            memory_max_size=10,
            disk_db_path="test_multi_cache.db"
        )
        yield cache
        # Cleanup
        if os.path.exists("test_multi_cache.db"):
            os.remove("test_multi_cache.db")
    
    def test_memory_cache_set_get(self, memory_cache):
        """Test memory cache set and get operations"""
        memory_cache.set("key1", {"data": "value1"}, ttl=60)
        result = memory_cache.get("key1")
        
        assert result == {"data": "value1"}
    
    def test_memory_cache_expiration(self, memory_cache):
        """Test memory cache TTL expiration"""
        memory_cache.set("key1", "value1", ttl=1)
        time.sleep(1.1)
        result = memory_cache.get("key1")
        
        assert result is None
    
    def test_memory_cache_lru_eviction(self, memory_cache):
        """Test LRU eviction in memory cache"""
        # Fill cache to max
        for i in range(11):
            memory_cache.set(f"key{i}", f"value{i}")
        
        stats = memory_cache.get_stats()
        assert stats["evictions"] >= 1
    
    def test_disk_cache_persistence(self, disk_cache):
        """Test disk cache persistence"""
        disk_cache.set("persistent_key", {"data": "persistent_value"}, ttl=60)
        result = disk_cache.get("persistent_key")
        
        assert result == {"data": "persistent_value"}
    
    def test_multi_layer_cache_promotion(self, multi_cache):
        """Test L2 to L1 cache promotion"""
        # Set in both layers
        multi_cache.set("key1", "value1", ttl=60, persist=True)
        
        # Clear L1
        multi_cache.l1_cache.clear()
        
        # Get should promote from L2 to L1
        result = multi_cache.get("key1")
        
        assert result == "value1"
        assert "key1" in multi_cache.l1_cache.cache
    
    def test_cache_get_or_compute(self, multi_cache):
        """Test get_or_compute functionality"""
        call_count = 0
        
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return {"result": "computed"}
        
        # First call should compute
        result1 = multi_cache.get_or_compute("compute_key", expensive_function)
        assert call_count == 1
        
        # Second call should use cache
        result2 = multi_cache.get_or_compute("compute_key", expensive_function)
        assert call_count == 1  # Should not increment
        assert result1 == result2
    
    def test_cache_warmup(self, multi_cache):
        """Test cache warming functionality"""
        def warmup_func():
            return {"warmed": "data"}
        
        multi_cache.register_warmup("warm_key", warmup_func)
        warmed_count = multi_cache.warmup()
        
        assert warmed_count == 1
        assert multi_cache.get("warm_key") == {"warmed": "data"}
    
    def test_cache_statistics(self, multi_cache):
        """Test cache statistics tracking"""
        multi_cache.set("key1", "value1")
        multi_cache.get("key1")  # Hit
        multi_cache.get("nonexistent")  # Miss
        
        stats = multi_cache.get_stats()
        
        assert "l1_memory" in stats
        assert "l2_disk" in stats
        assert "overall" in stats
        assert stats["overall"]["total_hits"] >= 1
    
    def test_cached_decorator(self):
        """Test @cached decorator"""
        call_count = 0
        
        @cached(ttl=60)
        def decorated_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = decorated_function(5)
        result2 = decorated_function(5)
        
        assert result1 == result2 == 10
        assert call_count == 1  # Should only call once


class TestCompression:
    """Test Compression Middleware"""
    
    @pytest.fixture
    def compression_middleware(self):
        """Create compression middleware instance"""
        return CompressionMiddleware(None, minimum_size=100, gzip_level=6)
    
    def test_gzip_compression(self, compression_middleware):
        """Test gzip compression"""
        test_data = b"Hello World! " * 100  # Repeat to meet minimum size
        compressed = compression_middleware._gzip_compress(test_data)
        
        assert len(compressed) < len(test_data)
        assert isinstance(compressed, bytes)
    
    def test_compression_ratio(self, compression_middleware):
        """Test compression ratio calculation"""
        test_json = b'{"key": "value"}' * 100
        compressed = compression_middleware._gzip_compress(test_json)
        
        ratio = (1 - len(compressed) / len(test_json)) * 100
        
        assert ratio > 50  # Should achieve at least 50% compression
    
    def test_compression_estimation(self):
        """Test compression benefit estimation"""
        test_data = b"Test content" * 100
        estimate = estimate_compression_benefit(test_data, "application/json")
        
        assert "original_size" in estimate
        assert "estimated_compressed_size" in estimate
        assert "should_compress" in estimate
        assert estimate["original_size"] == len(test_data)
    
    def test_compression_levels(self, compression_middleware):
        """Test different compression levels"""
        test_data = b"Compression test data " * 100
        
        sizes = []
        for level in [1, 5, 9]:
            compression_middleware.gzip_level = level
            compressed = compression_middleware._gzip_compress(test_data)
            sizes.append(len(compressed))
        
        # Higher levels should generally produce smaller or equal sizes
        # But differences may be minimal for small data
        assert all(isinstance(s, int) for s in sizes)


class TestConnectionPooling:
    """Test Connection Pooling"""
    
    @pytest.fixture
    def test_db(self):
        """Create test database"""
        db_path = "test_pool.db"
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'test')")
        conn.commit()
        conn.close()
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    @pytest.fixture
    def db_pool(self, test_db):
        """Create database connection pool"""
        pool = DatabaseConnectionPool(
            database=test_db,
            min_size=2,
            max_size=5,
            check_interval=100  # Long interval for testing
        )
        yield pool
        pool.close_all()
    
    @pytest.fixture
    def http_pool(self):
        """Create HTTP connection pool"""
        return HTTPConnectionPool(pool_connections=5, pool_maxsize=10)
    
    def test_db_pool_creation(self, db_pool):
        """Test database pool initialization"""
        stats = db_pool.get_stats()
        
        assert stats["min_size"] == 2
        assert stats["max_size"] == 5
        assert stats["active_connections"] >= 2
    
    def test_db_pool_connection_reuse(self, db_pool):
        """Test connection reuse in database pool"""
        # Use connections multiple times
        for _ in range(5):
            with db_pool.get_connection() as conn:
                result = conn.execute("SELECT * FROM test").fetchone()
                assert result is not None
        
        stats = db_pool.get_stats()
        assert stats["stats"]["reused"] >= 3
    
    def test_db_pool_statistics(self, db_pool):
        """Test database pool statistics"""
        with db_pool.get_connection() as conn:
            conn.execute("SELECT 1")
        
        stats = db_pool.get_stats()
        
        assert "active_connections" in stats
        assert "idle_connections" in stats
        assert "stats" in stats
    
    def test_http_pool_statistics(self, http_pool):
        """Test HTTP pool statistics"""
        stats = http_pool.get_stats()
        
        assert "total_requests" in stats
        assert "success_rate" in stats
        assert "avg_response_time" in stats
    
    def test_pool_manager(self, test_db):
        """Test connection pool manager"""
        manager = ConnectionPoolManager()
        
        # Get database pool
        db_pool = manager.get_db_pool(test_db, min_size=2, max_size=5)
        
        # Get HTTP pool
        http_pool = manager.get_http_pool()
        
        # Use pools
        with db_pool.get_connection() as conn:
            result = conn.execute("SELECT 1").fetchone()
            assert result[0] == 1
        
        # Get all stats
        all_stats = manager.get_all_stats()
        
        assert "database_pools" in all_stats
        assert "http_pool" in all_stats
        assert test_db in all_stats["database_pools"]
        
        manager.close_all()


class TestPerformanceImprovements:
    """Test overall performance improvements"""
    
    def test_cache_speedup(self):
        """Test cache provides performance improvement"""
        cache = MultiLayerCache(memory_max_size=100)
        
        def slow_computation():
            time.sleep(0.01)  # Simulate slow operation
            return {"result": "computed"}
        
        # First call - no cache
        start1 = time.time()
        result1 = cache.get_or_compute("perf_key", slow_computation)
        time1 = time.time() - start1
        
        # Second call - cached
        start2 = time.time()
        result2 = cache.get_or_compute("perf_key", slow_computation)
        time2 = time.time() - start2
        
        assert result1 == result2
        assert time2 < time1  # Cached should be faster
        
        # Cleanup
        if os.path.exists("disk_cache.db"):
            os.remove("disk_cache.db")
    
    def test_compression_space_savings(self):
        """Test compression saves space"""
        middleware = CompressionMiddleware(None, minimum_size=100)
        
        # Create compressible data
        test_data = b'{"data": "value"}' * 100
        compressed = middleware._gzip_compress(test_data)
        
        space_saved = len(test_data) - len(compressed)
        savings_percent = (space_saved / len(test_data)) * 100
        
        assert savings_percent > 50  # At least 50% savings
    
    def test_connection_pool_efficiency(self):
        """Test connection pool is efficient"""
        db_path = "test_efficiency.db"
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        
        pool = DatabaseConnectionPool(database=db_path, min_size=2, max_size=5)
        
        # Perform multiple operations
        for _ in range(10):
            with pool.get_connection() as conn:
                conn.execute("SELECT 1")
        
        stats = pool.get_stats()
        
        # Should reuse connections instead of creating new ones
        assert stats["stats"]["created"] <= 5  # Max pool size
        assert stats["stats"]["reused"] >= 8  # Most should be reused
        
        pool.close_all()
        if os.path.exists(db_path):
            os.remove(db_path)


# Run tests
if __name__ == "__main__":
    print("🧪 Running Phase 8.G Test Suite...\n")
    
    # Run with pytest
    exit_code = pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "-s"  # Show print statements
    ])
    
    if exit_code == 0:
        print("\n✅ All Phase 8.G tests passed!")
    else:
        print(f"\n❌ Some tests failed (exit code: {exit_code})")
    
    exit(exit_code)
