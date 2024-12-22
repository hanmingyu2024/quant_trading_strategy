"""
日志模块
负责配置和管理系统的日志记录功能
支持同时输出到文件和控制台
文件日志支持按大小轮转
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(name):
    """设置日志记录器"""
    # 创建logs目录（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 文件处理器 - 添加 encoding='utf-8'
    log_file = os.path.join('logs', 'quant_trading.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'        # 添加 UTF-8 编码
    )
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化器 - 指定 ascii=False
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

if __name__ == "__main__":
    # 测试日志
    logger = setup_logger("test")
    logger.info("测试日志信息")
    logger.error("测试错误信息")
