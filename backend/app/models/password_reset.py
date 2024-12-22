"""
密码重置模块

该模块用于管理用户密码重置功能,主要功能:
- 存储密码重置令牌
- 记录重置请求的创建和过期时间
- 跟踪令牌的使用状态
- 与用户模型建立关联关系
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.models.base import Base

class PasswordReset(Base):
    """密码重置记录"""
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reset_token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="password_resets") 