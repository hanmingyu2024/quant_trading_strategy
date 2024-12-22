"""
贝叶斯优化模块

用于超参数优化的贝叶斯优化实现
作者: BiGan团队
日期: 2024-01
"""

from typing import Dict, Any, Callable, List
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
from scipy.stats import norm

class BayesianOptimizer:
    def __init__(
        self,
        objective_function: Callable,
        bounds: Dict[str, List[float]],
        n_iterations: int = 50
    ):
        self.objective_function = objective_function
        self.bounds = bounds
        self.n_iterations = n_iterations
        self.X_sample = []
        self.y_sample = []
        
    def _acquisition_function(self, X, model):
        """计算采集函数值（Expected Improvement）"""
        mu, sigma = model.predict(X.reshape(1, -1), return_std=True)
        
        if len(self.y_sample) == 0:
            return mu
        
        mu = mu.reshape(-1)
        sigma = sigma.reshape(-1)
        
        # 计算期望改进
        imp = mu - np.max(self.y_sample)
        Z = imp / sigma
        ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
        
        return ei
        
    def optimize(self):
        """执行贝叶斯优化"""
        # 初始随机采样
        n_random = 5
        dims = len(self.bounds)
        
        for _ in range(n_random):
            x = np.array([
                np.random.uniform(self.bounds[k][0], self.bounds[k][1])
                for k in self.bounds.keys()
            ])
            y = self.objective_function(x)
            self.X_sample.append(x)
            self.y_sample.append(y)
            
        # 主优化循环
        kernel = Matern(nu=2.5)
        for i in range(self.n_iterations):
            # 训练GP模型
            model = GaussianProcessRegressor(
                kernel=kernel,
                n_restarts_optimizer=25
            )
            model.fit(np.array(self.X_sample), np.array(self.y_sample))
            
            # 寻找下一个采样点
            best_x = None
            best_acq = -np.inf
            
            # 随机搜索采集函数
            for _ in range(100):
                x = np.array([
                    np.random.uniform(self.bounds[k][0], self.bounds[k][1])
                    for k in self.bounds.keys()
                ])
                acq = self._acquisition_function(x, model)
                
                if acq > best_acq:
                    best_acq = acq
                    best_x = x
                    
            # 评估新点
            y = self.objective_function(best_x)
            self.X_sample.append(best_x)
            self.y_sample.append(y)
            
        # 返回最优结果
        best_idx = np.argmax(self.y_sample)
        return self.X_sample[best_idx], self.y_sample[best_idx] 