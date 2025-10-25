"""
Phase 8.G: Performance Optimization - Query Optimizer
Slow query detection, automatic indexing, query caching
"""

import sqlite3
import time
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict
import re

class QueryOptimizer:
    """Database query optimization and performance monitoring"""
    
    def __init__(
        self,
        db_path: str = "query_optimizer.db",
        slow_query_threshold: float = 1.0  # seconds
    ):
        self.db_path = Path(db_path)
        self.slow_query_threshold = slow_query_threshold
        self.query_cache = {}  # In-memory query result cache
        self.query_stats = defaultdict(lambda: {"count": 0, "total_time": 0, "slow_count": 0})
        self.ensure_tables()
    
    def ensure_tables(self):
        """Create optimizer tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Slow queries log
            conn.execute("""
                CREATE TABLE IF NOT EXISTS slow_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    database_name TEXT,
                    table_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes separately
            conn.execute("CREATE INDEX IF NOT EXISTS idx_slow_query_hash ON slow_queries(query_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_slow_execution_time ON slow_queries(execution_time)")
            
            # Query statistics
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_statistics (
                    query_hash TEXT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    execution_count INTEGER DEFAULT 0,
                    total_execution_time REAL DEFAULT 0,
                    avg_execution_time REAL DEFAULT 0,
                    min_execution_time REAL,
                    max_execution_time REAL,
                    slow_query_count INTEGER DEFAULT 0,
                    last_executed TIMESTAMP,
                    optimization_applied INTEGER DEFAULT 0
                )
            """)
            
            # Index recommendations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS index_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    database_name TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    column_names TEXT NOT NULL,
                    reason TEXT,
                    estimated_improvement REAL,
                    applied INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Query cache metadata
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_cache_metadata (
                    cache_key TEXT PRIMARY KEY,
                    query_hash TEXT NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    hit_count INTEGER DEFAULT 0,
                    size_bytes INTEGER
                )
            """)
            
            conn.commit()
    
    def execute_with_monitoring(
        self,
        db_path: str,
        query: str,
        params: Tuple = None,
        use_cache: bool = True
    ) -> Tuple[List, float]:
        """Execute query with performance monitoring"""
        query_hash = self._hash_query(query)
        cache_key = self._generate_cache_key(query, params)
        
        # Check cache first
        if use_cache and cache_key in self.query_cache:
            cached_data = self.query_cache[cache_key]
            if cached_data['expires_at'] > datetime.now():
                self._update_cache_hit(cache_key)
                return cached_data['results'], 0  # Cache hit, no execution time
        
        # Execute query
        start_time = time.time()
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params or ())
                results = [dict(row) for row in cursor.fetchall()]
            
            execution_time = time.time() - start_time
            
            # Log query statistics
            self._log_query_execution(query_hash, query, execution_time)
            
            # Check if slow query
            if execution_time > self.slow_query_threshold:
                self._log_slow_query(query_hash, query, execution_time, db_path)
                self._analyze_and_recommend(query, db_path)
            
            # Cache results
            if use_cache:
                self._cache_results(cache_key, query_hash, results, execution_time)
            
            return results, execution_time
            
        except Exception as e:
            execution_time = time.time() - start_time
            raise Exception(f"Query execution failed: {e}")
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query normalization"""
        # Normalize query (remove extra whitespace, parameters)
        normalized = re.sub(r'\s+', ' ', query.strip().lower())
        normalized = re.sub(r'\?|\$\d+|:\w+', '?', normalized)  # Normalize params
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _generate_cache_key(self, query: str, params: Tuple = None) -> str:
        """Generate unique cache key for query + params"""
        key_data = f"{query}:{str(params)}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _log_query_execution(self, query_hash: str, query: str, execution_time: float):
        """Log query execution statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if exists
                existing = conn.execute(
                    "SELECT * FROM query_statistics WHERE query_hash = ?",
                    (query_hash,)
                ).fetchone()
                
                if existing:
                    # Update existing
                    new_count = existing[2] + 1
                    new_total = existing[3] + execution_time
                    new_avg = new_total / new_count
                    new_min = min(existing[5] or execution_time, execution_time)
                    new_max = max(existing[6] or execution_time, execution_time)
                    new_slow = existing[7] + (1 if execution_time > self.slow_query_threshold else 0)
                    
                    conn.execute("""
                        UPDATE query_statistics
                        SET execution_count = ?,
                            total_execution_time = ?,
                            avg_execution_time = ?,
                            min_execution_time = ?,
                            max_execution_time = ?,
                            slow_query_count = ?,
                            last_executed = ?
                        WHERE query_hash = ?
                    """, (new_count, new_total, new_avg, new_min, new_max, new_slow, 
                          datetime.now(), query_hash))
                else:
                    # Insert new
                    conn.execute("""
                        INSERT INTO query_statistics
                        (query_hash, query_text, execution_count, total_execution_time,
                         avg_execution_time, min_execution_time, max_execution_time,
                         slow_query_count, last_executed)
                        VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?)
                    """, (query_hash, query, execution_time, execution_time,
                          execution_time, execution_time,
                          1 if execution_time > self.slow_query_threshold else 0,
                          datetime.now()))
                
                conn.commit()
        except Exception as e:
            print(f"Error logging query stats: {e}")
    
    def _log_slow_query(
        self,
        query_hash: str,
        query: str,
        execution_time: float,
        db_path: str
    ):
        """Log slow query for analysis"""
        try:
            table_name = self._extract_table_name(query)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO slow_queries
                    (query_hash, query_text, execution_time, database_name, table_name)
                    VALUES (?, ?, ?, ?, ?)
                """, (query_hash, query, execution_time, db_path, table_name))
                conn.commit()
        except Exception as e:
            print(f"Error logging slow query: {e}")
    
    def _extract_table_name(self, query: str) -> Optional[str]:
        """Extract table name from query"""
        # Simple regex to find table name
        match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _analyze_and_recommend(self, query: str, db_path: str):
        """Analyze query and recommend indexes"""
        try:
            # Extract table and columns
            table = self._extract_table_name(query)
            if not table:
                return
            
            # Find WHERE clause columns
            where_columns = self._extract_where_columns(query)
            if not where_columns:
                return
            
            # Check if index exists
            with sqlite3.connect(db_path) as conn:
                existing_indexes = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=?",
                    (table,)
                ).fetchall()
                existing_index_names = [idx[0] for idx in existing_indexes]
            
            # Recommend index if not exists
            for column in where_columns:
                index_name = f"idx_{table}_{column}"
                if index_name not in existing_index_names:
                    self._create_index_recommendation(
                        db_path, table, column,
                        "WHERE clause optimization"
                    )
        except Exception as e:
            print(f"Error analyzing query: {e}")
    
    def _extract_where_columns(self, query: str) -> List[str]:
        """Extract column names from WHERE clause"""
        columns = []
        # Simple regex - finds column names before = or IN
        matches = re.findall(r'WHERE\s+(\w+)\s*[=<>]|AND\s+(\w+)\s*[=<>]|OR\s+(\w+)\s*[=<>]', 
                            query, re.IGNORECASE)
        for match in matches:
            for col in match:
                if col:
                    columns.append(col)
        return list(set(columns))
    
    def _create_index_recommendation(
        self,
        database_name: str,
        table_name: str,
        column_names: str,
        reason: str
    ):
        """Create index recommendation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO index_recommendations
                    (database_name, table_name, column_names, reason, estimated_improvement)
                    VALUES (?, ?, ?, ?, ?)
                """, (database_name, table_name, column_names, reason, 50.0))  # Estimated 50% improvement
                conn.commit()
        except Exception as e:
            print(f"Error creating recommendation: {e}")
    
    def _cache_results(
        self,
        cache_key: str,
        query_hash: str,
        results: List,
        execution_time: float,
        ttl_seconds: int = 300
    ):
        """Cache query results"""
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        size_bytes = len(json.dumps(results))
        
        self.query_cache[cache_key] = {
            'results': results,
            'expires_at': expires_at,
            'cached_at': datetime.now(),
            'size': size_bytes
        }
        
        # Store metadata
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO query_cache_metadata
                    (cache_key, query_hash, cached_at, expires_at, size_bytes)
                    VALUES (?, ?, ?, ?, ?)
                """, (cache_key, query_hash, datetime.now(), expires_at, size_bytes))
                conn.commit()
        except Exception:
            pass
    
    def _update_cache_hit(self, cache_key: str):
        """Update cache hit count"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE query_cache_metadata
                    SET hit_count = hit_count + 1
                    WHERE cache_key = ?
                """, (cache_key,))
                conn.commit()
        except Exception:
            pass
    
    def get_slow_queries(self, limit: int = 20) -> List[Dict]:
        """Get slowest queries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                queries = conn.execute("""
                    SELECT query_hash, query_text, 
                           AVG(execution_time) as avg_time,
                           MAX(execution_time) as max_time,
                           COUNT(*) as occurrences
                    FROM slow_queries
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY query_hash
                    ORDER BY avg_time DESC
                    LIMIT ?
                """, (limit,)).fetchall()
                
                return [dict(q) for q in queries]
        except Exception as e:
            return []
    
    def get_query_statistics(self) -> Dict:
        """Get overall query statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                total = conn.execute("""
                    SELECT SUM(execution_count) as total_queries,
                           AVG(avg_execution_time) as overall_avg_time,
                           SUM(slow_query_count) as total_slow_queries
                    FROM query_statistics
                """).fetchone()
                
                cache_stats = conn.execute("""
                    SELECT COUNT(*) as cached_queries,
                           SUM(hit_count) as total_hits,
                           SUM(size_bytes) as total_cache_size
                    FROM query_cache_metadata
                    WHERE expires_at > datetime('now')
                """).fetchone()
                
                return {
                    "total_queries": total['total_queries'] or 0,
                    "avg_execution_time": round(total['overall_avg_time'] or 0, 3),
                    "slow_queries": total['total_slow_queries'] or 0,
                    "cached_queries": cache_stats['cached_queries'] or 0,
                    "cache_hits": cache_stats['total_hits'] or 0,
                    "cache_size_mb": round((cache_stats['total_cache_size'] or 0) / 1024 / 1024, 2),
                    "cache_hit_rate": round(
                        (cache_stats['total_hits'] or 0) / (total['total_queries'] or 1) * 100, 2
                    )
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_index_recommendations(self) -> List[Dict]:
        """Get index recommendations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                recommendations = conn.execute("""
                    SELECT database_name, table_name, column_names, reason,
                           estimated_improvement, applied, created_at
                    FROM index_recommendations
                    WHERE applied = 0
                    ORDER BY estimated_improvement DESC, created_at DESC
                """).fetchall()
                
                return [dict(r) for r in recommendations]
        except Exception as e:
            return []
    
    def apply_index_recommendation(self, recommendation_id: int) -> bool:
        """Apply index recommendation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get recommendation
                rec = conn.execute("""
                    SELECT * FROM index_recommendations WHERE id = ?
                """, (recommendation_id,)).fetchone()
                
                if not rec:
                    return False
                
                # Create index
                db_conn = sqlite3.connect(rec['database_name'])
                index_name = f"idx_{rec['table_name']}_{rec['column_names']}"
                db_conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name}
                    ON {rec['table_name']} ({rec['column_names']})
                """)
                db_conn.commit()
                db_conn.close()
                
                # Mark as applied
                conn.execute("""
                    UPDATE index_recommendations SET applied = 1 WHERE id = ?
                """, (recommendation_id,))
                conn.commit()
                
                return True
        except Exception as e:
            print(f"Error applying index: {e}")
            return False
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, data in self.query_cache.items()
            if data['expires_at'] < now
        ]
        
        for key in expired_keys:
            del self.query_cache[key]
        
        # Clean metadata
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM query_cache_metadata
                    WHERE expires_at < ?
                """, (now,))
                conn.commit()
        except Exception:
            pass
        
        return len(expired_keys)


# Test code
if __name__ == "__main__":
    print("🔍 Testing Query Optimizer...")
    
    optimizer = QueryOptimizer(slow_query_threshold=0.1)
    
    # Test query execution with monitoring
    print("\n📊 Executing test query...")
    test_db = "api_metrics.db"
    test_query = "SELECT * FROM request_logs WHERE status_code = ? ORDER BY timestamp DESC LIMIT 10"
    
    results, exec_time = optimizer.execute_with_monitoring(
        test_db, test_query, (200,), use_cache=True
    )
    print(f"   Execution time: {exec_time:.3f}s")
    print(f"   Results: {len(results)} rows")
    
    # Test cache hit
    print("\n🚀 Testing cache hit...")
    results2, exec_time2 = optimizer.execute_with_monitoring(
        test_db, test_query, (200,), use_cache=True
    )
    print(f"   Execution time: {exec_time2:.3f}s (cached)")
    
    # Get statistics
    print("\n📈 Query Statistics:")
    stats = optimizer.get_query_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Get slow queries
    print("\n🐌 Slow Queries:")
    slow = optimizer.get_slow_queries(limit=5)
    for q in slow:
        print(f"   {q['query_text'][:60]}... - {q['avg_time']:.3f}s avg")
    
    # Get recommendations
    print("\n💡 Index Recommendations:")
    recs = optimizer.get_index_recommendations()
    for r in recs:
        print(f"   {r['table_name']}.{r['column_names']} - {r['reason']}")
    
    print("\n✅ Query Optimizer test complete!")
