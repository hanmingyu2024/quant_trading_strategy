"""
这是一个数据库性能测试文件。
主要测试以下功能:
1. 批量插入 - 测试大量数据的插入性能
2. 查询性能 - 测试不同类型查询的响应时间
3. 并发操作 - 测试多线程并发访问数据库的性能
"""

from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime, timedelta
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import random

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def test_bulk_insert(conn, num_records=1000):
    """测试大量数据插入性能"""
    print(f"\n=== 测试批量插入 {num_records} 条交易记录 ===")
    symbols = ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT', 'BNBUSDT', 'ADAUSDT']
    start_time = time.time()
    
    try:
        # 批量插入交易记录
        for i in range(num_records):
            conn.execute(text("""
                INSERT INTO trades (user_id, symbol, quantity, price, trade_type, created_at)
                VALUES (:user_id, :symbol, :quantity, :price, :trade_type, :created_at)
            """), {
                "user_id": 1,
                "symbol": random.choice(symbols),
                "quantity": round(random.uniform(0.1, 10.0), 2),
                "price": round(random.uniform(100, 50000), 2),
                "trade_type": random.choice(['buy', 'sell']),
                "created_at": datetime.now() - timedelta(days=random.randint(0, 30))
            })
            
            if i % 100 == 0:  # 每100条提交一次
                conn.commit()
                print(f"已插入 {i+1} 条记录...")
        
        conn.commit()
        end_time = time.time()
        print(f"批量插入完成，耗时: {end_time - start_time:.2f}秒")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        conn.rollback()

def test_query_performance(conn):
    """测试查询性能"""
    print("\n=== 测试查询性能 ===")
    queries = [
        ("按时间范围查询", """
            SELECT COUNT(*) FROM trades 
            WHERE created_at > :start_date
        """),
        ("按用户分组统计", """
            SELECT user_id, COUNT(*), SUM(quantity * price) 
            FROM trades 
            GROUP BY user_id
        """),
        ("复杂联合查询", """
            SELECT u.username, t.symbol, 
                   COUNT(*) as trade_count, 
                   SUM(CASE WHEN t.trade_type = 'buy' THEN 1 ELSE 0 END) as buy_count,
                   SUM(CASE WHEN t.trade_type = 'sell' THEN 1 ELSE 0 END) as sell_count,
                   AVG(t.price) as avg_price
            FROM users u
            JOIN trades t ON u.id = t.user_id
            GROUP BY u.username, t.symbol
            HAVING trade_count > 5
        """)
    ]
    
    for query_name, query in queries:
        start_time = time.time()
        try:
            result = conn.execute(text(query), {
                "start_date": datetime.now() - timedelta(days=7)
            }).fetchall()
            end_time = time.time()
            print(f"\n{query_name}:")
            print(f"耗时: {end_time - start_time:.3f}秒")
            print(f"结果数量: {len(result)}")
        except Exception as e:
            print(f"查询错误 {query_name}: {str(e)}")

def concurrent_trade(thread_id):
    """并发交易测试"""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                INSERT INTO trades (user_id, symbol, quantity, price, trade_type, created_at)
                VALUES (:user_id, :symbol, :quantity, :price, :trade_type, :created_at)
            """), {
                "user_id": 1,
                "symbol": "BTCUSDT",
                "quantity": 1.0,
                "price": 50000.0,
                "trade_type": "buy",
                "created_at": datetime.now()
            })
            conn.commit()
            print(f"线程 {thread_id} 完成交易")
        except Exception as e:
            print(f"线程 {thread_id} 错误: {str(e)}")
            conn.rollback()

def test_concurrent_operations(num_threads=10):
    """测试并发操作"""
    print(f"\n=== 测试 {num_threads} 个并发操作 ===")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(concurrent_trade, range(num_threads))
    
    end_time = time.time()
    print(f"并发测试完成，总耗时: {end_time - start_time:.2f}秒")

def main():
    print("开始性能测试...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. 批量插入测试
        test_bulk_insert(conn)
        
        # 2. 查询性能测试
        test_query_performance(conn)
        
        # 3. 并发操作测试
        test_concurrent_operations()

if __name__ == "__main__":
    main() 