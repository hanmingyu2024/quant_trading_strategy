import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from backend.app.utils.log_monitor import log_monitor, LogAlert
from backend.app.utils.logger import setup_logger

# 告警配置
ALERT_THRESHOLDS = {
    'file_size_mb': 200,      # 文件大小阈值
    'error_rate': 0.05,       # 错误率阈值
    'memory_percent': 85,     # 内存使用阈值
    'cpu_percent': 85,        # CPU使用阈值
    'alert_interval': 300     # 告警间隔(秒)
}

def send_dingtalk_message(alert: LogAlert):
    """发送钉钉告警"""
    print(f"[钉钉] 发送告警: {alert.level} - {alert.message}")
    # TODO: 实现钉钉通知
    
def send_email_alert(alert: LogAlert):
    """发送邮件告警"""
    print(f"[邮件] 发送告警: {alert.level} - {alert.message}")
    # TODO: 实现邮件通知

def send_alert(alert: LogAlert):
    """发送告警通知"""
    print(f"\n=== 发送告警通知 ===")
    if alert.level == 'WARNING':
        send_dingtalk_message(alert)
    elif alert.level == 'ERROR':
        send_email_alert(alert)
    print(f"告警内容: {alert.message}")
    print(f"告警时间: {alert.timestamp}")
    print(f"告警上下文: {alert.context}")

def test_monitor():
    """测试日志监控"""
    print("\n=== 测试日志监控 ===")
    
    # 更新监控阈值
    log_monitor.thresholds = ALERT_THRESHOLDS
    print("监控阈值配置:", log_monitor.thresholds)
    
    # 启动监控
    log_monitor.start()
    print("监控系统已启动")
    
    # 创建测试日志器
    logger = setup_logger("test.monitor")
    
    # 测试错误率告警
    print("\n测试错误率告警...")
    for i in range(100):
        try:
            1/0
        except:
            logger.error(f"测试错误 #{i+1}")
    
    # 测试大文件告警
    print("\n测试大文件告警...")
    large_data = "x" * (1024 * 1024)  # 1MB
    for i in range(50):
        logger.info(f"大文件测试 #{i+1}: {large_data[:100]}...")
    
    # 等待监控检查
    print("\n等待监控检查(65秒)...")
    time.sleep(65)
    
    # 显示告警
    print("\n最近告警:")
    recent_alerts = log_monitor.get_alerts(minutes=5)
    for alert in recent_alerts:
        print(f"[{alert.timestamp}] {alert.level}: {alert.message}")
        send_alert(alert)
    
    # 输出统计信息
    print("\n=== 监控统计信息 ===")
    print(f"总告警数: {len(recent_alerts)}")
    print(f"警告数: {sum(1 for a in recent_alerts if a.level == 'WARNING')}")
    print(f"错误数: {sum(1 for a in recent_alerts if a.level == 'ERROR')}")
    
    # 停止监控
    log_monitor.stop()
    print("\n监控系统已停止")

def test_metrics():
    """测试监控指标"""
    print("\n=== 测试监控指标 ===")
    
    logger = setup_logger("test.metrics")
    
    # 测试日志延迟
    start_time = time.time()
    logger.info("测试日志延迟")
    latency = time.time() - start_time
    print(f"日志写入延迟: {latency*1000:.2f}ms")
    
    # 测试系统资源
    import psutil
    process = psutil.Process()
    print(f"内存使用: {process.memory_percent():.1f}%")
    print(f"CPU使用: {process.cpu_percent():.1f}%")
    print(f"打开文件数: {len(process.open_files())}")

if __name__ == "__main__":
    try:
        test_monitor()
        test_metrics()
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        if log_monitor._running:
            log_monitor.stop()