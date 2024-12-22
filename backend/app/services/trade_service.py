"""
交易服务模块

该模块提供交易相关的功能:
- 创建交易
- 查询交易
- 关闭交易

主要类:
    TradeService: 交易服务类,提供交易相关的核心业务逻辑
"""

import os
import sys

# 获取项目根目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.trade import Trade
from backend.app.models.user import User
from backend.app.schemas.trade import TradeCreate, TradeUpdate


class TradeService:
    @staticmethod
    def create_trade(db: Session, trade: TradeCreate, user_id: int) -> Trade:
        db_trade = Trade(
            user_id=user_id,
            symbol=trade.symbol,
            type=trade.type,
            volume=trade.volume,
            open_price=trade.open_price,
            status="OPEN"
        )
        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)
        return db_trade

    @staticmethod
    def get_trades(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Trade]:
        return db.query(Trade).filter(Trade.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_trade(db: Session, trade_id: int, user_id: int) -> Optional[Trade]:
        return db.query(Trade).filter(Trade.id == trade_id, Trade.user_id == user_id).first()

    @staticmethod
    def close_trade(db: Session, trade_id: int, user_id: int, close_data: TradeUpdate) -> Trade:
        trade = TradeService.get_trade(db, trade_id, user_id)
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found"
            )
        if trade.status == "CLOSED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trade already closed"
            )
        
        for key, value in close_data.dict(exclude_unset=True).items():
            setattr(trade, key, value)
        
        trade.status = "CLOSED"
        trade.close_time = datetime.utcnow()
        
        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def calculate_profit(trade: Trade) -> float:
        if trade.type == "BUY":
            return (trade.close_price - trade.open_price) * trade.volume
        else:  # SELL
            return (trade.open_price - trade.close_price) * trade.volume
