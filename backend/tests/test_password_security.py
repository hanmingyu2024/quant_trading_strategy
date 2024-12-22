"""
密码安全功能测试模块

该模块测试系统的密码安全相关功能:
- 密码强度验证
- 密码历史记录
- 密码重复使用限制

主要测试:
    - 密码复杂度要求验证
    - 密码历史记录保存
    - 防止重复使用历史密码
    - 密码更新频率限制
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.models.user import User
from backend.app.models.password_history import PasswordHistory
from backend.app.schemas.user import UserCreate
from backend.app.services.user_service import UserService
from backend.app.utils.password_validator import password_validator

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
        password="Test@123456"  # 符合密码策略的密码
    )
    return UserService.create_user(test_db, user_data)

def test_password_validator_success():
    """测试有效的密码"""
    valid_password = "Test@123456"
    is_valid, errors = password_validator.validate_password(valid_password)
    assert is_valid
    assert len(errors) == 0

def test_password_validator_weak_password():
    """测试弱密码"""
    weak_passwords = [
        "short",  # 太短
        "nouppercase@123",  # 没有大写字母
        "NOLOWERCASE@123",  # 没有小写字母
        "NoSpecial123",  # 没有特殊字符
        "No@Numbers",  # 没有数字
        "Password@123",  # 包含常见模式
    ]
    
    for password in weak_passwords:
        is_valid, errors = password_validator.validate_password(password)
        assert not is_valid
        assert len(errors) > 0

def test_create_user_with_weak_password(test_db):
    """测试使用弱密码创建用户"""
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="weak"  # 弱密码
    )
    
    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(test_db, user_data)
    assert exc_info.value.status_code == 400
    assert "密码不符合安全要求" in str(exc_info.value.detail)

def test_password_history(test_db, test_user):
    """测试密码历史功能"""
    # 尝试更新为相同的密码
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_user_password(test_db, test_user.id, "Test@123456")
    assert "不能与最近" in str(exc_info.value.detail)

def test_password_age_limit(test_db, test_user):
    """测试密码最短使用期限"""
    # 尝试快速更新密码
    new_password = "NewTest@123456"
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_user_password(test_db, test_user.id, new_password)
    assert "密码修改过于频繁" in str(exc_info.value.detail)

def test_password_update_success(test_db, test_user):
    """测试成功更新密码"""
    # 模拟等待密码最短使用期限
    latest_password = (
        test_db.query(PasswordHistory)
        .filter(PasswordHistory.user_id == test_user.id)
        .first()
    )
    latest_password.created_at = datetime.utcnow() - timedelta(days=2)
    test_db.commit()

    # 更新密码
    new_password = "NewTest@123456"
    updated_user = UserService.update_user_password(test_db, test_user.id, new_password)
    assert updated_user is not None

    # 验证密码历史被记录
    password_history = (
        test_db.query(PasswordHistory)
        .filter(PasswordHistory.user_id == test_user.id)
        .all()
    )
    assert len(password_history) == 2  # 原始密码 + 新密码

def test_multiple_password_updates(test_db, test_user):
    """测试多次密码更新"""
    # 模拟多次密码更新
    passwords = [
        "Test@123456",  # 原始密码
        "NewTest@123456",
        "AnotherTest@123456",
        "DifferentTest@123456",
        "FinalTest@123456"
    ]
    
    # 模拟时间流逝
    for i, password in enumerate(passwords[1:]):
        # 设置上一次密码更新时间
        latest_password = (
            test_db.query(PasswordHistory)
            .filter(PasswordHistory.user_id == test_user.id)
            .first()
        )
        latest_password.created_at = datetime.utcnow() - timedelta(days=2)
        test_db.commit()
        
        # 更新密码
        UserService.update_user_password(test_db, test_user.id, password)
    
    # 尝试使用历史密码
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_user_password(test_db, test_user.id, passwords[0])
    assert "不能与最近" in str(exc_info.value.detail)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 