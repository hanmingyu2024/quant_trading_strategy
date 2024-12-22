"""
密码过期管理模块

该模块提供密码过期相关的功能:
- 计算密码过期日期
- 检查密码是否过期
- 获取即将过期的用户列表
- 发送密码过期提醒

主要类:
    PasswordExpiryManager: 密码过期管理器类
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.user import User

class PasswordExpiryManager:
    """密码过期管理器"""
    
    # 密码有效期（天）
    PASSWORD_VALIDITY_DAYS = 90
    # 过期提醒提前天数
    EXPIRY_WARNING_DAYS = [30, 15, 7, 3, 1]
    
    @staticmethod
    def calculate_expiry_date(from_date: datetime) -> datetime:
        """计算密码过期日期"""
        return from_date + timedelta(days=PasswordExpiryManager.PASSWORD_VALIDITY_DAYS)
    
    @staticmethod
    def check_password_expiry(user: User) -> Optional[str]:
        """
        检查密码是否过期或即将过期
        返回提醒消息或None
        """
        if not user.password_expires_at:
            return None
            
        now = datetime.utcnow()
        
        # 检查是否已过期
        if now >= user.password_expires_at:
            return "您的密码已过期，请立即更新密码"
            
        # 检查是否需要提醒
        days_until_expiry = (user.password_expires_at - now).days
        
        for warning_day in PasswordExpiryManager.EXPIRY_WARNING_DAYS:
            if days_until_expiry <= warning_day:
                return f"您的密码将在{days_until_expiry}天后过期，请及时更新"
                
        return None
    
    @staticmethod
    def get_users_with_expiring_passwords(db: Session, days: int) -> List[User]:
        """获取密码即将过期的用户列表"""
        expiry_date = datetime.utcnow() + timedelta(days=days)
        return (
            db.query(User)
            .filter(User.password_expires_at <= expiry_date)
            .filter(User.password_expires_at > datetime.utcnow())
            .all()
        )
    
    @staticmethod
    def force_password_change(db: Session, user_id: int) -> None:
        """强制用户在下次登录时更改密码"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.force_password_change = True
            db.commit()

# 创建全局实例
password_expiry_manager = PasswordExpiryManager() 