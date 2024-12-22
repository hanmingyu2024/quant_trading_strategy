"""
这是一个数据库备份脚本文件。
主要功能包括:
1. 自动备份数据库 - 使用mysqldump创建数据库备份
2. 备份文件管理 - 管理和维护备份文件
3. 日志记录 - 记录备份过程和结果

使用场景:
- 定期数据库备份
- 重要更新前的备份
- 数据恢复需要时的备份
"""

from aliyunsdkcore.client import AcsClient
from aliyunsdkrds.request.v20140815 import CreateBackupRequest
from aliyunsdkrds.request.v20140815.DescribeBackupsRequest import DescribeBackupsRequest
import time
import json
from datetime import datetime
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv(Path(__file__).parent.parent / '.env')

# 从.env文件获取配置
ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
REGION_ID = "cn-hangzhou"  # 阿里云华东1（杭州）
DB_INSTANCE_ID = "rm-bp1on391pisu4c2ms"  # 从数据库连接字符串提取的实例ID

# 配置日志
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"backup_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

def create_backup():
    try:
        # 增加超时时间设置
        client = AcsClient(
            ACCESS_KEY_ID, 
            ACCESS_KEY_SECRET, 
            REGION_ID,
            timeout=300  # 设置5分钟超时
        )
        
        request = CreateBackupRequest.CreateBackupRequest()
        request.set_protocol_type("HTTPS")  # 使用HTTPS
        request.set_DBInstanceId(DB_INSTANCE_ID)
        
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.do_action_with_exception(request)
                return response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(5)  # 等待5秒后重试
                
    except Exception as e:
        logging.error(f"创建备份时出错: {str(e)}")
        raise

def wait_for_backup_complete(client, backup_id, timeout=3600):
    """等待备份完成"""
    start_time = time.time()
    while True:
        try:
            # 查询备份状态
            request = DescribeBackupsRequest()
            request.set_DBInstanceId(DB_INSTANCE_ID)
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            
            # 检查备份状态
            backups = response_json.get('Items', {}).get('Backup', [])
            for backup in backups:
                if backup.get('BackupId') == backup_id:
                    status = backup.get('BackupStatus')
                    if status == 'Success':
                        logging.info("备份完成！")
                        return True
                    elif status == 'Failed':
                        logging.error("备份失败！")
                        return False
            
            # 检查超时
            if time.time() - start_time > timeout:
                logging.error("备份超时！")
                return False
                
            # 等待10秒后再次检查
            time.sleep(10)
            
        except Exception as e:
            logging.error(f"检查备份状态时出错: {str(e)}")
            return False

def main():
    try:
        backup_id = create_backup()
        if backup_id:
            logging.info(f"成功创建备份，备份ID: {backup_id}")
    except Exception as e:
        logging.error(f"备份过程失败: {str(e)}")

if __name__ == "__main__":
    main() 