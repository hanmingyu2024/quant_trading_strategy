from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from backend.app.models.base import Base

class AccountType(enum.Enum):
    DEMO = "DEMO"
    LIVE = "LIVE"

class Account(Base):
    """交易账户模型"""
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    account_number = Column(String(50), unique=True, nullable=False)
    broker = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.DEMO)
    
    # 账户信息
    balance = Column(Float, default=0.0)
    equity = Column(Float, default=0.0)
    margin = Column(Float, default=0.0)
    free_margin = Column(Float, default=0.0)
    leverage = Column(Integer, default=100)
    
    # API配置
    api_key = Column(String(200))
    api_secret = Column(String(200))
    
    # 关系
    user = relationship("User", back_populates="accounts")
    trades = relationship("Trade", back_populates="account")

    def __repr__(self):
        return f"<Account {self.account_number}>" 