"""Cache manager with SQLite backend and TTL support.

This module provides a thread-safe caching mechanism for Yahoo Finance data
using SQLite as the storage backend with time-to-live (TTL) functionality.
"""

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional


# Cache TTL configurations (in seconds)
CACHE_TTL = {
    "current_price": 60,  # 1 minute - real-time data
    "historical_data": 3600,  # 1 hour
    "stock_info": 86400,  # 24 hours
    "dividends": 86400,  # 24 hours
    "stock_actions": 86400,  # 24 hours
    "income_statement": 86400,  # 24 hours
    "balance_sheet": 86400,  # 24 hours
    "cashflow": 86400,  # 24 hours
    "holder_info": 3600,  # 1 hour
    "option_expiration_dates": 3600,  # 1 hour
    "option_chain": 300,  # 5 minutes - options data changes frequently
    "news": 1800,  # 30 minutes
    "recommendations": 86400,  # 24 hours
    "earning_dates": 86400,  # 24 hours
    "stock_splits": 86400,  # 24 hours
    "analyst_price_targets": 3600,  # 1 hour
    "default": 3600,  # 1 hour - fallback
}


class CacheManager:
    """Thread-safe SQLite-based cache manager with TTL support.

    This class provides caching functionality with automatic expiration
    of cached entries based on time-to-live (TTL) values.

    Attributes:
        db_path: Path to the SQLite database file.
        _lock: Threading lock for thread-safe operations.
        _conn: SQLite database connection.
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the cache manager.

        Args:
            db_path: Path to SQLite database. If None, uses default path
                    at ~/.mcp-yfinance/cache.db
        """
        if db_path is None:
            cache_dir = Path.home() / ".mcp-yfinance"
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(cache_dir / "cache.db")

        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database schema with indexes."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Create cache table with expires_at index for efficient cleanup
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)

            # Create index on expires_at for efficient expired entry queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON cache(expires_at)
            """)

            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection.

        Returns:
            SQLite database connection.
        """
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0
            )
        return self._conn

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache if it exists and hasn't expired.

        Automatically cleans up expired entries during retrieval.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value if found and valid, None otherwise.
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            current_time = time.time()

            # Retrieve entry if not expired
            cursor.execute("""
                SELECT value FROM cache
                WHERE key = ? AND expires_at > ?
            """, (key, current_time))

            result = cursor.fetchone()

            # Clean up expired entries opportunistically
            cursor.execute("""
                DELETE FROM cache WHERE expires_at <= ?
            """, (current_time,))
            conn.commit()

            if result:
                return json.loads(result[0])
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in cache with TTL.

        Args:
            key: Cache key to store under.
            value: Value to cache (must be JSON-serializable).
            ttl: Time-to-live in seconds. If None, uses default TTL.
        """
        if ttl is None:
            ttl = CACHE_TTL["default"]

        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            current_time = time.time()
            expires_at = current_time + ttl

            # Serialize value to JSON
            value_json = json.dumps(value)

            # Insert or replace cache entry
            cursor.execute("""
                INSERT OR REPLACE INTO cache
                (key, value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (key, value_json, current_time, expires_at))

            conn.commit()

    def delete(self, key: str) -> bool:
        """Delete a specific cache entry.

        Args:
            key: Cache key to delete.

        Returns:
            True if entry was deleted, False if not found.
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()

            return cursor.rowcount > 0

    def clear_expired(self) -> int:
        """Remove all expired cache entries.

        Returns:
            Number of entries deleted.
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            current_time = time.time()
            cursor.execute("""
                DELETE FROM cache WHERE expires_at <= ?
            """, (current_time,))

            deleted_count = cursor.rowcount
            conn.commit()

            return deleted_count

    def clear_all(self) -> int:
        """Remove all cache entries.

        Returns:
            Number of entries deleted.
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM cache")
            deleted_count = cursor.rowcount
            conn.commit()

            return deleted_count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache statistics including total entries,
            expired entries, valid entries, and database size.
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            current_time = time.time()

            # Total entries
            cursor.execute("SELECT COUNT(*) FROM cache")
            total_entries = cursor.fetchone()[0]

            # Expired entries
            cursor.execute("""
                SELECT COUNT(*) FROM cache WHERE expires_at <= ?
            """, (current_time,))
            expired_entries = cursor.fetchone()[0]

            # Valid entries
            valid_entries = total_entries - expired_entries

            # Database file size
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0

            return {
                "total_entries": total_entries,
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "database_size_bytes": db_size,
                "database_path": self.db_path,
            }

    def close(self) -> None:
        """Close the database connection."""
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
