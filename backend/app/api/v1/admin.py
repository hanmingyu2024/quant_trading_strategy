from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any
from datetime import datetime, timedelta

from backend.app.utils import email_monitor
from backend.app.utils.queue_manager import queue_manager
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User
from backend.app.utils.alert_manager import alert_manager, AlertLevel, AlertChannel
from backend.app.utils.alert_rules import Rule, Condition, Operator, rule_engine
from pydantic import BaseModel

router = APIRouter(
    prefix="/admin",
    tags=["管理接口"],
    dependencies=[Depends(AuthService.get_current_admin_user)]
)

class ConditionSchema(BaseModel):
    field: str
    operator: str
    value: Any

class RuleSchema(BaseModel):
    name: str
    conditions: List[ConditionSchema]
    alert_level: str
    alert_message: str
    channels: List[str]
    cooldown_minutes: int = 5

@router.get("/email/stats")
def get_email_stats():
    """获取邮件统计信息"""
    return {
        "stats": email_monitor.get_stats(),
        "queue_size": queue_manager.get_queue_size()
    }

@router.get("/email/queue")
def get_queue_status():
    """获取队列状态"""
    return {
        "queue_size": queue_manager.get_queue_size(),
        "is_processing": queue_manager.is_processing,
        "batch_size": queue_manager.batch_size,
        "delay": queue_manager.delay
    }

@router.post("/email/queue/config")
def update_queue_config(batch_size: int = None, delay: float = None):
    """更新队列配置"""
    if batch_size is not None:
        if batch_size < 1 or batch_size > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size must be between 1 and 50"
            )
        queue_manager.batch_size = batch_size
        
    if delay is not None:
        if delay < 0.1 or delay > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delay must be between 0.1 and 10 seconds"
            )
        queue_manager.delay = delay
        
    return {
        "batch_size": queue_manager.batch_size,
        "delay": queue_manager.delay
    } 

@router.get("/alerts/stats")
async def get_alert_stats():
    """获取告警统计信息"""
    return alert_manager.get_alert_stats()

@router.post("/alerts/test")
async def send_test_alert(
    level: AlertLevel,
    message: str,
    channels: List[AlertChannel] = [AlertChannel.EMAIL]
):
    """发送测试告警"""
    await alert_manager.send_alert(
        Alert(
            title="测试告警",
            message=message,
            level=level
        ),
        channels=channels
    )
    return {"message": "Test alert sent"} 

@router.get("/alerts/rules")
async def get_rules():
    """获取所有规则"""
    return [
        {
            "name": rule.name,
            "conditions": [
                {
                    "field": c.field,
                    "operator": c.operator.value,
                    "value": c.value
                }
                for c in rule.conditions
            ],
            "alert_level": rule.alert_level.value,
            "alert_message": rule.alert_message,
            "channels": [c.value for c in rule.channels],
            "cooldown_minutes": int(rule.cooldown.total_seconds() / 60)
        }
        for rule in rule_engine.rules
    ]

@router.post("/alerts/rules")
async def create_rule(rule: RuleSchema):
    """创建新规则"""
    new_rule = Rule(
        name=rule.name,
        conditions=[
            Condition(
                field=c.field,
                operator=Operator(c.operator),
                value=c.value
            )
            for c in rule.conditions
        ],
        alert_level=AlertLevel(rule.alert_level),
        alert_message=rule.alert_message,
        channels=[AlertChannel(c) for c in rule.channels],
        cooldown=timedelta(minutes=rule.cooldown_minutes)
    )
    
    rule_engine.add_rule(new_rule)
    return {"message": "Rule created successfully"}

@router.delete("/alerts/rules/{rule_name}")
async def delete_rule(rule_name: str):
    """删除规则"""
    rule_engine.remove_rule(rule_name)
    return {"message": "Rule deleted successfully"} 