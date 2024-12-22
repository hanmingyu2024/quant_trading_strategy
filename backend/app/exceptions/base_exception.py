"""
基础异常类模块
定义系统中所有异常的基类
"""
from typing import Any, Dict, Optional

class BaseException(Exception):
    """
    基础异常类
    所有自定义异常都应继承此类
    """
    def __init__(
        self,
        message: str = "系统错误",
        code: int = 500,
        data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        将异常转换为字典格式
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }

class ValidationException(BaseException):
    """数据验证错误"""
    def __init__(
        self,
        message: str = "数据验证失败",
        errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=400,
            data={"errors": errors or {}}
        )

class DatabaseException(BaseException):
    """数据库错误"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message=message, code=500)

class ResourceNotFoundError(BaseException):
    """资源未找到错误"""
    def __init__(self, message: str = "请求的资源不存在"):
        super().__init__(message=message, code=404)

class DuplicateResourceError(BaseException):
    """资源重复错误"""
    def __init__(self, message: str = "资源已存在"):
        super().__init__(message=message, code=409)

class OperationNotAllowedError(BaseException):
    """操作不允许错误"""
    def __init__(self, message: str = "当前操作不被允许"):
        super().__init__(message=message, code=403)

class BusinessException(BaseException):
    """业务逻辑错误"""
    def __init__(self, message: str = "业务处理失败"):
        super().__init__(message=message, code=400)

# 导出所有异常类
__all__ = [
    "BaseException",
    "ValidationException",
    "DatabaseException",
    "ResourceNotFoundError",
    "DuplicateResourceError",
    "OperationNotAllowedError",
    "BusinessException"
]