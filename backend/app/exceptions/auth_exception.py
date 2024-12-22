"""
认证相关异常类
"""
from typing import Optional, Dict, Any
from backend.app.exceptions.base_exception import BaseException

class AuthenticationError(BaseException):
    """
    认证错误异常
    用于处理用户认证失败的情况
    """
    def __init__(
        self,
        message: str = "认证失败",
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=401,
            data=data
        )

class AuthorizationError(BaseException):
    """
    授权错误异常
    用于处理用户权限不足的情况
    """
    def __init__(
        self,
        message: str = "权限不足",
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=403,
            data=data
        )

# 导出异常类
__all__ = ["AuthenticationError", "AuthorizationError"] 