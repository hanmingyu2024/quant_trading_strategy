"""
日志中间件模块

该模块提供请求日志记录功能:
- 记录请求的开始和结束时间
- 生成并跟踪请求ID
- 记录请求处理时间和状态码
- 记录异常信息

主要用途:
- 请求追踪
- 性能监控
- 错误排查
- 请求响应关联
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.core.config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        request_id = request.headers.get("X-Request-ID", "")
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent", "")
        
        # 记录请求日志
        logger.info(
            f"Request started: {method} {url}",
            extra={
                "request_id": request_id,
                "method": method,
                "url": url,
                "client_ip": client_ip,
                "user_agent": user_agent
            }
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应日志
            logger.info(
                f"Request completed: {method} {url}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s"
                }
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            return response
            
        except Exception as e:
            # 记录错误日志
            logger.error(
                f"Request failed: {method} {url}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "error": str(e)
                },
                exc_info=True
            )
            raise 