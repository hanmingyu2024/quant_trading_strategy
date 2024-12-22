"""
数据验证异常模块

该模块定义了数据验证相关的异常类:
- ValidationError: 数据验证异常,用于处理请求参数验证失败等情况

主要用途:
- 处理请求参数验证失败
- 处理数据格式错误
- 提供统一的验证错误处理机制
"""

from typing import List, Dict, Any, Optional
from backend.app.exceptions.base_exception import BaseException

class ValidationError(BaseException):
    """验证错误"""
    def __init__(
        self,
        message: str,
        errors: List[Dict[str, str]],
        field: Optional[str] = None
    ):
        details = {
            "errors": errors,
            "field": field
        }
        super().__init__(message=message, details=details, status_code=422)

class InvalidParameterError(ValidationError):
    """参数无效错误"""
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Invalid parameter: {field}",
            errors=[{"field": field, "reason": reason}],
            field=field
        )

class MissingParameterError(ValidationError):
    """缺少参数错误"""
    def __init__(self, field: str):
        super().__init__(
            message=f"Missing required parameter: {field}",
            errors=[{"field": field, "reason": "This field is required"}],
            field=field
        )