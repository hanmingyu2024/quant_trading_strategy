"""数据处理服务"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from bigan_financial_model.data.fetcher import DataFetcher
from bigan_financial_model.core.config import Config

class DataService:
    def __init__(self, config: Config):
        """初始化数据服务"""
        self.config = config
        self.fetcher = DataFetcher()
        self.logger = logging.getLogger(__name__)
        
    def get_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取并处理数据"""
        try:
            # 1. 获取原始数据
            df = self.fetcher.fetch_from_yfinance(symbol, start_date, end_date)
            if df.empty:
                df = self.fetcher.fetch_from_backup(symbol, start_date, end_date)
                
            # 2. 处理数据
            if not df.empty:
                df = self.process_data(df)
                
            return df
            
        except Exception as e:
            self.logger.error(f"数据获取处理失败: {str(e)}")
            return pd.DataFrame()
            
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理数据并添加技术指标"""
        try:
            # 1. 基础技术指标
            df['SMA_5'] = df['Close'].rolling(window=5, min_periods=1).mean()
            df['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['EMA_3'] = df['Close'].ewm(span=3, adjust=False).mean()
            
            # 2. 趋势指标
            df['Trend_Direction'] = np.where(df['Close'] > df['SMA_20'], 1, -1)
            df['Trend_Strength'] = abs(df['Close'].pct_change())
            
            # 3. 成交量指标
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Trend'] = df['Volume'].ewm(span=10).mean()
            
            return df
            
        except Exception as e:
            self.logger.error(f"数据处理失败: {str(e)}")
            return df
