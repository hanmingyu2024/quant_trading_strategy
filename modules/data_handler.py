"""
数据处理模块
负责从MT5获取历史数据和交易品种信息
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from modules.logger import setup_logger
from modules.mt5_connector import MT5Connector

logger = setup_logger('data_handler')


class DataHandler:
    def __init__(self, mt5_connector):
        self.mt5_connector = mt5_connector
        self.logger = setup_logger('data_handler')
        
    def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime, count: int):
        """获取历史数据"""
        try:
            if not self.mt5_connector.is_connected():
                self.logger.error("MT5未连接")
                raise ConnectionError("MT5未连接，请确保MetaTrader 5正在运行")
            
            data = self.mt5_connector.get_historical_data(
                symbol, 
                start_date, 
                end_date, 
                count
            )
            if data is None or len(data) == 0:
                raise ValueError(f"未能获取到{symbol}的历史数据")
            
            return data
        
        except Exception as e:
            self.logger.error(f"获取历史数据失败: {str(e)}")
            raise
    
    def get_symbol_info(self, symbol):
        """获取交易品种信息"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            self.logger.error(f"获取{symbol}信息失败")
            return None
            
        return {
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'point': symbol_info.point,
            'digits': symbol_info.digits,
            'spread': symbol_info.spread,
            'trade_mode': symbol_info.trade_mode
        }


if __name__ == "__main__":
    # 创建MT5连接
    connector = MT5Connector()
    if connector.connect():
        # 创建数据处理器
        data_handler = DataHandler(connector)
        
        try:
            # 测试获取黄金数据
            print("\n=== 获取XAUUSD数据 ===")
            df = data_handler.get_historical_data(
                "XAUUSD",
                mt5.TIMEFRAME_D1,
                pd.Timestamp.now() - pd.Timedelta(days=100),
                pd.Timestamp.now()
            )
            if df is not None:
                print(f"获取到 {len(df)} 条数据")
                print("\n最新5条数据：")
                print(df.tail())
            
            # 测试获取品种信息
            print("\n=== XAUUSD 品种信息 ===")
            symbol_info = data_handler.get_symbol_info("XAUUSD")
            if symbol_info:
                for key, value in symbol_info.items():
                    print(f"{key}: {value}")
                    
        except Exception as e:
            logger.error(f"测试过程出错: {str(e)}")
            
        finally:
            connector.close()
    else:
        print("MT5连接失败")
