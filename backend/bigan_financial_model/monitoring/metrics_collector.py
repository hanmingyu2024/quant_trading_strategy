"""
指标收集器模块

用于收集和管理模型性能、系统性能和交易指标
作者: BiGan团队
日期: 2024-01
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'model_performance': [],
            'system_metrics': [],
            'trading_metrics': []
        }
        
    def log_model_metric(
        self,
        model_name: str,
        metric_name: str,
        value: float,
        timestamp: Optional[datetime] = None
    ):
        """记录模型性能指标"""
        timestamp = timestamp or datetime.now()
        self.metrics['model_performance'].append({
            'timestamp': timestamp,
            'model_name': model_name,
            'metric_name': metric_name,
            'value': value
        })
        
    def log_system_metric(
        self,
        metric_name: str,
        value: float,
        component: str,
        timestamp: Optional[datetime] = None
    ):
        """记录系统性能指标"""
        timestamp = timestamp or datetime.now()
        self.metrics['system_metrics'].append({
            'timestamp': timestamp,
            'component': component,
            'metric_name': metric_name,
            'value': value
        })
        
    def get_metrics_summary(self) -> Dict[str, pd.DataFrame]:
        """获取指标摘要"""
        return {
            key: pd.DataFrame(data) 
            for key, data in self.metrics.items()
        } 