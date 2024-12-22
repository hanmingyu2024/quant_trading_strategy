"""
这是一个基础数据库操作的测试文件。
主要测试以下功能:
1. 用户创建 - 测试插入新用户
2. 交易创建 - 测试插入新交易记录
3. 数据查询 - 测试联表查询用户和交易信息
"""

from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def test_data_operations():
    print("开始测试数据操作...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # 1. 插入测试用户
            print("\n1. 插入测试用户...")
            result = conn.execute(text("""
                INSERT INTO users (username, email, hashed_password, created_at, updated_at)
                VALUES (:username, :email, :password, :created_at, :updated_at)
            """), {
                "username": "test_user",
                "email": "test@example.com",
                "password": "hashed_password_123",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            conn.commit()
            user_id = result.lastrowid
            print(f"用户创建成功，ID: {user_id}")

            # 2. 插入测试交易
            print("\n2. 插入测试交易...")
            result = conn.execute(text("""
                INSERT INTO trades (user_id, symbol, quantity, price, trade_type, created_at)
                VALUES (:user_id, :symbol, :quantity, :price, :trade_type, :created_at)
            """), {
                "user_id": user_id,
                "symbol": "BTCUSDT",
                "quantity": 1.5,
                "price": 50000.0,
                "trade_type": "buy",
                "created_at": datetime.now()
            })
            conn.commit()
            trade_id = result.lastrowid
            print(f"交易创建成功，ID: {trade_id}")

            # 3. 查询测试
            print("\n3. 查询用户和交易...")
            result = conn.execute(text("""
                SELECT u.username, t.symbol, t.quantity, t.price, t.trade_type
                FROM users u
                JOIN trades t ON u.id = t.user_id
                WHERE u.id = :user_id
            """), {"user_id": user_id})
            
            for row in result:
                print(f"用户: {row[0]}")
                print(f"交易: {row[1]} {row[2]} @ {row[3]} ({row[4]})")

        except Exception as e:
            print(f"错误: {str(e)}")
            conn.rollback()

if __name__ == "__main__":
    test_data_operations() 