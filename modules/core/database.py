"""
数据库模块

功能:
- 初始化和管理SQLite数据库
- 保存历史数据和交易记录
- 保存交易信号
- 分析策略性能
- 导出交易报告

作者: Han Mingyu
邮箱: 13364694109ai@gmail.com
"""

import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import json
from modules.logger import setup_logger
import os
import random

logger = setup_logger('database')

class Database:
    def __init__(self, db_path='data/trading.db'):
        """初始化数据库"""
        # 确保目录存在
        os.makedirs('data', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        
        # 如果数据库文件存在，先删除
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"删除旧数据库: {db_path}")
        
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
        
    def initialize_database(self):
        """初始化数据库表"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # 1. 创建历史数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    timestamp DATETIME,
                    timeframe TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    spread REAL,
                    UNIQUE(symbol, timestamp, timeframe)
                )
            ''')
            
            # 2. 创建交易记录表（新结构）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket INTEGER UNIQUE,
                    symbol TEXT,
                    order_type TEXT,
                    volume REAL,
                    open_price REAL,
                    open_time DATETIME,
                    close_price REAL,
                    close_time DATETIME,
                    profit REAL,
                    swap REAL,
                    commission REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    magic_number INTEGER,
                    comment TEXT,
                    strategy_name TEXT,
                    holding_time REAL,
                    risk_reward_ratio REAL,
                    market_trend TEXT,
                    volatility REAL,
                    spread REAL
                )
            ''')
            
            # 3. 创建信号记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    timestamp DATETIME,
                    signal_type TEXT,
                    signal_reason TEXT,
                    price REAL,
                    indicators TEXT,
                    strength REAL
                )
            ''')
            
            self.conn.commit()
            logger.info("数据库初始化成功")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            
    def save_historical_data(self, symbol, timeframe, data):
        """保存历史数据"""
        try:
            df = pd.DataFrame(data)
            df.to_sql('historical_data', self.conn, if_exists='append', index=False)
            logger.info(f"保存了 {len(df)} 条 {symbol} 历史数据")
        except Exception as e:
            logger.error(f"保存历史数据失败: {str(e)}")
            
    def save_trade(self, trade_info):
        """保存更完整的交易记录"""
        try:
            # 计算持仓时间（小时）
            holding_time = (trade_info['close_time'] - trade_info['open_time']).total_seconds() / 3600
            
            # 计算盈亏比
            if trade_info['profit'] > 0:
                risk = abs(trade_info['open_price'] - trade_info['stop_loss'])
                reward = abs(trade_info['close_price'] - trade_info['open_price'])
                risk_reward_ratio = reward / risk if risk != 0 else 0
            else:
                risk_reward_ratio = 0

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO trades (
                    ticket, symbol, order_type, volume, 
                    open_price, open_time, close_price, close_time,
                    profit, swap, commission, stop_loss, take_profit,
                    magic_number, comment, strategy_name,
                    holding_time, risk_reward_ratio,
                    market_trend, volatility, spread
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_info['ticket'],
                trade_info['symbol'],
                trade_info['order_type'],
                trade_info['volume'],
                trade_info['open_price'],
                trade_info['open_time'],
                trade_info['close_price'],
                trade_info['close_time'],
                trade_info['profit'],
                trade_info.get('swap', 0),          # 隔夜利息
                trade_info.get('commission', -0.5),  # 默认手续费
                trade_info['stop_loss'],
                trade_info['take_profit'],
                trade_info.get('magic_number', 234000),  # 策略标识号
                trade_info.get('comment', ''),
                trade_info.get('strategy_name', 'MA_RSI_Strategy'),
                holding_time,                        # 持仓时间
                risk_reward_ratio,                   # 盈亏比
                trade_info.get('market_trend', ''),  # 市场趋势
                trade_info.get('volatility', 0),     # 波动率
                trade_info.get('spread', 0)          # 点差
            ))
            self.conn.commit()
            
            # 同时保存信号记录
            self.save_signal({
                'symbol': trade_info['symbol'],
                'timestamp': trade_info['open_time'],
                'signal_type': trade_info['order_type'],
                'signal_reason': trade_info.get('signal_reason', ''),
                'price': trade_info['open_price'],
                'indicators': trade_info.get('indicators', ''),
                'strength': trade_info.get('signal_strength', 0)
            })
            
            logger.info(f"保存交易记录成功: {trade_info['ticket']}")
            return True
            
        except Exception as e:
            logger.error(f"保存交易记录失败: {str(e)}")
            return False
            
    def save_signal(self, signal_info):
        """保存信号记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO signals (
                    symbol, timestamp, signal_type, 
                    signal_reason, price, indicators
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                signal_info['symbol'],
                signal_info['timestamp'],
                signal_info['signal_type'],
                signal_info['signal_reason'],
                signal_info['price'],
                signal_info['indicators']
            ))
            self.conn.commit()
            logger.info(f"保存信号记录成功: {signal_info['signal_type']}")
        except Exception as e:
            logger.error(f"保存信号记录失败: {str(e)}")
            
    def get_trades_history(self, symbol=None, start_date=None, end_date=None):
        """获取交易历史"""
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        if start_date:
            query += " AND open_time >= ?"
            params.append(start_date)
        if end_date:
            query += " AND open_time <= ?"
            params.append(end_date)
            
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            return df
        except Exception as e:
            logger.error(f"获取交易历史失败: {str(e)}")
            return None
            
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

    def analyze_performance(self, strategy_name, start_date=None, end_date=None):
        """分析策略性能"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(profit) as total_profit,
                    AVG(CASE WHEN profit > 0 THEN profit END) as avg_win,
                    AVG(CASE WHEN profit < 0 THEN profit END) as avg_loss,
                    MAX(profit) as max_profit,
                    MIN(profit) as max_loss
                FROM trades 
                WHERE strategy_name = ?
            """
            params = [strategy_name]
            
            if start_date:
                query += " AND open_time >= ?"
                params.append(start_date)
            if end_date:
                query += " AND open_time <= ?"
                params.append(end_date)
                
            df = pd.read_sql_query(query, self.conn, params=params)
            return df
            
        except Exception as e:
            logger.error(f"分析策略性能失败: {str(e)}")
            return None

    def get_market_statistics(self, symbol, timeframe, days=30):
        """获取市场统计数据"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            query = """
                SELECT 
                    AVG(high - low) as avg_range,
                    AVG(volume) as avg_volume,
                    AVG(spread) as avg_spread,
                    MAX(high) as period_high,
                    MIN(low) as period_low
                FROM historical_data
                WHERE symbol = ? 
                AND timeframe = ?
                AND timestamp >= ?
            """
            
            df = pd.read_sql_query(query, self.conn, 
                                 params=[symbol, timeframe, start_date])
            return df
            
        except Exception as e:
            logger.error(f"获取市场统计失败: {str(e)}")
            return None

    def export_trade_report(self, start_date=None, end_date=None, format='csv'):
        """导出交易报告"""
        try:
            query = """
                SELECT 
                    t.*,
                    s.signal_reason,
                    s.indicators
                FROM trades t
                LEFT JOIN signals s ON t.symbol = s.symbol 
                    AND t.open_time = s.timestamp
                WHERE 1=1
            """
            
            params = []
            if start_date:
                query += " AND t.open_time >= ?"
                params.append(start_date)
            if end_date:
                query += " AND t.open_time <= ?"
                params.append(end_date)
                
            df = pd.read_sql_query(query, self.conn, params=params)
            
            if format == 'csv':
                df.to_csv(f'reports/trade_report_{datetime.now():%Y%m%d}.csv')
            elif format == 'excel':
                df.to_excel(f'reports/trade_report_{datetime.now():%Y%m%d}.xlsx')
                
            return True
            
        except Exception as e:
            logger.error(f"导出交易报告失败: {str(e)}")
            return False

if __name__ == "__main__":
    # 创建数据库实例
    db = Database()
    
    try:
        # 1. 测试保存历史数据
        print("\n=== 测试保存历史数据 ===")
        test_data = {
            'symbol': 'SPT_DXY',
            'timestamp': datetime.now(),
            'timeframe': 'M5',
            'open': 106.939,
            'high': 106.959,
            'low': 106.939,
            'close': 106.939,
            'volume': 50,
            'spread': 81
        }
        db.save_historical_data('SPT_DXY', 'M5', [test_data])
        
        # 2. 测试保存完整交易记录
        print("\n=== 测试保存交易记录 ===")
        test_trade = {
            'ticket': random.randint(100000, 999999),
            'symbol': 'SPT_DXY',
            'order_type': 'BUY',
            'volume': 0.05,
            'open_price': 106.939,
            'open_time': datetime.now(),
            'close_price': 107.000,
            'close_time': datetime.now() + timedelta(hours=1),
            'profit': 3.05,
            'swap': -0.01,
            'commission': -0.5,
            'stop_loss': 106.889,
            'take_profit': 107.039,
            'magic_number': 234000,
            'comment': 'MA交叉信号',
            'strategy_name': 'MA_RSI_Strategy',
            'market_trend': '上升趋势',
            'volatility': 0.02,
            'spread': 81
        }
        db.save_trade(test_trade)
        
        # 3. 显示保存的数据
        print("\n=== 最新交易记录 ===")
        df = pd.read_sql_query(
            "SELECT * FROM trades ORDER BY id DESC LIMIT 1", 
            db.conn
        )
        print(df.to_string())
        
    except Exception as e:
        print(f"测试过程出错: {str(e)}")
        
    finally:
        db.close()
        print("\n数据库连接已关闭")
