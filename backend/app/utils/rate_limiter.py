"""
登录频率限制工具模块

该模块提供登录频率限制相关的功能:
- 登录尝试次数限制
- 时间窗口限制
- 尝试次数重置

主要类:
    RateLimiter: 频率限制器类,提供登录频率限制相关的核心逻辑
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import HTTPException, status

class RateLimiter:
    """
    登录频率限制器
    """
    def __init__(self):
        # 存储用户登录尝试记录 {username: (attempts, first_attempt_time)}
        self._attempts: Dict[str, Tuple[int, datetime]] = {}
        # 最大尝试次数
        self.MAX_ATTEMPTS = 5
        # 重置时间窗口（分钟）
        self.WINDOW_MINUTES = 15

    def check_rate_limit(self, username: str) -> None:
        """
        检查用户是否超过登录尝试限制
        """
        current_time = datetime.now()
        
        if username in self._attempts:
            attempts, first_attempt_time = self._attempts[username]
            
            # 如果超过时间窗口，重置计数
            if current_time - first_attempt_time > timedelta(minutes=self.WINDOW_MINUTES):
                self._attempts[username] = (1, current_time)
                return
            
            # 如果在时间窗口内超过最大尝试次数
            if attempts >= self.MAX_ATTEMPTS:
                time_remaining = (first_attempt_time + timedelta(minutes=self.WINDOW_MINUTES) - current_time)
                minutes_remaining = int(time_remaining.total_seconds() / 60) + 1
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many login attempts. Please try again in {minutes_remaining} minutes."
                )
            
            # 增加尝试次数
            self._attempts[username] = (attempts + 1, first_attempt_time)
        else:
            # 第一次尝试
            self._attempts[username] = (1, current_time)

    def reset_attempts(self, username: str) -> None:
        """
        重置用户的登录尝试记录（登录成功时调用）
        """
        if username in self._attempts:
            del self._attempts[username]

# 创建全局实例
rate_limiter = RateLimiter() 