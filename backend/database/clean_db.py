"""
这是一个数据库清理文件。
主要功能:
1. 清空数据库 - 删除所有表
2. 重置数据库 - 重置数据库到初始状态
3. 维护清理 - 定期清理无用数据
"""

from sqlalchemy import create_engine, text
import urllib.parse
import os

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def clean_database():
    print("开始清理数据库...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 获取所有表名
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        
        # 删除所有表
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in tables:
            print(f"删除表: {table}")
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        
        print("数据库清理完成！")

if __name__ == "__main__":
    clean_database() 