"""
密码验证工具
"""
import re
from typing import Tuple, List

class PasswordValidator:
    def __init__(self):
        self.min_length = 8
        self.max_length = 32
        
    def validate(self, password: str) -> Tuple[bool, List[str]]:
        errors = []
        if len(password) < self.min_length:
            errors.append(f"密码长度必须至少为{self.min_length}个字符")
        if not re.search(r'[A-Z]', password):
            errors.append("密码必须包含大写字母")
        if not re.search(r'[a-z]', password):
            errors.append("密码必须包含小写字母")
        if not re.search(r'\d', password):
            errors.append("密码必须包含数字")
        return len(errors) == 0, errors

# 创建实例
password_validator = PasswordValidator()

# 为了兼容性，同时提供函数形式
def validate_password(password: str) -> Tuple[bool, List[str]]:
    return password_validator.validate(password)

# 导出两种形式
__all__ = ['password_validator', 'validate_password'] 