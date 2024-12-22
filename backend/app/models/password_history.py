"""
密码历史记录模块

该模块用于记录用户密码的历史变更记录,主要功能:
- 存储用户历史密码的哈希值
- 记录密码变更时间
- 与用户模型建立关联关系
- 用于防止用户重复使用最近使用过的密码
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.models.base import Base

class PasswordHistory(Base):
    """密码历史记录"""
    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="password_history") 