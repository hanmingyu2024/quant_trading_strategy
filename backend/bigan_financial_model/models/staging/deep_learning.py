"""
时序CNN模型实现 - 预发布版本
用于金融数据的时序预测分析
"""

import torch
import torch.nn as nn


class TemporalCNN(nn.Module):
    """
    时序CNN模型
    用于处理金融时间序列数据的深度学习模型
    """
    def __init__(self, 
                 input_size=1,
                 hidden_channels=[32, 64, 128],
                 kernel_size=3,
                 dropout=0.2):
        """
        初始化模型参数
        
        Args:
            input_size (int): 输入特征维度
            hidden_channels (list): 卷积层通道数列表
            kernel_size (int): 卷积核大小
            dropout (float): dropout率
        """
        super(TemporalCNN, self).__init__()
        self.version = "1.0.0-beta"
        self.env = "staging"
        
        # 构建卷积层
        layers = []
        in_channels = input_size
        
        for out_channels in hidden_channels:
            layers.extend([
                nn.Conv1d(in_channels, out_channels, kernel_size, padding=kernel_size//2),
                nn.ReLU(),
                nn.BatchNorm1d(out_channels),
                nn.Dropout(dropout)
            ])
            in_channels = out_channels
            
        self.conv_layers = nn.Sequential(*layers)
        
        # 全连接层
        self.fc = nn.Linear(hidden_channels[-1], 1)
        
    def forward(self, x):
        """
        前向传播
        
        Args:
            x (torch.Tensor): 输入数据，形状为 [batch_size, sequence_length, input_size]
            
        Returns:
            torch.Tensor: 预测结果
        """
        # 调整输入维度 [batch_size, input_size, sequence_length]
        x = x.transpose(1, 2)
        
        # 卷积层
        x = self.conv_layers(x)
        
        # 全局平均池化
        x = torch.mean(x, dim=2)
        
        # 全连接层
        x = self.fc(x)
        
        return x
    
    def predict(self, x):
        """
        预测函数
        
        Args:
            x (torch.Tensor): 输入数据
            
        Returns:
            torch.Tensor: 预测结果
        """
        self.eval()  # 设置为评估模式
        with torch.no_grad():
            return self.forward(x) 