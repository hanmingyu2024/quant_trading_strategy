"""
响应工具模块
用于统一处理API响应格式
"""
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse

def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200
) -> JSONResponse:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码
    
    Returns:
        JSONResponse: FastAPI JSON响应对象
    """
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )

def error_response(
    message: str = "操作失败",
    code: int = 400,
    data: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    错误响应
    
    Args:
        message: 错误消息
        code: 错误码
        data: 错误详细信息
    
    Returns:
        JSONResponse: FastAPI JSON响应对象
    """
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": data or {}
        }
    )

# 导出函数
__all__ = ["success_response", "error_response"] 