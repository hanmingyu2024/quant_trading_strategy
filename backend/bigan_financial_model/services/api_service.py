"""
BiGan金融模型的API服务模块

该模块提供了基于FastAPI的HTTP API服务,用于模型的训练和预测。
主要功能包括:
- 模型训练API接口
- 模型预测API接口
- 数据处理和转换
- 智能体训练流程
- API服务配置和启动

作者: BiGan团队
日期: 2023-10
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
import logging

from core.logger import Logger
from core.config import Config
from bigan_financial_model.services.data_service import DataService
from agents.reinforcement_learning import RLAgent
from fastapi.templating import Jinja2Templates
from analysis.market_analysis import MarketAnalyzer
from bigan_financial_model.data.fetcher import DataFetcher

# 请求模型定义
class TrainingRequest(BaseModel):
    """训练请求模型"""
    symbol: str                    # 交易对符号
    start_date: str               # 开始日期
    end_date: str                 # 结束日期
    episodes: int = 100           # 训练轮数
    batch_size: int = 32          # 批次大小
    learning_rate: float = 0.001  # 学习率

class PredictionRequest(BaseModel):
    """预测请求模型"""
    symbol: str                   # 交易对符号
    features: List[float]         # 特征数据
    timestamp: Optional[str]      # 时间戳

class ModelStatus(BaseModel):
    """模型状态"""
    is_trained: bool             # 是否已训练
    last_trained: Optional[str]  # 最后训练时间
    total_episodes: int          # 总训练轮数
    current_episode: int         # 当前训练轮数
    training_loss: float         # 训练损失
    validation_accuracy: float   # 验证准确率

class APIService:
    def __init__(self, config: Config):
        """初始化API服务"""
        self.app = FastAPI(
            title="BiGan Financial Model",
            description="基于深度强化学习的金融交易模型",
            version="1.0.0"
        )
        
        # 设置CORS（跨域资源共享）
        from fastapi.middleware.cors import CORSMiddleware
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.logger = Logger("APIService")
        self.config = config
        self.data_service = DataService(self.config)
        self.market_analyzer = MarketAnalyzer(self.data_service)
        self.agent = None
        self.model_status = ModelStatus(
            is_trained=False,
            last_trained=None,
            total_episodes=0,
            current_episode=0,
            training_loss=0.0,
            validation_accuracy=0.0
        )
        self._setup_routes()
        
        # 挂载静态文件目录
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        
        # 设置模板
        self.templates = Jinja2Templates(directory="templates")
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            return self.templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "logo_url": "/static/images/logo.png"
                }
            )

        # 设置favicon
        @self.app.get("/favicon.ico")
        async def favicon():
            return self.app.send_file("static/favicon.ico")

    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/")
        async def root():
            """根路由"""
            return {
                "message": "BiGan Financial Model API",
                "version": "1.0.0",
                "status": "running"
            }

        @self.app.get("/status")
        async def get_status():
            """获取模型状态"""
            return {
                "model_status": self.model_status.dict(),
                "system_info": {
                    "cpu_usage": self._get_cpu_usage(),
                    "memory_usage": self._get_memory_usage(),
                    "uptime": self._get_uptime()
                }
            }

        @self.app.post("/train")
        async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
            """训练模型"""
            try:
                # 验证请求参数
                self._validate_dates(request.start_date, request.end_date)
                
                # 加载数据
                data = self.data_service.load_data(
                    request.symbol,
                    request.start_date,
                    request.end_date
                )
                if data is None:
                    raise HTTPException(status_code=400, detail="数据加载失败")

                # 处理数据
                processed_data = self.data_service.process_data(data)
                if processed_data is None:
                    raise HTTPException(status_code=400, detail="数据处理失败")

                # 初始化模型（如果需要）
                if self.agent is None:
                    state_dim = processed_data['features'].shape[1]
                    action_dim = 3  # 买入、卖出、持有
                    self.agent = RLAgent(state_dim, action_dim)

                # 在后台开始训练
                background_tasks.add_task(
                    self._train_model_task,
                    processed_data,
                    request.episodes,
                    request.batch_size,
                    request.learning_rate
                )

                return {
                    "status": "success",
                    "message": "模型训练已开始",
                    "task_id": str(datetime.now().timestamp())
                }

            except Exception as e:
                self.logger.error(f"训练失败: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/predict")
        async def predict(request: PredictionRequest):
            """进行预测"""
            try:
                if not self.model_status.is_trained:
                    raise HTTPException(status_code=400, detail="模型未训练")

                if self.agent is None:
                    raise HTTPException(status_code=500, detail="模型未初始化")

                # 特征预处理
                features = np.array(request.features).reshape(1, -1)
                
                # 获取预测
                action = self.agent.act(features)
                confidence = self.agent.get_action_confidence(features)

                # 转换预测结果
                action_map = {0: "卖出", 1: "持有", 2: "买入"}
                prediction = action_map[action]

                return {
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "prediction": prediction,
                    "confidence": float(confidence),
                    "metadata": {
                        "model_version": "1.0.0",
                        "last_trained": self.model_status.last_trained
                    }
                }

            except Exception as e:
                self.logger.error(f"预测失败: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/model/performance")
        async def get_model_performance():
            """获取模型性能指标"""
            if not self.model_status.is_trained:
                raise HTTPException(status_code=400, detail="模型未训练")

            return {
                "accuracy": self.model_status.validation_accuracy,
                "training_loss": self.model_status.training_loss,
                "metrics": {
                    "sharpe_ratio": self._calculate_sharpe_ratio(),
                    "max_drawdown": self._calculate_max_drawdown(),
                    "win_rate": self._calculate_win_rate()
                }
            }

        @self.app.get("/market/data")
        async def get_market_data(symbol: str, start_date: str, end_date: str):
            """获取市场数据API"""
            return self.data_service.get_data(symbol, start_date, end_date)
        
        @self.app.get("/market/analysis")
        async def get_market_analysis(symbol: str, start_date: str, end_date: str):
            """获取市场分析API"""
            return self.market_analyzer.analyze_market(symbol, start_date, end_date)

    async def _train_model_task(self, data: Dict, episodes: int, batch_size: int, learning_rate: float):
        """后台训练任务"""
        try:
            self.model_status.is_trained = False
            self.model_status.total_episodes = episodes
            
            # 训练模型
            for episode in range(episodes):
                self.model_status.current_episode = episode + 1
                
                # 训练一个回合
                episode_loss = self.agent.train_episode(
                    data['features'],
                    data['prices'],
                    batch_size
                )
                
                self.model_status.training_loss = episode_loss
                
                # 每10个回合记录日志
                if (episode + 1) % 10 == 0:
                    self.logger.info(f"Episode {episode + 1}/{episodes}, Loss: {episode_loss:.4f}")

            # 更新模型状态
            self.model_status.is_trained = True
            self.model_status.last_trained = datetime.now().isoformat()
            
            # 评估模型
            self.model_status.validation_accuracy = self.agent.evaluate(
                data['features'],
                data['prices']
            )
            
            self.logger.info("模型训练完成")

        except Exception as e:
            self.logger.error(f"训练任务失败: {str(e)}")
            self.model_status.is_trained = False
            raise

    def _validate_dates(self, start_date: str, end_date: str):
        """验证日期格式"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start >= end:
                raise ValueError("开始日期必须早于结束日期")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def _get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        # 这里可以使用psutil库获取实际CPU使用率
        return 0.0

    def _get_memory_usage(self) -> float:
        """获取内存使用率"""
        # 这里可以使用psutil库获取实际内存使用率
        return 0.0

    def _get_uptime(self) -> str:
        """获取运行时间"""
        # 返回服务启动时间
        return "0:00:00"

    def _calculate_sharpe_ratio(self) -> float:
        """计算夏普比率"""
        return 0.0

    def _calculate_max_drawdown(self) -> float:
        """计算最大回撤"""
        return 0.0

    def _calculate_win_rate(self) -> float:
        """计算胜率"""
        return 0.0

    def start(self, host: str = "127.0.0.1", port: int = 8000):
        """启动API服务"""
        import uvicorn
        self.logger.info(f"启动API服务 at {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)
