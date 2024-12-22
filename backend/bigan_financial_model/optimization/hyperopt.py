"""
超参数优化模块

使用Optuna库实现的超参数优化功能
作者: BiGan团队
日期: 2024-01
"""

from typing import Dict, Any, Callable
import optuna
import numpy as np
from sklearn.model_selection import cross_val_score

class HyperParameterOptimizer:
    def __init__(
        self,
        model_creator: Callable,
        param_space: Dict[str, Any],
        n_trials: int = 100,
        cv_folds: int = 5
    ):
        self.model_creator = model_creator
        self.param_space = param_space
        self.n_trials = n_trials
        self.cv_folds = cv_folds
        self.study = None
        
    def objective(self, trial, X, y):
        # 从参数空间采样参数
        params = {}
        for param_name, param_config in self.param_space.items():
            if param_config['type'] == 'int':
                params[param_name] = trial.suggest_int(
                    param_name,
                    param_config['low'],
                    param_config['high']
                )
            elif param_config['type'] == 'float':
                params[param_name] = trial.suggest_float(
                    param_name,
                    param_config['low'],
                    param_config['high'],
                    log=param_config.get('log', False)
                )
            elif param_config['type'] == 'categorical':
                params[param_name] = trial.suggest_categorical(
                    param_name,
                    param_config['choices']
                )
        
        # 创建模型并评估
        model = self.model_creator(**params)
        scores = cross_val_score(
            model, X, y,
            cv=self.cv_folds,
            scoring='neg_mean_squared_error'
        )
        return -scores.mean()  # 最小化MSE
        
    def optimize(self, X, y):
        """运行优化过程"""
        self.study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler()
        )
        
        self.study.optimize(
            lambda trial: self.objective(trial, X, y),
            n_trials=self.n_trials
        )
        
        return self.study.best_params 