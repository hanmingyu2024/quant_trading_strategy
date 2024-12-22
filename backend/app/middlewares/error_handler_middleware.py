"""
错误处理中间件
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.exceptions.base_exception import BaseException
from backend.app.utils.response import error_response

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    错误处理中间件
    用于捕获和处理所有异常
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except BaseException as e:
            # 处理自定义异常
            return error_response(
                code=e.code,
                message=e.message,
                data=e.data
            )
            
        except Exception as e:
            # 处理其他未知异常
            return error_response(
                code=500,
                message=f"系统错误: {str(e)}",
                data={"type": type(e).__name__}
            )

# 导出中间件
__all__ = ["ErrorHandlerMiddleware"] 