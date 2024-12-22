"""
交易路由模块

该模块提供交易相关的API路由,主要功能:
- 创建新的交易记录
- 查询用户的交易历史
- 获取特定交易的详细信息
- 关闭/更新交易状态
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.trade import Trade, TradeCreate, TradeUpdate
from backend.app.services.trade_service import TradeService
from backend.app.utils.database import get_db
from backend.app.utils.security import get_current_user

router = APIRouter()

@router.post("/trades/", response_model=Trade)
def create_trade(
    trade: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新交易"""
    return TradeService.create_trade(db=db, trade=trade, user_id=current_user.id)

@router.get("/trades/", response_model=List[Trade])
def read_trades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的所有交易"""
    trades = TradeService.get_trades(db, user_id=current_user.id, skip=skip, limit=limit)
    return trades

@router.get("/trades/{trade_id}", response_model=Trade)
def read_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取特定交易详情"""
    trade = TradeService.get_trade(db, trade_id=trade_id, user_id=current_user.id)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@router.put("/trades/{trade_id}/close", response_model=Trade)
def close_trade(
    trade_id: int,
    close_data: TradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """关闭交易"""
    return TradeService.close_trade(
        db=db,
        trade_id=trade_id,
        user_id=current_user.id,
        close_data=close_data
    )
