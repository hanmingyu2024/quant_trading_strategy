import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.app.core.config import settings

def test_env_variables():
    """测试环境变量加载"""
    print("\n开始测试环境变量...")
    
    # 检查.env文件位置
    env_path = Path(project_root) / '.env'
    print(f"\n1. 检查.env文件")
    print(f"预期位置: {env_path}")
    print(f"文件存在: {env_path.exists()}")
    
    # 打印关键配置
    print("\n2. 当前配置:")
    print(f"数据库主机: {settings.DB_HOST}")
    print(f"数据库端口: {settings.DB_PORT}")
    print(f"数据库名称: {settings.DB_NAME}")
    print(f"数据库用户: {settings.DB_USER}")
    print(f"环境: {settings.ENVIRONMENT}")
    print(f"调试模式: {settings.DEBUG}")
    
    # 检查必要的环境变量
    print("\n3. 环境变量检查:")
    required_vars = [
        'DB_HOST', 'DB_PORT', 'DB_USER', 
        'DB_PASSWORD', 'DB_NAME', 'SECRET_KEY'
    ]
    
    for var in required_vars:
        value = getattr(settings, var, None)
        is_set = value is not None and value != ''
        print(f"{var}: {'✓ 已设置' if is_set else '✗ 未设置'}")

if __name__ == "__main__":
    test_env_variables() 