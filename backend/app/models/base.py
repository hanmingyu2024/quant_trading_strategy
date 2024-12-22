"""
基础模型模块

该模块定义了所有模型的基类Base,以及相关的元数据配置。
主要功能:
- 提供SQLAlchemy的声明性基类
- 配置数据库表的元数据
- 定义通用的列类型导入
"""

from datetime import datetime
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime

@as_declarative()
class Base:
    """基础模型类"""
    id: Any
    __name__: str
    
    # 自动生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # 通用字段
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)