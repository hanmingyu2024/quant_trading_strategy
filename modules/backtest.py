"""
回测模块

功能:
- 运行策略回测
- 模拟交易执行
- 计算回测性能指标
- 保存回测结果

作者: Han Mingyu
邮箱: 13364694109ai@gmail.com
"""

from datetime import datetime
import pandas as pd
import numpy as np
from modules.data_handler import DataHandler
from modules.strategy import Strategy
from modules.logger import setup_logger

class Backtester:
    def __init__(self, mt5_connector, symbol: str, start_date: datetime, end_date: datetime, count: int):
        self.logger = setup_logger(name="backtest")
        self.data_handler = DataHandler(mt5_connector)
        self.strategy = Strategy()
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.count = count
        
    def run_backtest(self, 
                    symbol: str,
                    start_date: datetime,
                    end_date: datetime,
                    initial_capital: float = 100000,
                    count: int = 1000):
        """
        运行回测
        """
        try:
            # 获取历史数据
            historical_data = self.data_handler.get_historical_data(
                symbol, start_date, end_date, count
            )
            
            # 输出历史数据的基本信息
            self.logger.info(f"获取到的历史数据行数: {len(historical_data)}")
            self.logger.info(f"数据列名: {historical_data.columns}")
            
            # 检查 'close' 列是否存在
            if 'close' not in historical_data.columns:
                self.logger.error("历史数据中缺少 'close' 列")
                raise ValueError("历史数据中缺少 'close' 列")
            
            # 清洗数据，去除缺失值
            historical_data.dropna(inplace=True)
            
            # 添加日志记录以检查清洗后的数据
            self.logger.info(f"清洗后数据行数: {len(historical_data)}")
            self.logger.info(f"清洗后数据列名: {historical_data.columns}")
            
            # 运行策略
            signals = self.strategy.generate_signals(historical_data)
            
            # 检查 signals 是否有效
            if signals is None or signals.empty:
                raise ValueError("生成的交易信号无效")
            
            # 模拟交易
            portfolio = self.simulate_trades(signals, initial_capital)
            
            # 计算性能指标
            performance = self.calculate_performance(portfolio)
            
            # 保存回测结果
            self.save_results(performance)
            
            return performance
            
        except Exception as e:
            self.logger.error(f"回测过程出错: {str(e)}")
            raise 

    def simulate_trades(self, signals: pd.DataFrame, initial_capital: float):
        """模拟交易执行"""
        # 获取原始数据时，确保传递所有必要的参数
        historical_data = self.data_handler.get_historical_data(
            symbol=self.symbol,
            start_date=self.start_date,
            end_date=self.end_date,
            count=self.count
        )
        
        # 将 signals 和 historical_data 合并，以确保包含 'close' 列
        signals = signals.join(historical_data['close'], how='left')

        portfolio = pd.DataFrame()
        position = 0
        capital = initial_capital
        trades = []
        stop_loss = 0.05  # 5% stop loss
        take_profit = 0.1  # 10% take profit
        
        for index, row in signals.iterrows():
            if row['signal'] == 1 and position <= 0:  # 买入信号
                position = capital / row['close']  # 计算可买入数量
                entry_price = row['close']
                trades.append({
                    'date': index,
                    'type': 'BUY',
                    'price': entry_price,
                    'size': position,
                    'capital': capital
                })
                
            elif row['signal'] == -1 and position > 0:  # 卖出信号
                profit = position * (row['close'] - entry_price)
                capital += profit
                position = 0
                trades.append({
                    'date': index,
                    'type': 'SELL',
                    'price': row['close'],
                    'profit': profit,
                    'capital': capital
                })
            
            # Implement stop loss and take profit
            if position > 0:
                if (row['close'] <= entry_price * (1 - stop_loss)) or (row['close'] >= entry_price * (1 + take_profit)):
                    profit = position * (row['close'] - entry_price)
                    capital += profit
                    position = 0
                    trades.append({
                        'date': index,
                        'type': 'SELL',
                        'price': row['close'],
                        'profit': profit,
                        'capital': capital
                    })
        
        return pd.DataFrame(trades)

    def calculate_performance(self, portfolio: pd.DataFrame) -> dict:
        """
        计算回测的性能指标
        """
        # 示例性能指标计算
        total_return = (portfolio['capital'].iloc[-1] - portfolio['capital'].iloc[0]) / portfolio['capital'].iloc[0]
        num_trades = len(portfolio)
        performance = {
            'total_return': total_return,
            'num_trades': num_trades
        }
        self.logger.info(f"计算的性能指标: {performance}")
        return performance

    def save_results(self, performance: dict):
        """
        保存回测结果
        """
        # 这里可以实现保存结果的逻辑，比如保存到文件或数据库
        self.logger.info(f"保存回测结果: {performance}")
        # 示例：将结果保存到一个 JSON 文件
        import json
        with open('backtest_results.json', 'w') as f:
            json.dump(performance, f)

if __name__ == "__main__":
    # 创建 MT5 连接器实例
    from modules.mt5_connector import MT5Connector
    mt5_connector = MT5Connector()
    
    # 确保MT5成功连接
    if not mt5_connector.initialize():
        print("MT5连接失败，请检查MetaTrader 5是否正在运行")
        exit()
    
    # 设置回测参数
    symbol = "XAUUSD"  # 现货黄金
    start_date = datetime(2011, 12, 29)  # 从2023年开始
    end_date = datetime(2024, 12, 17)    # 到现在
    initial_capital = 1000000          # 初始资金100万
    count = 1000  # 假设需要的历史数据行数
    
    # 创建回测器实例
    backtester = Backtester(mt5_connector, symbol, start_date, end_date, count)
    
    # 运行回测
    try:
        results = backtester.run_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        
        print("回测结果:", results)
        
    except Exception as e:
        print(f"回测过程出错: {str(e)}")