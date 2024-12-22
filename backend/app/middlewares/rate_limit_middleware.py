"""
限流中间件模块

该模块提供请求限流功能:
- 基于客户端IP进行请求频率限制
- 支持配置最大请求数和时间窗口
- 防止API被滥用

主要用途:
- 限制API访问频率
- 防止DoS攻击
- 保护系统资源
- 确保服务质量
"""

import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# 配置日志
logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_limit: int = 100, window_size: int = 60):
        """
        初始化速率限制中间件
        
        Args:
            app: FastAPI 应用
            requests_limit: 时间窗口内允许的最大请求数
            window_size: 时间窗口大小(秒)
        """
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_size = window_size
        self.requests: Dict[str, List[datetime]] = {}
        logger.info(f"速率限制中间件已初始化: 限制={requests_limit}/每{window_size}秒")

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        try:
            client_ip = request.client.host
            now = datetime.now()

            # 清理过期的请求记录
            if client_ip in self.requests:
                self.requests[client_ip] = [
                    req_time for req_time in self.requests[client_ip]
                    if now - req_time < timedelta(seconds=self.window_size)
                ]

            # 检查请求频率
            if client_ip in self.requests and len(self.requests[client_ip]) >= self.requests_limit:
                logger.warning(f"IP {client_ip} 请求过于频繁")
                return JSONResponse(
                    status_code=429,
                    content={"error": "请求过于频繁，请稍后再试"}
                )

            # 记录新请求
            if client_ip not in self.requests:
                self.requests[client_ip] = []
            self.requests[client_ip].append(now)

            # 处理请求
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"速率限制中间件错误: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": f"内部服务器错误: {str(e)}"}
            ) 