"""
OAuth2认证模块

该模块提供OAuth2认证相关功能:
- 定义OAuth2 scheme用于令牌认证
"""

from fastapi.security import OAuth2PasswordBearer

# 创建 OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") 