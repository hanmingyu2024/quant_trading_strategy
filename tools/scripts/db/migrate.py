import os
import sys
import subprocess
from pathlib import Path

def migrate_database():
    """执行数据库迁移"""
    try:
        # 获取项目根目录
        root_dir = Path(__file__).parent.parent.parent.parent
        migrations_dir = root_dir / 'backend' / 'migrations'
        
        # 检查migrations目录是否存在
        if not migrations_dir.exists():
            print("未找到migrations目录,请先初始化alembic")
            sys.exit(1)
            
        # 从环境变量获取数据库配置
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        if not all([db_name, db_user, db_password]):
            raise ValueError("数据库配置不完整,请检查环境变量")
            
        # 设置数据库URL环境变量
        os.environ['DATABASE_URL'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # 执行数据库迁移
        alembic_path = root_dir / 'backend' / 'alembic.ini'
        cmd = ['alembic', '-c', str(alembic_path), 'upgrade', 'head']
        
        subprocess.run(cmd, check=True)
        print("数据库迁移成功")
        
    except Exception as e:
        print(f"数据库迁移失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    migrate_database()
