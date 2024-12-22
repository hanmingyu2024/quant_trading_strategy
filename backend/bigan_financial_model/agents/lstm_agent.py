"""
LSTM智能体模块

该模块实现了基于LSTM的交易智能体,用于金融市场预测和决策。
主要功能包括:
- 基于LSTM的序列建模
- 交易动作预测
- 模型训练和更新
- 状态管理和缓存

作者: BiGan团队
日期: 2023-10
"""

import torch
import torch.nn as nn
from typing import Dict, Any, List
import numpy as np
from bigan_financial_model.core.logger import Logger

class LSTMModel(nn.Module):
    """LSTM神经网络模型"""
    
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, output_dim: int):
        super().__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM层
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        # 全连接层
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, output_dim)
        )

class LSTMAgent:
    """基于LSTM的交易智能体"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化LSTM智能体
        
        Args:
            config: 配置参数字典
        """
        self.logger = Logger("LSTMAgent")
        self.config = config
        
        # 模型参数
        self.input_dim = config.get('input_dim', 10)
        self.hidden_dim = config.get('hidden_dim', 128)
        self.num_layers = config.get('num_layers', 2)
        self.output_dim = config.get('output_dim', 3)  # 买入/卖出/持有
        self.sequence_length = config.get('sequence_length', 20)
        self.learning_rate = config.get('learning_rate', 0.001)
        
        # 初始化模型
        self.model = LSTMModel(
            input_dim=self.input_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            output_dim=self.output_dim
        )
        
        # 优化器
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.learning_rate
        )
        
        # 损失函数
        self.criterion = nn.MSELoss()
        
        # 状态缓存
        self.state_buffer: List[np.ndarray] = []
        self.hidden = None
        
    def predict(self, state: np.ndarray) -> Dict[str, Any]:
        """
        预测交易动作
        
        Args:
            state: 当前状态向量
            
        Returns:
            预测结果字典
        """
        # 更新状态缓存
        self.state_buffer.append(state)
        if len(self.state_buffer) > self.sequence_length:
            self.state_buffer.pop(0)
            
        # 数据不足时返回持有动作
        if len(self.state_buffer) < self.sequence_length:
            return {
                'action_type': 'hold',
                'confidence': 0.5
            }
            
        # 准备模型输入
        x = torch.tensor(self.state_buffer, dtype=torch.float32)
        x = x.unsqueeze(0)  # 添加批次维度
        
        # 模型推理
        with torch.no_grad():
            self.model.eval()
            output = self.model(x)
            probabilities = torch.softmax(output[0], dim=-1)
            
        # 获取预测结果
        action_idx = torch.argmax(probabilities).item()
        confidence = probabilities[action_idx].item()
        
        # 映射到动作类型
        action_types = ['buy', 'sell', 'hold']
        
        return {
            'action_type': action_types[action_idx],
            'confidence': confidence,
            'raw_output': probabilities.numpy()
        }
        
    def update(self, state: Dict[str, Any], reward: float):
        """
        更新模型
        
        Args:
            state: 状态信息
            reward: 奖励值
        """
        if len(self.state_buffer) < self.sequence_length:
            return
            
        self.model.train()
        
        # 准备训练数据
        x = torch.tensor(self.state_buffer, dtype=torch.float32)
        x = x.unsqueeze(0)
        
        # 计算目标值
        target = torch.zeros(1, self.output_dim)
        if reward > 0:
            target[0, 0] = 1.0  # 买入信号
        elif reward < 0:
            target[0, 1] = 1.0  # 卖出信号
        else:
            target[0, 2] = 1.0  # 持有信号
            
        # 前向传播
        output = self.model(x)
        loss = self.criterion(output, target)
        
        # 反向传播和优化
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)  # 梯度裁剪
        self.optimizer.step()
        
        self.logger.debug(f"LSTM更新 - Loss: {loss.item():.4f}")
        
    def get_state_dict(self) -> Dict[str, Any]:
        """
        获取模型状态
        
        Returns:
            模型状态字典
        """
        return {
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'state_buffer': self.state_buffer,
            'hidden': self.hidden
        }
        
    def load_state_dict(self, state_dict: Dict[str, Any]):
        """
        加载模型状态
        
        Args:
            state_dict: 模型状态字典
        """
        self.model.load_state_dict(state_dict['model_state'])
        self.optimizer.load_state_dict(state_dict['optimizer_state'])
        self.state_buffer = state_dict['state_buffer']
        self.hidden = state_dict['hidden']
        
    def reset_hidden(self):
        """重置LSTM隐藏状态"""
        self.hidden = None 