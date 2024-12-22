import sys
import os
import shutil
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import hashlib

class ProjectSetup:
    """项目设置和检查"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent  # 修改为项目根目录
        self.setup_logging()
        
        self.existing_files = []
        self.created_files = []
        self.skipped_files = []
        
    def setup_logging(self):
        """设置日志"""
        log_file = self.project_root / 'logs' / 'setup.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('project_setup')

    def _check_directories(self):
        """检查并创建目录结构"""
        dirs = [
            # 后端目录结构
            'backend/app/api/v1',
            'backend/app/core',
            'backend/app/exceptions',
            'backend/app/middlewares',
            'backend/app/migrations/versions',
            'backend/app/models',
            'backend/app/routes',
            'backend/app/schemas',
            'backend/app/services',
            'backend/app/static/css',
            'backend/app/static/images',
            'backend/app/static/js',
            'backend/app/strategies',
            'backend/app/templates/email',
            'backend/app/utils',
            'backend/database',
            'backend/monitoring',
            'backend/scripts',
            'backend/tests/logs',
            'backend/tests/reports',
            
            # 其他主要目录
            'backups/daily',
            'backups/weekly',
            'config',
            'data/samples',
            'docs/api',
            'docs/architecture',
            'docs/deployment',
            'logs',
            'modules',
            'monitoring/apm',
            'monitoring/metrics',
            'reports',
            'tools/project'
        ]
        
        for dir_path in dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True)
                self.logger.info(f"创建目录: {full_path}")
            else:
                self.logger.debug(f"目录已存在: {full_path}")

    def _check_files(self):
        """检查并创建必要文件"""
        files = {
            # 配置文件
            'config/config.py': self._get_config_content(),
            'config/logging_config.yaml': self._get_logging_config_content(),
            'config/monitoring.yaml': self._get_monitoring_config_content(),
            'config/trading_params.yaml': self._get_trading_params_content(),
            
            # 后端核心文件
            'backend/app/core/config.py': self._get_backend_config_content(),
            'backend/app/models/base.py': self._get_base_model_content(),
            'backend/app/utils/logger.py': self._get_logger_content(),
            'backend/app/utils/database.py': self._get_database_content(),
            'backend/app/strategies/base_strategy.py': self._get_base_strategy_content(),
            
            # 测试文件
            'backend/tests/conftest.py': self._get_conftest_content(),
            'backend/tests/test_config.py': self._get_test_config_content(),
            'backend/tests/test_base.py': self._get_test_base_content(),
            
            # 文档文件
            'docs/api_documentation.md': self._get_api_doc_content(),
            'docs/deployment.md': self._get_deployment_doc_content(),
            
            # 项目配置文件
            '.env': self._get_env_content(),
            'requirements.txt': self._get_requirements_content(),
            'docker-compose.yml': self._get_docker_compose_content()
        }
        
        for file_path, content in files.items():
            full_path = self.project_root / file_path
            
            if self._check_file_exists(full_path):
                self.logger.info(f"跳过已存在的文件: {full_path}")
                self.skipped_files.append(full_path)
                
                # 创建备份
                backup_path = full_path.parent / f"{full_path.stem}_backup{full_path.suffix}"
                if not backup_path.exists():
                    shutil.copy2(full_path, backup_path)
                    self.logger.info(f"创建备份: {backup_path}")
            else:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                self.logger.info(f"创建新文件: {full_path}")
                self.created_files.append(full_path)

    def _verify_imports(self):
        """验证关键模块导入"""
        try:
            # 验证核心模块
            from backend.app.core.config import Config
            from backend.app.models.base import Base
            from backend.app.utils.logger import setup_logger
            from backend.app.strategies.base_strategy import BaseStrategy
            
            # 验证测试模块
            from backend.tests.test_config import TestConfig
            from backend.tests.test_base import TestBase
            
            self.logger.info("所有必要模块导入成功")
            
        except ImportError as e:
            self.logger.error(f"模块导入失败: {e}")
            raise

    def _check_permissions(self):
        """检查关键目录权限"""
        dirs_to_check = [
            'logs',
            'data',
            'backups/daily',
            'backups/weekly',
            'backend/tests/logs',
            'backend/tests/reports'
        ]
        
        for dir_path in dirs_to_check:
            full_path = self.project_root / dir_path
            test_file = full_path / 'test_permissions.txt'
            try:
                test_file.write_text('test')
                test_file.unlink()
                self.logger.info(f"目录权限正常: {full_path}")
            except PermissionError:
                self.logger.error(f"权限错误: {full_path}")
                raise

    def _show_structure(self):
        """显示项目结构"""
        self.logger.info("\n=== 项目结构 ===")
        
        def print_tree(path: Path, prefix: str = ""):
            if path.is_file():
                self.logger.info(f"{prefix}└── {path.name}")
            else:
                self.logger.info(f"{prefix}└── {path.name}/")
                prefix += "    "
                for child in sorted(path.iterdir()):
                    if child.name not in ['__pycache__', '.git', '.pytest_cache']:
                        print_tree(child, prefix)
        
        print_tree(self.project_root)

    def _check_file_exists(self, file_path: Path) -> bool:
        """检查文件是否存在且有内容"""
        return file_path.exists() and file_path.stat().st_size > 0

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希值"""
        return hashlib.md5(file_path.read_bytes()).hexdigest()

    def show_summary(self):
        """显示文件处理摘要"""
        self.logger.info("\n=== 文件处理摘要 ===")
        
        if self.skipped_files:
            self.logger.info("\n跳过的文件:")
            for file in self.skipped_files:
                self.logger.info(f"- {file}")
        
        if self.created_files:
            self.logger.info("\n新创建的文件:")
            for file in self.created_files:
                self.logger.info(f"- {file}")

    def check_and_fix(self) -> bool:
        """检查并修复项目结构"""
        try:
            self.logger.info("=== 开始项目检查和修复 ===")
            
            # 1. 检查Python路径
            self._check_python_path()
            
            # 2. 检查并创建目录结构
            self._check_directories()
            
            # 3. 检查并创建必要文件（跳过已存在的）
            self._check_files()
            
            # 4. 验证导入
            self._verify_imports()
            
            # 5. 检查权限
            self._check_permissions()
            
            # 6. 显示项目结构
            self._show_structure()
            
            # 7. 显示处理摘要
            self.show_summary()
            
            self.logger.info("=== 项目检查和修复完成 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"项目设置失败: {e}")
            return False

    def _check_python_path(self):
        """检查并添加Python路径"""
        try:
            # 确保项目根目录在Python路径中
            project_root_str = str(self.project_root)
            if project_root_str not in sys.path:
                sys.path.append(project_root_str)
                self.logger.info(f"添加项目根目录到Python路径: {project_root_str}")
            
            # 检查backend目录
            backend_path = str(self.project_root / 'backend')
            if backend_path not in sys.path:
                sys.path.append(backend_path)
                self.logger.info(f"添加backend目录到Python路径: {backend_path}")
            
            # 验证路径
            self.logger.info("Python路径设置成功")
            self.logger.debug(f"当前Python路径: {sys.path}")
            
        except Exception as e:
            self.logger.error(f"设置Python路径失败: {e}")
            raise

    def _get_config_content(self) -> str:
        """获取配置文件内容"""
        return '''
from pathlib import Path

class Config:
    """配置类"""
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent.parent
        
        # 基础配置
        self.DEBUG = False
        self.TESTING = False
        self.SECRET_KEY = "your-secret-key-here"
        
        # 数据库配置
        self.DATABASE_URL = "sqlite:///./data/trading.db"
        
        # API配置
        self.API_V1_STR = "/api/v1"
        self.PROJECT_NAME = "Quant Trading Strategy"
        
        # 日志配置
        self.LOG_LEVEL = "INFO"
        self.LOG_DIR = self.BASE_DIR / "logs"
        
        # 监控配置
        self.METRICS_ENABLED = True
        self.METRICS_PORT = 8000
        
        # 交易配置
        self.BACKTEST_DATA_DIR = self.BASE_DIR / "data" / "samples"
        self.STRATEGY_DIR = self.BASE_DIR / "backend" / "app" / "strategies"

config = Config()
'''

    def _get_logging_config_content(self) -> str:
        """获取日志配置内容"""
        return '''
version: 1
disable_existing_loggers: false

formatters:
    standard:
        format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    error:
        format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

handlers:
    console:
        class: logging.StreamHandler
        level: INFO
        formatter: standard
        stream: ext://sys.stdout

    file:
        class: logging.handlers.RotatingFileHandler
        level: INFO
        formatter: standard
        filename: logs/app.log
        maxBytes: 10485760
        backupCount: 5

    error_file:
        class: logging.handlers.RotatingFileHandler
        level: ERROR
        formatter: error
        filename: logs/error.log
        maxBytes: 10485760
        backupCount: 5

loggers:
    "":
        level: INFO
        handlers: [console, file, error_file]
        propagate: true
'''

    def _get_monitoring_config_content(self) -> str:
        """获取监控配置内容"""
        return '''
metrics:
    enabled: true
    port: 8000
    path: /metrics

apm:
    enabled: true
    service_name: quant_trading
    server_url: http://localhost:8200

logging:
    level: INFO
    file: logs/monitoring.log
'''

    def _get_trading_params_content(self) -> str:
        """获取交易参数配置内容"""
        return '''
backtest:
    start_date: "2023-01-01"
    end_date: "2023-12-31"
    initial_capital: 100000
    commission: 0.0003

strategy:
    ma_cross:
        short_window: 5
        long_window: 20
        risk_limit: 0.02

risk_management:
    max_position_size: 0.1
    stop_loss: 0.02
    take_profit: 0.05
'''

    def _get_backend_config_content(self) -> str:
        """获取后端配置内容"""
        return '''
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """后端配置设置"""
    PROJECT_NAME: str = "Quant Trading Strategy"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/trading.db"
    
    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    
    class Config:
        case_sensitive = True

settings = Settings()
'''

    def _get_base_model_content(self) -> str:
        """获取基础模型内容"""
        return '''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
'''

    def _get_logger_content(self) -> str:
        """获取日志工具内容"""
        return '''
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: str = "INFO",
    rotation: int = 5242880,  # 5MB
    retention: int = 5
) -> logging.Logger:
    """设置日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=rotation,
            backupCount=retention
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
'''

    def _get_database_content(self) -> str:
        """获取数据库工具内容"""
        return '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
from backend.app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

    def _get_base_strategy_content(self) -> str:
        """获取基础策略内容"""
        return '''
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd
from backend.app.utils.logger import setup_logger

class BaseStrategy(ABC):
    """基础策略类"""
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.logger = setup_logger(self.__class__.__name__)
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        pass
        
    @abstractmethod
    def calculate_position(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算仓位"""
        pass
        
    def validate_params(self) -> bool:
        """验证参数"""
        return True
        
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        """运行策略"""
        if not self.validate_params():
            raise ValueError("策略参数无效")
            
        signals = self.generate_signals(data)
        positions = self.calculate_position(signals)
        return positions
'''

    def _get_conftest_content(self) -> str:
        """获取测试配置内容"""
        return '''
import pytest
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.base import Base
from backend.tests.test_config import test_config

# 测试数据库引擎
test_engine = create_engine(test_config.DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=test_engine)

@pytest.fixture(scope="session")
def db_engine():
    """创建测试数据库引擎"""
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator:
    """创建测试数据库会话"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
'''

    def _get_test_config_content(self) -> str:
        """获取测试配置内容"""
        return '''
from pathlib import Path
from backend.app.core.config import Config

class TestConfig(Config):
    """测试配置类"""
    
    def __init__(self):
        super().__init__()
        
        # 测试专用配置
        self.TESTING = True
        self.DATABASE_URL = "sqlite:///./test.db"
        self.LOG_DIR = self.BASE_DIR / "tests" / "logs"
        
        # 测试资源限制
        self.MEMORY_LIMIT = 90.0  # %
        self.CPU_LIMIT = 85.0     # %

test_config = TestConfig()
'''

    def _get_test_base_content(self) -> str:
        """获取测试基类内容"""
        return '''
import unittest
import logging
from pathlib import Path
from backend.app.core.base import BaseClass
from backend.tests.test_config import test_config

class TestBase(BaseClass, unittest.TestCase):
    """测试基类"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        cls.config = test_config
        cls.logger = cls.setup_logger(
            cls.__name__,
            cls.config.LOG_DIR / f"{cls.__name__}.log"
        )
        
    def setUp(self):
        """设置测试用例"""
        self.check_test_resources()
        
    @classmethod
    def check_test_resources(cls):
        """检查测试资源"""
        cls.check_system_resources(
            memory_limit=cls.config.MEMORY_LIMIT,
            cpu_limit=cls.config.CPU_LIMIT
        )
'''

    def _get_api_doc_content(self) -> str:
        """获取API文档内容"""
        return '''
# API Documentation

## Overview
This document describes the API endpoints for the Quant Trading Strategy system.

## Authentication
All API requests require authentication using JWT tokens.

## Endpoints

### User Management
- POST /api/v1/users/register
- POST /api/v1/users/login
- GET /api/v1/users/me

### Trading
- GET /api/v1/trades
- POST /api/v1/trades
- GET /api/v1/trades/{trade_id}

### Strategy
- GET /api/v1/strategies
- POST /api/v1/strategies
- GET /api/v1/strategies/{strategy_id}
'''

    def _get_deployment_doc_content(self) -> str:
        """获取部署文档内容"""
        return '''
# Deployment Guide

## Requirements
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

## Installation
1. Clone the repository
2. Install dependencies
3. Configure environment variables
4. Initialize database
5. Start the application

## Docker Deployment
See kubernetes/ directory for manifests.
'''

    def _get_env_content(self) -> str:
        """获取环境变量内容"""
        return '''
# Application
DEBUG=False
SECRET_KEY=your-secret-key-here
API_V1_STR=/api/v1

# Database
DATABASE_URL=sqlite:///./data/trading.db

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Monitoring
METRICS_ENABLED=True
METRICS_PORT=8000
'''

    def _get_requirements_content(self) -> str:
        """获取依赖要求内容"""
        return '''
# Core
fastapi>=0.68.0
uvicorn>=0.15.0
sqlalchemy>=1.4.23
pydantic>=1.8.2
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.5
email-validator>=1.1.3

# Database
alembic>=1.7.3
psycopg2-binary>=2.9.1

# Testing
pytest>=6.2.5
pytest-cov>=2.12.1
httpx>=0.19.0

# Monitoring
prometheus-client>=0.11.0
elastic-apm>=6.3.3

# Utils
python-dotenv>=0.19.0
pyyaml>=5.4.1
pandas>=1.3.3
numpy>=1.21.2
'''

    def _get_docker_compose_content(self) -> str:
        """获取Docker Compose内容"""
        return '''
version: "3.8"

services:
  api:
    build: 
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/trading
    depends_on:
      - db
      
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=trading
    volumes:
      - postgres_data:/var/lib/postgresql/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

volumes:
  postgres_data:
'''

def main():
    """主函数"""
    setup = ProjectSetup()
    if setup.check_and_fix():
        setup.logger.info("\n项目设置成功!")
        setup.logger.info("\n下一步:")
        setup.logger.info("1. 检查生成的配置文件")
        setup.logger.info("2. 根据需要修改配置")
        setup.logger.info("3. 运行覆盖率测试")
    else:
        setup.logger.error("\n项目设置失败!")
        setup.logger.error("请检查日志文件了解详细错误信息。")

if __name__ == "__main__":
    main() 