"""
数据库工具模块
提供数据库连接和会话管理
"""
from typing import Generator, Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
import logging
from contextlib import contextmanager
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import random

from backend.app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionStats:
    """连接统计管理类"""
    def __init__(self):
        self._stats = {
            "total_connections": 0,
            "active_connections": 0,
            "connection_errors": 0,
            "last_error": None,
            "last_connection_time": None
        }
        self._lock = threading.Lock()
    
    def update(self, **kwargs):
        with self._lock:
            self._stats.update(kwargs)
    
    def get_stats(self):
        with self._lock:
            return self._stats.copy()

# 创建全局统计实例
connection_stats = ConnectionStats()

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=int(settings.DB_POOL_SIZE),
    max_overflow=int(settings.DB_MAX_OVERFLOW),
    pool_timeout=int(settings.DB_POOL_TIMEOUT),
    pool_recycle=int(settings.DB_POOL_RECYCLE),
    pool_pre_ping=True,
    echo=False,
    pool_use_lifo=True,
    connect_args={
        'connect_timeout': 5,
        'read_timeout': 10,
        'charset': 'utf8mb4'
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def create_connection_with_retry(max_retries: int = 3, retry_delay: float = 1) -> Optional[object]:
    """创建带重试机制的数据库连接"""
    last_error = None
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            conn = engine.connect()
            connection_time = time.time() - start_time
            
            connection_stats.update(
                total_connections=connection_stats.get_stats()["total_connections"] + 1,
                active_connections=connection_stats.get_stats()["active_connections"] + 1,
                last_connection_time=connection_time
            )
            
            logger.info(f"数据库连接成功 (尝试 {attempt + 1}/{max_retries})，耗时: {connection_time:.2f}秒")
            return conn
        except Exception as e:
            last_error = str(e)
            connection_stats.update(
                connection_errors=connection_stats.get_stats()["connection_errors"] + 1,
                last_error=last_error
            )
            
            if attempt == max_retries - 1:
                logger.error(f"数据库连接失败，已达到最大重试次数: {last_error}")
                raise
            
            logger.warning(f"连接失败，将在 {retry_delay} 秒后重试 ({attempt + 1}/{max_retries}): {last_error}")
            time.sleep(retry_delay)

async def create_async_connection():
    """异步创建数据库连接"""
    try:
        conn = await engine.connect()
        connection_time = time.time() - conn.info['connect_start']
        
        connection_stats.update(
            total_connections=connection_stats.get_stats()["total_connections"] + 1,
            active_connections=connection_stats.get_stats()["active_connections"] + 1,
            last_connection_time=connection_time
        )
        
        logger.info(f"数据库连接成功，耗时: {connection_time:.2f}秒")
        return conn
    except Exception as e:
        logger.error(f"连接创建失败: {str(e)}")
        return None

async def warm_up_pool():
    """优化的连接池预热"""
    try:
        logger.info("开始预热数据库连接池...")
        start_time = time.time()
        connections = []
        
        # 修改批次大小和重试策略
        batch_size = 3  # 增加批次大小
        retry_delay = 0.3  # 减少重试延迟
        
        async def create_single_connection():
            for attempt in range(3):
                try:
                    conn = await asyncio.to_thread(create_connection_with_retry)
                    if conn:
                        connections.append(conn)
                        logger.info(f"成功创建连接 {len(connections)}/{engine.pool.size()}")
                        return conn
                except Exception as e:
                    if attempt < 2:  # 最后一次尝试不等待
                        await asyncio.sleep(retry_delay)
                    continue
            return None
        
        # 分批处理
        total_connections = engine.pool.size()
        for i in range(0, total_connections, batch_size):
            batch_start = time.time()
            tasks = [create_single_connection() 
                    for _ in range(min(batch_size, total_connections - i))]
            await asyncio.gather(*tasks)
            logger.info(f"批次完成，耗时: {time.time() - batch_start:.2f}秒")
            
        # 检查是否需要补充连接
        missing = engine.pool.size() - len(connections)
        if missing > 0:
            logger.warning(f"需要补充 {missing} 个连接")
            tasks = [create_single_connection() for _ in range(missing)]
            await asyncio.gather(*tasks)
            
        return True
    finally:
        for conn in connections:
            conn.close()

@event.listens_for(engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """查询执行前的监听器"""
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(engine, 'after_cursor_execute')
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """查询执行后的监听器"""
    total_time = time.time() - conn.info['query_start_time'].pop()
    if total_time > settings.DB_SLOW_QUERY_THRESHOLD:
        logger.warning(f"慢查询警告: {total_time:.2f}秒\nSQL: {statement}")

@contextmanager
def get_db_context():
    """获取数据库会话的上下文管理器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（生成器）"""
    with get_db_context() as db:
        yield db

def init_db() -> None:
    """初始化数据库，创建所有表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

def check_db_connection() -> bool:
    """检查数据库连接是否正常"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return False

def get_connection_stats():
    """获取连接统计信息"""
    stats = connection_stats.get_stats()
    return {
        **stats,
        "pool_size": engine.pool.size(),
        "overflow": engine.pool.overflow()
    }

async def check_db_health() -> bool:
    """检查数据库健康状态"""
    try:
        # 使用 asyncio.to_thread 执行同步数据库操作
        def _check():
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
                
        return await asyncio.to_thread(_check)
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        return False

# 应用启动时预热连接池
if __name__ != "__main__":
    pass

# 导出所需的组件
__all__ = [
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    'init_db',
    'check_db_connection',
    'get_connection_stats'
]
