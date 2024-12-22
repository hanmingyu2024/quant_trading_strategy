"""
密码重置服务模块

该模块提供密码重置相关的功能:
- 生成密码重置令牌
- 创建和验证重置请求
- 执行密码重置
- 管理重置令牌的有效期

主要功能:
    generate_reset_token: 生成安全的重置令牌
    create_reset_token: 创建密码重置请求
    validate_reset_token: 验证重置令牌
    reset_password: 执行密码重置
"""

from datetime import datetime, timedelta
import secrets
from typing import Optional
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.models.password_reset import PasswordReset
from backend.app.models.user import User
from backend.app.utils.mail_service import email_manager
from backend.app.utils.password_validator import password_validator
from backend.app.utils.security import get_password_hash
from backend.app.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    BusinessError
)
from backend.app.services.rate_limiter import rate_limiter
from backend.app.services.user_service import UserService

class PasswordResetService:
    """密码重置服务"""
    
    # 重置令牌有效期（小时）
    TOKEN_VALIDITY_HOURS = 24
    # 令牌长度
    TOKEN_LENGTH = 32
    
    @staticmethod
    def generate_reset_token() -> str:
        """生成重置令牌"""
        return secrets.token_urlsafe(PasswordResetService.TOKEN_LENGTH)
    
    @staticmethod
    def create_reset_token(db: Session, email: str, request: Request) -> str:
        """创建密码重置令牌"""
        # 应用速率限制
        rate_limiter.check_rate_limit(f"reset_{request.client.host}")
        
        # 查找用户
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise ResourceNotFoundError("User", f"with email {email}")

        # 生成令牌
        token = secrets.token_urlsafe(PasswordResetService.TOKEN_LENGTH)
        expires_at = datetime.utcnow() + timedelta(
            hours=PasswordResetService.TOKEN_VALIDITY_HOURS
        )

        try:
            # 创建或更新重置记录
            reset_record = db.query(PasswordReset).filter(
                PasswordReset.user_id == user.id,
                PasswordReset.used_at.is_(None)
            ).first()

            if reset_record:
                reset_record.token = token
                reset_record.expires_at = expires_at
            else:
                reset_record = PasswordReset(
                    user_id=user.id,
                    token=token,
                    expires_at=expires_at
                )
                db.add(reset_record)

            db.commit()

            # 发送重置邮件
            email_manager.send_password_reset_email_sync(
                email_to=email,
                username=user.username,
                token=token,
                expires_in=PasswordResetService.TOKEN_VALIDITY_HOURS
            )

            return token

        except Exception as e:
            db.rollback()
            raise BusinessError(
                message="Failed to create reset token",
                details={"error": str(e)}
            )
    
    @staticmethod
    def validate_reset_token(db: Session, token: str) -> Optional[PasswordReset]:
        """验证重置令牌"""
        reset = (
            db.query(PasswordReset)
            .filter(
                PasswordReset.reset_token == token,
                PasswordReset.used_at.is_(None),
                PasswordReset.expires_at > datetime.utcnow()
            )
            .first()
        )
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
            
        return reset
    
    @staticmethod
    def reset_password(
        db: Session, 
        token: str, 
        new_password: str, 
        request: Request
    ) -> User:
        """重置密码"""
        # 应用速率限制
        rate_limiter.check_rate_limit(f"confirm_{request.client.host}")
        
        # 验证新密码
        if len(new_password) < 8:
            raise ValidationError(
                message="Password is too weak",
                errors=[{
                    "field": "password",
                    "reason": "Password must be at least 8 characters long"
                }],
                field="password"
            )

        # 查找有效的重置记录
        reset_record = db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.used_at.is_(None),
            PasswordReset.expires_at > datetime.utcnow()
        ).first()

        if not reset_record:
            raise ValidationError(
                message="Invalid or expired reset token",
                errors=[{
                    "field": "token",
                    "reason": "Token is invalid or has expired"
                }],
                field="token"
            )

        try:
            # 检查密码历史
            UserService.check_password_history(db, reset_record.user.id, new_password)
            
            # 更新密码
            user = reset_record.user
            hashed_password = get_password_hash(new_password)
            user.hashed_password = hashed_password
            
            # 更新密码历史
            UserService.update_password_history(db, user.id, hashed_password)
            
            # 标记令牌为已使用
            reset_record.used_at = datetime.utcnow()

            db.commit()

            # 发送成功通知邮件
            email_manager.send_password_reset_success_email_sync(
                email_to=user.email,
                username=user.username,
                reset_time=datetime.utcnow(),
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "Unknown")
            )

            return user

        except Exception as e:
            db.rollback()
            raise BusinessError(
                message="Failed to reset password",
                details={"error": str(e)}
            )

# 创建全局实例
password_reset_service = PasswordResetService() 