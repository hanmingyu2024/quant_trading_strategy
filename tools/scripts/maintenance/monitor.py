"""
系统监控脚本

功能:
- 监控系统资源使用情况(CPU、内存、磁盘等)
- 监控关键服务状态
- 发送告警通知
- 生成监控报告

作者: Han Mingyu 
邮箱: 13364694109ai@gmail.com
"""

import os
import psutil
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SystemMonitor:
    def __init__(self):
        # 初始化日志
        self.logger = self._setup_logging()
        
        # 告警阈值配置
        self.thresholds = {
            'cpu_percent': 80.0,  # CPU使用率阈值
            'memory_percent': 85.0,  # 内存使用率阈值
            'disk_percent': 90.0,  # 磁盘使用率阈值
        }
        
        # 邮件通知配置
        self.smtp_config = {
            'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD'),
            'from_addr': os.getenv('ALERT_FROM_EMAIL'),
            'to_addrs': os.getenv('ALERT_TO_EMAILS', '').split(',')
        }

    def _setup_logging(self) -> logging.Logger:
        """配置日志"""
        logger = logging.getLogger('system_monitor')
        logger.setLevel(logging.INFO)
        
        # 创建日志目录
        log_dir = Path(__file__).parent.parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 设置日志文件
        log_file = log_dir / f'monitor_{datetime.now().strftime("%Y%m%d")}.log'
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def get_system_metrics(self) -> Dict:
        """获取系统指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'percent': psutil.disk_usage('/').percent
            }
        }
        return metrics

    def check_services(self) -> List[Dict]:
        """检查关键服务状态"""
        services = ['docker', 'mysql', 'nginx']  # 需要监控的服务列表
        service_status = []
        
        for service in services:
            try:
                cmd = f"systemctl is-active {service}"
                status = os.system(cmd) == 0
                service_status.append({
                    'name': service,
                    'status': 'running' if status else 'stopped',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"检查服务{service}状态时出错: {str(e)}")
                
        return service_status

    def send_alert(self, subject: str, message: str):
        """发送告警邮件"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from_addr']
            msg['To'] = ', '.join(self.smtp_config['to_addrs'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
                
            self.logger.info(f"已发送告警邮件: {subject}")
        except Exception as e:
            self.logger.error(f"发送告警邮件失败: {str(e)}")

    def check_alerts(self, metrics: Dict):
        """检查是否需要发送告警"""
        alerts = []
        
        if metrics['cpu_percent'] > self.thresholds['cpu_percent']:
            alerts.append(f"CPU使用率过高: {metrics['cpu_percent']}%")
            
        if metrics['memory']['percent'] > self.thresholds['memory_percent']:
            alerts.append(f"内存使用率过高: {metrics['memory']['percent']}%")
            
        if metrics['disk']['percent'] > self.thresholds['disk_percent']:
            alerts.append(f"磁盘使用率过高: {metrics['disk']['percent']}%")
            
        if alerts:
            alert_message = "\n".join(alerts)
            self.send_alert("系统资源告警", alert_message)

    def run(self, interval: int = 300):
        """运行监控"""
        self.logger.info("开始系统监控...")
        
        while True:
            try:
                # 获取系统指标
                metrics = self.get_system_metrics()
                self.logger.info(f"系统指标: {json.dumps(metrics, ensure_ascii=False)}")
                
                # 检查服务状态
                service_status = self.check_services()
                self.logger.info(f"服务状态: {json.dumps(service_status, ensure_ascii=False)}")
                
                # 检查告警
                self.check_alerts(metrics)
                
                # 等待下一次检查
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"监控过程出错: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再重试

if __name__ == '__main__':
    monitor = SystemMonitor()
    monitor.run()
