"""风险报告生成器"""
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd

@dataclass
class RiskReport:
    """风险报告类"""
    
    @staticmethod
    def generate_report(returns: pd.Series, market_returns: pd.Series) -> str:
        """生成风险报告"""
        from .risk import RiskMetrics
        
        metrics = RiskMetrics.calculate_risk_metrics(returns)
        report = ["风险分析报告", "=" * 50]
        
        # 添加各类指标
        report.extend([
            f"波动率风险: {metrics['波动率']:.2f}%",
            f"下行风险: {metrics['下行波动率']:.2f}%",
            f"VaR (95%): {metrics['VaR']:.2f}%",
            f"最大回撤: {metrics['最大回撤']:.2f}%",
        ])
        
        return "\n".join(report) 