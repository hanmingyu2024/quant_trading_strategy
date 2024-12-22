"""
这是一个数据库表结构测试文件。
主要测试以下功能:
1. 检查数据库中存在的表
2. 检查每个表的具体结构,包括:
   - 列名
   - 数据类型
   - 是否可为空
   - 键类型
"""

from sqlalchemy import create_engine, text
import urllib.parse

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def test_database_tables():
    print("开始测试数据库表结构...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. 检查表是否存在
        tables = conn.execute(text("SHOW TABLES")).fetchall()
        print("\n存在的表:")
        for table in tables:
            print(f"- {table[0]}")
            
        # 2. 检查表结构
        for table in tables:
            print(f"\n{table[0]}表的结构:")
            columns = conn.execute(text(f"DESCRIBE {table[0]}")).fetchall()
            for col in columns:
                print(f"- {col[0]}: {col[1]} (Null: {col[2]}, Key: {col[3]})")

if __name__ == "__main__":
    test_database_tables() 