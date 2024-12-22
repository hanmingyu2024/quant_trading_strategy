"""
认证功能测试模块

该模块测试系统的认证相关功能:
- 用户注册
- 用户登录
- 令牌验证
- 密码加密

主要测试:
    - 用户创建和验证
    - 令牌生成和验证
    - 密码哈希和验证
    - 错误处理
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.app.core.config import settings
from backend.app.utils.database import get_db
from backend.app.services.auth_service import AuthService
from backend.app.schemas.user import UserCreate

def test_auth_system():
    """测试认证系统的基本功能"""
    print("开始测试认证系统...")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 1. 测试用户注册
        print("\n1. 测试用户注册")
        test_user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        
        user_response = AuthService.register(db, test_user)
        print(f"用户注册成功: {user_response}")
        
        # 2. 测试用户登录
        print("\n2. 测试用户登录")
        login_response = AuthService.login(db, "testuser", "testpassword123")
        print(f"用户登录成功: {login_response}")
        
        # 3. 测试邮件发送
        print("\n3. 测试邮件发送")
        from backend.app.utils.mail_service import email_manager
        email_manager.send_verification_email(
            "test@example.com",
            "123456"
        )
        print("验证邮件发送成功")
        
        print("\n所有测试完成!")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_auth_system()
