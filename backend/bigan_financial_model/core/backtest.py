"""
回测引擎模块

实现了一个完整的回测系统,包含以下功能:
- 支持多种交易策略回测
- 提供详细的绩效分析
- 包含风险管理功能
- 可视化分析结果
- 支持自定义指标计算

参数:
    config: 配置字典,包含回测参数
    analyzer: 市场分析器实例(可选)

作者: BiGan团队
日期: 2024-01
"""

"""回测引擎模块"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from datetime import datetime
import matplotlib.pyplot as plt

from bigan_financial_model.analysis import MarketAnalyzer
from bigan_financial_model.utils.metrics import calculate_metrics

logger = logging.getLogger(__name__)

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital=100000, commission=0.001, slippage=0.001):
        """初始化回测引擎
        
        Args:
            initial_capital (float): 初始资金
            commission (float): 手续费率
            slippage (float): 滑点率
        """
        # 基础参数
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.portfolio_value = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # 持仓管理
        self.positions = []  # 改用列表而不是字典
        self.max_positions = 5
        
        # 风险参数
        self.risk_params = {
            'stop_loss': 0.02,        # 止损比例
            'take_profit': 0.05,      # 止盈比例
            'max_position_size': 0.3,  # 单个持仓最大比例
            'risk_per_trade': 0.01    # 每笔交易风险比例
        }
        
        # 初始化统计数据
        self.stats = {
            'total_trades': 0,         # 总交易次数
            'winning_trades': 0,       # 盈利交易次数
            'losing_trades': 0,        # 亏损交易次数
            'total_profit': 0.0,       # 总盈利
            'total_loss': 0.0,         # 总亏损
            'max_drawdown': 0.0,       # 最大回撤
            'peak_value': initial_capital,  # 峰值
            'portfolio_values': [],     # 组合价值历史
            'daily_returns': [],        # 日收益率
            'positions_history': []     # 持仓历史
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"回测引擎初始化完成: 初始资金={initial_capital}, 手续费率={commission}, 滑点率={slippage}")

    def run(self, data):
        """运行回测
        
        Args:
            data (pd.DataFrame): 回测数据
            
        Returns:
            dict: 回测结果统计
        """
        try:
            self.logger.info(f"开始回测: 数据长度={len(data)}")
            results = []
            
            # 遍历每个交易日
            for i in range(len(data)):
                # 获取当日数据
                current_data = data.iloc[i]
                current_price = current_data['close']
                current_date = data.index[i]
                
                # 更新持仓状态
                self._update_positions(current_price)
                
                # 检查止损止盈
                self._check_stop_conditions(current_price)
                
                # 生成交易信号
                signals = self._calculate_signals(data, i)
                
                # 执行交易
                if len(self.positions) < self.max_positions:
                    self._execute_trades(current_price, signals, current_date)
                
                # 记录每日结果
                daily_result = {
                    'date': current_date,
                    'portfolio_value': self.calculate_portfolio_value(current_price),
                    'cash': self.cash,
                    'positions': len(self.positions),
                    'price': current_price
                }
                results.append(daily_result)
                
                # 更新统计数据
                self._update_stats(daily_result)
            
            return self._process_final_results(results)
            
        except Exception as e:
            self.logger.error(f"回测执行失败: {str(e)}")
            raise

    def calculate_portfolio_value(self, current_price):
        """计算当前组合价值"""
        position_value = sum(pos['size'] * current_price for pos in self.positions)
        return self.cash + position_value

    def _calculate_signals(self, data, index):
        """计算交易信号
        
        Args:
            data (pd.DataFrame): 历史数据
            index (int): 当前索引
            
        Returns:
            dict: 交易信号字典
        """
        try:
            signals = {}
            
            # 计算趋势信号
            if 'sma_20' in data.columns and 'sma_50' in data.columns:
                sma_20 = data['sma_20'].iloc[index]
                sma_50 = data['sma_50'].iloc[index]
                signals['trend'] = 1 if sma_20 > sma_50 else -1
            
            # 计算动量信号
            if 'rsi_14' in data.columns:
                rsi = data['rsi_14'].iloc[index]
                signals['momentum'] = 1 if rsi > 50 else -1
            
            # 计算波动率信号
            if 'macd' in data.columns:
                macd = data['macd'].iloc[index]
                signals['volatility'] = abs(macd)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"信号计算失败: {str(e)}")
            return {'trend': 0, 'momentum': 0, 'volatility': 0}

    def _update_stats(self, daily_result):
        """更新统计数据"""
        try:
            # 更新最大回撤
            self.stats['peak_value'] = max(self.stats['peak_value'], daily_result['portfolio_value'])
            current_drawdown = (self.stats['peak_value'] - daily_result['portfolio_value']) / self.stats['peak_value']
            self.stats['max_drawdown'] = max(self.stats['max_drawdown'], current_drawdown)
            
            # 计算日收益率
            if len(self.stats['portfolio_values']) > 0:
                prev_value = self.stats['portfolio_values'][-1]
                daily_return = (daily_result['portfolio_value'] - prev_value) / prev_value
                self.stats['daily_returns'].append(daily_return)
            
            self.stats['portfolio_values'].append(daily_result['portfolio_value'])
            
        except Exception as e:
            self.logger.error(f"统计数据更新失败: {str(e)}")

    def _execute_trades(self, current_price, signals, current_date):
        """执行交易决策
        
        Args:
            current_price (float): 当前价格
            signals (dict): 交易信号
            current_date: 当前日期
        """
        try:
            # 从信号字典中获取具体的交易方向
            trade_direction = self._get_trade_direction(signals)
            
            if trade_direction != 0:  # 0表示不交易
                # 考虑滑点的实际成交价格
                execution_price = current_price * (1 + self.slippage * (1 if trade_direction > 0 else -1))
                
                # 计算交易规模
                position_size = self._calculate_position_size(execution_price)
                
                if position_size > 0:
                    # 计算手续费
                    commission_cost = position_size * self.commission
                    
                    # 检查是否有足够的资金（包括手续费）
                    if self.cash >= (position_size + commission_cost):
                        self._open_position(trade_direction, execution_price, position_size, current_date)
                        self.cash -= commission_cost
                        
        except Exception as e:
            self.logger.error(f"交易执行失败: {str(e)}")

    def _get_trade_direction(self, signals):
        """从信号字典中获取交易方向
        
        Args:
            signals (dict): 交易信号字典
            
        Returns:
            int: 交易方向 (1: 买入, -1: 卖出, 0: 不交易)
        """
        try:
            # 如果signals是简单数值
            if isinstance(signals, (int, float)):
                return int(signals)
                
            # 如果signals是字典，解析交易信号
            if isinstance(signals, dict):
                # 示例：根据技术指标组合判断
                trend = signals.get('trend', 0)
                momentum = signals.get('momentum', 0)
                volatility = signals.get('volatility', 0)
                
                # 综合信号判断
                if trend > 0 and momentum > 0 and volatility < 0.5:
                    return 1  # 买入信号
                elif trend < 0 and momentum < 0:
                    return -1  # 卖出信号
                    
            return 0  # 默认不交易
            
        except Exception as e:
            self.logger.error(f"信号解析失败: {str(e)}")
            return 0

    def _update_positions(self, current_price):
        """更新持仓状态"""
        for position in self.positions:
            # 计算当前收益
            price_change = (current_price - position['entry_price']) / position['entry_price']
            position['current_price'] = current_price
            position['profit_loss'] = price_change * position['size'] * (1 if position['direction'] == 1 else -1)

    def _check_stop_conditions(self, current_price):
        """检查止损止盈条件"""
        positions_to_remove = []  # 创建要移除的持仓列表
        
        for position in self.positions:
            # 计算收益率
            price_change = (current_price - position['entry_price']) / position['entry_price']
            
            # 止损检查
            if (position['direction'] == 1 and price_change <= -self.risk_params['stop_loss']) or \
               (position['direction'] == -1 and price_change >= self.risk_params['stop_loss']):
                positions_to_remove.append((position, 'stop_loss'))
                continue
                
            # 止盈检查
            if (position['direction'] == 1 and price_change >= self.risk_params['take_profit']) or \
               (position['direction'] == -1 and price_change <= -self.risk_params['take_profit']):
                positions_to_remove.append((position, 'take_profit'))
        
        # 在循环外处理平仓
        for position, reason in positions_to_remove:
            self._close_position(position, current_price, reason)

    def _generate_trade_decision(self, signals):
        """生成交易决策"""
        try:
            # 信号权重
            weights = {
                'trend': 0.4,
                'momentum': 0.3,
                'macd': 0.3
            }
            
            # 计算加权信号
            total_signal = 0
            for signal_type, signal in signals.items():
                if signal_type in weights:
                    total_signal += signal * weights[signal_type]
            
            # 设置信号阈值
            if total_signal > 0.3:
                return 1  # 买入信号
            elif total_signal < -0.3:
                return -1  # 卖出信号
            return 0  # 不操作
            
        except Exception as e:
            self.logger.error(f"交易决策生成失败: {str(e)}")
            return 0

    def _calculate_position_size(self, price):
        """计算仓位大小，考虑手续费和滑点"""
        try:
            # 基础仓位大小
            position_size = self.portfolio_value * self.risk_params['risk_per_trade']
            
            # 考虑手续费和滑点的总成本
            total_cost_ratio = self.commission + self.slippage
            
            # 调整仓位大小
            adjusted_size = position_size / (1 + total_cost_ratio)
            
            # 确保不超过最大仓位限制
            max_position_size = self.portfolio_value * self.risk_params['max_position_size']
            return min(adjusted_size, max_position_size)
            
        except Exception as e:
            self.logger.error(f"仓位计算失败: {str(e)}")
            return 0

    def _open_position(self, direction, price, size, date):
        """开仓"""
        try:
            # 创建新仓位
            position = {
                'direction': direction,
                'entry_price': price,
                'size': size,
                'entry_date': date,
                'current_price': price,
                'profit_loss': 0
            }
            
            # 更新资金
            self.cash -= size
            self.positions.append(position)
            
            # 记录交易
            self.stats['total_trades'] += 1
            
            self.logger.info(f"开仓: 方向={direction}, 价格={price:.2f}, 大小={size:.2f}")
            
        except Exception as e:
            self.logger.error(f"开仓失败: {str(e)}")

    def _close_position(self, position, price, reason):
        """平仓"""
        try:
            # 计算收益
            profit_loss = position['profit_loss']
            
            # 更新资金
            self.cash += position['size'] + profit_loss
            self.positions.remove(position)
            
            # 更新统计
            if profit_loss > 0:
                self.stats['winning_trades'] += 1
                self.stats['total_profit'] += profit_loss
            else:
                self.stats['losing_trades'] += 1
                self.stats['total_loss'] += abs(profit_loss)
                
            self.logger.info(f"平仓: 价格={price:.2f}, 收益={profit_loss:.2f}, 原因={reason}")
            
        except Exception as e:
            self.logger.error(f"平仓失败: {str(e)}")

    def _process_final_results(self, results):
        """处理最终回测结果"""
        try:
            # 计算关键指标
            total_return = (self.portfolio_value - self.initial_capital) / self.initial_capital
            win_rate = self.stats['winning_trades'] / self.stats['total_trades'] if self.stats['total_trades'] > 0 else 0
            
            # 计算夏普比率
            if len(self.stats['daily_returns']) > 0:
                returns_array = np.array(self.stats['daily_returns'])
                sharpe_ratio = np.sqrt(252) * (returns_array.mean() / returns_array.std()) if returns_array.std() != 0 else 0
            else:
                sharpe_ratio = 0
            
            return {
                'total_return': total_return,
                'win_rate': win_rate,
                'max_drawdown': self.stats['max_drawdown'],
                'total_trades': self.stats['total_trades'],
                'winning_trades': self.stats['winning_trades'],
                'losing_trades': self.stats['losing_trades'],
                'total_profit': self.stats['total_profit'],
                'total_loss': self.stats['total_loss'],
                'sharpe_ratio': sharpe_ratio,
                'final_portfolio_value': self.portfolio_value,
                'daily_portfolio_values': self.stats['portfolio_values']
            }
            
        except Exception as e:
            self.logger.error(f"结果处理失败: {str(e)}")
            return {}