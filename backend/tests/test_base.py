import unittest
import logging
import time
from backend.app.core.base import BaseClass  # 导入主基类

class TestBase(BaseClass, unittest.TestCase):
    """测试基类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = test_config  # 使用测试配置
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        super().setUpClass()
        cls.setup_test_logging()
        cls.check_test_resources()
    
    @classmethod
    def setup_test_logging(cls):
        """设置测试日志"""
        log_file = cls.config.LOG_DIR / f"{cls.__name__}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        cls.logger = cls.setup_logger(
            name=cls.__name__,
            log_file=log_file,
            level=logging.DEBUG if cls.config.DEBUG else logging.INFO
        )
    
    @classmethod
    def check_test_resources(cls):
        """检查测试资源"""
        cls.check_system_resources(
            memory_limit=cls.config.MEMORY_LIMIT,
            cpu_limit=cls.config.CPU_LIMIT
        ) 