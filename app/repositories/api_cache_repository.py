"""
API cache repository for LockIn AI.

Handles caching of external API responses (OpenFoodFacts, etc.).
"""

import hashlib
import json
from datetime import datetime, timedelta
from app.database.connection import db
from app.config import settings


class ApiCacheRepository:
    """Repository for API response caching."""
    
    def __init__(self, expiry_days: int | None = None):
        """
        Initialize cache repository.
        
        Args:
            expiry_days: Number of days before cache expires. Uses config default if None.
        """
        self.expiry_days = expiry_days or settings.cache_expiry_days
    
    def get(self, source: str, query: str) -> dict | None:
        """
        Get cached API response.
        
        Args:
            source: API source (e.g., 'openfoodfacts', 'ciqual')
            query: Query string
        
        Returns:
            Cached response as dict or None if not found/expired
        """
        cache_key = self._generate_cache_key(source, query)
        
        sql = """
            SELECT response_json, expires_at 
            FROM api_cache 
            WHERE cache_key = ?
        """
        
        row = db.fetchone(sql, (cache_key,))
        
        if not row:
            return None
        
        # Check if expired
        expires_at = datetime.fromisoformat(row['expires_at'])
        if datetime.utcnow() > expires_at:
            # Delete expired entry
            self.delete(cache_key)
            return None
        
        return json.loads(row['response_json'])
    
    def set(self, source: str, query: str, response: dict) -> None:
        """
        Cache an API response.
        
        Args:
            source: API source
            query: Query string
            response: Response data to cache
        """
        cache_key = self._generate_cache_key(source, query)
        expires_at = datetime.utcnow() + timedelta(days=self.expiry_days)
        
        sql = """
            INSERT OR REPLACE INTO api_cache (
                cache_key, source, query, response_json, expires_at
            ) VALUES (?, ?, ?, ?, ?)
        """
        
        params = (
            cache_key,
            source,
            query,
            json.dumps(response),
            expires_at.isoformat(),
        )
        
        db.execute(sql, params)
    
    def delete(self, cache_key: str) -> None:
        """
        Delete a cached entry.
        
        Args:
            cache_key: Cache key to delete
        """
        sql = "DELETE FROM api_cache WHERE cache_key = ?"
        db.execute(sql, (cache_key,))
    
    def clear_expired(self) -> int:
        """
        Clear all expired cache entries.
        
        Returns:
            Number of entries deleted
        """
        sql = "DELETE FROM api_cache WHERE expires_at < ?"
        
        with db.get_connection() as conn:
            cursor = conn.execute(sql, (datetime.utcnow().isoformat(),))
            return cursor.rowcount
    
    def clear_all(self) -> None:
        """Clear all cache entries."""
        sql = "DELETE FROM api_cache"
        db.execute(sql)
    
    def _generate_cache_key(self, source: str, query: str) -> str:
        """
        Generate a cache key from source and query.
        
        Args:
            source: API source
            query: Query string
        
        Returns:
            MD5 hash of source + query
        """
        key_string = f"{source}:{query.lower().strip()}"
        return hashlib.md5(key_string.encode()).hexdigest()


# Global repository instance
api_cache_repository = ApiCacheRepository()
