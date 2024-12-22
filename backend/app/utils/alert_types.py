from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"

@dataclass
class Alert:
    title: str
    message: str
    level: AlertLevel
    details: Optional[Dict] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "message": self.message,
            "level": self.level.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        } 