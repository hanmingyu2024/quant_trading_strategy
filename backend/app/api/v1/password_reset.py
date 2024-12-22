"""
密码重置相关的API路由
主要功能:
1. 请求密码重置 - 用户输入邮箱获取重置链接
2. 确认密码重置 - 用户通过重置链接设置新密码
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Dict, Any

from backend.app.utils.database import get_db
from backend.app.services.password_reset_service import password_reset_service
from backend.app.exceptions import ValidationError, ResourceNotFoundError, BusinessError

router = APIRouter(
    prefix="/password",
    tags=["密码重置"],
    responses={404: {"description": "Not found"}}
)

class PasswordResetRequest(BaseModel):
    """
    密码重置请求模型
    
    Attributes:
        email: 用户注册的邮箱地址
    """
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

class PasswordResetConfirm(BaseModel):
    """
    密码重置确认模型
    
    Attributes:
        token: 重置令牌
        new_password: 新密码
    """
    token: str
    new_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123...",
                "new_password": "newSecurePassword123"
            }
        }

class PasswordResetResponse(BaseModel):
    """
    密码重置响应模型
    """
    message: str
    details: Dict[str, Any] = {}

@router.post(
    "/reset-request",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="请求密码重置",
    description="发送密码重置邮件到指定邮箱"
)
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> PasswordResetResponse:
    """
    请求密码重置
    
    - **email**: 用户注册的邮箱地址
    
    返回:
        - 发送重置邮件的确认信息
    """
    try:
        token = password_reset_service.create_reset_token(db, request.email)
        return PasswordResetResponse(
            message="Password reset email sent",
            details={"email": request.email}
        )
    except (ValidationError, ResourceNotFoundError, BusinessError) as e:
        raise HTTPException(status_code=e.code, detail=e.message)

@router.post(
    "/reset-confirm",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="确认密码重置",
    description="使用重置令牌更新密码"
)
def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> PasswordResetResponse:
    """
    确认密码重置
    
    - **token**: 从重置邮件中获取的令牌
    - **new_password**: 新的密码
    
    返回:
        - 密码重置成功的确认信息
    """
    try:
        user = password_reset_service.reset_password(
            db,
            reset_data.token,
            reset_data.new_password
        )
        return PasswordResetResponse(
            message="Password reset successful",
            details={"username": user.username}
        )
    except (ValidationError, ResourceNotFoundError, BusinessError) as e:
        raise HTTPException(status_code=e.code, detail=e.message) 