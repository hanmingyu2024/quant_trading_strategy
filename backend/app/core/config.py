"""
应用配置模块
包含所有应用配置项
"""
from typing import List, Optional, Dict, Any, ClassVar
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from pathlib import Path
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Quant Trading Strategy"
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # 数据库连接池配置
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_CONNECT_TIMEOUT: int = 10
    DB_READ_TIMEOUT: int = 30
    DB_MAX_RETRIES: int = 3
    DB_RETRY_DELAY: float = 1.0
    DB_SLOW_QUERY_THRESHOLD: float = 1.0
    
    # 路径配置
    @property
    def PROJECT_ROOT(self) -> Path:
        return Path(__file__).parent.parent.parent.parent
    
    @property
    def LOG_DIR(self) -> Path:
        log_dir = self.PROJECT_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        return log_dir
    
    @property
    def STATIC_DIR(self) -> Path:
        static_dir = self.PROJECT_ROOT / "static"
        static_dir.mkdir(exist_ok=True)
        return static_dir
    
    @property
    def DATA_DIR(self) -> Path:
        data_dir = self.PROJECT_ROOT / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    # 性能监控配置
    PERFORMANCE_CONFIG: ClassVar[Dict[str, Any]] = {
        "thresholds": {
            "db_connection_time": 2.5,    # 单个连接最大耗时（秒）
            "total_warmup_time": 5.0,     # 总预热最大耗时（秒）
            "error_rate": 0.05,           # 允许的最大错误率（5%）
            "min_connections": 2,         # 最小可用连接数
        },
        "monitoring": {
            "enabled": True,
            "log_slow_queries": True,
            "slow_query_threshold": 1.0,  # 慢查询阈值（秒）
        }
    }
    
    # 数据库 URL 构建
    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{self.DB_USER}:{password}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    # 验证器
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # 邮件配置
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Quant Trading"
    SMTP_USE_TLS: bool = False
    SMTP_USE_SSL: bool = True
    SMTP_TIMEOUT: int = 30
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    # 缓存配置
    DEFAULT_CACHE_EXPIRE: int = 300  # 默认缓存时间(秒)
    MAX_CACHE_SIZE: int = 1000  # 最大缓存条目数
    CACHE_STRATEGY: str = "simple"  # 默认缓存策略
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "allow"

# 创建全局设置实例
settings = Settings()

# 确保所有必要的目录存在
for dir_path in [settings.LOG_DIR, settings.STATIC_DIR, settings.DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"确保目录存在: {dir_path}")
