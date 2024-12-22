from typing import Dict, Any
import logging

class AutonomousSystemManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.auto_learning = AutoLearningSystem(config)
        self.evolution = ModelEvolutionSystem(config)
        self.research = FinancialResearchSystem(config)
        self.maintenance = SystemMaintenanceManager(config)
        self.logger = logging.getLogger(__name__)
        
    def run_autonomous_cycle(self):
        """运行自主循环"""
        while True:
            try:
                # 1. 评估当前性能
                performance = self.auto_learning.evaluate_performance()
                
                # 2. 检测市场状态
                market_regime = self.auto_learning.detect_market_regime()
                
                # 3. 适应性调整
                self.auto_learning.adapt_strategy(market_regime)
                
                # 4. 模型进化
                if self._should_evolve(performance):
                    self.evolution.evolve_architecture(performance)
                    
                # 5. 研究新理论和指标
                self.research.discover_new_patterns()
                self.research.research_new_indicators()
                
                # 6. 系统维护
                self.maintenance.monitor_system_health()
                self.maintenance.perform_self_optimization()
                
                # 7. 记录和报告
                self._log_autonomous_cycle()
                
            except Exception as e:
                self.logger.error(f"自主循环出错: {str(e)}")
                self._handle_error(e) 