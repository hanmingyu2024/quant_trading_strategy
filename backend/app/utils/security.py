"""
安全工具模块

该模块提供安全相关的功能:
- JWT令牌生成和验证
- 密码加密和验证
- 用户认证

主要功能:
    create_access_token: 创建访问令牌
    verify_password: 验证密码
    get_current_user: 获取当前认证用户
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.utils.database import get_db
from backend.app.utils.token_validator import token_validator
from backend.app.services.user_service import UserService
from backend.app.utils.password import get_password_hash, verify_password

# 基本配置
SECRET_KEY = "your-secret-key"  # 开发环境使用，生产环境应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 添加这个常量

# 密码处理
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 设置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """获取当前用户"""
    # 验证令牌
    payload = token_validator.verify_token(token)
    username = payload.get("sub")
    
    # 获取用户
    user = UserService.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
