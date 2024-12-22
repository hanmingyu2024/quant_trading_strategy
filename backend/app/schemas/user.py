"""
用户模式模块

该模块定义了用户相关的数据模式(Schema),主要功能:
- 定义用户基础数据结构(UserBase)
- 处理用户创建请求数据验证(UserCreate)
- 处理用户更新请求数据验证(UserUpdate) 
- 定义用户信息的响应模式(UserResponse)
- 定义令牌相关的数据结构(Token/TokenData)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """用户创建模型"""
    password: str

class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    """用户数据库模型"""
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None
