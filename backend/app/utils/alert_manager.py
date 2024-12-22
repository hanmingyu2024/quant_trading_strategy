from enum import Enum
from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"

class Alert(BaseModel):
    title: str
    message: str
    level: AlertLevel
    timestamp: datetime = datetime.now()

class AlertManager:
    def __init__(self):
        self.alerts: List[Alert] = []
        self.stats: Dict[AlertLevel, int] = {
            level: 0 for level in AlertLevel
        }

    async def send_alert(self, alert: Alert, channels: List[AlertChannel]):
        """发送告警"""
        self.alerts.append(alert)
        self.stats[alert.level] += 1
        
        # 实现具体的告警发送逻辑
        for channel in channels:
            if channel == AlertChannel.EMAIL:
                await self._send_email_alert(alert)
            elif channel == AlertChannel.SMS:
                await self._send_sms_alert(alert)
            elif channel == AlertChannel.WEBHOOK:
                await self._send_webhook_alert(alert)

    def get_alert_stats(self) -> Dict:
        """获取告警统计信息"""
        return {
            "total_alerts": len(self.alerts),
            "by_level": self.stats,
            "recent_alerts": [
                alert.dict() 
                for alert in self.alerts[-10:]  # 最近10条告警
            ]
        }

    async def _send_email_alert(self, alert: Alert):
        """发送邮件告警"""
        # 实现邮件发送逻辑
        pass

    async def _send_sms_alert(self, alert: Alert):
        """发送短信告警"""
        # 实现短信发送逻辑
        pass

    async def _send_webhook_alert(self, alert: Alert):
        """发送webhook告警"""
        # 实现webhook发送逻辑
        pass

# 创建全局实例
alert_manager = AlertManager()