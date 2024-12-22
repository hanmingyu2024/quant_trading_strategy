"""
认证服务模块

该模块提供用户认证相关的功能:
- 用户认证
- 用户创建
- Token生成

主要函数:
    authenticate_user: 验证用户凭据
    create_user: 创建新用户
    create_user_token: 生成用户访问令牌
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserResponse
from backend.app.utils.security import (create_access_token, get_password_hash,
                                        verify_password)
from backend.app.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    DuplicateResourceError,
    BusinessError,
    ResourceNotFoundError,
    OperationNotAllowedError
)
from backend.app.utils.database import get_db
from backend.app.utils.oauth2 import oauth2_scheme
from backend.app.utils.mail_service import email_manager
from backend.app.utils.password_validator import validate_password
from backend.app.services.user_service import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_token(user: User):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.REFRESH_SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    async def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """用户认证"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
            
        if not AuthService.verify_password(password, user.hashed_password):
            # 更新失败登录次数
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.is_active = False
                await email_manager.send_account_locked_email(user.email)
            db.commit()
            return None
            
        # 登录成功，重置失败次数
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.commit()
        return user

    @staticmethod
    async def register_user(db: Session, user_data: UserCreate) -> User:
        """用户注册"""
        # 验证密码强度
        validate_password(user_data.password)
        
        # 检查邮箱是否已存在
        if db.query(User).filter(User.email == user_data.email).first():
            raise ValidationError(
                message="Email already registered",
                errors=[{"field": "email", "message": "Email is already in use"}]
            )
        
        # 创建新用户
        hashed_password = AuthService.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # 发送欢迎邮件
            await email_manager.send_welcome_email(db_user.email)
            
            return db_user
            
        except Exception as e:
            db.rollback()
            raise ValidationError(
                message="Failed to register user",
                errors=[{"field": "database", "message": str(e)}]
            )

    @staticmethod
    def create_tokens(user: User) -> Dict[str, str]:
        """创建访问令牌和刷新令牌"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def register(db: Session, user_data: UserCreate) -> UserResponse:
        """用户注册"""
        # 验证用户名
        if len(user_data.username) < 3:
            raise ValidationError(
                message="Username is too short",
                errors=[{
                    "field": "username",
                    "reason": "Username must be at least 3 characters long"
                }],
                field="username"
            )

        # 验证密码
        if len(user_data.password) < 8:
            raise ValidationError(
                message="Password is too weak",
                errors=[{
                    "field": "password",
                    "reason": "Password must be at least 8 characters long"
                }],
                field="password"
            )

        # 检查用户名是否已存在
        if db.query(User).filter(User.username == user_data.username).first():
            raise DuplicateResourceError("Username", user_data.username)

        # 检查邮箱是否已存在
        if db.query(User).filter(User.email == user_data.email).first():
            raise DuplicateResourceError("Email", user_data.email)

        try:
            # 创建新用户
            hashed_password = get_password_hash(user_data.password)
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return UserResponse.model_validate(db_user)
            
        except Exception as e:
            db.rollback()
            raise BusinessError(
                message="Failed to register user",
                details={"error": str(e)}
            )

    @staticmethod
    def login(db: Session, username: str, password: str) -> dict:
        """用户登录"""
        # 验证输入
        if not username or not password:
            raise ValidationError(
                message="Missing credentials",
                errors=[{
                    "field": "username/password",
                    "reason": "Both username and password are required"
                }]
            )

        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise AuthenticationError("Invalid username or password")

        # 验证密码
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid username or password")

        # 检查账户状态
        if not user.is_active:
            raise AuthenticationError("Account is disabled")

        try:
            # 创建访问令牌
            access_token = AuthService.create_access_token(
                data={"sub": user.username}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse.model_validate(user)
            }
            
        except Exception as e:
            raise BusinessError(
                message="Failed to create login session",
                details={"error": str(e)}
            )

    @staticmethod
    async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """获取当前用户"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise AuthenticationError("Invalid authentication credentials")
                
        except JWTError:
            raise AuthenticationError("Invalid authentication credentials")

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise AuthenticationError("User not found")
            
        if not user.is_active:
            raise AuthenticationError("User is inactive")
            
        return user

    @staticmethod
    def check_permission(user_id: int, resource: str):
        if not has_permission(user_id, resource):
            raise AuthorizationError(
                f"User does not have permission to access {resource}"
            )

    @staticmethod
    async def get_current_admin_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """验证管理员权限"""
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    @staticmethod
    async def authenticate_user(db: Session, username: str, password: str) -> User:
        """验证用户"""
        user = UserService.authenticate_user(db, username, password)
        if not user:
            raise AuthenticationError("用户名或密码错误")
        return user

    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> User:
        """获取当前用户"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise AuthenticationError("无效的认证令牌")
        except JWTError:
            raise AuthenticationError("无效的认证令牌")

        user = UserService.get_user_by_username(db, username)
        if user is None:
            raise ResourceNotFoundError("User", username)
            
        return user

    @staticmethod
    async def get_current_active_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """获取当前活跃用户"""
        if not current_user.is_active:
            raise OperationNotAllowedError("用户已被禁用")
        return current_user

    @staticmethod
    async def get_current_admin_user(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """获取当前管理员用户"""
        if not current_user.is_admin:
            raise OperationNotAllowedError("需要管理员权限")
        return current_user
