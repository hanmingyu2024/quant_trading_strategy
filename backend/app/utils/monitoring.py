"""
监控工具模块
用于系统监控和性能指标收集
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from prometheus_client import Counter, Histogram, start_http_server, CollectorRegistry
from backend.app.core.config import Settings
from backend.app.utils.database import get_connection_stats
from .logger import setup_logger

# 设置日志
logger = setup_logger(__name__)

# 创建独立的注册表
registry = CollectorRegistry()

class EmailMonitor:
    """邮件监控类"""
    
    def __init__(self, registry=None):
        self.registry = registry
        self.email_count = Counter(
            'email_sent_total',
            'Total number of emails sent',
            ['type'],
            registry=self.registry
        )
        self.email_latency = Histogram(
            'email_send_duration_seconds',
            'Email sending duration in seconds',
            registry=self.registry
        )
        self.failed_count = Counter(
            'email_failed_total',
            'Total number of failed email attempts',
            ['reason'],
            registry=self.registry
        )
        self._stats = {
            "total_sent": 0,
            "failed": 0,
            "queued": 0
        }
        
    def record_sent(self, email_type: str = "general") -> None:
        """记录发送的邮件"""
        self.email_count.labels(type=email_type).inc()
        self._stats["total_sent"] += 1
        
    def record_failure(self, reason: str) -> None:
        """记录失败的邮件"""
        self.failed_count.labels(reason=reason).inc()
        self._stats["failed"] += 1
        
    def record_queued(self) -> None:
        """记录排队的邮件"""
        self._stats["queued"] += 1
        
    def get_stats(self) -> Dict[str, int]:
        """获取统计数据"""
        return self._stats.copy()

# 创建全局实例
email_monitor = EmailMonitor(registry=registry)

def setup_monitoring(port: int = 8000, addr: str = '') -> None:
    """设置监控服务"""
    try:
        start_http_server(port, addr)
        logger.info(f"监控服务已启动在 {addr}:{port}")
    except Exception as e:
        logger.error(f"监控服务启动失败: {str(e)}")
        raise

def check_database_health() -> Dict[str, Any]:
    """检查数据库健康状态"""
    stats = get_connection_stats()
    warnings: List[str] = []
    
    if stats["last_connection_time"] > Settings.PERFORMANCE_CONFIG["thresholds"]["db_connection_time"]:
        warnings.append(f"连接时间过长: {stats['last_connection_time']:.2f}秒")
    
    if stats["active_connections"] < Settings.PERFORMANCE_CONFIG["thresholds"]["min_connections"]:
        warnings.append(f"可用连接数过低: {stats['active_connections']}")
    
    if stats["connection_errors"] > 0:
        error_rate = stats["connection_errors"] / stats["total_connections"]
        if error_rate > Settings.PERFORMANCE_CONFIG["thresholds"]["error_rate"]:
            warnings.append(f"连接错误率过高: {error_rate:.2%}")
    
    return {
        "status": "warning" if warnings else "healthy",
        "warnings": warnings,
        "stats": stats
    }

# 导出
__all__ = [
    "EmailMonitor",
    "email_monitor",
    "setup_monitoring",
    "registry"  # 导出注册表
]