"""
日志管理模块

提供统一的日志记录功能,支持控制台和文件输出
作者: BiGan团队
日期: 2024-01
"""

import logging
from datetime import datetime
from typing import Optional

class Logger:
    def __init__(self, name: str, log_file: Optional[str] = None, 
                 level: int = logging.INFO):
        """
        增强的初始化函数
        
        Args:
            name: 日志器名称
            log_file: 日志文件路径
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 添加时间戳到日志文件名
        if log_file:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = log_file.replace('.log', f'_{timestamp}.log')
            
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def error(self, msg):
        self.logger.error(msg)
