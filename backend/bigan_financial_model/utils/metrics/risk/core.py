"""风险指标计算模块"""
from typing import Dict, Any, List, Union, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from dataclasses import dataclass
import logging
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskCategory(Enum):
    """风险类别枚举"""
    VOLATILITY = "波动性指标"
    TAIL = "尾部风险指标"
    LIQUIDITY = "流动性指标"
    PRICE = "价格风险指标"
    STRESS = "压力测试指标"
    SYSTEMATIC = "系统性风险指标"
    OTHER = "其他指标"

@dataclass
class RiskThreshold:
    """风险阈值配置"""
    high_volatility: float = 30.0
    high_var: float = 3.0
    low_liquidity: float = 0.5
    high_drawdown: float = 20.0
    low_sharpe: float = 0.5

class RiskMetrics:
    """风险指标计算器"""
    
    def __init__(self, risk_threshold: Optional[RiskThreshold] = None):
        """
        初始化风险指标计算器
        Args:
            risk_threshold: 风险阈值配置
        """
        self.threshold = risk_threshold or RiskThreshold()
        self.metrics_cache = {}
    
    @staticmethod
    def preprocess_data(
        data: Union[pd.Series, List[float]]
    ) -> pd.Series:
        """数据预处理"""
        if isinstance(data, list):
            return pd.Series(data)
        return data
    
    def calculate_risk_metrics(
        self,
        returns: Union[pd.Series, List[float]],
        prices: Union[pd.Series, List[float]],
        volume: Union[pd.Series, List[float]],
        market_returns: Optional[pd.Series] = None,
        confidence_level: float = 0.95,
        periods_per_year: int = 252
    ) -> Dict[str, Any]:
        """计算所有风险指标"""
        try:
            logger.info("开始计算风险指标...")
            
            # 数据预处理
            returns = self.preprocess_data(returns)
            prices = self.preprocess_data(prices)
            volume = self.preprocess_data(volume)
            
            # 基础风险指标计算
            metrics = self._calculate_base_metrics(
                returns, prices, volume, 
                confidence_level, periods_per_year
            )
            
            # 系统性风险指标计算
            if market_returns is not None:
                metrics.update(self._calculate_systematic_metrics(
                    returns, market_returns
                ))
            
            # 风险评估
            metrics.update(self._evaluate_risk_levels(metrics))
            
            # 缓存结果
            self.metrics_cache = metrics
            
            logger.info("风险指标计算完成")
            return metrics
            
        except Exception as e:
            logger.error(f"计算风险指标时出错: {str(e)}")
            raise
    
    def _calculate_base_metrics(
        self,
        returns: pd.Series,
        prices: pd.Series,
        volume: pd.Series,
        confidence_level: float,
        periods_per_year: int
    ) -> Dict[str, Any]:
        """计算基础风险指标"""
        try:
            logger.info("开始计算基础风险指标...")
            metrics = {
                RiskCategory.VOLATILITY.value: {
                    "波动率": self.calculate_volatility(returns, periods_per_year),
                    "下行波动率": self.calculate_downside_volatility(returns, periods_per_year),
                    "上行波动率": self.calculate_upside_volatility(returns, periods_per_year),
                    "波动率偏斜度": self.calculate_volatility_skew(returns),
                    "波动率峰度": self.calculate_volatility_kurtosis(returns),
                },
                RiskCategory.TAIL.value: {
                    "VaR": self.calculate_var(returns, confidence_level),
                    "CVaR": self.calculate_cvar(returns, confidence_level),
                    "尾部风险比率": self.calculate_tail_ratio(returns),
                    "最大连续亏损天数": self.calculate_max_consecutive_losses(returns),
                }
            }
            logger.info("基础风险指标计算完成")
            return metrics
        except Exception as e:
            logger.error(f"计算基础风险指标时出错: {str(e)}")
            raise
    
    def _evaluate_risk_levels(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """
        评估风险水平
        
        Args:
            metrics: 风险指标字典
            
        Returns:
            Dict[str, str]: 风险等级评估结果
        """
        try:
            logger.info("开始评估风险水平...")
            
            # 获取各类指标值
            volatility = metrics[RiskCategory.VOLATILITY.value]["波动率"]
            var = metrics[RiskCategory.TAIL.value]["VaR"]
            cvar = metrics[RiskCategory.TAIL.value]["CVaR"]
            
            risk_levels = {
                "波动率风险等级": self._get_risk_level(
                    volatility,
                    self.threshold.high_volatility
                ),
                "VaR风险等级": self._get_risk_level(
                    var,
                    self.threshold.high_var
                ),
                "CVaR风险等级": self._get_risk_level(
                    cvar,
                    self.threshold.high_var * 1.2  # CVaR阈值略高于VaR
                ),
            }
            
            # 添加综合风险评估
            risk_scores = {
                "高": 3,
                "中": 2,
                "低": 1
            }
            
            avg_score = np.mean([risk_scores[level] for level in risk_levels.values()])
            risk_levels["综合风险等级"] = (
                "高" if avg_score > 2.5 else
                "中" if avg_score > 1.5 else
                "低"
            )
            
            logger.info("风险等级评估完成")
            return risk_levels
            
        except KeyError as e:
            logger.error(f"评估风险等级时找不到指标: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"评估风险等级时出错: {str(e)}")
            raise
    
    def _get_risk_level(self, value: float, threshold: float) -> str:
        """
        获取风险等级
        
        Args:
            value: 指标值
            threshold: 阈值
            
        Returns:
            str: 风险等级（高/中/低）
        """
        if value > threshold:
            return "高"
        elif value > threshold / 2:
            return "中"
        else:
            return "低"
    
    def generate_risk_report(self) -> str:
        """生成风险报告"""
        if not self.metrics_cache:
            raise ValueError("请先计算风险指标")
        
        report = ["风险分析报告", "=" * 50, ""]
        
        # 添加风险等级评估
        risk_levels = self._evaluate_risk_levels(self.metrics_cache)
        report.extend([
            "风险等级评估:",
            *[f"{k}: {v}" for k, v in risk_levels.items()],
            ""
        ])
        
        # 添加详细指标
        for category in RiskCategory:
            if category.value in self.metrics_cache:
                report.extend([
                    f"{category.value}:",
                    *[f"  {k}: {v:.2f}" if isinstance(v, (int, float)) else f"  {k}: {v}"
                      for k, v in self.metrics_cache[category.value].items()],
                    ""
                ])
        
        return "\n".join(report)
    
    def calculate_volatility(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """计算波动率"""
        return returns.std() * np.sqrt(periods_per_year) * 100
    
    def calculate_downside_volatility(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """计算下行波动率"""
        downside_returns = returns[returns < 0]
        return downside_returns.std() * np.sqrt(periods_per_year) * 100
    
    def calculate_upside_volatility(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        """计算上行波动率"""
        upside_returns = returns[returns > 0]
        return upside_returns.std() * np.sqrt(periods_per_year) * 100
    
    def calculate_volatility_skew(self, returns: pd.Series) -> float:
        """计算波动率偏斜度"""
        return stats.skew(returns)
    
    def calculate_volatility_kurtosis(self, returns: pd.Series) -> float:
        """计算波动率峰度"""
        return stats.kurtosis(returns)
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """计算VaR"""
        return abs(np.percentile(returns, (1 - confidence_level) * 100))
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """计算CVaR"""
        var = self.calculate_var(returns, confidence_level)
        return abs(returns[returns <= -var].mean())
    
    def calculate_tail_ratio(self, returns: pd.Series) -> float:
        """计算尾部风险比率"""
        return abs(np.percentile(returns, 95) / np.percentile(returns, 5))
    
    def calculate_max_consecutive_losses(self, returns: pd.Series) -> int:
        """计算最大连续亏损天数"""
        losses = returns < 0
        max_consecutive = 0
        current_consecutive = 0
        
        for loss in losses:
            if loss:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_systematic_metrics(
        self,
        returns: pd.Series,
        market_returns: pd.Series
    ) -> Dict[str, Any]:
        """
        计算系统性风险指标
        
        Args:
            returns: 收益率序列
            market_returns: 市场收益率序列
            
        Returns:
            Dict[str, Any]: 系统性风险指标字典
        """
        try:
            logger.info("开始计算系统性风险指标...")
            
            metrics = {
                RiskCategory.SYSTEMATIC.value: {
                    "系统性风险": self.calculate_systematic_risk(returns, market_returns),
                    "特质性风险": self.calculate_idiosyncratic_risk(returns, market_returns),
                    "Beta波动率": self.calculate_beta_volatility(returns, market_returns),
                    **self.calculate_correlation_metrics(returns, market_returns)
                }
            }
            
            logger.info("系统性风险指标计算完成")
            return metrics
            
        except Exception as e:
            logger.error(f"计算系统性风险指标时出错: {str(e)}")
            raise
    
    def calculate_systematic_risk(
        self, 
        returns: pd.Series, 
        market_returns: pd.Series
    ) -> float:
        """计算系统性风险"""
        beta = returns.cov(market_returns) / market_returns.var()
        return (beta * market_returns.std()) ** 2
    
    def calculate_idiosyncratic_risk(
        self, 
        returns: pd.Series, 
        market_returns: pd.Series
    ) -> float:
        """计算特质性风险"""
        total_risk = returns.var()
        systematic_risk = self.calculate_systematic_risk(returns, market_returns)
        return np.sqrt(total_risk - systematic_risk) * 100
    
    def calculate_beta_volatility(
        self, 
        returns: pd.Series, 
        market_returns: pd.Series, 
        window: int = 20
    ) -> float:
        """
        计算Beta波动率
        
        Args:
            returns: 收益率序列
            market_returns: 市场收益率序列
            window: 滚动窗口大小
            
        Returns:
            float: Beta波动率
        """
        rolling_beta = returns.rolling(window).cov(market_returns) / \
                      market_returns.rolling(window).var()
        return rolling_beta.std() * 100
    
    def calculate_correlation_metrics(
        self, 
        returns: pd.Series, 
        market_returns: pd.Series
    ) -> Dict[str, float]:
        """
        计算相关性指标
        
        Args:
            returns: 收益率序列
            market_returns: 市场收益率序列
            
        Returns:
            Dict[str, float]: 相关性指标字典
        """
        return {
            "与市场相关性": returns.corr(market_returns),
            "条件相关性（熊市）": returns[market_returns < 0].corr(
                market_returns[market_returns < 0]
            ),
            "条件相关性（牛市）": returns[market_returns > 0].corr(
                market_returns[market_returns > 0]
            ),
        }
    
    def add_advanced_metrics(self):
        return {
            "信息比率": self.calculate_information_ratio(),
            "夏普比率": self.calculate_sharpe_ratio(),
            "索提诺比率": self.calculate_sortino_ratio(),
            "最大回撤": self.calculate_max_drawdown()
        }

@dataclass
class RiskReport:
    """风险报告类"""
    
    @staticmethod
    def generate_report(metrics: Dict[str, Any]) -> str:
        """生成风险报告"""
        report = ["风险分析报告", "=" * 50, ""]
        
        # 添加风险等级评估
        report.extend([
            "风险等级评估:",
            f"波动率风险: {metrics.get('波动率风险等级', 'N/A')}",
            f"VaR风险: {metrics.get('VaR风险等级', 'N/A')}",
            f"CVaR风险: {metrics.get('CVaR风险等级', 'N/A')}",
            ""
        ])
        
        # 添加详细指标
        for category in RiskCategory:
            if category.value in metrics:
                report.extend([
                    f"{category.value}:",
                    *[f"  {k}: {v:.2f}" if isinstance(v, (int, float)) else f"  {k}: {v}"
                      for k, v in metrics[category.value].items()],
                    ""
                ])
        
        return "\n".join(report)

class DynamicThreshold:
    def __init__(self, base_value: float, market_sensitivity: float,
                 min_value: float, max_value: float):
        self.base_value = base_value
        self.market_sensitivity = market_sensitivity
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = base_value
        
    def adjust(self, market_condition: float):
        """根据市场条件调整阈值"""
        adjustment = (market_condition - 0.5) * self.market_sensitivity
        new_value = self.base_value + adjustment
        
        # 确保值在允许范围内
        self.current_value = max(min(new_value, self.max_value), self.min_value)
        return self.current_value

if __name__ == '__main__':
    # 测试代码
    try:
        # 创建风险计算器实例
        risk_calculator = RiskMetrics()
        
        # 生成测试数据
        np.random.seed(42)
        sample_size = 252
        
        test_data = {
            'returns': pd.Series(np.random.normal(0.0001, 0.02, sample_size)),
            'prices': pd.Series(100 * (1 + pd.Series(np.random.normal(0.0001, 0.02, sample_size))).cumprod()),
            'volume': pd.Series(np.random.lognormal(10, 1, sample_size)),
            'market_returns': pd.Series(np.random.normal(0.0002, 0.015, sample_size))
        }
        
        # 计算风险指标
        metrics = risk_calculator.calculate_risk_metrics(**test_data)
        
        # 生成并打印报告
        print(risk_calculator.generate_risk_report())
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise