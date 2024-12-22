"""
MT5连接器模块

功能:
- 连接到MT5平台
- 获取账户信息
- 管理MT5连接状态

作者: Han Mingyu
邮箱: 13364694109ai@gmail.com
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from config.config import MT5_CONFIG
import MetaTrader5 as mt5
from modules.logger import setup_logger

logger = setup_logger('mt5_connector')

class MT5Connector:
    def __init__(self):
        self.connected = False
        # 加载.env文件
        load_dotenv()
        
    def connect(self):
        """连接到MT5平台"""
        if not mt5.initialize():
            logger.error("MT5初始化失败")
            return False
            
        # 从环境变量获取登录信息
        login_result = mt5.login(
            login=int(os.getenv('MT5_ACCOUNT')),  # 转换为整数
            password=os.getenv('MT5_PASSWORD'),
            server=os.getenv('MT5_SERVER')
        )
        
        if not login_result:
            logger.error(f"MT5登录失败: {mt5.last_error()}")
            return False
            
        self.connected = True
        logger.info("MT5连接成功")
        return True
    
    def get_account_info(self):
        """获取账户信息"""
        if not self.connected:
            logger.error("未连接到MT5")
            return None
            
        account_info = mt5.account_info()
        if account_info is None:
            logger.error("获取账户信息失败")
            return None
            
        return {
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'profit': account_info.profit
        }
    
    def close(self):
        """关闭MT5连接"""
        mt5.shutdown()
        self.connected = False
        logger.info("MT5连接已关闭")

    def initialize(self) -> bool:
        """
        初始化与 MetaTrader 5 的连接
        
        Returns:
            bool: 连接成功返回 True，失败返回 False
        """
        try:
            import MetaTrader5 as mt5
            if not mt5.initialize():
                print(f"初始化失败，错误代码: {mt5.last_error()}")
                return False
            return True
        except Exception as e:
            print(f"连接 MT5 时发生错误: {str(e)}")
            return False

    def is_connected(self) -> bool:
        """
        检查是否已连接到 MetaTrader 5
        
        Returns:
            bool: 如果已连接返回 True，否则返回 False
        """
        try:
            import MetaTrader5 as mt5
            return mt5.terminal_info() is not None
        except Exception as e:
            print(f"检查连接状态时发生错误: {str(e)}")
            return False

    def get_historical_data(self, symbol: str, start_date, end_date, count: int = 1000):
        """
        从 MT5 获取历史数据
        
        Args:
            symbol (str): 交易品种代码，如 "XAUUSD"
            start_date: 开始日期
            end_date: 结束日期
            count (int): 获取的数据条数
            
        Returns:
            pd.DataFrame: 包含历史数据的DataFrame
        """
        try:
            import MetaTrader5 as mt5
            import pandas as pd
            
            # 确保连接正常
            if not self.is_connected():
                raise ConnectionError("未连接到 MetaTrader 5")
                
            # 获取历史数据
            rates = mt5.copy_rates_range(
                symbol,
                mt5.TIMEFRAME_D1,  # 日线数据
                start_date,
                end_date
            )
            
            if rates is None:
                raise Exception(f"获取数据失败，错误码：{mt5.last_error()}")
                
            # 转换为 DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # 检查并处理成交量数据
            volume_col = 'tick_volume' if 'tick_volume' in df.columns else 'volume'
            
            # 返回基本价格数据
            return df[['open', 'high', 'low', 'close', volume_col]].rename(
                columns={volume_col: 'volume'}
            )
            
        except Exception as e:
            raise Exception(f"获取历史数据时发生错误: {str(e)}")

if __name__ == "__main__":
    # 创建MT5连接实例
    connector = MT5Connector()
    
    # 测试连接
    print("正在连接到MT5...")
    if connector.connect():
        print("连接成功！")
        
        # 获取账户信息
        account_info = connector.get_account_info()
        print("\n=== 账户信息 ===")
        for key, value in account_info.items():
            print(f"{key}: {value}")
        
        # 关闭连接
        connector.close()
        print("\nMT5连接已关闭")
    else:
        print("连接失败！")
