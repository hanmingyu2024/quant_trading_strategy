"""
交易模式模块

该模块定义了交易相关的数据模式(Schema),主要功能:
- 定义交易基础数据结构(TradeBase)
- 处理交易创建请求数据验证(TradeCreate) 
- 处理交易更新请求数据验证(TradeUpdate)
- 定义完整交易信息的响应模式(Trade)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TradeBase(BaseModel):
    symbol: str
    type: str
    volume: float
    open_price: float

class TradeCreate(TradeBase):
    pass

class TradeUpdate(BaseModel):
    close_price: Optional[float] = None
    close_time: Optional[datetime] = None
    profit: Optional[float] = None
    status: Optional[str] = None

class Trade(TradeBase):
    id: int
    user_id: int
    open_time: datetime
    close_price: Optional[float] = None
    close_time: Optional[datetime] = None
    profit: Optional[float] = None
    status: str

    class Config:
        from_attributes = True
