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

    def set(self, key: str, value: str, expire: Optional[int] = None):
        try:
            if expire:
                self.redis.setex(key, expire, value)
            else:
                self.redis.set(key, value)
        except RedisError as e:
            logger.error(f"Failed to set key:{key} with error: {traceback.format_exc()}")

    def get(self, key: str) -> Optional[str]:
        try:
            return self.redis.get(key)
        except RedisError as e:
            logger.error(f"Failed to get key:{key} with error: {traceback.format_exc()}")
            return ""

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