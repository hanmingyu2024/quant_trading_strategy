from typing import Any, Dict, Optional
from fastapi import HTTPException, status, Request
import logging
import traceback
from datetime import datetime
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "message": self.message,
                "code": self.code,
                "details": self.details
            }
        }

def handle_error(error: Exception) -> Dict[str, Any]:
    """统一错误处理"""
    if isinstance(error, AppError):
        logger.error(f"Application error: {error.message}", exc_info=error)
        return error.to_dict()
    
    elif isinstance(error, HTTPException):
        logger.error(f"HTTP error: {error.detail}", exc_info=error)
        return {
            "error": {
                "message": error.detail,
                "code": error.status_code,
                "details": {}
            }
        }
    
    else:
        logger.error("Unexpected error", exc_info=error)
        return {
            "error": {
                "message": "Internal server error",
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "details": {
                    "type": type(error).__name__,
                    "trace": traceback.format_exc() if logger.level <= logging.DEBUG else None
                }
            }
        } 

def log_error(error: Exception, request: Request = None):
    """记录错误信息"""
    
    # 获取错误详情
    error_detail = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    
    # 如果有请求信息，添加请求详情
    if request:
        error_detail.update({
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "headers": dict(request.headers)
        })
    
    # 根据错误类型使用不同的日志级别
    if isinstance(error, Exception):
        logger.error(
            f"Error occurred: {error_detail['error_type']} - {error_detail['error_message']}",
            extra=error_detail
        )
    else:
        logger.exception(
            f"Unexpected error: {error_detail['error_type']} - {error_detail['error_message']}",
            extra=error_detail
        )
    
    # 如果在开发环境，打印完整堆栈
    if settings.DEBUG:
        print("\nError Details:")
        for key, value in error_detail.items():
            print(f"{key}: {value}")
        print("\n") 