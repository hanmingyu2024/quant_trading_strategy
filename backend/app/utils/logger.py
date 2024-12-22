import os
import sys
import logging
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import psutil

class LoggerManager:
    """日志管理器（单例模式）"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化日志管理器"""
        self._loggers: Dict[str, logging.Logger] = {}
        self._stats: Dict[str, Dict] = {}
        self._start_time = datetime.now()
        self._root_dir = self._get_project_root()
        
    def _get_project_root(self) -> Path:
        """获取项目根目录"""
        current_file = Path(__file__).resolve()
        for parent in [current_file, *current_file.parents]:
            if (parent / '.git').exists() or (parent / 'pyproject.toml').exists():
                return parent
        return current_file.parent.parent.parent.parent
    
    def _setup_logger(self, logger: logging.Logger, name: str):
        """配置日志器"""
        # 1. 基本设置
        logger.setLevel(logging.INFO)
        
        # 2. 创建日志目录
        log_dir = self._root_dir / 'logs'
        log_dir.mkdir(exist_ok=True, parents=True)
        
        # 3. 配置文件处理器
        file_handler = RotatingFileHandler(
            filename=str(log_dir / 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # 4. 配置格式化器
        formatter = logging.Formatter(
            '%(asctime)s - [%(process)d:%(threadName)s] - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 5. 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 6. 初始化统计信息
        self._stats[name] = {
            'created_at': datetime.now(),
            'log_count': 0,
            'error_count': 0,
            'last_error': None,
            'last_log_time': None
        }
        
        # 7. 添加日志计数过滤器
        def count_logs(record):
            stats = self._stats[name]
            stats['log_count'] += 1
            stats['last_log_time'] = datetime.now()
            if record.levelno >= logging.ERROR:
                stats['error_count'] += 1
                stats['last_error'] = record.getMessage()
            return True
            
        logger.addFilter(count_logs)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取或创建日志器"""
        # 1. 检查缓存
        if name in self._loggers:
            return self._loggers[name]
        
        # 2. 线程安全创建
        with self._lock:
            if name in self._loggers:
                return self._loggers[name]
            
            # 3. 创建新的日志器
            logger = logging.getLogger(name)
            if not logger.handlers:
                self._setup_logger(logger, name)
                
                # 4. 输出初始化信息
                if not self._loggers:  # 首次初始化
                    self._print_debug_info()
                
                logger.info(
                    "日志配置成功",
                    extra={
                        'pid': os.getpid(),
                        'memory_mb': psutil.Process().memory_info().rss / 1024 / 1024
                    }
                )
            
            # 5. 缓存并返回
            self._loggers[name] = logger
            return logger
    
    def _print_debug_info(self):
        """打印调试信息"""
        debug_info = {
            "初始化时间": self._start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "进程信息": f"PID: {os.getpid()} | 线程: {threading.current_thread().name}",
            "当前文件": str(Path(__file__).resolve()),
            "项目根目录": str(self._root_dir),
            "日志目录": str(self._root_dir / 'logs'),
            "日志文件": str(self._root_dir / 'logs' / 'app.log'),
            "Python路径": '\n  - '.join([''] + sorted(set(str(Path(p).resolve()) for p in sys.path))),
            "工作目录": str(Path.cwd().resolve())
        }
        
        print("\n=== 日志配置调试信息 ===")
        for key, value in debug_info.items():
            print(f"{key}: {value}")
        print("=====================\n")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "运行时间": (datetime.now() - self._start_time).total_seconds(),
            "日志器数量": len(self._loggers),
            "统计信息": self._stats,
            "系统信息": {
                "内存使用(MB)": psutil.Process().memory_info().rss / 1024 / 1024,
                "CPU使用率": psutil.Process().cpu_percent(),
                "线程数": len(threading.enumerate())
            }
        }

# 全局实例和接口
_logger_manager = None

def get_logger_manager() -> LoggerManager:
    """获取日志管理器实例"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager

def setup_logger(name: str) -> logging.Logger:
    """统一的日志配置入口"""
    return get_logger_manager().get_logger(name)