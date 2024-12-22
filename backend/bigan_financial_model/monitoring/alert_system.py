"""
警报系统模块

提供邮件和Slack警报功能,用于监控系统指标和发送通知
作者: BiGan团队
日期: 2024-01
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import logging

class AlertSystem:
    def __init__(
        self,
        email_config: Optional[Dict[str, str]] = None,
        slack_webhook: Optional[str] = None
    ):
        self.email_config = email_config
        self.slack_webhook = slack_webhook
        self.logger = logging.getLogger(__name__)
        
    def check_threshold(
        self,
        metric_name: str,
        value: float,
        threshold: float,
        comparison: str = 'greater'
    ) -> bool:
        """检查指标是否超过阈值"""
        if comparison == 'greater':
            return value > threshold
        elif comparison == 'less':
            return value < threshold
        elif comparison == 'equal':
            return value == threshold
        else:
            raise ValueError(f"Unknown comparison type: {comparison}")
            
    def send_email_alert(
        self,
        subject: str,
        message: str
    ) -> bool:
        """发送邮件警报"""
        if not self.email_config:
            self.logger.warning("Email configuration not provided")
            return False
            
        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            
            with smtplib.SMTP_SSL(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            ) as server:
                server.login(
                    self.email_config['username'],
                    self.email_config['password']
                )
                server.send_message(msg)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
            return False
            
    def send_slack_alert(
        self,
        message: str
    ) -> bool:
        """发送Slack警报"""
        if not self.slack_webhook:
            self.logger.warning("Slack webhook not provided")
            return False
            
        try:
            import requests
            response = requests.post(
                self.slack_webhook,
                json={"text": message}
            )
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {str(e)}")
            return False 