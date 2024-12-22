"""
密码过期功能测试模块

该模块测试系统的密码过期相关功能:
- 密码过期日期设置
- 密码过期检查
- 密码更新时间追踪

主要测试:
    - 新用户密码过期日期设置
    - 密码过期状态检查
    - 密码更新后过期日期重置
    - 密码过期提醒
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate
from backend.app.services.user_service import UserService
from backend.app.utils.password_expiry import password_expiry_manager

# 测试数据库设置
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(test_db):
    """创建测试用户"""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Test@123456"
    )
    return UserService.create_user(test_db, user_data)

def test_password_expiry_date_set(test_user):
    """测试创建用户时设置密码过期日期"""
    assert test_user.password_last_update is not None
    assert test_user.password_expires_at is not None
    assert test_user.password_expires_at > test_user.password_last_update

def test_password_expiry_warning(test_db, test_user):
    """测试密码过期警告"""
    # 设置密码即将过期
    test_user.password_expires_at = datetime.utcnow() + timedelta(days=7)
    test_db.commit()
    
    # 检查警告消息
    warning = password_expiry_manager.check_password_expiry(test_user)
    assert warning is not None
    assert "7天后过期" in warning

def test_password_expired(test_db, test_user):
    """测试密码已过期"""
    # 设置密码已过期
    test_user.password_expires_at = datetime.utcnow() - timedelta(days=1)
    test_db.commit()
    
    # 检查过期消息
    message = password_expiry_manager.check_password_expiry(test_user)
    assert message is not None
    assert "已过期" in message

def test_force_password_change(test_db, test_user):
    """测试强制密码更改"""
    # 强制更改密码
    password_expiry_manager.force_password_change(test_db, test_user.id)
    
    # 验证标记已设置
    test_db.refresh(test_user)
    assert test_user.force_password_change is True
    
    # 检查状态消息
    message = UserService.check_password_status(test_user)
    assert message is not None
    assert "需要更改密码" in message

def test_password_update_resets_expiry(test_db, test_user):
    """测试更新密码重置过期时间"""
    old_expires_at = test_user.password_expires_at
    
    # 等待一秒以确保时间戳不同
    import time
    time.sleep(1)
    
    # 更新密码
    UserService.update_user_password(test_db, test_user.id, "NewTest@123456")
    
    # 验证过期时间已更新
    test_db.refresh(test_user)
    assert test_user.password_expires_at > old_expires_at
    assert test_user.force_password_change is False

def test_get_expiring_passwords(test_db):
    """测试获取即将过期的密码列表"""
    # 创建多个用户，设置不同的过期时间
    users_data = [
        ("user1", datetime.utcnow() + timedelta(days=5)),
        ("user2", datetime.utcnow() + timedelta(days=10)),
        ("user3", datetime.utcnow() + timedelta(days=20)),
    ]
    
    for username, expires_at in users_data:
        user = User(
            username=username,
            email=f"{username}@example.com",
            hashed_password="dummy",
            password_expires_at=expires_at
        )
        test_db.add(user)
    test_db.commit()
    
    # 获取7天内过期的用户
    expiring_users = password_expiry_manager.get_users_with_expiring_passwords(test_db, 7)
    assert len(expiring_users) == 1
    assert expiring_users[0].username == "user1"

def test_password_expiry_calculation():
    """测试密码过期日期计算"""
    now = datetime.utcnow()
    expiry_date = password_expiry_manager.calculate_expiry_date(now)
    
    # 验证过期日期
    expected_days = password_expiry_manager.PASSWORD_VALIDITY_DAYS
    assert (expiry_date - now).days == expected_days

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 