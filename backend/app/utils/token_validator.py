"""
Token验证工具
用于验证JWT令牌的有效性
"""
from typing import Optional, Dict, Any
from datetime import datetime
from jose import JWTError, jwt
from fastapi import HTTPException, status

from backend.app.core.config import settings

class TokenValidator:
    """Token验证器类"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        
    def validate(self, token: str) -> Dict[str, Any]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            Dict[str, Any]: 解码后的令牌数据
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            user_id: str = payload.get("sub")
            exp: int = payload.get("exp")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证令牌"
                )
                
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="令牌已过期"
                )
                
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌"
            )
    
    def get_user_id(self, token: str) -> str:
        """
        从令牌中获取用户ID
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            str: 用户ID
        """
        payload = self.validate(token)
        return payload.get("sub")

# 创建全局实例
token_validator = TokenValidator()

# 为了向后兼容，保留函数形式
def validate_token(token: str) -> Dict[str, Any]:
    return token_validator.validate(token)

def get_token_user_id(token: str) -> str:
    return token_validator.get_user_id(token)

# 导出所有接口
__all__ = [
    "token_validator",
    "validate_token",
    "get_token_user_id",
    "TokenValidator"
]