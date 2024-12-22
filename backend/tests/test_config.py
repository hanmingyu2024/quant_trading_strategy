from pathlib import Path
import sys
from backend.app.config.config import Config  # 导入主配置

class TestConfig(Config):
    """测试环境配置"""
    
    def __init__(self):
        super().__init__()
        
        # 继承主配置的同时添加测试专用配置
        self.test_config = {
            'test_dirs': [
                'utils',
                'models', 
                'services',
                'strategies',
                'api'
            ],
            
            'coverage_source': [
                'backend/app/utils',
                'backend/app/models',
                'backend/app/services',
                'backend/app/strategies',
                'backend/app/api'
            ],
            
            'coverage_omit': [
                '*/tests/*',
                '*/__init__.py',
                '*/migrations/*'
            ]
        }
        
        # 测试环境特定设置
        self.DEBUG = True
        self.TESTING = True
        
        # 测试数据库配置
        self.DATABASE_URL = "sqlite:///test.db"
        
        # 测试报告路径
        self.REPORT_DIR = self.BASE_DIR / 'tests' / 'reports'
        self.LOG_DIR = self.BASE_DIR / 'tests' / 'logs'
        
        # 资源限制
        self.MEMORY_LIMIT = 90.0  # %
        self.CPU_LIMIT = 85.0     # %

# 全局测试配置实例
test_config = TestConfig() 