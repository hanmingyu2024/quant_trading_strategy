"""风险管理模块增强版"""
from typing import Dict, Any, Optional, Tuple, List, Union
import logging
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from datetime import datetime, timedelta
import joblib
import warnings
from enum import Enum
from sklearn.ensemble import IsolationForest, RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score
import websocket
import json
import queue
from threading import Thread
from bigan_financial_model.utils.metrics.risk import RiskMetrics
from bigan_financial_model.utils.metrics.performance import PerformanceMetrics

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """风险预测模型类型"""
    GRADIENT_BOOSTING = "gradient_boosting"
    RANDOM_FOREST = "random_forest"
    NEURAL_NETWORK = "neural_network"

@dataclass
class DynamicThreshold:
    """动态风险阈值"""
    base_value: float
    market_sensitivity: float = 1.0
    min_value: float = 0.0
    max_value: float = float('inf')
    
    def adjust(self, market_condition: float) -> float:
        """根据市场状况调整阈值"""
        adjusted = self.base_value * (1 + self.market_sensitivity * market_condition)
        return np.clip(adjusted, self.min_value, self.max_value)

@dataclass
class RiskModelConfig:
    """风险模型配置"""
    model_type: ModelType = ModelType.GRADIENT_BOOSTING
    use_ensemble: bool = True
    retrain_frequency: int = 7  # 天
    cache_size: int = 1000
    
class MarketDataStream:
    """实时市场数据流"""
    def __init__(self, websocket_url: str):
        self.url = websocket_url
        self.data_queue = queue.Queue()
        self.ws = None
        self._start_streaming()
    
    def _start_streaming(self):
        def on_message(ws, message):
            self.data_queue.put(json.loads(message))
            
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=on_message
        )
        Thread(target=self.ws.run_forever).start()
    
    def get_latest_data(self) -> Dict[str, Any]:
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return {}

class RiskManager:
    """增强版风险管理器"""
    
    def __init__(self, config=None):
        self.config = self._validate_config(config or {})
        self._setup_cache()
        
    def _validate_risk_parameters(self, config):
        """验证并自动调整风险参数"""
        adjusted_config = config.copy()
        
        # 自动调整参数到安全范围
        if adjusted_config['stop_loss'] > 0.02:
            logger.warning(f"止损比例 {adjusted_config['stop_loss']} 过高，已自动调整为 2%")
            adjusted_config['stop_loss'] = 0.02
            
        if adjusted_config['max_position_size'] > 0.3:
            logger.warning(f"最大仓位 {adjusted_config['max_position_size']} 过高，已自动调整为 30%")
            adjusted_config['max_position_size'] = 0.3
            
        if adjusted_config['risk_per_trade'] > 0.01:
            logger.warning(f"每笔交易风险 {adjusted_config['risk_per_trade']} 过高，已自动调整为 1%")
            adjusted_config['risk_per_trade'] = 0.01
            
        # 添加新的风险参数（如果不存在）
        if 'position_limit' not in adjusted_config:
            adjusted_config['position_limit'] = 0.5
            
        if 'volatility_scaling' not in adjusted_config:
            adjusted_config['volatility_scaling'] = True
            
        return adjusted_config

    def _validate_config(self, config):
        """验证并返回更严格的风险管理配置"""
        default_config = {
            'stop_loss': 0.01,          # 默认止损1%
            'take_profit': 0.02,        # 默认止盈2%
            'max_position_size': 0.2,   # 默认最大仓位20%
            'risk_per_trade': 0.005,    # 默认每笔交易风险0.5%
            'max_drawdown': 0.1,        # 默认最大回撤10%
            'position_limit': 0.5,      # 默认总仓位限制50%
            'volatility_scaling': True,  # 默认启用波动率调整
        }
        
        # 合并配置
        validated_config = default_config.copy()
        validated_config.update(config)
        
        # 验证并调整参数
        return self._validate_risk_parameters(validated_config)

    def _setup_cache(self):
        """初始化风险监控缓存"""
        self._cache = {
            'current_drawdown': 0.0,
            'peak_value': None,
            'positions': [],
            'total_exposure': 0.0,
            'daily_var': None,
            'position_correlations': {},
            'risk_metrics': {
                'daily_returns': [],
                'volatility': None,
                'var_95': None,
                'expected_shortfall': None
            }
        }

    def calculate_position_size(self, price, volatility, account_value):
        """计算动态仓位大小"""
        try:
            # 基于波动率的仓位调整
            vol_scalar = 0.15 / volatility if volatility > 0 else 1
            base_size = account_value * self.config['risk_per_trade']
            
            # 考虑当前总敞口
            remaining_capacity = self.config['position_limit'] - self._cache['total_exposure']
            
            # 计算最终仓位大小
            position_size = min(
                base_size * vol_scalar,
                account_value * self.config['max_position_size'],
                remaining_capacity * account_value
            )
            
            return max(0, position_size)
            
        except Exception as e:
            logger.error(f"仓位计算失败: {str(e)}")
            return 0

    def should_close_position(self, position, current_price, current_value):
        """判断是否应该平仓"""
        try:
            # 计算收益率
            returns = (current_price - position['entry_price']) / position['entry_price']
            
            # 止损检查
            if returns < -self.config['stop_loss']:
                return True, 'stop_loss'
                
            # 止盈检查
            if returns > self.config['take_profit']:
                return True, 'take_profit'
                
            # 回撤检查
            if self._cache['current_drawdown'] < -self.config['max_drawdown']:
                return True, 'max_drawdown'
                
            # 波动率检查
            if self._cache['risk_metrics']['volatility'] > 0.2:  # 日波动率超过20%
                return True, 'high_volatility'
                
            return False, None
            
        except Exception as e:
            logger.error(f"平仓检查失败: {str(e)}")
            return True, 'error'

    def update_risk_metrics(self, current_value, positions):
        """更新风险指标"""
        try:
            # 更新最大回撤
            if self._cache['peak_value'] is None or current_value > self._cache['peak_value']:
                self._cache['peak_value'] = current_value
            
            self._cache['current_drawdown'] = (current_value - self._cache['peak_value']) / self._cache['peak_value']
            
            # 更新总敞口
            self._cache['total_exposure'] = sum(p['size'] for p in positions) / current_value
            
            # 更新其他风险指标
            self._update_var_metrics()
            
        except Exception as e:
            logger.error(f"风险指标更新失败: {str(e)}")

    def _update_var_metrics(self):
        """更新VaR相关指标"""
        try:
            if len(self._cache['risk_metrics']['daily_returns']) > 0:
                returns = np.array(self._cache['risk_metrics']['daily_returns'])
                self._cache['risk_metrics']['volatility'] = np.std(returns)
                self._cache['risk_metrics']['var_95'] = np.percentile(returns, 5)
                self._cache['risk_metrics']['expected_shortfall'] = returns[returns < self._cache['risk_metrics']['var_95']].mean()
        except Exception as e:
            logger.error(f"VaR指标更新失败: {str(e)}")