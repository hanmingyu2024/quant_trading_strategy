"""性能指标计算模块"""
from typing import Dict, Any, List, Union, Optional
import pandas as pd
import numpy as np
from datetime import datetime

class PerformanceMetrics:
    """性能指标计算器"""
    
    @staticmethod
    def calculate_metrics(
        returns: Union[pd.Series, List[float]],
        benchmark_returns: Optional[pd.Series] = None,
        risk_free_rate: float = 0.03,
        periods_per_year: int = 252
    ) -> Dict[str, Any]:
        """
        计算所有性能指标
        
        Args:
            returns: 策略收益率序列
            benchmark_returns: 基准收益率序列（可选）
            risk_free_rate: 无风险利率，默认3%
            periods_per_year: 年化周期，日度=252，月度=12
            
        Returns:
            Dict[str, Any]: 包含所有性能指标的字典
        """
        if isinstance(returns, list):
            returns = pd.Series(returns)
            
        metrics = {
            # 基础收益指标
            "总收益率": PerformanceMetrics.calculate_total_return(returns),
            "年化收益率": PerformanceMetrics.calculate_annual_return(returns, periods_per_year),
            "年化波动率": PerformanceMetrics.calculate_volatility(returns, periods_per_year),
            "最大回撤": PerformanceMetrics.calculate_max_drawdown(returns),
            "最大回撤持续期": PerformanceMetrics.calculate_max_drawdown_duration(returns),
            
            # 风险调整收益指标
            "夏普比率": PerformanceMetrics.calculate_sharpe_ratio(returns, risk_free_rate, periods_per_year),
            "索提诺比率": PerformanceMetrics.calculate_sortino_ratio(returns, risk_free_rate, periods_per_year),
            "卡尔马比率": PerformanceMetrics.calculate_calmar_ratio(returns, periods_per_year),
            
            # 交易效率指标
            "胜率": PerformanceMetrics.calculate_win_rate(returns),
            "盈亏比": PerformanceMetrics.calculate_profit_loss_ratio(returns),
            "日均交易次数": PerformanceMetrics.calculate_avg_trades_per_day(returns),
            "平均持仓时间": PerformanceMetrics.calculate_avg_holding_period(returns),
            
            # 稳定性指标
            "偏度": PerformanceMetrics.calculate_skewness(returns),
            "峰度": PerformanceMetrics.calculate_kurtosis(returns),
            "信息比率": 0.0,  # 如果有benchmark才计算
            "跟踪误差": 0.0   # 如果有benchmark才计算
        }
        
        # 如果提供了基准收益率，计算相对指标
        if benchmark_returns is not None:
            metrics.update({
                "超额收益": PerformanceMetrics.calculate_excess_return(returns, benchmark_returns),
                "信息比率": PerformanceMetrics.calculate_information_ratio(returns, benchmark_returns),
                "跟踪误差": PerformanceMetrics.calculate_tracking_error(returns, benchmark_returns),
                "Beta": PerformanceMetrics.calculate_beta(returns, benchmark_returns),
                "Alpha": PerformanceMetrics.calculate_alpha(returns, benchmark_returns, risk_free_rate)
            })
            
        return metrics

    @staticmethod
    def calculate_total_return(returns: pd.Series) -> float:
        """计算总收益率"""
        return ((1 + returns).prod() - 1) * 100

    @staticmethod
    def calculate_annual_return(returns: pd.Series, periods_per_year: int = 252) -> float:
        """计算年化收益率"""
        total_return = (1 + returns).prod() - 1
        years = len(returns) / periods_per_year
        return ((1 + total_return) ** (1 / years) - 1) * 100

    @staticmethod
    def calculate_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
        """计算年化波动率"""
        return returns.std() * np.sqrt(periods_per_year) * 100

    @staticmethod
    def calculate_max_drawdown(returns: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdowns = (cumulative - running_max) / running_max
        return abs(drawdowns.min()) * 100

    @staticmethod
    def calculate_max_drawdown_duration(returns: pd.Series) -> int:
        """计算最大回撤持续期"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdowns = (cumulative - running_max) / running_max
        
        # 找到最大回撤结束点
        end_idx = drawdowns.idxmin()
        
        # 找到该回撤的开始点
        peak_idx = running_max.loc[:end_idx].idxmax()
        
        return (end_idx - peak_idx).days

    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.Series, 
        risk_free_rate: float = 0.03,
        periods_per_year: int = 252
    ) -> float:
        """计算夏普比率"""
        excess_returns = returns - risk_free_rate/periods_per_year
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()

    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.03,
        periods_per_year: int = 252
    ) -> float:
        """计算索提诺比率"""
        excess_returns = returns - risk_free_rate/periods_per_year
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return float('inf')
        return np.sqrt(periods_per_year) * excess_returns.mean() / downside_returns.std()

    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
        """计算卡尔马比率"""
        max_dd = PerformanceMetrics.calculate_max_drawdown(returns) / 100
        if max_dd == 0:
            return float('inf')
        annual_return = PerformanceMetrics.calculate_annual_return(returns, periods_per_year) / 100
        return annual_return / max_dd

    @staticmethod
    def calculate_win_rate(returns: pd.Series) -> float:
        """计算胜率"""
        return (returns > 0).mean() * 100

    @staticmethod
    def calculate_profit_loss_ratio(returns: pd.Series) -> float:
        """计算盈亏比"""
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        if len(losses) == 0 or losses.mean() == 0:
            return float('inf')
        return abs(wins.mean() / losses.mean())

    @staticmethod
    def calculate_avg_trades_per_day(returns: pd.Series) -> float:
        """计算日均交易次数"""
        # 这里假设每个非零收益代表一次交易
        return (returns != 0).sum() / len(returns)

    @staticmethod
    def calculate_avg_holding_period(returns: pd.Series) -> float:
        """计算平均持仓时间（天）"""
        # 这里需要根据实际交易记录计算，这里只是示例
        non_zero_returns = returns[returns != 0]
        if len(non_zero_returns) == 0:
            return 0
        return len(returns) / len(non_zero_returns)

    @staticmethod
    def calculate_skewness(returns: pd.Series) -> float:
        """计算偏度"""
        return returns.skew()

    @staticmethod
    def calculate_kurtosis(returns: pd.Series) -> float:
        """计算峰度"""
        return returns.kurtosis()

    @staticmethod
    def calculate_information_ratio(returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """计算信息比率"""
        active_returns = returns - benchmark_returns
        if active_returns.std() == 0:
            return 0
        return np.sqrt(252) * active_returns.mean() / active_returns.std()

    @staticmethod
    def calculate_tracking_error(returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """计算跟踪误差"""
        active_returns = returns - benchmark_returns
        return active_returns.std() * np.sqrt(252) * 100

    @staticmethod
    def calculate_beta(returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """计算Beta值"""
        covariance = returns.cov(benchmark_returns)
        benchmark_variance = benchmark_returns.var()
        if benchmark_variance == 0:
            return 0
        return covariance / benchmark_variance

    @staticmethod
    def calculate_alpha(
        returns: pd.Series,
        benchmark_returns: pd.Series,
        risk_free_rate: float = 0.03
    ) -> float:
        """计算Alpha值"""
        beta = PerformanceMetrics.calculate_beta(returns, benchmark_returns)
        excess_return = returns.mean() * 252 - risk_free_rate
        benchmark_excess_return = benchmark_returns.mean() * 252 - risk_free_rate
        return excess_return - beta * benchmark_excess_return 

    def add_advanced_ratios(self):
        return {
            "omega比率": self.calculate_omega_ratio(),
            "特雷诺比率": self.calculate_treynor_ratio(),
            "詹森alpha": self.calculate_jensen_alpha()
        }