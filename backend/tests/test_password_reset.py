"""
密码重置功能测试模块

该模块测试系统的密码重置相关功能:
- 重置令牌创建
- 重置令牌验证
- 密码重置执行

主要测试:
    - 重置令牌生成
    - 重置令牌有效性验证
    - 密码重置流程
    - 重置密码强度验证
    - 重置令牌重复使用限制
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models.base import Base
from backend.app.models.user import User
from backend.app.models.password_reset import PasswordReset
from backend.app.schemas.user import UserCreate
from backend.app.services.user_service import UserService
from backend.app.services.password_reset_service import password_reset_service

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

def test_create_reset_token(test_db, test_user):
    """测试创建重置令牌"""
    token = password_reset_service.create_reset_token(test_db, test_user.email)
    
    # 验证令牌创建
    assert token is not None
    
    # 验证数据库记录
    reset = test_db.query(PasswordReset).filter(
        PasswordReset.user_id == test_user.id
    ).first()
    assert reset is not None
    assert reset.reset_token == token
    assert reset.used_at is None
    assert reset.expires_at > datetime.utcnow()

def test_create_reset_token_nonexistent_email(test_db):
    """测试为不存在的邮箱创建重置令牌"""
    token = password_reset_service.create_reset_token(
        test_db, 
        "nonexistent@example.com"
    )
    assert token is None

def test_validate_reset_token(test_db, test_user):
    """测试验证重置令牌"""
    # 创建令牌
    token = password_reset_service.create_reset_token(test_db, test_user.email)
    
    # 验证令牌
    reset = password_reset_service.validate_reset_token(test_db, token)
    assert reset is not None
    assert reset.user_id == test_user.id

def test_validate_expired_token(test_db, test_user):
    """测试验证过期令牌"""
    # 创建令牌
    token = password_reset_service.create_reset_token(test_db, test_user.email)
    
    # 手动设置令牌过期
    reset = test_db.query(PasswordReset).filter(
        PasswordReset.reset_token == token
    ).first()
    reset.expires_at = datetime.utcnow() - timedelta(hours=1)
    test_db.commit()
    
    # 验证过期令牌
    with pytest.raises(HTTPException) as exc_info:
        password_reset_service.validate_reset_token(test_db, token)
    assert exc_info.value.status_code == 400
    assert "Invalid or expired" in str(exc_info.value.detail)

def test_reset_password(test_db, test_user):
    """测试重置密码"""
    # 创建令牌
    token = password_reset_service.create_reset_token(test_db, test_user.email)
    
    # 重置密码
    new_password = "NewTest@123456"
    user = password_reset_service.reset_password(test_db, token, new_password)
    
    # 验证密码已更新
    assert user.id == test_user.id
    
    # 验证令牌已使用
    reset = test_db.query(PasswordReset).filter(
        PasswordReset.reset_token == token
    ).first()
    assert reset.used_at is not None

def test_reset_password_weak_password(test_db, test_user):
    """测试使用弱密码重置"""
    token = password_reset_service.create_reset_token(test_db, test_user.email)
    
    with pytest.raises(HTTPException) as exc_info:
        password_reset_service.reset_password(test_db, token, "weak")
    assert exc_info.value.status_code == 400
    assert "密码不符合安全要求" in str(exc_info.value.detail)

def test_reset_password_used_token(test_db, test_user):
    """测试使用已使用的令牌"""
    # 创建并使用令牌
    token = password_reset_service.create_reset_token(test_db, test_user.email)
    password_reset_service.reset_password(test_db, token, "NewTest@123456")
    
    # 尝试再次使用令牌
    with pytest.raises(HTTPException) as exc_info:
        password_reset_service.reset_password(test_db, token, "AnotherTest@123456")
    assert exc_info.value.status_code == 400
    assert "Invalid or expired" in str(exc_info.value.detail)

def test_multiple_reset_requests(test_db, test_user):
    """测试多次请求重置"""
    # 第一次请求
    token1 = password_reset_service.create_reset_token(test_db, test_user.email)
    
    # 第二次请求
    token2 = password_reset_service.create_reset_token(test_db, test_user.email)
    
    # 验证是否返回相同的令牌
    assert token1 == token2
    
    # 验证数据库中只有一条记录
    resets = test_db.query(PasswordReset).filter(
        PasswordReset.user_id == test_user.id
    ).all()
    assert len(resets) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 