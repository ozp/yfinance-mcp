"""SQLite-based cache manager with TTL support.

This module provides a thread-safe caching mechanism using SQLite
with configurable time-to-live (TTL) for different data types.
"""

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any


# Default TTL configurations (in seconds)
CACHE_TTL = {
    "current_price": 30,  # 30 seconds for real-time prices
    "historical": 3600,  # 1 hour for historical data
    "info": 86400,  # 24 hours for company info
    "financials": 86400,  # 24 hours for financial statements
    "holders": 86400,  # 24 hours for holder information
    "options": 300,  # 5 minutes for options data
    "news": 1800,  # 30 minutes for news
    "recommendations": 3600,  # 1 hour for recommendations
    "default": 3600,  # 1 hour default
}


class CacheManager:
    """Thread-safe SQLite cache manager with automatic expiration.

    This class provides a simple key-value cache with TTL support,
    backed by SQLite for persistence across sessions.

    Attributes:
        db_path: Path to the SQLite database file
    """

    def __init__(self, db_path: str | None = None):
        """Initialize the cache manager.

        Args:
            db_path: Path to the SQLite database file. If None, uses
                    ~/.mcp-yfinance/cache.db
        """
        if db_path is None:
            cache_dir = Path.home() / ".mcp-yfinance"
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(cache_dir / "cache.db")

        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        expires_at REAL NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_expires_at
                    ON cache(expires_at)
                    """
                )
                conn.commit()
            finally:
                conn.close()

    def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache.

        Args:
            key: Cache key

        Returns:
            The cached value if found and not expired, None otherwise
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute(
                    "SELECT value, expires_at FROM cache WHERE key = ?",
                    (key,),
                )
                row = cursor.fetchone()

                if row is None:
                    return None

                value_json, expires_at = row
                current_time = time.time()

                # Check if expired
                if current_time > expires_at:
                    # Delete expired entry
                    conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                    conn.commit()
                    return None

                return json.loads(value_json)
            finally:
                conn.close()

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time to live in seconds. If None, uses default TTL
        """
        if ttl is None:
            ttl = CACHE_TTL["default"]

        expires_at = time.time() + ttl
        value_json = json.dumps(value)

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache (key, value, expires_at)
                    VALUES (?, ?, ?)
                    """,
                    (key, value_json, expires_at),
                )
                conn.commit()
            finally:
                conn.close()

    def delete(self, key: str) -> None:
        """Delete a value from the cache.

        Args:
            key: Cache key to delete
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
            finally:
                conn.close()

    def clear_expired(self) -> int:
        """Remove all expired entries from the cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE expires_at < ?",
                    (current_time,),
                )
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
            finally:
                conn.close()

    def clear_all(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("DELETE FROM cache")
                conn.commit()
            finally:
                conn.close()

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics including total entries,
            expired entries, and active entries
        """
        current_time = time.time()

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                total = cursor.fetchone()[0]

                cursor = conn.execute(
                    "SELECT COUNT(*) FROM cache WHERE expires_at < ?",
                    (current_time,),
                )
                expired = cursor.fetchone()[0]

                return {
                    "total_entries": total,
                    "expired_entries": expired,
                    "active_entries": total - expired,
                }
            finally:
                conn.close()
