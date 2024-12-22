import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import pymysql
from backend.app.core.config import settings

def quick_test():
    """快速测试数据库连接"""
    print("\n开始快速数据库测试...")
    
    try:
        # 尝试直接连接
        print("\n1. 尝试连接到数据库...")
        conn = pymysql.connect(
            host=settings.DB_HOST,
            port=int(settings.DB_PORT),
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            connect_timeout=settings.DB_CONNECT_TIMEOUT
        )
        
        print("✓ 连接成功!")
        
        # 测试查询
        print("\n2. 执行测试查询...")
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"数据库版本: {version[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"现有表数量: {len(tables)}")
            if tables:
                print("表列表:")
                for table in tables:
                    print(f"  - {table[0]}")
        
        conn.close()
        print("\n✓ 测试完成!")
        
    except Exception as e:
        print(f"\n连接失败: {str(e)}")
        print("\n当前连接信息:")
        print(f"主机: {settings.DB_HOST}")
        print(f"端口: {settings.DB_PORT}")
        print(f"用户: {settings.DB_USER}")
        print(f"数据库: {settings.DB_NAME}")
        print("\n可能的问题:")
        print("1. 网络连接问题")
        print("2. 数据库凭据错误")
        print("3. 数据库未启动")
        print("4. 防火墙设置")

if __name__ == "__main__":
    quick_test() 