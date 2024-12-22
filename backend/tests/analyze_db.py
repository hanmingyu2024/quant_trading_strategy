import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy import text, inspect
from backend.app.utils.database import engine, SessionLocal
from backend.app.models import User, Trade, Strategy, Account

def analyze_database():
    """详细分析数据库结构"""
    print("\n开始数据库分析...")
    
    try:
        inspector = inspect(engine)
        
        # 1. 分析表结构
        print("\n1. 数据库表结构分析")
        tables = inspector.get_table_names()
        
        for table in tables:
            print(f"\n表名: {table}")
            
            # 获取列信息
            columns = inspector.get_columns(table)
            print("  列信息:")
            for col in columns:
                nullable = "可空" if col['nullable'] else "非空"
                print(f"    • {col['name']}: {col['type']} ({nullable})")
            
            # 获取索引信息
            indexes = inspector.get_indexes(table)
            if indexes:
                print("  索引:")
                for idx in indexes:
                    unique = "唯一" if idx['unique'] else "非唯一"
                    print(f"    • {idx['name']}: {unique} - 列: {idx['column_names']}")
            
            # 获取外键信息
            foreign_keys = inspector.get_foreign_keys(table)
            if foreign_keys:
                print("  外键:")
                for fk in foreign_keys:
                    print(f"    • {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # 2. 测试数据库连接
        print("\n2. 数据库连接测试")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar()
            print(f"  数据库版本: {version}")
        
        # 3. 分析表关系
        print("\n3. 模型关系分析")
        print("  User 模型关系:")
        print(f"    • User -> Account: 一对多")
        print(f"    • User -> Strategy: 一对多")
        print(f"    • User -> Trade: 一对多")
        
        print("\n  Account 模型关系:")
        print(f"    • Account -> User: 多对一")
        print(f"    • Account -> Trade: 一对多")
        
        print("\n  Strategy 模型关系:")
        print(f"    • Strategy -> User: 多对一")
        print(f"    • Strategy -> Trade: 一对多")
        
        # 4. 检查约束
        print("\n4. 数据库约束检查")
        with SessionLocal() as session:
            for table in tables:
                constraints = inspector.get_unique_constraints(table)
                if constraints:
                    print(f"\n  {table} 表的唯一约束:")
                    for constraint in constraints:
                        print(f"    • {constraint['name']}: {constraint['column_names']}")
        
        print("\n✓ 数据库分析完成!")
        
    except Exception as e:
        print(f"\n分析过程出错: {str(e)}")

if __name__ == "__main__":
    analyze_database() 