"""
缓存服务模块
提供统一的缓存接口和管理
"""
from typing import Any, Optional, Union
import json
from datetime import timedelta
import redis
from backend.app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
            
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置缓存值"""
        try:
            serialized = json.dumps(value)
            return self.redis.set(key, serialized, ex=expire)
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
            
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False

# 创建全局实例
cache_service = CacheService() 