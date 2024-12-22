"""
性能分析模块
负责计算和分析交易策略的各项性能指标
包括总收益率、年化收益、夏普比率、最大回撤和胜率等
"""

import numpy as np
import pandas as pd

class PerformanceAnalyzer:
    def __init__(self):
        self.logger = setup_logger()
        
    def calculate_metrics(self, portfolio: pd.DataFrame):
        """
        计算关键性能指标
        """
        try:
            metrics = {
                "总收益率": self._calculate_total_return(portfolio),
                "年化收益": self._calculate_annual_return(portfolio),
                "夏普比率": self._calculate_sharpe_ratio(portfolio),
                "最大回撤": self._calculate_max_drawdown(portfolio),
                "胜率": self._calculate_win_rate(portfolio)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"性能指标计算出错: {str(e)}")
            raise 