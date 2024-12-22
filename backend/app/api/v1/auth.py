"""
认证相关的API路由
主要功能:
1. 用户注册 - 新用户创建账号
2. 用户登录 - 使用用户名和密码获取访问令牌
3. 获取用户信息 - 获取当前登录用户的详细信息
"""

import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from backend.app.models.user import User as UserModel
from backend.app.schemas.user import Token, UserCreate, UserResponse, UserInDB
from backend.app.utils.database import get_db
from backend.app.utils.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password
)
from backend.app.services.user_service import UserService
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserResponse
from backend.app.services.auth_service import AuthService
from backend.app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["认证"],
    responses={
        401: {
            "description": "认证失败",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        500: {
            "description": "服务器错误",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            }
        }
    }
)

class LoginData(BaseModel):
    """登录数据模型"""
    username: str
    password: str

@router.post("/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新用户，需要提供用户名、邮箱和密码",
    responses={
        201: {
            "description": "注册成功",
            "content": {
                "application/json": {
                    "example": {"status": "success", "detail": "User registered successfully"}
                }
            }
        },
        400: {
            "description": "注册失败",
            "content": {
                "application/json": {
                    "example": {"status": "error", "detail": "Username already registered"}
                }
            }
        }
    }
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # 创建新用户
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=AuthService.get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }

@router.post("/token",
    response_model=UserResponse,
    summary="用户登录",
    description="使用用户名和密码登录，返回访问令牌",
    responses={
        200: {
            "description": "登录成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "登录失败",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            }
        }
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "is_admin": user.is_admin
    }

@router.get("/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="获取已登录用户的详细信息",
    responses={
        200: {
            "description": "成功获取用户信息",
            "content": {
                "application/json": {
                    "example": {
                        "username": "testuser",
                        "email": "test@example.com",
                        "id": 1
                    }
                }
            }
        }
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    需要在请求头中提供有效的JWT令牌
    """
    return current_user
