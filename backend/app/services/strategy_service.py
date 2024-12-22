"""
策略管理服务
负责策略的创建、运行和监控
"""
from typing import Dict, List
from datetime import datetime
from backend.app.strategies.base_strategy import BaseStrategy
from backend.app.strategies.ma_cross_strategy import MACrossStrategy
from backend.app.utils.alert_manager import alert_manager, AlertLevel

class StrategyService:
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        
    async def create_strategy(
        self, 
        strategy_type: str, 
        symbol: str, 
        params: Dict
    ) -> BaseStrategy:
        """创建新策略"""
        if strategy_type == "MA_CROSS":
            strategy = MACrossStrategy(
                symbol=symbol,
                short_window=params.get('short_window', 10),
                long_window=params.get('long_window', 20)
            )
            self.strategies[f"{strategy_type}_{symbol}"] = strategy
            return strategy
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
            
    async def run_strategy(self, strategy_id: str) -> bool:
        """运行指定策略"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy not found: {strategy_id}")
            
        strategy = self.strategies[strategy_id]
        try:
            success = await strategy.run()
            if success:
                await alert_manager.send_alert(
                    title=f"策略 {strategy_id} 运行成功",
                    message=f"完成时间: {datetime.now()}",
                    level=AlertLevel.INFO
                )
            return success
        except Exception as e:
            await alert_manager.send_alert(
                title=f"策略 {strategy_id} 运行失败",
                message=str(e),
                level=AlertLevel.ERROR
            )
            return False
            
    def get_strategy_state(self, strategy_id: str) -> Dict:
        """获取策略状态"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy not found: {strategy_id}")
            
        strategy = self.strategies[strategy_id]
        return strategy.get_state().dict()
        
    def get_all_strategies(self) -> List[Dict]:
        """获取所有策略信息"""
        return [
            {
                "id": strategy_id,
                "name": strategy.name,
                "symbol": strategy.symbol,
                "state": strategy.get_state().dict()
            }
            for strategy_id, strategy in self.strategies.items()
        ]

# 创建全局实例
strategy_service = StrategyService() 