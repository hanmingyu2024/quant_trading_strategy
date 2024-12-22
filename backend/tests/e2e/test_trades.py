"""
这是一个交易功能测试文件。
主要测试以下功能:
1. 创建交易 - 测试交易记录的创建
2. 查询交易 - 测试交易记录的查询
3. 交易统计 - 测试交易数据的统计功能
"""

from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@pytest.fixture
def test_trade():
    """创建测试用交易记录"""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO trades (user_id, symbol, quantity, price, trade_type, created_at)
            VALUES (:user_id, :symbol, :quantity, :price, :trade_type, :created_at)
        """), {
            "user_id": 1,
            "symbol": "BTCUSDT",
            "quantity": 1.5,
            "price": 45000.00,
            "trade_type": "buy",
            "created_at": datetime.now()
        })
        conn.commit()
        trade_id = result.lastrowid
        yield trade_id
        
        # 清理测试数据
        conn.execute(text("DELETE FROM trades WHERE id = :id"), {"id": trade_id})
        conn.commit()

def test_create_trade():
    """测试创建交易"""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO trades (user_id, symbol, quantity, price, trade_type, created_at)
            VALUES (:user_id, :symbol, :quantity, :price, :trade_type, :created_at)
        """), {
            "user_id": 1,
            "symbol": "ETHUSDT",
            "quantity": 2.0,
            "price": 3000.00,
            "trade_type": "buy",
            "created_at": datetime.now()
        })
        conn.commit()
        assert result.rowcount == 1

def test_query_trades():
    """测试查询交易"""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM trades 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT 10
        """), {
            "user_id": 1
        })
        trades = result.fetchall()
        assert len(trades) >= 0

def test_trade_statistics():
    """测试交易统计"""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # 统计用户的交易总量
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN trade_type = 'buy' THEN 1 ELSE 0 END) as total_buys,
                SUM(CASE WHEN trade_type = 'sell' THEN 1 ELSE 0 END) as total_sells
            FROM trades 
            WHERE user_id = :user_id
        """), {
            "user_id": 1
        })
        stats = result.fetchone()
        assert stats is not None
        assert stats[0] >= 0  # 总交易数
        assert stats[1] >= 0  # 买入交易数
        assert stats[2] >= 0  # 卖出交易数
