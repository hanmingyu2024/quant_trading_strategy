
"""
这是一个数据库优化文件。
主要功能:
1. 添加性能优化索引 - 为trades表添加多个索引提升查询性能
2. 优化表结构 - 优化表的存储结构和配置
3. 数据库维护 - 定期优化和维护数据库性能
"""

from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime, timedelta
import time

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def add_indexes(conn):
    """添加优化索引"""
    print("\n=== 添加性能优化索引 ===")
    try:
        # 为trades表添加组合索引
        print("1. 添加交易时间索引...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_trades_created_at 
            ON trades (created_at)
        """))
        
        print("2. 添加交易symbol和type组合索引...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_trades_symbol_type 
            ON trades (symbol, trade_type)
        """))
        
        print("3. 添加用户交易组合索引...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_trades_user_symbol 
            ON trades (user_id, symbol, created_at)
        """))
        
        conn.commit()
        print("索引添加完成！")
        
    except Exception as e:
        print(f"添加索引时出错: {str(e)}")
        conn.rollback()

def optimize_tables(conn):
    """优化表结构"""
    print("\n=== 优化表结构 ===")
    try:
        print("1. 优化trades表...")
        conn.execute(text("OPTIMIZE TABLE trades"))
        
        print("2. 优化users表...")
        conn.execute(text("OPTIMIZE TABLE users"))
        
        print("表优化完成！")
        
    except Exception as e:
        print(f"优化表时出错: {str(e)}")

def analyze_table_status(conn):
    """分析表状态"""
    print("\n=== 分析表状态 ===")
    try:
        print("\n1. trades表状态:")
        result = conn.execute(text("SHOW TABLE STATUS LIKE 'trades'")).fetchone()
        print(f"- 行数: {result.Rows}")
        print(f"- 数据大小: {result.Data_length/1024:.2f} KB")
        print(f"- 索引大小: {result.Index_length/1024:.2f} KB")
        
        print("\n2. 查看索引使用情况:")
        result = conn.execute(text("SHOW INDEX FROM trades")).fetchall()
        for idx in result:
            print(f"- 索引名: {idx.Key_name}")
            print(f"  列: {idx.Column_name}")
            print(f"  唯一性: {'是' if idx.Non_unique == 0 else '否'}")
        
    except Exception as e:
        print(f"分析表状态时出错: {str(e)}")

def test_optimized_queries(conn):
    """测试优化后的查询性能"""
    print("\n=== 测试优化后的查询性能 ===")
    queries = [
        ("按时间范围查询", """
            SELECT COUNT(*) 
            FROM trades 
            WHERE created_at > :start_date
        """),
        ("按symbol和type分组查询", """
            SELECT symbol, trade_type, COUNT(*) 
            FROM trades 
            GROUP BY symbol, trade_type
        """),
        ("用户交易统计", """
            SELECT u.username, t.symbol,
                   COUNT(*) as trade_count,
                   SUM(t.quantity * t.price) as total_value
            FROM users u
            JOIN trades t ON u.id = t.user_id
            WHERE t.created_at > :start_date
            GROUP BY u.username, t.symbol
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
            print(f"查询出错 {query_name}: {str(e)}")

def main():
    print("开始数据库优化...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. 添加优化索引
        add_indexes(conn)
        
        # 2. 优化表结构
        optimize_tables(conn)
        
        # 3. 分析表状态
        analyze_table_status(conn)
        
        # 4. 测试优化后的查询
        test_optimized_queries(conn)

if __name__ == "__main__":
    main() 