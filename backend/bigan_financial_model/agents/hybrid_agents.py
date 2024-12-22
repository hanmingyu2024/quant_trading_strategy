"""
混合智能体模块

该模块实现了一个混合智能体类,结合多种AI方法来优化金融交易决策。
主要功能包括:
- 状态处理和特征提取
- 动作预测和决策
- 模型训练和更新
- 模型保存和加载

作者: BiGan团队
日期: 2023-10
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime, timedelta

# 使用绝对导入
from bigan_financial_model.agents.reinforcement_learning import RLAgent
from bigan_financial_model.agents.transformer_agent import TransformerAgent
from bigan_financial_model.agents.lstm_agent import LSTMAgent
from bigan_financial_model.core.logger import Logger
from bigan_financial_model.utils.metrics import calculate_sharpe_ratio, calculate_sortino_ratio
from bigan_financial_model.utils.metrics.risk.manager import RiskManager
from bigan_financial_model.utils.metrics.risk.core import DynamicThreshold

class HybridAgent:
    """高级混合智能体，集成多种AI模型和风险管理"""
    
    def __init__(self, config: dict):
        """初始化混合智能体"""
        print("HybridAgent初始化配置:", config)
        
        # 保存配置
        self.config = config
        
        # 获取基本参数
        self.state_dim = config['state_dim']
        self.action_dim = config['action_dim']
        
        try:
            # 获取 RL 配置
            rl_config = config.get('agents', {}).get('rl_config', {})
            
            # 初始化 RL 代理
            self.rl_agent = RLAgent(
                state_dim=self.state_dim,
                action_dim=self.action_dim,
                **rl_config  # 传入其他配置参数
            )
            print("RL代理初始化成功")
            
            # 初始化其他代理
            self.transformer_agent = TransformerAgent(
                config=config.get('agents', {}).get('transformer_config', {})
            )
            print("Transformer代理初始化成功")
            
            self.lstm_agent = LSTMAgent(
                config=config.get('agents', {}).get('lstm_config', {})
            )
            print("LSTM代理初始化成功")
            
            # 初始化风险管理器
            self.risk_manager = RiskManager(
                config=config.get('risk_management', {})
            )
            print("风险管理器初始化成功")
            
            # 设置集成权重
            self.model_weights = {
                'rl': 0.4,
                'transformer': 0.3,
                'lstm': 0.3
            }
            
        except Exception as e:
            print(f"代理初始化失败: {str(e)}")
            raise
        
        # 初始化集成学习模型
        self.ensemble_model = self._build_ensemble_model()
        
        # 历史记录
        self.state_history = []
        self.action_history = []
        self.performance_metrics = {
            'sharpe_ratio': [],
            'sortino_ratio': [],
            'max_drawdown': [],
            'win_rate': []
        }
        
        # 性能监控
        self.last_update_time = datetime.now()
        self.training_steps = 0
        
        # 添加新的监控组件
        self.risk_monitor = RiskMonitor(
            alert_threshold=config.get('risk_alert_threshold', 0.8),
            monitoring_interval=config.get('monitoring_interval', 300)  # 5分钟
        )
        
        # 添加模型性能追踪
        self.model_performance_tracker = {
            'rl': [],
            'transformer': [],
            'lstm': []
        }
        
        # 初始化风险控制参数
        self._init_risk_control()
        
    def _init_risk_control(self):
        """初始化增强版风险控制"""
        self.risk_params = {
            'max_position_size': self.config.get('max_position_size', 1.0),
            'max_drawdown_threshold': self.config.get('max_drawdown_threshold', 0.15),
            'volatility_threshold': self.config.get('volatility_threshold', 0.25),
            'risk_adjustment_factor': self.config.get('risk_adjustment_factor', 0.8)
        }
        
        # 动态风险阈值
        self.dynamic_thresholds = {
            'position': DynamicThreshold(
                base_value=0.5,
                market_sensitivity=1.2,
                min_value=0.1,
                max_value=1.0
            ),
            'stop_loss': DynamicThreshold(
                base_value=0.05,
                market_sensitivity=1.5,
                min_value=0.02,
                max_value=0.1
            )
        }
    
    def _build_ensemble_model(self) -> nn.Module:
        """构建集成学习模型"""
        return nn.Sequential(
            nn.Linear(self.config['state_dim'] * 3, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, self.config['action_dim'])
        )
        
    def process_state(self, state: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        增强版状态处理
        
        Args:
            state: 原始状态数据
            
        Returns:
            处理后的状态向量和额外特征
        """
        # 基础特征
        base_features = np.array([
            state.get('price', 0),
            state.get('volume', 0),
            state.get('volatility', 0)
        ])
        
        # 技术指标
        technical_indicators = self._calculate_technical_indicators(state)
        
        # 市场情绪
        sentiment_features = self._analyze_market_sentiment(state)
        
        # 合并特征
        combined_features = np.concatenate([
            base_features,
            technical_indicators,
            sentiment_features
        ])
        
        # 特征标准化
        normalized_features = self._normalize_features(combined_features)
        
        # 保存历史
        self.state_history.append(normalized_features)
        
        return normalized_features, {
            'technical': technical_indicators,
            'sentiment': sentiment_features
        }
        
    def _calculate_technical_indicators(self, state: Dict[str, Any]) -> np.ndarray:
        """计算技术指标"""
        price_history = state.get('price_history', [])
        if len(price_history) < 2:
            return np.zeros(5)
            
        return np.array([
            self._calculate_rsi(price_history),
            self._calculate_macd(price_history),
            self._calculate_bollinger_bands(price_history),
            self._calculate_momentum(price_history),
            self._calculate_vwap(price_history, state.get('volume_history', []))
        ])
        
    def _analyze_market_sentiment(self, state: Dict[str, Any]) -> np.ndarray:
        """分析市场情绪"""
        news_sentiment = state.get('news_sentiment', 0)
        social_sentiment = state.get('social_sentiment', 0)
        market_fear_index = state.get('fear_index', 50)
        
        return np.array([
            news_sentiment,
            social_sentiment,
            market_fear_index / 100  # 归一化
        ])
        
    def predict_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """增强版动作预测"""
        # 处理状态
        state_vector, extra_features = self.process_state(state)
        
        # 获取市场状况
        market_condition = self._analyze_market_condition(state)
        
        # 调整风险阈值
        self._adjust_risk_thresholds(market_condition)
        
        # 获取各模型���测
        model_predictions = self._get_model_predictions(state_vector)
        
        # 优化模型权重
        self._optimize_model_weights()
        
        # 加权融合
        final_prediction = self._weighted_ensemble(model_predictions)
        
        # 风险评估和调整
        risk_score = self.risk_manager.calculate_risk_score(state)
        
        # 实时风险监控
        self.risk_monitor.check_risk_levels(risk_score)
        
        # 生成风险调整后的行动
        action = self._generate_risk_adjusted_action(final_prediction, risk_score)
        
        return action
        
    def _analyze_market_condition(self, state: Dict[str, Any]) -> float:
        """增强版市场状况分析"""
        market_metrics = {
            'volatility': state.get('volatility', 0),
            'volume': state.get('volume', 0),
            'trend': state.get('trend', 0),
            'sentiment': state.get('market_sentiment', 0)
        }
        
        # 计算市场压力指数
        market_stress = (
            0.4 * market_metrics['volatility'] +
            0.2 * abs(market_metrics['trend']) +
            0.2 * (1 - market_metrics['volume']) +
            0.2 * (1 - market_metrics['sentiment'])
        )
        
        return np.clip(market_stress, 0, 1)
        
    def _adjust_risk_thresholds(self, market_condition: float):
        """动态调整风险阈值"""
        for threshold in self.dynamic_thresholds.values():
            threshold.adjust(market_condition)
            
    def _get_model_predictions(self, state_vector: np.ndarray) -> Dict[str, Dict[str, float]]:
        """获取所有模型的预测"""
        return {
            'rl': self.rl_agent.get_action(state_vector),
            'transformer': self.transformer_agent.predict(state_vector),
            'lstm': self.lstm_agent.predict(state_vector)
        }
        
    def _optimize_model_weights(self):
        """优化模型权重"""
        recent_window = 100  # 最近100次预测的表现
        
        # 计算每个模型的表现分数
        performance_scores = {}
        for model_name in self.model_performance_tracker:
            recent_performance = self.model_performance_tracker[model_name][-recent_window:]
            if recent_performance:
                performance_scores[model_name] = np.mean(recent_performance)
            else:
                performance_scores[model_name] = 1/3  # 默认权重
                
        # 使用softmax计算新权重
        scores = np.array(list(performance_scores.values()))
        exp_scores = np.exp(scores - np.max(scores))
        new_weights = exp_scores / exp_scores.sum()
        
        # 平滑更新
        alpha = 0.1  # 平滑因子
        for i, model_name in enumerate(performance_scores):
            self.model_weights[model_name] = (
                (1 - alpha) * self.model_weights[model_name] +
                alpha * new_weights[i]
            )
            
    def _weighted_ensemble(self, predictions: Dict[str, Dict[str, float]]) -> float:
        """加权集成预测结果"""
        weighted_sum = 0
        for model_name, prediction in predictions.items():
            weighted_sum += (
                self.model_weights[model_name] * 
                prediction['confidence']
            )
        return weighted_sum
        
    def _generate_risk_adjusted_action(
        self,
        prediction: float,
        risk_score: float
    ) -> Dict[str, Any]:
        """生成风险调整后的行动"""
        # 基础仓位大小
        base_position = self._calculate_position_size(prediction)
        
        # 风险调整
        risk_adjusted_position = base_position * (1 - risk_score)
        
        # 应用动态阈值
        position_threshold = self.dynamic_thresholds['position'].current_value
        stop_loss_threshold = self.dynamic_thresholds['stop_loss'].current_value
        
        # 生成行动
        action = {
            'action_type': self._get_action_type(prediction),
            'amount': min(risk_adjusted_position, position_threshold),
            'confidence': float(prediction),
            'risk_score': risk_score,
            'stop_loss': stop_loss_threshold,
            'timestamp': datetime.now().isoformat()
        }
        
        return action
        
    def update(self, state: Dict[str, Any], action: Dict[str, Any], 
               reward: float, next_state: Optional[Dict[str, Any]] = None):
        """
        增强版更新方法
        
        Args:
            state: 当前状态
            action: 执行的动作
            reward: 获得的奖励
            next_state: 下一个状态（可选）
        """
        # 更新各个模型
        self.rl_agent.update(state, action, reward)
        self.transformer_agent.update(state, reward)
        self.lstm_agent.update(state, reward)
        
        # 更新集成模型
        self._update_ensemble_model(state, action, reward)
        
        # 更新模型权重
        self._update_model_weights()
        
        # 更新性能指标
        self._update_performance_metrics()
        
        # 记录训练步骤
        self.training_steps += 1
        
        # 定期保存检查点
        if self.training_steps % self.config.get('save_interval', 1000) == 0:
            self.save_checkpoint()
            
    def _update_model_weights(self):
        """动态更新模型权重"""
        # 基于最近的性能调整权重
        recent_performance = self._calculate_recent_performance()
        total_performance = sum(recent_performance.values())
        
        if total_performance > 0:
            self.model_weights = {
                model: perf/total_performance 
                for model, perf in recent_performance.items()
            }
            
    def save_checkpoint(self):
        """保存完整的检查点"""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'training_steps': self.training_steps,
            'model_weights': self.model_weights,
            'performance_metrics': self.performance_metrics,
            'rl_agent_state': self.rl_agent.get_state_dict(),
            'transformer_state': self.transformer_agent.get_state_dict(),
            'lstm_state': self.lstm_agent.get_state_dict(),
            'ensemble_model': self.ensemble_model.state_dict(),
            'config': self.config
        }
        
        torch.save(checkpoint, f"checkpoints/hybrid_agent_{self.training_steps}.pt")
        self.logger.info(f"保��检��点: training_steps={self.training_steps}")
    
    def save_model(self, path: str):
        """
        保存模型
        
        Args:
            path: 保存路径
        """
        self.rl_agent.save_model(f"{path}/rl_model")
        # 保存其他模型...
        
    def load_model(self, path: str):
        """
        加载模型
        
        Args:
            path: 模型路径
        """
        self.rl_agent.load_model(f"{path}/rl_model")
        # 加载其他模型...

class RiskMonitor:
    """风险监控组件"""
    
    def __init__(self, alert_threshold: float, monitoring_interval: int):
        self.alert_threshold = alert_threshold
        self.monitoring_interval = monitoring_interval
        self.last_check_time = datetime.now()
        self.risk_history = []
        
    def check_risk_levels(self, current_risk: float):
        """检查风险水平并触发警告"""
        current_time = datetime.now()
        
        # 记录风险历史
        self.risk_history.append({
            'timestamp': current_time,
            'risk_level': current_risk
        })
        
        # 检查是否需要发出警告
        if current_risk > self.alert_threshold:
            self._trigger_risk_alert(current_risk)
            
        # 定期清理历史数据
        if (current_time - self.last_check_time).seconds > self.monitoring_interval:
            self._clean_risk_history()
            self.last_check_time = current_time
            
    def _trigger_risk_alert(self, risk_level: float):
        """触发风险警告"""
        alert_message = (
            f"风险警告: 当前风险水平 {risk_level:.2f} "
            f"超过警戒阈值 {self.alert_threshold}"
        )
        logger.warning(alert_message)
        # 这里可以添加其他警告方式,如发送邮件或消息通知
        
    def _clean_risk_history(self):
        """清理过期的风险历史数据"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(
            seconds=self.monitoring_interval * 2
        )
        
        self.risk_history = [
            record for record in self.risk_history
            if record['timestamp'] > cutoff_time
        ]
