from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.base import Base

class Strategy(Base):
    """交易策略模型"""
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 策略参数
    parameters = Column(JSON)  # 存储策略参数
    risk_limit = Column(Float, default=0.02)  # 风险限制
    max_positions = Column(Integer, default=5)  # 最大持仓数
    
    # 性能指标
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    # 关系
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")

    def __repr__(self):
        return f"<Strategy {self.name}>" 