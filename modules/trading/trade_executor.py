"""
交易执行模块
负责执行开仓和平仓操作
"""

import MetaTrader5 as mt5
from modules.logger import setup_logger

logger = setup_logger('trade_executor')

class TradeExecutor:
    def __init__(self, mt5_connector):
        self.mt5_connector = mt5_connector
        
    def open_position(self, symbol, order_type, volume, price=None, sl=None, tp=None):
        """开仓"""
        if not self.mt5_connector.connected:
            logger.error("MT5未连接")
            return None
            
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "deviation": 20,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if price is not None:
            request["price"] = price
        if sl is not None:
            request["sl"] = sl
        if tp is not None:
            request["tp"] = tp
            
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"开仓失败: {result.comment}")
            return None
            
        return result
    
    def close_position(self, position_ticket):
        """平仓"""
        position = mt5.positions_get(ticket=position_ticket)
        if position is None:
            logger.error(f"未找到持仓: {position_ticket}")
            return None
            
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position_ticket,
            "symbol": position[0].symbol,
            "volume": position[0].volume,
            "type": mt5.ORDER_TYPE_SELL if position[0].type == 0 else mt5.ORDER_TYPE_BUY,
            "deviation": 20,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"平仓失败: {result.comment}")
            return None
            
        return result
