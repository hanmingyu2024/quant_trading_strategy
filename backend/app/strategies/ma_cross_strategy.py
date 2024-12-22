"""
均线交叉策略
使用短期和长期移动平均线的交叉来产生交易信号
"""
from typing import Dict, List
import numpy as np
import pandas as pd
from backend.app.strategies.base_strategy import BaseStrategy
from backend.app.utils.alert_manager import alert_manager, AlertLevel

class MACrossStrategy(BaseStrategy):
    def __init__(
        self, 
        symbol: str,
        short_window: int = 10,
        long_window: int = 20
    ):
        super().__init__(name="MA Cross", symbol=symbol)
        self.short_window = short_window
        self.long_window = long_window
        self.data = pd.DataFrame()
        
    async def initialize(self):
        """初始化策略数据"""
        # 这里应该从数据源获取历史数据
        # 示例数据
        self.data = pd.DataFrame({
            'close': np.random.random(100) * 100
        })
        
    async def analyze(self) -> Dict:
        """分析市场数据"""
        # 计算移动平均线
        self.data['MA_short'] = self.data['close'].rolling(
            window=self.short_window
        ).mean()
        self.data['MA_long'] = self.data['close'].rolling(
            window=self.long_window
        ).mean()
        
        # 计算交叉信号
        self.data['signal'] = 0
        self.data.loc[
            self.data['MA_short'] > self.data['MA_long'], 'signal'
        ] = 1
        self.data.loc[
            self.data['MA_short'] < self.data['MA_long'], 'signal'
        ] = -1
        
        return {
            'last_short_ma': self.data['MA_short'].iloc[-1],
            'last_long_ma': self.data['MA_long'].iloc[-1],
            'current_signal': self.data['signal'].iloc[-1]
        }
        
    async def generate_signals(self) -> List[Dict]:
        """生成交易信号"""
        signals = []
        last_signal = self.data['signal'].iloc[-1]
        
        if last_signal != 0:
            signals.append({
                'type': 'BUY' if last_signal == 1 else 'SELL',
                'symbol': self.symbol,
                'price': self.data['close'].iloc[-1],
                'timestamp': pd.Timestamp.now()
            })
            
            # 发送告警
            await alert_manager.send_alert(
                title=f"{self.symbol} 交易信号",
                message=f"生成{'买入' if last_signal == 1 else '卖出'}信号",
                level=AlertLevel.INFO
            )
            
        return signals
        
    async def execute_trade(self, signal: Dict) -> bool:
        """执行交易"""
        try:
            # 这里应该实现实际的交易逻辑
            print(f"执行交易: {signal}")
            
            # 更新持仓
            if signal['type'] == 'BUY':
                self.state.current_position += 1
            else:
                self.state.current_position -= 1
                
            return True
            
        except Exception as e:
            await alert_manager.send_alert(
                title=f"{self.symbol} 交易失败",
                message=str(e),
                level=AlertLevel.ERROR
            )
            return False 