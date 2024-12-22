"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dotenv import load_dotenv
import logging
from urllib.parse import quote_plus

# 创建日志实例
logger = logging.getLogger(__name__)

class Config:
    """配置类"""
    def __init__(self):
        self._config = self._load_config()
        self._setup_database_uri()

        # Redis配置
        self.config['redis'] = self.get_redis_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        # 加载环境变量
        load_dotenv()

        # 获取配置文件路径
        config_path = Path("config/environments/development.yaml")
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        # 读取配置文件
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return self._replace_env_vars(config)

    def _replace_env_vars(self, config: Dict) -> Dict:
        """递归替换配置中的环境变量"""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(v) for v in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            env_value = os.getenv(env_var)
            if env_value is None:
                return config
            return env_value
        return config

    def __getattr__(self, name: str) -> Any:
        """获取配置项"""
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"配置项 '{name}' 不存在")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持默认值"""
        return self._config.get(key, default)

    @property
    def config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config

    def _setup_database_uri(self):
        """设置数据库URI"""
        try:
            db = self.config['database']
            logger.info(f"数据库配置: {db}")

            # URL编码用户名和密码
            encoded_user = quote_plus(db['user'])
            encoded_password = quote_plus(db['password'])
            database_name = db.get('name', 'reinforcementlearningbot')

            self.DATABASE_URI = (
                f"mysql+pymysql://{encoded_user}:{encoded_password}@"
                f"{db['host']}:{db['port']}/{database_name}"
            )

            logger.info(f"数据库URI创建成功: {self.DATABASE_URI}")

        except KeyError as e:
            logger.error(f"数据库配置错误: 缺少必要的配置项 {e}")
            raise
        except Exception as e:
            logger.error(f"设置数据库URI时发生错误: {e}")
            raise

    def get_redis_config(self):
        return {
            'host': '172.22.255.181',
            'port': 6379,
            'password': 'complex_redis_password',
            'db': 0,
            'is_cluster': True,
            'cluster_nodes': [
                {'host': '172.16.1.1', 'port': 6379},
                {'host': '172.16.1.2', 'port': 6380},
                {'host': '172.16.1.3', 'port': 6381}
            ],
            'ssl': True,
            'timeout': 5,
            'max_connections': 100,
            'decode_responses': True
        }

# 创建全局配置实例
settings = Config()

# 导出配置类和实例
__all__ = ['Config', 'settings']
