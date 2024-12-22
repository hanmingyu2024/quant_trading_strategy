"""
这是一个数据库连接测试文件。
主要测试以下功能:
1. 数据库连接 - 测试能否成功连接到数据库
2. 基础查询 - 测试简单的SELECT查询
3. 错误处理 - 测试连接失败时的错误信息展示
"""

from sqlalchemy import create_engine, text
import urllib.parse
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.app.core.config import settings
from backend.app.utils.database import engine, create_tables
from backend.app.models.base import Base
from backend.app.models.user import User

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
# 对密码中的特殊字符进行 URL 编码
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")  # 将 @ 编码为 %40
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建正确的数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("尝试连接数据库...")
print(f"使用的连接URL（密码已隐藏）: mysql+pymysql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("数据库连接成功！")
        # 使用 text() 包装 SQL 语句
        result = conn.execute(text("SELECT 1"))
        print("查询测试成功！")
        print(f"查询结果: {result.fetchone()}")
except Exception as e:
    print(f"连接失败：{str(e)}")
    print("\n详细错误信息：")
    print(f"- 用户名: {DB_USER}")
    print(f"- 主机: {DB_HOST}")
    print(f"- 端口: {DB_PORT}")
    print(f"- 数据库: {DB_NAME}")

def test_database_connection():
    """测试数据库连接"""
    print("\n开始测试数据库连接...")
    
    try:
        # 1. 测试数据库连接
        print("\n1. 测试数据库连接")
        result = engine.connect()
        print("✓ 数据库连接成功")
        result.close()
        
        # 2. 创建表
        print("\n2. 创建数据库表")
        create_tables()
        print("✓ 数据库表创建成功")
        
        # 3. 验证表是否存在
        print("\n3. 验证表是否存在")
        inspector = engine.inspect()
        tables = inspector.get_table_names()
        print(f"发现的表: {tables}")
        
        print("\n数据库测试完成!")
        return True
        
    except Exception as e:
        print(f"\n数据库测试失败: {str(e)}")
        print("\n当前数据库配置:")
        print(f"数据库URL: {settings.DATABASE_URL}")
        print(f"数据库主机: {settings.DB_HOST}")
        print(f"数据库端口: {settings.DB_PORT}")
        print(f"数据库名称: {settings.DB_NAME}")
        print(f"数据库用户: {settings.DB_USER}")
        return False

if __name__ == "__main__":
    test_database_connection() 