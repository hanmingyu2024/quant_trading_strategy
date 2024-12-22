"""工具模块"""
import sys
from pathlib import Path
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)

# 路径设置
current_dir = Path(__file__).parent  # utils 目录
module_dir = current_dir.parent      # bigan_financial_model 目录
src_dir = module_dir.parent         # src 目录
project_root = src_dir.parent       # 项目根目录

# 确保所有必要的路径都在 sys.path 中
for path in [str(src_dir), str(module_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

try:
    # 只导入确认存在的模块
    from bigan_financial_model.utils.metrics import performance, risk
    from bigan_financial_model.utils.metrics.performance import PerformanceMetrics
    from bigan_financial_model.utils.metrics.risk import RiskMetrics
    
    logger.info("成功导入基础模块")
    
except ImportError as e:
    logger.warning(f"模块导入失败: {e}")

if __name__ == '__main__':
    logger.info("工具模块初始化成功")
    logger.info(f"项目根目录: {project_root}")

# 更新 API 列表
__all__ = [
    'RiskMetrics',
    'performance',
    'risk'
] 