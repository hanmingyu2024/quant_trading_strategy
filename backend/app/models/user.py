"""
用户模型模块

该模块定义了系统用户的数据模型,主要功能:
- 存储用户基本信息(用户名、邮箱等)
- 管理用户密码及其安全相关属性
- 跟踪用户账户状态
- 与密码历史等其他模型建立关联关系
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    
    # 关系
    accounts = relationship("Account", back_populates="user")
    strategies = relationship("Strategy", back_populates="user")
    trades = relationship("Trade", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"