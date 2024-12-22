"""
异常处理中间件模块

该模块提供全局异常处理中间件:
- ExceptionHandlerMiddleware: 捕获并处理系统中的各类异常,提供统一的错误响应格式

主要功能:
    - 捕获验证异常(ValidationError)
    - 捕获认证异常(AuthenticationError) 
    - 捕获授权异常(AuthorizationError)
    - 捕获业务异常(BusinessError)
    - 统一异常日志记录
    - 统一错误响应格式
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from typing import Union, Dict, Any

from backend.app.exceptions import (
    BaseAppException,
    ValidationError,
    BusinessError,
    AuthenticationError,
    AuthorizationError
)

logger = logging.getLogger(__name__)

class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Union[JSONResponse, Any]:
        try:
            return await call_next(request)
            
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=e.code,
                content=e.to_dict()
            )
            
        except AuthenticationError as e:
            logger.warning(f"Authentication error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=e.code,
                content=e.to_dict()
            )
            
        except AuthorizationError as e:
            logger.warning(f"Authorization error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=e.code,
                content=e.to_dict()
            )
            
        except BusinessError as e:
            logger.error(f"Business error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=e.code,
                content=e.to_dict()
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": "Internal server error",
                        "details": {"type": str(type(e).__name__)}
                    }
                }
            ) 