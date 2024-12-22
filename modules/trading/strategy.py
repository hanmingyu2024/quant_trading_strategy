"""
策略模块
负责计算技术指标、生成交易信号和计算仓位大小
包含MA、RSI和布林带等技术分析指标
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from modules.logger import setup_logger

logger = setup_logger('strategy')

class BaseStrategy:
    def __init__(self, data_handler, trade_executor):
        self.data_handler = data_handler
        self.trade_executor = trade_executor
        
    def calculate_indicators(self, df):
        """计算技术指标"""
        try:
            # 确保数据量足够
            if len(df) < 50:
                logger.error("数据量不足以计算技术指标")
                return pd.DataFrame()  # 返回空的DataFrame
            
            # 计算MA
            df['MA20'] = df['close'].rolling(window=20, min_periods=1).mean()
            df['MA50'] = df['close'].rolling(window=50, min_periods=1).mean()
            
            # 计算RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 计算布林带
            df['BB_middle'] = df['close'].rolling(window=20).mean()
            df['BB_upper'] = df['BB_middle'] + 2 * df['close'].rolling(window=20).std()
            df['BB_lower'] = df['BB_middle'] - 2 * df['close'].rolling(window=20).std()
            
            return df.dropna()  # 去除NaN行
            
        except Exception as e:
            logger.error(f"计算指标时出错: {str(e)}")
            return pd.DataFrame()  # 返回空的DataFrame
    
    def check_signals(self, df):
        """检查交易信号"""
        try:
            if len(df) < 2:
                logger.error("数据量不足以检查信号")
                return []
            
            signals = []
            
            # 最新的K线数据
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # MA交叉信号
            if prev['MA20'] < prev['MA50'] and latest['MA20'] > latest['MA50']:
                signals.append(('BUY', 'MA交叉向上'))
            elif prev['MA20'] > prev['MA50'] and latest['MA20'] < latest['MA50']:
                signals.append(('SELL', 'MA交叉向下'))
                
            # RSI超买超卖信号
            if latest['RSI'] < 30:
                signals.append(('BUY', 'RSI超卖'))
            elif latest['RSI'] > 70:
                signals.append(('SELL', 'RSI超买'))
                
            # 布林带信号
            if latest['close'] < latest['BB_lower']:
                signals.append(('BUY', '布林带下轨支撑'))
            elif latest['close'] > latest['BB_upper']:
                signals.append(('SELL', '布林带上轨压力'))
                
            return signals
            
        except Exception as e:
            logger.error(f"检查信号时出错: {str(e)}")
            return []
    
    def calculate_position_size(self, symbol, risk_percent=0.02):
        """计算仓位大小"""
        try:
            account_info = self.trade_executor.mt5_connector.get_account_info()
            if not account_info:
                return None
                
            symbol_info = self.data_handler.get_symbol_info(symbol)
            if not symbol_info:
                return None
                
            # 计算每点价值
            point_value = symbol_info['point']
            
            # 假设使用50点止损
            stop_loss_points = 50
            
            # 计算可承受的损失金额
            risk_amount = account_info['balance'] * risk_percent
            
            # 计算合适的交易量
            position_size = risk_amount / (stop_loss_points * point_value)
            
            # 确保不超过最小交易量
            position_size = max(0.01, round(position_size, 2))
            
            return position_size
            
        except Exception as e:
            logger.error(f"计算仓位大小时出错: {str(e)}")
            return None

class Strategy:
    def __init__(self):
        self.logger = setup_logger(name="strategy")

    def generate_signals(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        """
        logger = setup_logger(name="strategy")
        logger.info(f"传入数据列名: {historical_data.columns}")
        logger.info(f"传入数据前几行: {historical_data.head()}")

        # 确保 'close' 列存在
        if 'close' not in historical_data.columns:
            logger.error("数据中缺少 'close' 列")
            raise ValueError("数据中缺少 'close' 列")
        
        # 生成信号的逻辑
        signals = pd.DataFrame(index=historical_data.index)
        signals['signal'] = 0  # 默认信号为0
        short_window = 40
        long_window = 100
        signals['short_mavg'] = historical_data['close'].rolling(window=short_window, min_periods=1).mean()
        signals['long_mavg'] = historical_data['close'].rolling(window=long_window, min_periods=1).mean()
        
        # 使用 .loc 进行赋值以避免警告
        signals.loc[signals.index[short_window:], 'signal'] = np.where(
            signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1, 0
        )
        signals['positions'] = signals['signal'].diff()

        # 添加日志记录以检查信号生成后的数据
        logger.info(f"生成的信号数据列名: {signals.columns}")
        logger.info(f"生成的信号数据前几行: {signals.head()}")

        return signals

def get_sufficient_data(data_handler, symbol, timeframe, min_data_points=50):
    """使用二分法自动获取足够的数据"""
    total_data = pd.DataFrame()
    max_attempts = 10  # 最大尝试次数，防止无限循环
    attempt = 0

    # 假设我们从当前时间开始向过去请求数据
    end_time = pd.Timestamp.now()
    start_time = end_time - pd.Timedelta(days=365)  # 初始时间范围为过去一年

    while len(total_data) < min_data_points and attempt < max_attempts:
        attempt += 1
        logger.info(f"尝试获取数据: 第 {attempt} 次")

        # 获取数据
        df = data_handler.get_historical_data(
            symbol,
            timeframe,
            start_time,
            end_time
        )

        if df is not None and not df.empty:
            total_data = pd.concat([df, total_data]).drop_duplicates().sort_index()
            logger.info(f"当前数据量: {len(total_data)}")

            if len(total_data) < min_data_points:
                # 如果数据量不足，扩大时间范围
                start_time -= pd.Timedelta(days=365)  # 向过去再请求一年数据
            else:
                break
        else:
            logger.warning("未能获取到数据，可能是数据源问题")
            break

    if len(total_data) < min_data_points:
        logger.error("无法获取足够的数据")
    else:
        logger.info("成功获取到足够的数据")

    return total_data

if __name__ == "__main__":
    from mt5_connector import MT5Connector
    from data_handler import DataHandler
    from trade_executor import TradeExecutor
    
    # 创建MT5连接
    connector = MT5Connector()
    if connector.connect():
        try:
            # 创建必要的实例
            data_handler = DataHandler(connector)
            trade_executor = TradeExecutor(connector)
            strategy = BaseStrategy(data_handler, trade_executor)
            
            # 自动获取足够的数据
            df = get_sufficient_data(data_handler, "XAUUSD", mt5.TIMEFRAME_M5)
            
            if df is not None and not df.empty:
                print(f"获取到的数据量: {len(df)}")  # 输出数据量
                print(df.head())  # 输出数据的前几行
                
                # 计算指标
                df = strategy.calculate_indicators(df)
                
                if df.empty:
                    logger.error("指标计算失败，数据不足")
                else:
                    print("\n=== 最新指标数据 ===")
                    latest = df.iloc[-1]
                    print(f"MA20: {latest['MA20']:.3f}")
                    print(f"MA50: {latest['MA50']:.3f}")
                    print(f"RSI: {latest['RSI']:.2f}")
                    print(f"布林带上轨: {latest['BB_upper']:.3f}")
                    print(f"布林带中轨: {latest['BB_middle']:.3f}")
                    print(f"布林带下轨: {latest['BB_lower']:.3f}")
                    
                    # 检查信号
                    signals = strategy.check_signals(df)
                    print("\n=== 交易信号 ===")
                    for direction, reason in signals:
                        print(f"{direction}: {reason}")
                    
                    # 计算建议仓位
                    position_size = strategy.calculate_position_size("SPT_DXY")
                    print(f"\n建议交易量: {position_size}")
            else:
                logger.error("未能获取到足够的数据")
                
        except Exception as e:
            logger.error(f"测试过程出错: {str(e)}")
            
        finally:
            connector.close()
    else:
        print("MT5连接失败")
