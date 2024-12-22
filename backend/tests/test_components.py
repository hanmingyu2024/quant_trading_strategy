"""
组件功能测试脚本：测试各个核心组件的具体功能
"""
import asyncio
from datetime import timedelta
from backend.app.utils import (
    email_monitor, 
    queue_manager, 
    alert_manager, 
    rule_engine
)
from backend.app.utils.alert_manager import Alert, AlertLevel, AlertChannel
from backend.app.utils.alert_rules import Rule, Condition, Operator

async def test_email_monitor():
    """测试邮件监控组件"""
    print("\n=== 测试 Email Monitor ===")
    
    # 记录几封测试邮件
    print("发送测试邮件...")
    email_monitor.record_sent(0.5)  # 成功发送，延迟0.5秒
    email_monitor.record_sent(0.3)  # 成功发送，延迟0.3秒
    email_monitor.record_failure()   # 记录一次失败
    
    # 获取统计信息
    stats = email_monitor.get_stats()
    print(f"邮件统计:\n{stats}")

async def test_queue_manager():
    """测试队列管理器"""
    print("\n=== 测试 Queue Manager ===")
    
    # 添加测试任务
    print("添加测试任务...")
    for i in range(5):
        queue_manager.add_task({"task_id": i, "data": f"test_data_{i}"})
    
    print(f"当前队列大小: {queue_manager.get_queue_size()}")
    print(f"队列状态: {'处理中' if queue_manager.is_processing else '空闲'}")
    
    # 处理队列
    print("开始处理队列...")
    await queue_manager.process_queue()

async def test_alert_manager():
    """测试告警管理器"""
    print("\n=== 测试 Alert Manager ===")
    
    # 创建并发送不同级别的告警
    alerts = [
        Alert(title="测试信息", message="这是一条信息告警", level=AlertLevel.INFO),
        Alert(title="测试警告", message="这是一条警告告警", level=AlertLevel.WARNING),
        Alert(title="测试错误", message="这是一条错误告警", level=AlertLevel.ERROR),
        Alert(title="测试严重", message="这是一条严重告警", level=AlertLevel.CRITICAL)
    ]
    
    print("发送测试告警...")
    for alert in alerts:
        await alert_manager.send_alert(alert, [AlertChannel.EMAIL])
    
    # 获取告警统计
    stats = alert_manager.get_alert_stats()
    print(f"告警统计:\n{stats}")

def test_rule_engine():
    """测试规则引擎"""
    print("\n=== 测试 Rule Engine ===")
    
    # 创建测试规则
    test_rules = [
        Rule(
            name="CPU使用率告警",
            conditions=[
                Condition(field="cpu_usage", operator=Operator.GREATER_THAN, value=90)
            ],
            alert_level=AlertLevel.WARNING,
            alert_message="CPU使用率超过90%",
            channels=[AlertChannel.EMAIL],
            cooldown=timedelta(minutes=5)
        ),
        Rule(
            name="内存使用率告警",
            conditions=[
                Condition(field="memory_usage", operator=Operator.GREATER_THAN, value=85)
            ],
            alert_level=AlertLevel.ERROR,
            alert_message="内存使用率超过85%",
            channels=[AlertChannel.EMAIL],
            cooldown=timedelta(minutes=5)
        )
    ]
    
    # 添加规则
    print("添加测试规则...")
    for rule in test_rules:
        rule_engine.add_rule(rule)
    
    # 测试规则评估
    test_data = {
        "cpu_usage": 95,
        "memory_usage": 80
    }
    
    print(f"测试数据: {test_data}")
    matched_rules = rule_engine.evaluate(test_data)
    print(f"匹配规则数量: {len(matched_rules)}")
    for rule in matched_rules:
        print(f"- 匹配规则: {rule.name}")

async def run_all_tests():
    """运行所有测试"""
    print("开始组件功能测试...\n")
    
    # 运行所有测试
    await test_email_monitor()
    await test_queue_manager()
    await test_alert_manager()
    test_rule_engine()
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(run_all_tests()) 