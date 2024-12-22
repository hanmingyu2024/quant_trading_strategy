"""
用户服务模块

该模块提供用户管理相关的功能:
- 用户密码历史管理
- 密码有效期管理 
- 用户信息更新

主要类:
    UserService: 用户服务类,提供用户管理相关的核心业务逻辑
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from backend.app.models.user import User
from backend.app.models.password_history import PasswordHistory
from backend.app.schemas.user import UserCreate, UserUpdate, UserResponse
from backend.app.utils.password import get_password_hash, verify_password
from backend.app.utils.rate_limiter import rate_limiter
from backend.app.utils.password_validator import password_validator
from backend.app.utils.password_expiry import password_expiry_manager
from backend.app.exceptions import (
    ResourceNotFoundError,
    DuplicateResourceError,
    ValidationError,
    OperationNotAllowedError,
    BusinessError
)
from backend.app.utils.cache_decorators import cached
from backend.app.services.cache_service import cache_service


class UserService:
    # 密码历史检查的配置
    PASSWORD_HISTORY_LIMIT = 5  # 检查最近5个密码
    PASSWORD_MIN_AGE_DAYS = 1   # 密码最短使用期限（天）

    @staticmethod
    def check_password_history(db: Session, user_id: int, new_password: str) -> bool:
        """检查密码是否最近使用过"""
        # 获取最近的5个密码
        recent_passwords = db.query(PasswordHistory)\
            .filter(PasswordHistory.user_id == user_id)\
            .order_by(PasswordHistory.created_at.desc())\
            .limit(5)\
            .all()

        # 检查新密码是否与历史密码相同
        new_hash = get_password_hash(new_password)
        for history in recent_passwords:
            if verify_password(new_password, history.hashed_password):
                raise ValidationError(
                    message="Password has been used recently",
                    errors=[{
                        "field": "password",
                        "reason": "Please choose a password you haven't used recently"
                    }]
                )

        return True

    @staticmethod
    def add_to_password_history(db: Session, user_id: int, hashed_password: str):
        """
        添加密码到历史记录
        """
        password_history = PasswordHistory(
            user_id=user_id,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )
        db.add(password_history)
        db.commit()

    @staticmethod
    def check_password_age(db: Session, user_id: int) -> bool:
        """
        检查密码是否满足最短使用期限
        """
        latest_password = (
            db.query(PasswordHistory)
            .filter(PasswordHistory.user_id == user_id)
            .order_by(desc(PasswordHistory.created_at))
            .first()
        )
        
        if latest_password:
            min_age = timedelta(days=UserService.PASSWORD_MIN_AGE_DAYS)
            if datetime.utcnow() - latest_password.created_at < min_age:
                return False
        return True

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        创建新用户
        """
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == user_data.username).first():
            raise DuplicateResourceError("User", user_data.username)
            
        # 检查邮箱是否已存在
        if db.query(User).filter(User.email == user_data.email).first():
            raise DuplicateResourceError("Email", user_data.email)
            
        # 验证密码强度
        if len(user_data.password) < 8:
            raise ValidationError(
                message="Password is too weak",
                errors=[{
                    "field": "password",
                    "reason": "Password must be at least 8 characters long"
                }],
                field="password"
            )

        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        now = datetime.utcnow()
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            password_last_update=now,
            password_expires_at=password_expiry_manager.calculate_expiry_date(now)
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # 添加到密码历史
            UserService.add_to_password_history(db, db_user.id, hashed_password)
            
            return db_user
        except Exception as e:
            db.rollback()
            raise BusinessError(
                message="Failed to create user",
                details={"error": str(e)}
            )

    @cached(expire=300, key_prefix="user")
    async def get_user(self, user_id: int) -> Optional[User]:
        """获取用户信息(带缓存)"""
        return await self.db.query(User).filter(User.id == user_id).first()
        
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ResourceNotFoundError(f"User {username} not found")
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        通过邮箱获取用户
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        获取用户列表
        """
        return db.query(User).offset(skip).limit(limit).all()

    async def update_user(self, user_id: int, user_data: dict) -> User:
        """更新用户信息"""
        user = await self.db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            await self.db.commit()
            
            # 删除用户缓存
            await cache_service.delete(f"user:get_user:{user_id}:{{}}")
            
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        删除用户
        """
        user = UserService.get_user(db, user_id)
        
        try:
            db.delete(user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise BusinessError(
                message="Failed to delete user",
                details={"error": str(e)}
            )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        用户认证
        """
        try:
            # 检查登录频率限制
            rate_limiter.check_rate_limit(username)
            
            # 获取用户
            user = UserService.get_user_by_username(db, username)
            if not user:
                return None
                
            # 验证密码
            if not verify_password(password, user.hashed_password):
                return None
                
            # 登录成功，重置尝试次数
            rate_limiter.reset_attempts(username)
            return user
            
        except HTTPException as e:
            # 重新抛出频率限制异常
            if e.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                raise
            return None

    @staticmethod
    def update_user_password(db: Session, user_id: int, new_password: str) -> User:
        """更新用户密码"""
        # 验证密码强度
        is_valid, errors = password_validator.validate(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "新密码不符合安全要求", "errors": errors}
            )

        # 检查密码最短使用期限
        if not UserService.check_password_age(db, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"密码修改过于频繁，请等待{UserService.PASSWORD_MIN_AGE_DAYS}天后再试"
            )

        # 检查密码历史
        if not UserService.check_password_history(db, user_id, new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"新密码不能与历史密码相同"
            )

        # 更新用户密码
        db_user = UserService.get_user(db, user_id)
        now = datetime.utcnow()
        db_user.hashed_password = get_password_hash(new_password)
        db_user.password_last_update = now
        db_user.password_expires_at = password_expiry_manager.calculate_expiry_date(now)
        db_user.force_password_change = False
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def check_password_status(user: User) -> Optional[str]:
        """检查密码状态"""
        if user.force_password_change:
            return "您需要更改密码才能继续使用系统"
            
        return password_expiry_manager.check_password_expiry(user)

    @staticmethod
    def update_password_history(db: Session, user_id: int, hashed_password: str):
        """更新密码历史"""
        history = PasswordHistory(
            user_id=user_id,
            hashed_password=hashed_password
        )
        db.add(history)
        db.commit()
