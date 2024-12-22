"""
这是一个数据库维护脚本文件。
主要功能包括:
1. 表统计信息分析 - 定期分析表的统计信息以优化查询性能
2. 索引使用情况检查 - 监控索引的使用情况
3. 数据库维护任务 - 执行定期维护任务如优化表、检查完整性等
"""

from sqlalchemy import create_engine, text
import urllib.parse
from datetime import datetime
import time
import logging
from pathlib import Path

# 配置日志
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"db_maintenance_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 在文件开头添加配置
SLOW_QUERY_THRESHOLD = 1.0  # 秒
TABLE_SIZE_ALERT = 1000  # MB

def analyze_tables(conn):
    """分析表统计信息"""
    logging.info("开始分析表统计信息...")
    try:
        tables = ['users', 'trades']
        for table in tables:
            conn.execute(text(f"ANALYZE TABLE {table}"))
            logging.info(f"完成分析表: {table}")
    except Exception as e:
        logging.error(f"分析表时出错: {str(e)}")

def check_index_usage(conn):
    """检查索引使用情况"""
    logging.info("检查索引使用情况...")
    try:
        result = conn.execute(text("""
            SELECT 
                table_name, 
                index_name,
                stat_value as usage_count
            FROM performance_schema.table_statistics
            WHERE table_schema = :db_name
        """), {"db_name": DB_NAME}).fetchall()
        
        for row in result:
            logging.info(f"表 {row.table_name} 的索引 {row.index_name} 使用次数: {row.usage_count}")
    except Exception as e:
        logging.error(f"检查索引使用情况时出错: {str(e)}")

def check_table_sizes(conn):
    """检查表大小和记录数"""
    logging.info("检查表大小和记录数...")
    try:
        tables = ['users', 'trades']
        for table in tables:
            result = conn.execute(text(f"SHOW TABLE STATUS LIKE '{table}'")).fetchone()
            size_mb = (result.Data_length + result.Index_length) / (1024 * 1024)
            logging.info(f"表 {table}:")
            logging.info(f"- 记录数: {result.Rows}")
            logging.info(f"- 总大小: {size_mb:.2f} MB")
            
            if size_mb > TABLE_SIZE_ALERT:
                logging.warning(f"警告: 表 {table} 大小超过 {TABLE_SIZE_ALERT}MB")
    except Exception as e:
        logging.error(f"检查表大小时出错: {str(e)}")

def check_slow_queries(conn):
    """检查慢查询"""
    logging.info("检查慢查询记录...")
    try:
        result = conn.execute(text("""
            SELECT start_time, query_time, sql_text
            FROM mysql.slow_log
            WHERE start_time > DATE_SUB(NOW(), INTERVAL 1 DAY)
            AND query_time > :threshold
            ORDER BY query_time DESC
            LIMIT 5
        """), {"threshold": SLOW_QUERY_THRESHOLD}).fetchall()
        
        for row in result:
            logging.warning(f"发现慢查询:")
            logging.warning(f"- 执行时间: {row.query_time}")
            logging.warning(f"- SQL: {row.sql_text}")
    except Exception as e:
        logging.error(f"检查慢查询时出错: {str(e)}")

def optimize_if_needed(conn):
    """根据需要优化表"""
    logging.info("检查是否需要优化...")
    try:
        tables = ['users', 'trades']
        for table in tables:
            result = conn.execute(text(f"SHOW TABLE STATUS LIKE '{table}'")).fetchone()
            if result.Data_free > 0:
                logging.info(f"优化表 {table}...")
                conn.execute(text(f"OPTIMIZE TABLE {table}"))
                logging.info(f"表 {table} 优化完成")
    except Exception as e:
        logging.error(f"优化表时出错: {str(e)}")

def generate_maintenance_report():
    """生成维护报告"""
    report_path = log_dir / f"maintenance_report_{datetime.now().strftime('%Y%m%d')}.txt"
    logging.info(f"生成维护报告: {report_path}")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"数据库维护报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n")
        
        # 添加日志内容
        with open(log_dir / f"db_maintenance_{datetime.now().strftime('%Y%m%d')}.log", 'r') as log_file:
            f.write(log_file.read())

def main():
    logging.info("开始数据库维护...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        analyze_tables(conn)
        check_index_usage(conn)
        check_table_sizes(conn)
        check_slow_queries(conn)
        optimize_if_needed(conn)
    
    generate_maintenance_report()
    logging.info("数据库维护完成!")

if __name__ == "__main__":
    main() 