"""
异常模块
导出所有自定义异常类
"""

from backend.app.exceptions.base_exception import (
    BaseException as BaseAppException,
    ValidationException as ValidationError,
    DatabaseException as DatabaseError,
    ResourceNotFoundError,
    DuplicateResourceError,
    OperationNotAllowedError,
    BusinessException as BusinessError
)

from backend.app.exceptions.auth_exception import (
    AuthenticationError,
    AuthorizationError
)

# 导出所有异常类
__all__ = [
    "BaseAppException",
    "ValidationError",
    "DatabaseError",
    "ResourceNotFoundError",
    "DuplicateResourceError",
    "OperationNotAllowedError",
    "BusinessError",
    "AuthenticationError",
    "AuthorizationError"
] 