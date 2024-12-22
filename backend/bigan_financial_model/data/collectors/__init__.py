"""
BiGan Financial Model 主包
"""
# 标准库导入
import sys
import logging
from pathlib import Path

# 设置版本号
__version__ = "0.1.0"

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加一些输出信息
logger.info("成功导入\n基础模块")
