from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import HTTPException, status

class RateLimiter:
    def __init__(self):
        self._attempts: Dict[str, list] = {}
        self._blocks: Dict[str, datetime] = {}
        
        # 配置
        self.MAX_ATTEMPTS = 5  # 最大尝试次数
        self.ATTEMPT_WINDOW = 15  # 尝试窗口(分钟)
        self.BLOCK_DURATION = 30  # 封禁时长(分钟)

    def check_rate_limit(self, key: str) -> Tuple[bool, int]:
        """
        检查是否超出速率限制
        
        Args:
            key: 限制键值(如IP或用户ID)
            
        Returns:
            (是否允许, 剩余尝试次数)
        """
        now = datetime.utcnow()
        
        # 检查是否被封禁
        if key in self._blocks:
            if now < self._blocks[key]:
                remaining = int((self._blocks[key] - now).total_seconds() / 60)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many attempts. Try again in {remaining} minutes."
                )
            else:
                del self._blocks[key]
                self._attempts[key] = []

        # 清理过期尝试记录
        window_start = now - timedelta(minutes=self.ATTEMPT_WINDOW)
        if key in self._attempts:
            self._attempts[key] = [
                attempt for attempt in self._attempts[key]
                if attempt > window_start
            ]
        else:
            self._attempts[key] = []

        # 检查尝试次数
        attempts = len(self._attempts[key])
        if attempts >= self.MAX_ATTEMPTS:
            self._blocks[key] = now + timedelta(minutes=self.BLOCK_DURATION)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many attempts. Try again in {self.BLOCK_DURATION} minutes."
            )

        # 记录本次尝试
        self._attempts[key].append(now)
        return True, self.MAX_ATTEMPTS - attempts - 1

# 创建全局实例
rate_limiter = RateLimiter() 