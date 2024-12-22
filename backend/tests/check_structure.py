from pathlib import Path
import sys

def check_project_structure():
    """检查项目结构"""
    project_root = Path(__file__).parent.parent
    
    # 必需的目录
    required_dirs = {
        'app': project_root / 'app',
        'tests': project_root / 'tests',
        'config': project_root / 'app' / 'config',
        'core': project_root / 'app' / 'core',
        'logs': project_root / 'tests' / 'logs',
        'reports': project_root / 'tests' / 'reports'
    }
    
    # 必需的文件
    required_files = {
        'main_config': project_root / 'app' / 'config' / 'config.py',
        'base_class': project_root / 'app' / 'core' / 'base.py',
        'test_config': project_root / 'tests' / 'test_config.py',
        'test_base': project_root / 'tests' / 'test_base.py'
    }
    
    # 检查并创建目录
    for name, path in required_dirs.items():
        if not path.exists():
            print(f"创建目录: {path}")
            path.mkdir(parents=True, exist_ok=True)
    
    # 检查文件
    missing_files = []
    for name, path in required_files.items():
        if not path.exists():
            missing_files.append(name)
    
    return missing_files

def setup_project():
    """设置项目结构"""
    missing_files = check_project_structure()
    
    if missing_files:
        print("\n缺少以下文件:")
        for file in missing_files:
            print(f"- {file}")
        
        # 创建缺失的基础文件
        if 'main_config' in missing_files:
            create_main_config()
        if 'base_class' in missing_files:
            create_base_class()
            
        print("\n基础文件已创建，请检查并完善其内容。")
    else:
        print("\n项目结构完整。")

def create_main_config():
    """创建主配置文件"""
    config_content = """
from pathlib import Path

class Config:
    \"\"\"主配置类\"\"\"
    
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent.parent
        
        # 基础配置
        self.DEBUG = False
        self.TESTING = False
        
        # 数据库配置
        self.DATABASE_URL = "sqlite:///app.db"
        
        # 日志配置
        self.LOG_LEVEL = "INFO"
        self.LOG_DIR = self.BASE_DIR / 'logs'
        
        # API配置
        self.API_PREFIX = "/api/v1"
        
        # 系统配置
        self.MEMORY_LIMIT = 85.0  # %
        self.CPU_LIMIT = 80.0     # %

# 全局配置实例
config = Config()
"""
    
    config_path = Path(__file__).parent.parent / 'app' / 'config' / 'config.py'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config_content)
    print(f"创建配置文件: {config_path}")

def create_base_class():
    """创建基础类文件"""
    base_content = """
import logging
import psutil
from pathlib import Path
from backend.app.config.config import config

class BaseClass:
    \"\"\"基础类\"\"\"
    
    @classmethod
    def setup_logger(cls, name, log_file=None, level=None):
        \"\"\"设置日志器\"\"\"
        logger = logging.getLogger(name)
        level = level or getattr(logging, config.LOG_LEVEL)
        logger.setLevel(level)
        
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        
        return logger
    
    @classmethod
    def check_system_resources(cls, memory_limit=None, cpu_limit=None):
        \"\"\"检查系统资源\"\"\"
        process = psutil.Process()
        memory_percent = process.memory_percent()
        cpu_percent = process.cpu_percent()
        
        memory_limit = memory_limit or config.MEMORY_LIMIT
        cpu_limit = cpu_limit or config.CPU_LIMIT
        
        if memory_percent > memory_limit:
            raise MemoryError(f"内存使用过高: {memory_percent}%")
        if cpu_percent > cpu_limit:
            raise ResourceWarning(f"CPU使用过高: {cpu_percent}%")
"""
    
    base_path = Path(__file__).parent.parent / 'app' / 'core' / 'base.py'
    base_path.parent.mkdir(parents=True, exist_ok=True)
    base_path.write_text(base_content)
    print(f"创建基础类文件: {base_path}")

if __name__ == "__main__":
    setup_project() 