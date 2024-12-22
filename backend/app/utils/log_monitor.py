import time
import threading
from pathlib import Path
from typing import Dict, List, Optional
import psutil
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogAlert:
    level: str
    message: str
    timestamp: datetime
    context: Dict

class LogMonitor:
    def __init__(self):
        self.alerts: List[LogAlert] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # 告警阈值
        self.thresholds = {
            'file_size_mb': 100,  # 日志文件大小阈值
            'error_rate': 0.1,    # 错误率阈值
            'memory_percent': 80,  # 内存使用阈值
            'cpu_percent': 80      # CPU使用阈值
        }
    
    def start(self):
        """启动监控"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(
                target=self._monitor_loop,
                name="LogMonitor",
                daemon=True
            )
            self._thread.start()
    
    def stop(self):
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join()
    
    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                self._check_log_files()
                self._check_system_resources()
                self._check_error_rates()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                self._add_alert('ERROR', f'监控异常: {str(e)}')
    
    def _check_log_files(self):
        """检查日志文件状态"""
        log_dir = Path("logs")
        if not log_dir.exists():
            return
        
        for log_file in log_dir.glob("*.log"):
            size_mb = log_file.stat().st_size / (1024 * 1024)
            if size_mb > self.thresholds['file_size_mb']:
                self._add_alert(
                    'WARNING',
                    f'日志文件过大: {log_file.name}',
                    {'size_mb': size_mb}
                )
    
    def _check_system_resources(self):
        """检查系统资源使用"""
        process = psutil.Process()
        
        # 检查内存使用
        memory_percent = process.memory_percent()
        if memory_percent > self.thresholds['memory_percent']:
            self._add_alert(
                'WARNING',
                f'内存使用率过高: {memory_percent:.1f}%',
                {'memory_percent': memory_percent}
            )
        
        # 检查CPU使用
        cpu_percent = process.cpu_percent()
        if cpu_percent > self.thresholds['cpu_percent']:
            self._add_alert(
                'WARNING',
                f'CPU使用率过高: {cpu_percent:.1f}%',
                {'cpu_percent': cpu_percent}
            )
    
    def _check_error_rates(self):
        """检查错误率"""
        from .logger import get_logger_manager
        stats = get_logger_manager().get_stats()
        
        for name, logger_stats in stats['统计信息'].items():
            if logger_stats['log_count'] > 0:
                error_rate = logger_stats['error_count'] / logger_stats['log_count']
                if error_rate > self.thresholds['error_rate']:
                    self._add_alert(
                        'WARNING',
                        f'日志器 {name} 错误率过高: {error_rate:.1%}',
                        {'error_rate': error_rate}
                    )
    
    def _add_alert(self, level: str, message: str, context: Dict = None):
        """添加告警"""
        alert = LogAlert(
            level=level,
            message=message,
            timestamp=datetime.now(),
            context=context or {}
        )
        self.alerts.append(alert)
        print(f"[{alert.timestamp}] {level}: {message}")
    
    def get_alerts(self, minutes: int = None) -> List[LogAlert]:
        """获取告警历史"""
        if minutes is None:
            return self.alerts
        
        cutoff = datetime.now().timestamp() - (minutes * 60)
        return [
            alert for alert in self.alerts
            if alert.timestamp.timestamp() > cutoff
        ]

# 全局监控器实例
log_monitor = LogMonitor() 