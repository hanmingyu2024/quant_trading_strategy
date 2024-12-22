from enum import Enum
from typing import List, Any
from datetime import timedelta
from dataclasses import dataclass
from backend.app.utils.alert_manager import AlertLevel, AlertChannel

class Operator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"

@dataclass
class Condition:
    field: str
    operator: Operator
    value: Any

    def evaluate(self, data: dict) -> bool:
        if self.field not in data:
            return False
            
        actual_value = data[self.field]
        
        if self.operator == Operator.EQUALS:
            return actual_value == self.value
        elif self.operator == Operator.NOT_EQUALS:
            return actual_value != self.value
        elif self.operator == Operator.GREATER_THAN:
            return actual_value > self.value
        elif self.operator == Operator.LESS_THAN:
            return actual_value < self.value
        elif self.operator == Operator.CONTAINS:
            return self.value in actual_value
        elif self.operator == Operator.NOT_CONTAINS:
            return self.value not in actual_value
        return False

@dataclass
class Rule:
    name: str
    conditions: List[Condition]
    alert_level: AlertLevel
    alert_message: str
    channels: List[AlertChannel]
    cooldown: timedelta

class RuleEngine:
    def __init__(self):
        self.rules: List[Rule] = []
        
    def add_rule(self, rule: Rule):
        """添加规则"""
        # 检查是否存在同名规则
        if any(r.name == rule.name for r in self.rules):
            raise ValueError(f"Rule with name '{rule.name}' already exists")
        self.rules.append(rule)
        
    def remove_rule(self, rule_name: str):
        """删除规则"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        
    def evaluate(self, data: dict) -> List[Rule]:
        """评估规则"""
        matched_rules = []
        for rule in self.rules:
            if all(condition.evaluate(data) for condition in rule.conditions):
                matched_rules.append(rule)
        return matched_rules

# 创建全局实例
rule_engine = RuleEngine() 