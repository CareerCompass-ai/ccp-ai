import logging
import traceback
from typing import Optional
import redis
import redis.connection
from redis.exceptions import RedisError
import constant.config as constant
from pkg.logging import logger

class RedisRepository:
    def __init__(self):
        try:
            logger.info("Connecting to Redis with redis_url: %s", constant.REDIS_URL)
            self.redis = redis.from_url(constant.REDIS_URL)
            logger.info("Connected to Redis")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get(self, key: str) -> Optional[str]:
        try:
            cached_value = self.redis.get(key)
            if cached_value:
                return cached_value.decode('utf-8')  # Decode from bytes to str
            return ""
        except RedisError as e:
            logger.error(f"[get] Failed to get key:{key} with traceback: {traceback.format_exc()}, with error: {e}")
            return ""

    def set(self, key: str, value: str, expire: Optional[int] = None):
        try:
            value_bytes = value.encode('utf-8')  # Encode str to bytes
            if expire:
                self.redis.setex(key, expire, value_bytes)
            else:
                self.redis.set(key, value_bytes)
        except RedisError as e:
            logger.error(f"[set] Failed to set key:{key} with with traceback: {traceback.format_exc()}, with error: {e}")

    def delete(self, key: str):
        try:
            self.redis.delete(key)
        except RedisError as e:
            logger.error(f"[delete] Failed to delete key:{key} with error: {traceback.format_exc()}")

    def exists(self, key: str) -> bool:
        try:
            return self.redis.exists(key)
        except RedisError as e:
            logger.error(f"[exists] Failed to check existence of key:{key} with error: {traceback.format_exc()}")

    def scan(self, pattern):
        try:
            cursor = '0'
            matched_keys = []

            while cursor != 0:
                cursor, keys = self.redis.scan(cursor=cursor, match=pattern)
                matched_keys.extend(keys)

            return matched_keys
        except RedisError as e:
            logger.error(f"[scan] Failed to scan with pattern:{pattern} with error: {traceback.format_exc()}")

    def smembers(self, pattern: str) -> list[str]:
        try:
            keys = self.redis.smembers(pattern)
            str_list = [x.decode('utf-8') for x in keys]
            return str_list
        except RedisError as e:
            logger.error(f"[smembers] Failed to smembers with pattern:{pattern} with error: {traceback.format_exc()}")

    def sadd(self, pattern: str, value: str):
        try:
            self.redis.sadd(pattern, value)
        except RedisError as e:
            logger.error(f"[sadd] Failed to sadd with pattern:{pattern} with error: {traceback.format_exc()}")