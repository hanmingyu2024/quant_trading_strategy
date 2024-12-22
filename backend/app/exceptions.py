from typing import Any, Dict, List, Optional

class BaseError(Exception):
    """基础异常类"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class AuthenticationError(BaseError):
    """认证错误"""
    pass

class AuthorizationError(BaseError):
    """授权错误"""
    pass

class ValidationError(BaseError):
    """验证错误"""
    def __init__(
        self, 
        message: str, 
        errors: List[Dict[str, str]], 
        field: Optional[str] = None
    ):
        super().__init__(message, {"errors": errors, "field": field})

class DuplicateResourceError(BaseError):
    """资源重复错误"""
    def __init__(self, resource_type: str, value: str):
        super().__init__(
            f"{resource_type} already exists: {value}",
            {"resource_type": resource_type, "value": value}
        )

class BusinessError(BaseError):
    """业务逻辑错误"""
    pass 