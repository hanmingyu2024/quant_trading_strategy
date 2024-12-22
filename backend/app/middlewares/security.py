from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        rate_limit_per_minute: int = 60,
        max_request_size: int = 1024 * 1024  # 1MB
    ):
        super().__init__(app)
        self.rate_limit = rate_limit_per_minute
        self.max_request_size = max_request_size
        self.request_history: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        # 检查请求大小
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if content_length > self.max_request_size:
                return Response(
                    content="Request too large",
                    status_code=413
                )

        # 速率限制
        client_ip = request.client.host
        current_time = time.time()
        
        # 清理旧的请求记录
        if client_ip in self.request_history:
            self.request_history[client_ip] = [
                t for t in self.request_history[client_ip]
                if t > current_time - 60
            ]
        else:
            self.request_history[client_ip] = []

        # 检查请求频率
        if len(self.request_history[client_ip]) >= self.rate_limit:
            return Response(
                content="Too many requests",
                status_code=429
            )

        # 记录本次请求
        self.request_history[client_ip].append(current_time)

        # 添加安全头
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response 