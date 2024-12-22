"""
数据获取模块

主要功能:
- 从mt5获取金融数据
- 处理和清洗数据
- 计算技术指标

作者: BiGan团队
日期: 2024-01
"""

import pandas as pd
import yfinance as yf
from typing import Dict, Any
import logging
import MetaTrader5 as mt5
import numpy as np
from datetime import datetime, timedelta
import pytz
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from bigan_financial_model.database.models import MarketData, Asset, IntervalType

class DataFetcher:
    """数据获取器"""
    
    def __init__(self):
        """初始化数据获取器"""
        self.logger = logging.getLogger(__name__)
        
    def fetch_data(self, symbol, start_date, end_date):
        """获取股票数据
        
        Args:
            symbol (str): 股票代码
            start_date (str): 开始日期
            end_date (str): 结束日期
            
        Returns:
            pd.DataFrame: 股票数据
        """
        try:
            self.logger.info(f"开始获取数据: {symbol}, {start_date} 到 {end_date}")
            
            # 添加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 使用 yfinance 获取数据
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(start=start_date, end=end_date, interval='1d')
                    
                    if len(data) > 0:
                        self.logger.info(f"数据获取成功: {len(data)} 条记录")
                        return data
                    else:
                        # 如果数据为空，尝试调整日期范围
                        adjusted_start = (pd.to_datetime(start_date) - pd.Timedelta(days=30)).strftime('%Y-%m-%d')
                        adjusted_end = (pd.to_datetime(end_date) + pd.Timedelta(days=30)).strftime('%Y-%m-%d')
                        
                        self.logger.warning(f"尝试调整日期范围: {adjusted_start} 到 {adjusted_end}")
                        data = ticker.history(start=adjusted_start, end=adjusted_end, interval='1d')
                        
                        if len(data) > 0:
                            # 裁剪到原始日期范围
                            mask = (data.index >= start_date) & (data.index <= end_date)
                            data = data.loc[mask]
                            self.logger.info(f"使用调整后的日期范围获取成功: {len(data)} 条记录")
                            return data
                            
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"第 {attempt + 1} 次获取失败，准备重试: {str(e)}")
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        raise
                        
            # 如果所有重试都失败，使用备用数据源
            self.logger.warning("尝试使用备用数据源")
            return self._fetch_from_backup_source(symbol, start_date, end_date)
            
        except Exception as e:
            self.logger.error(f"数据获取失败: {str(e)}")
            return pd.DataFrame()  # 返回空DataFrame而不是None

    def _fetch_from_backup_source(self, symbol, start_date, end_date):
        """从备用数据源获取数据"""
        try:
            # 这里可以添加其他数据源的实现
            # 例如：Alpha Vantage, IEX Cloud 
            
            # 临时返回示例数据用于测试
            dates = pd.date_range(start=start_date, end=end_date, freq='B')
            data = pd.DataFrame(index=dates)
            data['Close'] = np.random.normal(100, 2, len(dates))
            data['Open'] = data['Close'] * np.random.normal(1, 0.01, len(dates))
            data['High'] = data[['Open', 'Close']].max(axis=1) * np.random.normal(1.01, 0.005, len(dates))
            data['Low'] = data[['Open', 'Close']].min(axis=1) * np.random.normal(0.99, 0.005, len(dates))
            data['Volume'] = np.random.normal(1000000, 200000, len(dates))
            
            return data
            
        except Exception as e:
            self.logger.error(f"备用数据源获取失败: {str(e)}")
            return pd.DataFrame()

    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理数据"""
        if data.empty:
            return data
            
        processed = data.copy()
        processed['Returns'] = processed['Close'].pct_change()
        processed['MA5'] = processed['Close'].rolling(window=5).mean()
        processed['MA20'] = processed['Close'].rolling(window=20).mean()
        
        return processed.dropna()

class MT5DataFetcher:
    def __init__(self, config):
        """初始化 MT5 数获取器
        
        Args:
            config (dict): MT5配置信息
        """
        self.account = config['MT5_ACCOUNT']
        self.password = config['MT5_PASSWORD']
        self.server = config['MT5_SERVER']
        self.timeout = config.get('MT5_TIMEOUT', 60000)
        self.retry_count = config.get('MT5_RETRY_COUNT', 3)
        self.retry_delay = config.get('MT5_RETRY_DELAY', 5)
        self.logger = logging.getLogger(__name__)
        
        # 初始化MT5连接
        self._initialize_mt5()

    def _initialize_mt5(self):
        """初始化与MT5的连接"""
        try:
            if not mt5.initialize():
                self.logger.error("MT5初始化失败")
                raise Exception("MT5初始化失败")
                
            # 登录MT5
            login_result = mt5.login(
                login=self.account,
                password=self.password,
                server=self.server,
                timeout=self.timeout
            )
            
            if not login_result:
                self.logger.error(f"MT5登录失败: {mt5.last_error()}")
                raise Exception("MT5登录失败")
                
            self.logger.info("MT5连接成功")
            
        except Exception as e:
            self.logger.error(f"MT5连失败: {str(e)}")
            raise

    def fetch_data(self, symbol, start_date, end_date, timeframe=mt5.TIMEFRAME_D1):
        """从MT5获取数据
        
        Args:
            symbol (str): 交易品种
            start_date (str): 开始日期
            end_date (str): 结束日期
            timeframe: 时间周期
            
        Returns:
            pd.DataFrame: 行情数据
        """
        try:
            # 转换日期格式
            timezone = pytz.timezone("Etc/UTC")
            start_dt = pd.to_datetime(start_date).replace(tzinfo=timezone)
            end_dt = pd.to_datetime(end_date).replace(tzinfo=timezone)
            
            self.logger.info(f"开始获取MT5数据: {symbol}, {start_date} 到 {end_date}")
            
            # 重试机制
            for attempt in range(self.retry_count):
                try:
                    # 获取K线数据
                    rates = mt5.copy_rates_range(
                        symbol,
                        timeframe,
                        start_dt,
                        end_dt
                    )
                    
                    if rates is not None and len(rates) > 0:
                        # 转换为DataFrame
                        df = pd.DataFrame(rates)
                        df['time'] = pd.to_datetime(df['time'], unit='s')
                        df.set_index('time', inplace=True)
                        
                        # 重命名列
                        df = df.rename(columns={
                            'open': 'Open',
                            'high': 'High',
                            'low': 'Low',
                            'close': 'Close',
                            'tick_volume': 'Volume'
                        })
                        
                        self.logger.info(f"数据获取成功: {len(df)} 条记录")
                        return df
                        
                    else:
                        if attempt < self.retry_count - 1:
                            self.logger.warning(f"第 {attempt + 1} 次获取失败，准备重试")
                            time.sleep(self.retry_delay)
                        else:
                            raise Exception("无法获取数据")
                            
                except Exception as e:
                    if attempt < self.retry_count - 1:
                        self.logger.warning(f"第 {attempt + 1} 次获取失败: {str(e)}")
                        time.sleep(self.retry_delay)
                    else:
                        raise
                        
        except Exception as e:
            self.logger.error(f"MT5数据获取失败: {str(e)}")
            return pd.DataFrame()
            
        finally:
            # 确保在完成后关闭连接
            if mt5.initialize():
                mt5.shutdown()

    def get_symbols(self):
        """获取可交易品种列表"""
        try:
            symbols = mt5.symbols_get()
            return [symbol.name for symbol in symbols]
        except Exception as e:
            self.logger.error(f"获取交易品种失败: {str(e)}")
            return []

class MT5DataDownloader:
    """MT5数据下载器"""
    
    def __init__(self, db_url: str):
        """
        初始化MT5数据下载器
        
        Args:
            db_url: 数据库连接URL
        """
        # 初始化MT5连接
        if not mt5.initialize():
            raise Exception("MT5初始化失败")
            
        # 初始化数据库连接
        self.engine = create_engine(db_url)
        
    def __del__(self):
        """清理MT5连接"""
        mt5.shutdown()
    
    def _convert_timeframe(self, interval: IntervalType) -> int:
        """转换时间周期格式"""
        timeframe_map = {
            IntervalType.M1: mt5.TIMEFRAME_M1,
            IntervalType.M5: mt5.TIMEFRAME_M5,
            IntervalType.M15: mt5.TIMEFRAME_M15,
            IntervalType.H1: mt5.TIMEFRAME_H1,
            IntervalType.H4: mt5.TIMEFRAME_H4,
            IntervalType.D1: mt5.TIMEFRAME_D1,
            IntervalType.W1: mt5.TIMEFRAME_W1,
            IntervalType.MN: mt5.TIMEFRAME_MN1,
        }
        return timeframe_map[interval]
    
    def download_data(
        self,
        symbol: str,
        interval: IntervalType,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        asset_id: Optional[int] = None
    ) -> List[MarketData]:
        """
        下载MT5数据
        
        Args:
            symbol: 交易对符号
            interval: 时间周期
            start_time: 起始时间
            end_time: 结束时间(默认为当前时间)
            asset_id: 资产ID(如果已知)
            
        Returns:
            List[MarketData]: 市场数据列表
        """
        # 设置默认结束时间
        if end_time is None:
            end_time = datetime.now()
            
        # 获取K线数据
        timeframe = self._convert_timeframe(interval)
        rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
        
        if rates is None or len(rates) == 0:
            return []
            
        # 转换为DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # 如果没有提供asset_id,尝试从数据库获取
        if asset_id is None:
            with Session(self.engine) as session:
                asset = session.query(Asset).filter(Asset.symbol == symbol).first()
                if asset:
                    asset_id = asset.id
                else:
                    raise ValueError(f"找不到symbol={symbol}对应的asset记录")
        
        # 转换为MarketData对象列表
        market_data_list = []
        for _, row in df.iterrows():
            market_data = MarketData(
                asset_id=asset_id,
                symbol=symbol,
                interval=interval.value,
                timestamp=row['time'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['real_close'] if 'real_close' in row else row['close'],
                volume=row['tick_volume'],
                created_at=datetime.utcnow()
            )
            market_data_list.append(market_data)
            
        return market_data_list
    
    def save_to_db(self, market_data_list: List[MarketData]) -> None:
        """
        保存数据到数据库
        
        Args:
            market_data_list: 市场数据列表
        """
        if not market_data_list:
            return
            
        with Session(self.engine) as session:
            session.bulk_save_objects(market_data_list)
            session.commit()
            
    def download_and_save(
        self,
        symbol: str,
        interval: IntervalType,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        asset_id: Optional[int] = None
    ) -> int:
        """
        下载并保存数据
        
        Args:
            symbol: 交易对符号
            interval: 时间周期
            start_time: 起始时间
            end_time: 结束时间
            asset_id: 资产ID
            
        Returns:
            int: 保存的数据条数
        """
        market_data_list = self.download_data(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            asset_id=asset_id
        )
        
        self.save_to_db(market_data_list)
        return len(market_data_list)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # 数据库连接配置
        DB_CONFIG = {
            'host': 'rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com',
            'port': 3306,  # 改为数字类型
            'user': 'hanmingyushanbaoyue',
            'password': 'hanmingyu@208521',
            'database': 'reinforcementlearningbot'
        }
        
        # 使用 URL 编码处理特殊字符
        from urllib.parse import quote_plus
        password = quote_plus(DB_CONFIG['password'])
        
        # 修正 SQLAlchemy 连接 URL 格式
        DB_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        
        # 创建下载器实例
        downloader = MT5DataDownloader(DB_URL)
        
        # 下载最近1天的数据作为测试
        from datetime import datetime, timedelta
        start_time = datetime.now() - timedelta(days=1)
        
        # 测试下载EURUSD的15分钟数据
        count = downloader.download_and_save(
            symbol="EURUSD",
            interval=IntervalType.M15,
            start_time=start_time
        )
        
        logger.info(f"成功下载并保存了 {count} 条数据")
        
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        raise