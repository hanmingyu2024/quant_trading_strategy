"""
市场分析模块

该模块实现了市场分析功能,用于分析金融市场数据。
主要功能包括:
- 趋势分析
- 波动性分析  
- 成交量分析
- 技术指标分析

作者: BiGan团队
日期: 2024-01
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """市场分析器"""
    
    def __init__(self):
        """初始化市场分析器"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化市场分析器")
        
    def analyze(self, data):
        """执行市场分析"""
        try:
            self.logger.info("开始市场分析...")
            
            # 首先计算收益率
            data = self._prepare_data(data)
            
            analysis_results = {
                'trend': self._analyze_trend(data),
                'volatility': self._analyze_volatility(data),
                'momentum': self._analyze_momentum(data),
                'volume': self._analyze_volume(data)
            }
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"市场分析失败: {str(e)}")
            raise

    def _prepare_data(self, data):
        """准备分析所需的数据"""
        df = data.copy()
        # 计算日收益率
        df['returns'] = df['close'].pct_change()
        # 计算对数收益率
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        return df

    def _analyze_volatility(self, data):
        """分析市场波动性"""
        try:
            return {
                'daily_volatility': data['returns'].std(),
                'annualized_volatility': data['returns'].std() * np.sqrt(252),
                'rolling_volatility': data['returns'].rolling(window=20).std().iloc[-1],
                'volatility_trend': 'increasing' if data['returns'].rolling(window=20).std().iloc[-1] > 
                                   data['returns'].rolling(window=20).std().iloc[-5] else 'decreasing'
            }
        except Exception as e:
            self.logger.warning(f"波动率分析失败: {str(e)}")
            return {}

    def _analyze_trend(self, data):
        """分析市场趋势"""
        try:
            trend_strength = (data['sma_20'].iloc[-1] - data['sma_50'].iloc[-1]) / data['sma_50'].iloc[-1]
            return {
                'direction': 'uptrend' if trend_strength > 0 else 'downtrend',
                'strength': abs(trend_strength),
                'sma_20': data['sma_20'].iloc[-1],
                'sma_50': data['sma_50'].iloc[-1]
            }
        except Exception as e:
            self.logger.warning(f"趋势强度计算失败: {str(e)}")
            return {}

    def _analyze_momentum(self, data):
        """分析动量"""
        try:
            return {
                'rsi': data['rsi_14'].iloc[-1],
                'macd': data['macd'].iloc[-1],
                'macd_signal': data['macd_signal'].iloc[-1],
                'momentum_signal': 'bullish' if data['rsi_14'].iloc[-1] > 50 else 'bearish'
            }
        except Exception as e:
            self.logger.warning(f"动量分析失败: {str(e)}")
            return {}

    def _analyze_volume(self, data):
        """分析成交量"""
        try:
            return {
                'volume': data['Volume'].iloc[-1],
                'volume_ma': data['Volume'].rolling(window=20).mean().iloc[-1],
                'volume_trend': 'increasing' if data['Volume'].iloc[-1] > data['Volume'].rolling(window=20).mean().iloc[-1] else 'decreasing'
            }
        except Exception as e:
            self.logger.warning(f"成交量分析失败: {str(e)}")
            return {}
