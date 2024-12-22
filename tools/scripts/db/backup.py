import os
import sys
import datetime
import subprocess
from pathlib import Path

def backup_database():
    """备份数据库"""
    try:
        # 获取当前时间作为备份文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(__file__).parent.parent.parent.parent / 'backups'
        
        # 创建备份目录
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True)
            
        # 备份文件路径
        backup_file = backup_dir / f'db_backup_{timestamp}.sql'
        
        # 从环境变量获取数据库配置
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        if not all([db_name, db_user, db_password]):
            raise ValueError("数据库配置不完整,请检查环境变量")
            
        # 执行mysqldump命令
        cmd = [
            'mysqldump',
            f'--host={db_host}',
            f'--port={db_port}',
            f'--user={db_user}',
            f'--password={db_password}',
            db_name,
            f'--result-file={backup_file}'
        ]
        
        subprocess.run(cmd, check=True)
        print(f"数据库备份成功: {backup_file}")
        
    except Exception as e:
        print(f"数据库备份失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    backup_database()
