"""
认证中间件模块

该模块提供认证中间件功能:
- 验证请求中的认证令牌
- 处理认证失败的情况
- 将认证用户信息添加到请求状态中

主要用途:
- 请求认证拦截
- 令牌验证
- 用户身份识别
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from backend.app.utils.token_validator import validate_token
from backend.app.exceptions.auth_exception import AuthenticationError
from backend.app.core.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 检查是否是公开路径
        if self._is_public_path(request.url.path):
            return await call_next(request)
            
        # 获取认证令牌
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Authentication required",
                    "message": "No authentication token provided"
                }
            )
            
        try:
            # 验证令牌
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else ""
            user = await validate_token(token)
            
            # 将用户信息添加到请求状态
            request.state.user = user
            
            # 继续处理请求
            return await call_next(request)
            
        except AuthenticationError as e:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Authentication failed",
                    "message": str(e)
                }
            )
            
    def _is_public_path(self, path: str) -> bool:
        """检查是否是公开路径"""
        public_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/password-reset",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        return any(path.startswith(p) for p in public_paths) 