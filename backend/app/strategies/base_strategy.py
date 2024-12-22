"""
交易策略基类
定义了策略的基本接口和通用功能
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

class StrategyState(BaseModel):
    """策略状态"""
    is_running: bool = False
    last_run: Optional[datetime] = None
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    current_position: float = 0
    current_profit: float = 0

class BaseStrategy(ABC):
    def __init__(self, name: str, symbol: str):
        self.name = name
        self.symbol = symbol
        self.state = StrategyState()
        
    @abstractmethod
    async def initialize(self):
        """初始化策略"""
        pass
        
    @abstractmethod
    async def analyze(self) -> Dict:
        """分析市场数据"""
        pass
        
    @abstractmethod
    async def generate_signals(self) -> List[Dict]:
        """生成交易信号"""
        pass
        
    @abstractmethod
    async def execute_trade(self, signal: Dict) -> bool:
        """执行交易"""
        pass
        
    async def run(self):
        """运行策略"""
        try:
            self.state.is_running = True
            self.state.last_run = datetime.now()
            
            # 1. 初始化
            await self.initialize()
            
            # 2. 分析数据
            analysis = await self.analyze()
            
            # 3. 生成信号
            signals = await self.generate_signals()
            
            # 4. 执行交易
            for signal in signals:
                success = await self.execute_trade(signal)
                if success:
                    self.state.successful_trades += 1
                else:
                    self.state.failed_trades += 1
                self.state.total_trades += 1
                
            return True
            
        except Exception as e:
            # 记录错误
            print(f"Strategy error: {str(e)}")
            return False
            
        finally:
            self.state.is_running = False
            
    def get_state(self) -> StrategyState:
        """获取策略状态"""
        return self.state 