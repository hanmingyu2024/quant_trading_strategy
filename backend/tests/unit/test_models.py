import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy import text
from backend.app.utils.database import engine, SessionLocal
from backend.app.models import User, Trade, Strategy, Account
from backend.app.models.trade import TradeType, TradeStatus
from backend.app.models.account import AccountType

def test_models():
    """测试数据库模型"""
    print("\n开始测试数据库模型...")
    
    try:
        db = SessionLocal()
        
        # 1. 检查表结构
        print("\n1. 检查数据库表")
        inspector = engine.inspect()
        tables = inspector.get_table_names()
        print(f"发现的表: {tables}")
        
        # 2. 测试创建用户
        print("\n2. 测试创建用户")
        test_user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="test_password_hash"
        )
        db.add(test_user)
        db.commit()
        print("✓ 用户创建成功")
        
        # 3. 测试创建账户
        print("\n3. 测试创建账户")
        test_account = Account(
            user_id=test_user.id,
            account_number="TEST001",
            broker="Test Broker",
            account_type=AccountType.DEMO
        )
        db.add(test_account)
        db.commit()
        print("✓ 账户创建成功")
        
        # 4. 测试创建策略
        print("\n4. 测试创建策略")
        test_strategy = Strategy(
            name="Test Strategy",
            description="Test strategy description",
            user_id=test_user.id,
            parameters={"param1": "value1"}
        )
        db.add(test_strategy)
        db.commit()
        print("✓ 策略创建成功")
        
        # 5. 测试创建交易
        print("\n5. 测试创建交易")
        test_trade = Trade(
            user_id=test_user.id,
            account_id=test_account.id,
            strategy_id=test_strategy.id,
            symbol="EURUSD",
            trade_type=TradeType.BUY,
            status=TradeStatus.PENDING,
            quantity=1.0,
            entry_price=1.2000
        )
        db.add(test_trade)
        db.commit()
        print("✓ 交易创建成功")
        
        # 6. 测试关系
        print("\n6. 测试模型关系")
        user = db.query(User).first()
        print(f"用户 {user.username} 的账户数量: {len(user.accounts)}")
        print(f"用户 {user.username} 的策略数量: {len(user.strategies)}")
        print(f"用户 {user.username} 的交易数量: {len(user.trades)}")
        
        print("\n✓ 所有测试完成!")
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        db.rollback()
        
    finally:
        # 清理测试数据
        db.query(Trade).delete()
        db.query(Strategy).delete()
        db.query(Account).delete()
        db.query(User).delete()
        db.commit()
        db.close()

if __name__ == "__main__":
    test_models() 