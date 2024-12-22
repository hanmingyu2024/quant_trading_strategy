# metrics/__init__.py
from bigan_financial_model.utils.metrics.performance import PerformanceMetrics
from bigan_financial_model.utils.metrics.risk import (
    RiskMetrics,
    RiskAnalysis,
    RiskReport,
    RiskManager
)
import numpy as np
import pandas as pd
from typing import Optional

def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods: int = 252
) -> float:
    """计算夏普比率
    
    Args:
        returns (pd.Series): 收益率序列
        risk_free_rate (float): 无风险利率，默认0.02 (2%)
        periods (int): 年化周期，默认252个交易日
        
    Returns:
        float: 夏普比率
    """
    excess_returns = returns - risk_free_rate/periods
    return np.sqrt(periods) * excess_returns.mean() / returns.std()

def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods: int = 252
) -> float:
    """计算索提诺比率
    
    Args:
        returns (pd.Series): 收益率序列
        risk_free_rate (float): 无风险利率，默认0.02 (2%)
        periods (int): 年化周期，默认252个交易日
        
    Returns:
        float: 索提诺比率
    """
    excess_returns = returns - risk_free_rate/periods
    downside_returns = returns[returns < 0]
    downside_std = np.sqrt(np.mean(downside_returns**2))
    return np.sqrt(periods) * excess_returns.mean() / downside_std

def calculate_metrics(
    returns: pd.Series,
    prices: pd.Series,
    volume: Optional[pd.Series] = None,
    market_returns: Optional[pd.Series] = None
) -> dict:
    """计算所有指标的统一接口
    
    Args:
        returns (pd.Series): 收益率序列
        prices (pd.Series): 价格序列
        volume (pd.Series, optional): 成交量序列
        market_returns (pd.Series, optional): 市场收益率序列
        
    Returns:
        Dict[str, Any]: 包含所有计算指标的字典
    """
    # 初始化指标计算器
    risk_metrics = RiskMetrics()
    performance_metrics = PerformanceMetrics()
    
    # 计算风险指标
    risk_results = risk_metrics.calculate_risk_metrics(
        returns=returns,
        prices=prices,
        volume=volume,
        market_returns=market_returns
    )
    
    # 计算性能指标
    performance_results = performance_metrics.calculate_metrics(
        returns=returns,
        market_returns=market_returns
    )
    
    # 计算其他比率
    additional_metrics = {
        "夏普比率": calculate_sharpe_ratio(returns),
        "索提诺比率": calculate_sortino_ratio(returns)
    }
    
    # 合并所有结果
    return {
        "风险指标": risk_results,
        "性能指标": performance_results,
        "比率指标": additional_metrics
    }

# 导出所有公共接口
__all__ = [
    'RiskMetrics',
    'PerformanceMetrics',
    'calculate_metrics',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio'
]