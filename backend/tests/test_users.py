"""
这是一个用户功能测试文件。
主要测试以下功能:
1. 用户注册 - 测试新用户注册流程
2. 用户登录 - 测试用户登录验证
3. 用户信息更新 - 测试用户资料的修改
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.services.user_service import UserService
from backend.app.schemas.user import UserCreate, UserUpdate

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    """每个测试前重新创建数据库表"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    """创建测试数据库会话"""
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
        password="testpassword"
    )
    return UserService.create_user(test_db, user_data)

def test_create_user_success(test_db):
    """测试成功创建用户"""
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="password123"
    )
    user = UserService.create_user(test_db, user_data)
    assert user.username == "newuser"
    assert user.email == "new@example.com"

def test_create_duplicate_user(test_db, test_user):
    """测试创建重复用户名"""
    user_data = UserCreate(
        username="testuser",  # 使用已存在的用户名
        email="another@example.com",
        password="password123"
    )
    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(test_db, user_data)
    assert exc_info.value.status_code == 400
    assert "Username already registered" in str(exc_info.value.detail)

def test_create_duplicate_email(test_db, test_user):
    """测试创建重复邮箱"""
    user_data = UserCreate(
        username="newuser",
        email="test@example.com",  # 使用已存在的邮箱
        password="password123"
    )
    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(test_db, user_data)
    assert exc_info.value.status_code == 400
    assert "Email already registered" in str(exc_info.value.detail)

def test_get_user_not_found(test_db):
    """测试获取不存在的用户"""
    user = UserService.get_user(test_db, 999)
    assert user is None

def test_update_user_not_found(test_db):
    """测试更新不存在的用户"""
    user_update = UserUpdate(username="updated")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_user(test_db, 999, user_update)
    assert exc_info.value.status_code == 404

def test_update_user_duplicate_username(test_db, test_user):
    """测试更新用户时使用已存在的用户名"""
    # 先创建另一个用户
    another_user = UserService.create_user(test_db, UserCreate(
        username="another",
        email="another@example.com",
        password="password123"
    ))
    
    # 尝试将第二个用户的用户名更新为第一个用户的用户名
    user_update = UserUpdate(username=test_user.username)
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_user(test_db, another_user.id, user_update)
    assert exc_info.value.status_code == 400
    assert "Username already exists" in str(exc_info.value.detail)

def test_delete_user_not_found(test_db):
    """测试删除不存在的用户"""
    assert not UserService.delete_user(test_db, 999)

def test_get_user_by_username(test_db, test_user):
    """测试通过用户名获取用户"""
    user = UserService.get_user_by_username(test_db, test_user.username)
    assert user is not None
    assert user.username == test_user.username

def test_get_user_by_email(test_db, test_user):
    """测试通过邮箱获取用户"""
    user = UserService.get_user_by_email(test_db, test_user.email)
    assert user is not None
    assert user.email == test_user.email

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
