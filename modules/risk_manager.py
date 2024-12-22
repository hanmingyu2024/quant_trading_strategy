"""
风险管理模块
负责管理交易风险,包括仓位控制和止损设置
"""

class RiskManager:
    def __init__(self):
        self.logger = setup_logger()
        
    def check_position_size(self, 
                          account_balance: float,
                          position_size: float,
                          max_risk_per_trade: float = 0.02):
        """
        检查仓位大小是否符合风险控制要求
        """
        max_position = account_balance * max_risk_per_trade
        return position_size <= max_position
        
    def calculate_stop_loss(self, 
                          entry_price: float,
                          risk_per_trade: float = 0.01):
        """
        计算止损位置
        """
        return entry_price * (1 - risk_per_trade) 