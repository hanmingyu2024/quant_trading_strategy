"""
这是一个高级数据库操作的测试文件。
主要测试以下功能:
1. 错误处理 - 测试重复用户名等异常情况
2. 批量操作 - 测试批量插入交易记录
3. 事务回滚 - 测试外键约束违反时的事务回滚
"""

from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime
import time

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def test_error_handling(conn):
    print("\n=== 测试错误处理 ===")
    try:
        # 测试重复用户名
        print("\n1. 测试重复用户名...")
        conn.execute(text("""
            INSERT INTO users (username, email, hashed_password)
            VALUES (:username, :email, :password)
        """), {
            "username": "test_user",  # 已存在的用户名
            "email": "new@example.com",
            "password": "test123"
        })
        conn.commit()
        print("错误：应该抛出重复用户名异常")
    except Exception as e:
        print(f"预期的错误: {str(e)}")
        conn.rollback()

def test_batch_operations(conn):
    print("\n=== 测试批量操作 ===")
    try:
        # 批量插入交易记录
        print("\n1. 批量插入交易记录...")
        trades = [
            {"user_id": 1, "symbol": "ETHUSDT", "quantity": 2.0, "price": 3000.0, "trade_type": "buy"},
            {"user_id": 1, "symbol": "BTCUSDT", "quantity": 0.5, "price": 52000.0, "trade_type": "sell"},
            {"user_id": 1, "symbol": "DOGEUSDT", "quantity": 1000.0, "price": 0.25, "trade_type": "buy"}
        ]
        
        start_time = time.time()
        for trade in trades:
            conn.execute(text("""
                INSERT INTO trades (user_id, symbol, quantity, price, trade_type, created_at)
                VALUES (:user_id, :symbol, :quantity, :price, :trade_type, :created_at)
            """), {**trade, "created_at": datetime.now()})
        conn.commit()
        end_time = time.time()
        
        print(f"批量插入完成，耗时: {end_time - start_time:.2f}秒")
        
        # 验证插入的数据
        result = conn.execute(text("""
            SELECT COUNT(*) FROM trades WHERE user_id = 1
        """)).scalar()
        print(f"用户1的交易总数: {result}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        conn.rollback()

def test_transaction_rollback(conn):
    print("\n=== 测试事务回滚 ===")
    try:
        # 开始一个需要回滚的操作
        print("\n1. 测试事务回滚...")
        conn.execute(text("""
            INSERT INTO trades (user_id, symbol, quantity, price, trade_type, created_at)
            VALUES (:user_id, :symbol, :quantity, :price, :trade_type, :created_at)
        """), {
            "user_id": 999,  # 不存在的用户ID
            "symbol": "BTCUSDT",
            "quantity": 1.0,
            "price": 50000.0,
            "trade_type": "buy",
            "created_at": datetime.now()
        })
        conn.commit()
        print("错误：应该抛出外键约束异常")
    except Exception as e:
        print(f"预期的错误（外键约束）: {str(e)}")
        conn.rollback()
        print("事务已回滚")

def main():
    print("开始高级数据库测试...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 执行所有测试
        test_error_handling(conn)
        test_batch_operations(conn)
        test_transaction_rollback(conn)

if __name__ == "__main__":
    main() 