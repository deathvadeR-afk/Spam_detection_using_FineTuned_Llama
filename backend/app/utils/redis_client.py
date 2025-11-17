import redis
import json
import logging
from app.core.config import settings
from typing import Optional, Any

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self._connect()
    
    def _connect(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            self.connected = True
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.connected = False
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a key-value pair in Redis with expiration"""
        if not self.connected or not self.client:
            return False
            
        try:
            serialized_value = json.dumps(value)
            result = self.client.setex(key, expire, serialized_value)
            return result
        except Exception as e:
            logger.error(f"Failed to set key in Redis: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis by key"""
        if not self.connected or not self.client:
            return None
            
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to get key from Redis: {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        if not self.connected or not self.client:
            return False
            
        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete key from Redis: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        if not self.connected or not self.client:
            return False
            
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check key existence in Redis: {str(e)}")
            return False

# Create a singleton instance
redis_client = RedisClient()