"""
业务异常模块

该模块定义了业务相关的异常类:
- BusinessError: 业务逻辑异常,用于处理业务规则验证失败等情况

主要用途:
- 处理业务规则验证失败
- 处理业务流程异常
- 提供统一的业务错误处理机制
"""

from typing import Optional, Dict, Any
from backend.app.exceptions.base_exception import BaseError

class BusinessError(BaseError):
    """业务逻辑错误"""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        if details is None:
            details = {}
        details["error_code"] = error_code
        super().__init__(message=message, details=details, status_code=400)

class ResourceNotFoundError(BusinessError):
    """资源未找到异常"""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            code=404,
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

class DuplicateResourceError(BusinessError):
    """资源重复异常"""
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            message=f"{resource_type} already exists: {identifier}",
            code=409,
            details={
                "resource_type": resource_type,
                "identifier": identifier
            }
        )

class OperationNotAllowedError(BusinessError):
    """操作不允许异常"""
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Operation not allowed: {operation}",
            code=403,
            details={
                "operation": operation,
                "reason": reason
            }
        ) 