"""
交易模型模块

该模块定义了用户交易记录的数据模型,主要功能:
- 记录交易的基本信息(股票代码、数量、价格等)
- 存储交易类型(买入/卖出)
- 记录交易创建时间
- 与用户模型建立关联关系
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from backend.app.models.base import Base

class TradeType(enum.Enum):
    """交易类型枚举"""
    BUY = "BUY"
    SELL = "SELL"

class TradeStatus(enum.Enum):
    """交易状态枚举"""
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class Trade(Base):
    """交易模型"""
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategy.id"))
    
    # 交易信息
    symbol = Column(String(20), nullable=False, index=True)
    trade_type = Column(Enum(TradeType), nullable=False)
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    # 执行信息
    executed_price = Column(Float)
    executed_quantity = Column(Float)
    executed_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # 性能指标
    profit_loss = Column(Float)
    commission = Column(Float, default=0.0)
    swap = Column(Float, default=0.0)
    
    # 其他信息
    notes = Column(String(500))
    
    # 关系
    user = relationship("User", back_populates="trades")
    account = relationship("Account", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")

    def __repr__(self):
        return f"<Trade {self.symbol} {self.trade_type.value} {self.quantity}>"