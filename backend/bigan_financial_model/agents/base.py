"""
交易智能体基类模块

定义了所有交易智能体的基础接口,包括:
- 状态预测
- 模型更新
- 模型保存和加载
- 历史记录跟踪

作者: BiGan团队
日期: 2024-01
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import numpy as np

class BaseAgent(ABC):
    """交易智能体基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state_history: List[np.ndarray] = []
        self.action_history: List[Dict[str, Any]] = []
        
    @abstractmethod
    def predict(self, state: np.ndarray) -> Dict[str, Any]:
        """预测交易动作"""
        pass
        
    @abstractmethod
    def update(self, state: np.ndarray, action: Dict[str, Any], reward: float):
        """更新模型"""
        pass
        
    @abstractmethod
    def save(self, path: str):
        """保存模型"""
        pass
        
    @abstractmethod
    def load(self, path: str):
        """加载模型"""
        pass 