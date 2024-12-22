"""
BiGan金融模型的强化学习智能体模块

该模块实现了基于深度Q网络(DQN)的强化学习智能体,用于金融市场交易决策。
主要功能包括:
- DQN网络结构定义
- 经验回放记忆
- 动作选择策略
- 模型训练与优化
- 模型的保存和加载

作者: BiGan团队
日期: 2023-10
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
from typing import List, Tuple, Dict, Any
from core.logger import Logger
from core.config import Config

class DQN(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super(DQN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
    
    def forward(self, x):
        return self.network(x)

class RLAgent:
    """强化学习代理"""
    
    def __init__(self, state_dim: int, action_dim: int, **kwargs):
        """初始化强化学习代理
        
        Args:
            state_dim: 状态空间维度
            action_dim: 动作空间维度
            **kwargs: 其他配置参数
                - learning_rate: 学习率
                - batch_size: 批量大小
                - memory_size: 经验回放缓冲区大小
                - gamma: 折扣因子
        """
        self.logger = Logger("RLAgent")
        
        # 基本参数
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # 从 kwargs 获取其他参数
        self.learning_rate = kwargs.get('learning_rate', 0.001)
        self.batch_size = kwargs.get('batch_size', 32)
        self.memory_size = kwargs.get('memory_size', 10000)
        self.gamma = kwargs.get('gamma', 0.99)
        
        # 设备配置
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 创建网络
        self.policy_net = DQN(self.state_dim, self.action_dim).to(self.device)
        self.target_net = DQN(self.state_dim, self.action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # 优化器
        self.optimizer = optim.Adam(
            self.policy_net.parameters(), 
            lr=self.learning_rate
        )
        
        # 经验回放
        self.memory = deque(maxlen=self.memory_size)
        
        self.logger.info(
            f"初始化RL代理: state_dim={state_dim}, action_dim={action_dim}, "
            f"lr={self.learning_rate}, batch_size={self.batch_size}"
        )

    def act(self, state: np.ndarray) -> int:
        """选择动作"""
        if random.random() < self.epsilon:
            return random.randrange(self.action_dim)
        
        with torch.no_grad():
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state)
            return q_values.argmax().item()

    def train(self, batch: List[Tuple]) -> float:
        """训练智能体"""
        if len(self.memory) < self.batch_size:
            return 0.0

        # 采样batch
        transitions = random.sample(self.memory, self.batch_size)
        batch = list(zip(*transitions))

        # 准备数据
        state_batch = torch.FloatTensor(batch[0]).to(self.device)
        action_batch = torch.LongTensor(batch[1]).to(self.device)
        reward_batch = torch.FloatTensor(batch[2]).to(self.device)
        next_state_batch = torch.FloatTensor(batch[3]).to(self.device)
        done_batch = torch.FloatTensor(batch[4]).to(self.device)

        # 计算当前Q值
        current_q_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1))

        # 计算目标Q值
        with torch.no_grad():
            next_q_values = self.target_net(next_state_batch).max(1)[0]
            target_q_values = reward_batch + (1 - done_batch) * self.gamma * next_q_values

        # 计算损失
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)

        # 优化
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 更新目标网络
        self.steps += 1
        if self.steps % self.update_target_steps == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        return loss.item()

    def remember(self, state, action, reward, next_state, done):
        """存储经验"""
        self.memory.append((state, action, reward, next_state, done))

    def save(self, path: str):
        """保存模型"""
        torch.save({
            'policy_net': self.policy_net.state_dict(),
            'target_net': self.target_net.state_dict(),
            'optimizer': self.optimizer.state_dict()
        }, path)
        self.logger.info(f"模型已保存到: {path}")

    def load(self, path: str):
        """加载模型"""
        try:
            checkpoint = torch.load(path)
            self.policy_net.load_state_dict(checkpoint['policy_net'])
            self.target_net.load_state_dict(checkpoint['target_net'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            self.logger.info(f"模型已加载: {path}")
        except Exception as e:
            self.logger.error(f"加载模型失败: {str(e)}")
