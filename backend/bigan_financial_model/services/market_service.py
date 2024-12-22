"""市场服务模块"""
from datetime import datetime
from typing import Dict, Any
import logging
import pandas as pd
import numpy as np
from bigan_financial_model.analysis.market_analysis import MarketAnalyzer
from bigan_financial_model.core.config import Config

logger = logging.getLogger(__name__)

class MarketService:
    def __init__(self, config: Config):
        """初始化市场服务"""
        self.config = config
        self.analyzer = MarketAnalyzer()
        
    def get_market_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取市场数据和分析结果"""
        try:
            # 1. 获取原始数据
            data = self._fetch_data(symbol, start_date, end_date)
            
            # 2. 执行市场分析
            analysis = self.analyzer.analyze(data)
            
            # 3. 构建响应
            latest_data = self._get_latest_data(data)
            summary_data = self._get_summary_data(data)
            
            return {
                'success': True,
                'data': {
                    'latest': latest_data,
                    'summary': summary_data,
                    'analysis': analysis
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取市场数据失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def _get_latest_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """获取最新数据"""
        latest = data.iloc[-1]
        return {
            'price': self._format_number(latest['Close']),
            'volume': self._format_number(latest['Volume']),
            'change': self._format_number(
                (latest['Close'] - data.iloc[-2]['Close']) / data.iloc[-2]['Close'] * 100
            ),
            'timestamp': latest.name.isoformat()
        }
        
    def _get_summary_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """获取汇总数据"""
        return {
            'high': self._format_number(data['High'].max()),
            'low': self._format_number(data['Low'].min()),
            'avg_volume': self._format_number(data['Volume'].mean()),
            'volatility': self._format_number(
                data['Close'].pct_change().std() * np.sqrt(252) * 100
            )
        }
        
    @staticmethod
    def _format_number(value: float, decimals: int = 2) -> float:
        """格式化数字"""
        try:
            return round(float(value), decimals)
        except:
            return 0.0
            
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        df = data.copy()
        
        # 移动平均线
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        df['RSI'] = self._calculate_rsi(df['Close'])
        
        # MACD
        df['MACD'], df['Signal'], df['Histogram'] = self._calculate_macd(df['Close'])
        
        return df
        
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    @staticmethod
    def _calculate_macd(prices: pd.Series) -> tuple:
        """计算MACD指标"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram