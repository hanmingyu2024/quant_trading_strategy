"""
Transformer代理模块

该模块实现了基于Transformer的交易智能体,用于金融市场预测和决策。
主要功能包括:
- 基于Transformer的序列建模
- 交易动作预测
- 模型训练和更新
- 状态管理和缓存

作者: BiGan团队
日期: 2024-01
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List
import logging

class TransformerModel(nn.Module):
    """Transformer模型"""
    def __init__(self, 
                 input_dim: int,
                 d_model: int,
                 n_heads: int,
                 n_layers: int,
                 d_ff: int,
                 output_dim: int,
                 dropout: float = 0.1):
        super().__init__()
        
        self.input_projection = nn.Linear(input_dim, d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_ff,
            dropout=dropout,
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=n_layers
        )
        
        self.output_projection = nn.Linear(d_model, output_dim)
        
    def forward(self, x):
        # 输入投影
        x = self.input_projection(x)
        
        # Transformer编码
        x = self.transformer_encoder(x)
        
        # 取最后一个时间步的输出
        x = x[:, -1, :]
        
        # 输出投影
        predictions = self.output_projection(x)
        return predictions

class TransformerAgent:
    """Transformer交易代理"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化Transformer代理
        
        Args:
            config: 配置字典，包含:
                - n_layers: Transformer层数
                - n_heads: 注意力头数
                - d_model: 模型维度
                - d_ff: 前馈网络维度
                - dropout: Dropout率
        """
        self.config = config
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 如果没有处理器，添加一个
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
        # 模型参数
        self.input_dim = 10  # 特征数量
        self.d_model = config.get('d_model', 256)
        self.n_heads = config.get('n_heads', 8)
        self.n_layers = config.get('n_layers', 4)
        self.d_ff = config.get('d_ff', 1024)
        self.output_dim = 1  # 预测值维度
        self.dropout = config.get('dropout', 0.1)
        
        # 初始化模型
        self.model = TransformerModel(
            input_dim=self.input_dim,
            d_model=self.d_model,
            n_heads=self.n_heads,
            n_layers=self.n_layers,
            d_ff=self.d_ff,
            output_dim=self.output_dim,
            dropout=self.dropout
        )
        
        self.logger.info("Transformer代理初始化成功")
        self.logger.info(f"Transformer配置: {config}")
        self.logger.info(f"模型结构: input_dim={self.input_dim}, "
                        f"d_model={self.d_model}, "
                        f"n_heads={self.n_heads}, "
                        f"n_layers={self.n_layers}")
        
    def predict(self, state: Dict[str, Any]) -> float:
        """预测函数"""
        try:
            # 数据预处理
            features = self._preprocess_state(state)
            
            # 转换为tensor
            x = torch.FloatTensor(features).unsqueeze(0)
            
            # 预测
            with torch.no_grad():
                prediction = self.model(x)
                raw_prediction = prediction.item()
                
                # 添加预测值规范化
                normalized_prediction = np.tanh(raw_prediction)
                
                self.logger.info(f"原始预测值: {raw_prediction}")
                self.logger.info(f"归一化预测值: {normalized_prediction}")
                
                # 添加市场分析
                analysis = self._analyze_market(state)
                self.logger.info(f"市场分析: {analysis}")
                
                return normalized_prediction
                
        except Exception as e:
            self.logger.error(f"预测错误: {str(e)}")
            return 0.0
            
    def _analyze_market(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场状态"""
        try:
            prices = np.array(state['close'])
            volumes = np.array(state['volume'])
            
            # 计算基本指标
            price_change = (prices[-1] - prices[0]) / prices[0]
            price_volatility = np.std(prices) / np.mean(prices)
            volume_volatility = np.std(volumes) / np.mean(volumes)
            
            # 计算趋势
            price_trend = np.mean(np.diff(prices))
            volume_trend = np.mean(np.diff(volumes))
            
            # 计算动量
            momentum = price_change / price_volatility if price_volatility != 0 else 0
            
            return {
                'price_change_pct': float(price_change * 100),
                'price_volatility': float(price_volatility),
                'volume_volatility': float(volume_volatility),
                'price_trend': float(price_trend),
                'volume_trend': float(volume_trend),
                'momentum': float(momentum)
            }
            
        except Exception as e:
            self.logger.error(f"市场分析错误: {str(e)}")
            return {}
            
    def _preprocess_state(self, state: Dict[str, Any]) -> np.ndarray:
        """预处理状态数据"""
        features = np.zeros((10, self.input_dim))
        
        try:
            if 'close' in state:
                prices = np.array(state['close'])
                # 价格归一化
                features[:, 0] = (prices - np.mean(prices)) / np.std(prices)
                # 添加价格变化
                features[1:, 1] = np.diff(prices) / prices[:-1]
                
            if 'volume' in state:
                volumes = np.array(state['volume'])
                # 成交量归一化
                features[:, 2] = (volumes - np.mean(volumes)) / np.std(volumes)
                # 添加成交量变化
                features[1:, 3] = np.diff(volumes) / volumes[:-1]
                
            # 添加技术指标
            features[:, 4] = self._calculate_rsi(state['close'])
            features[:, 5] = self._calculate_ma_ratio(state['close'])
            
            self.logger.debug(f"特征统计: mean={np.mean(features):.4f}, std={np.std(features):.4f}")
            
        except Exception as e:
            self.logger.error(f"预处理错误: {str(e)}")
            
        return features
        
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """计算RSI指标"""
        try:
            deltas = np.diff(prices)
            seed = deltas[:period+1]
            up = seed[seed >= 0].sum()/period
            down = -seed[seed < 0].sum()/period
            rs = up/down if down != 0 else 0
            rsi = np.zeros_like(prices)
            rsi.fill(100 - 100/(1+rs))
            return rsi
        except:
            return np.zeros_like(prices)
            
    def _calculate_ma_ratio(self, prices: np.ndarray, fast: int = 5, slow: int = 20) -> np.ndarray:
        """计算均线比率"""
        try:
            ma_fast = np.convolve(prices, np.ones(fast)/fast, mode='valid')
            ma_slow = np.convolve(prices, np.ones(slow)/slow, mode='valid')
            ratio = np.zeros_like(prices)
            ratio[-len(ma_fast):] = ma_fast/ma_slow[-len(ma_fast):]
            return ratio
        except:
            return np.zeros_like(prices)

if __name__ == '__main__':
    # 设置随机种子以复现结果
    np.random.seed(42)
    torch.manual_seed(42)
    
    # 定义配置
    config = {
        'n_layers': 4,          # Transformer编码器层数
        'n_heads': 8,           # 注意力头数
        'd_model': 256,         # 模型维度
        'd_ff': 1024,          # 前馈网络维度
        'dropout': 0.1,         # Dropout率
        'learning_rate': 0.001  # 学习率
    }
    
    # 创建更真实的测试数据
    test_state = {
        'close': np.cumsum(np.random.randn(10) * 0.1) + 100,  # 模拟价格走势
        'volume': np.abs(np.random.randn(10) * 1000 + 5000)   # 模拟成交量
    }
    
    try:
        # 创建代理
        agent = TransformerAgent(config)
        print("\nTransformer代理创建成功")
        
        # 进行预测
        prediction = agent.predict(test_state)
        
        # 打印详细信息
        print(f"\n测试数据:")
        print(f"价格序列: {test_state['close']}")
        print(f"成交量序列: {test_state['volume']}")
        print(f"\n预测结果: {prediction}")
        
    except Exception as e:
        print(f"错误: {str(e)}") 