"""
缓存装饰器模块
提供方便的缓存注解功能
"""
from functools import wraps
from typing import Optional, Union
from datetime import timedelta

from backend.app.services.cache_service import cache_service

def cached(
    expire: Optional[Union[int, timedelta]] = 300,
    key_prefix: str = ""
):
    """
    缓存装饰器
    
    参数:
        expire: 过期时间(秒)或timedelta对象
        key_prefix: 缓存键前缀
    
    用法:
        @cached(expire=300, key_prefix="user")
        async def get_user(user_id: int):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            
            # 尝试获取缓存
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
                
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 设置缓存
            await cache_service.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

# 导出装饰器
__all__ = ["cached"] 