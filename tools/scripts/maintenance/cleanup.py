import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def cleanup():
    """清理临时文件和旧的备份"""
    try:
        # 获取项目根目录
        root_dir = Path(__file__).parent.parent.parent.parent
        
        # 清理备份目录中超过30天的备份文件
        backup_dir = root_dir / 'backups'
        if backup_dir.exists():
            print("清理旧的数据库备份...")
            threshold = datetime.now() - timedelta(days=30)
            
            for backup_file in backup_dir.glob('db_backup_*.sql'):
                # 从文件名中提取时间戳
                try:
                    timestamp_str = backup_file.stem.split('_')[2:4]
                    file_date = datetime.strptime('_'.join(timestamp_str), '%Y%m%d_%H%M%S')
                    
                    if file_date < threshold:
                        backup_file.unlink()
                        print(f"已删除旧备份: {backup_file.name}")
                except (IndexError, ValueError):
                    continue
        
        # 清理日志目录中的旧日志文件
        logs_dir = root_dir / 'logs'
        if logs_dir.exists():
            print("清理旧的日志文件...")
            threshold = datetime.now() - timedelta(days=7)
            
            for log_file in logs_dir.glob('*.log'):
                if log_file.stat().st_mtime < threshold.timestamp():
                    log_file.unlink()
                    print(f"已删除旧日志: {log_file.name}")
        
        # 清理临时文件
        print("清理临时文件...")
        patterns = ['**/*.pyc', '**/__pycache__', '**/.pytest_cache']
        for pattern in patterns:
            for path in root_dir.glob(pattern):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
                print(f"已删除: {path}")
                
        print("清理完成!")
        
    except Exception as e:
        print(f"清理过程中出错: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    cleanup()
