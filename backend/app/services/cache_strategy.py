"""
缓存策略模块
实现不同的缓存策略
"""
from enum import Enum
from typing import Any, Optional
from datetime import timedelta

class CacheStrategy(Enum):
    NONE = "none"  # 不缓存
    SIMPLE = "simple"  # 简单缓存
    SLIDING = "sliding"  # 滑动过期
    ADAPTIVE = "adaptive"  # 自适应缓存

class CacheManager:
    def __init__(self, strategy: CacheStrategy = CacheStrategy.SIMPLE):
        self.strategy = strategy
        self.cache_service = cache_service
        
    async def get_or_set(
        self,
        key: str,
        getter_func,
        expire: Optional[timedelta] = None,
        **kwargs
    ) -> Any:
        """获取或设置缓存"""
        if self.strategy == CacheStrategy.NONE:
            return await getter_func(**kwargs)
            
        # 尝试获取缓存
        cached_value = await self.cache_service.get(key)
        if cached_value is not None:
            if self.strategy == CacheStrategy.SLIDING:
                # 刷新过期时间
                await self.cache_service.set(key, cached_value, expire)
            return cached_value
            
        # 获取新值
        value = await getter_func(**kwargs)
        
        # 设置缓存
        if self.strategy == CacheStrategy.ADAPTIVE:
            # 根据数据大小和访问频率调整过期时间
            expire = self._calculate_adaptive_expire(value)
            
        await self.cache_service.set(key, value, expire)
        return value 