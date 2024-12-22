import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.app.utils.database import SessionLocal
from backend.app.models import User, Account, Strategy, Trade
from backend.app.models.trade import TradeType, TradeStatus
from backend.app.models.account import AccountType

def verify_database():
    """验证数据库数据"""
    print("\n开始验证数据库数据...")
    db = SessionLocal()
    
    try:
        # 1. 验证用户数据
        print("\n1. 验证用户数据")
        users = db.query(User).all()
        print(f"发现 {len(users)} 个用户")
        for user in users:
            print(f"  用户: {user.username}")
            print(f"    • 邮箱: {user.email}")
            print(f"    • 账户数: {len(user.accounts)}")
            print(f"    • 策略数: {len(user.strategies)}")
            print(f"    • 交易数: {len(user.trades)}")
        
        # 2. 验证账户数据
        print("\n2. 验证账户数据")
        accounts = db.query(Account).all()
        print(f"发现 {len(accounts)} 个账户")
        for account in accounts:
            print(f"  账户: {account.account_number}")
            print(f"    • 类型: {account.account_type.value}")
            print(f"    • 余额: {account.balance}")
            print(f"    • 杠杆: {account.leverage}")
        
        # 3. 验证策略数据
        print("\n3. 验证策略数据")
        strategies = db.query(Strategy).all()
        print(f"发现 {len(strategies)} 个策略")
        for strategy in strategies:
            print(f"  策略: {strategy.name}")
            print(f"    • 描述: {strategy.description}")
            print(f"    • 参数: {strategy.parameters}")
            print(f"    • 交易数: {len(strategy.trades)}")
        
        # 4. 验证交易数据
        print("\n4. 验证交易数据")
        trades = db.query(Trade).all()
        print(f"发现 {len(trades)} 笔交易")
        
        # 按状态统计交易
        status_counts = {}
        type_counts = {}
        for trade in trades:
            status_counts[trade.status.value] = status_counts.get(trade.status.value, 0) + 1
            type_counts[trade.trade_type.value] = type_counts.get(trade.trade_type.value, 0) + 1
        
        print("\n  交易状态统计:")
        for status, count in status_counts.items():
            print(f"    • {status}: {count}")
            
        print("\n  交易类型统计:")
        for type_, count in type_counts.items():
            print(f"    • {type_}: {count}")
        
        # 5. 验证关系完整性
        print("\n5. 验证关系完整性")
        for user in users:
            print(f"\n  用户 {user.username} 的关系:")
            for account in user.accounts:
                print(f"    • 账户 {account.account_number}:")
                print(f"      - 交易数: {len(account.trades)}")
            for strategy in user.strategies:
                print(f"    • 策略 {strategy.name}:")
                print(f"      - 交易数: {len(strategy.trades)}")
        
        print("\n✓ 数据验证完成!")
        return True
        
    except Exception as e:
        print(f"\n数据验证失败: {str(e)}")
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_database() 