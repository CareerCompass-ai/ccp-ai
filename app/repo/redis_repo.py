import logging
import traceback
from typing import Optional
import redis
from redis.exceptions import RedisError
import constant.config as constant
from pkg.logging import logger

class RedisRepository:
    def __init__(self):
        try:
            logger.info("Connecting to Redis with redis_url: %s", constant.REDIS_URL)
            self.redis = redis.from_url(constant.REDIS_URL)
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get_client(self) -> redis.Redis:
        return self.redis

    def get(self, key: str) -> Optional[str]:
        try:
            cached_value = self.redis.get(key)
            if cached_value:
                return cached_value.decode('utf-8')  # Decode from bytes to str
            return ""
        except RedisError as e:
            logger.error(f"Failed to get key:{key} with error: {traceback.format_exc()}")
            return ""

    def set(self, key: str, value: str, expire: Optional[int] = None):
        try:
            value_bytes = value.encode('utf-8')  # Encode str to bytes
            if expire:
                self.redis.setex(key, expire, value_bytes)
            else:
                self.redis.set(key, value_bytes)
        except RedisError as e:
            logger.error(f"Failed to set key:{key} with error: {traceback.format_exc()}")

    def delete(self, key: str):
        try:
            self.redis.delete(key)
        except RedisError as e:
            logger.error(f"Failed to delete key:{key} with error: {traceback.format_exc()}")

    def exists(self, key: str) -> bool:
        try:
            return self.redis.exists(key)
        except RedisError as e:
            logger.error(f"Failed to check existence of key:{key} with error: {traceback.format_exc()}")