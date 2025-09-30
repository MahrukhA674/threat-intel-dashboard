import redis
import json
from typing import Any, Optional, Union
from ..core.config import settings

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self._test_connection()

    def _test_connection(self) -> None:
        """Test Redis connection."""
        try:
            self.redis.ping()
        except redis.ConnectionError as e:
            raise Exception(f"Could not connect to Redis: {str(e)}")

    async def set_session(self, session_id: str, user_data: dict, expire: int = 3600) -> None:
        """Set session data with expiration time."""
        try:
            self.redis.setex(
                f"session:{session_id}",
                expire,
                json.dumps(user_data)
            )
        except Exception as e:
            raise Exception(f"Failed to set session: {str(e)}")

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        try:
            data = self.redis.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            raise Exception(f"Failed to get session: {str(e)}")

    async def delete_session(self, session_id: str) -> None:
        """Delete session data."""
        try:
            self.redis.delete(f"session:{session_id}")
        except Exception as e:
            raise Exception(f"Failed to delete session: {str(e)}")

    async def set_cache(self, key: str, value: Any, expire: int = 3600) -> None:
        """Set cache data with expiration time."""
        try:
            self.redis.setex(
                f"cache:{key}",
                expire,
                json.dumps(value)
            )
        except Exception as e:
            raise Exception(f"Failed to set cache: {str(e)}")

    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cached data."""
        try:
            data = self.redis.get(f"cache:{key}")
            return json.loads(data) if data else None
        except Exception as e:
            raise Exception(f"Failed to get cache: {str(e)}")

    async def delete_cache(self, key: str) -> None:
        """Delete cached data."""
        try:
            self.redis.delete(f"cache:{key}")
        except Exception as e:
            raise Exception(f"Failed to delete cache: {str(e)}")

    async def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        try:
            info = self.redis.info()
            return {
                "total_keys": self.redis.dbsize(),
                "memory_usage": info.get("used_memory_human", "N/A"),
                "cache_hits": info.get("keyspace_hits", 0),
                "cache_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            raise Exception(f"Failed to get cache stats: {str(e)}")

    async def clear_cache(self, pattern: str = "cache:*") -> None:
        """Clear all cached data matching pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            raise Exception(f"Failed to clear cache: {str(e)}")

# Create a global Redis client instance
redis_client = RedisClient()
