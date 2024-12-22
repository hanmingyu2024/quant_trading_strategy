"""
密码工具模块

该模块提供密码加密和验证相关的功能:
- 密码哈希生成
- 密码验证
- 使用 bcrypt 加密算法

主要函数:
    verify_password: 验证密码是否匹配
    get_password_hash: 生成密码的哈希值
"""

from passlib.context import CryptContext

# 密码上下文配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password) 