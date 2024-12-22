from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
import urllib.parse
import logging
import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = "hanmingyu@208521"
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{urllib.parse.quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
logger.info(f"Using database URL: {DATABASE_URL.replace(DB_PASSWORD, '****')}")

# 导入所有模型
try:
    from app.models.base import Base
    from app.models.user import User
    from app.models.trade import Trade
    
    # 设置 target_metadata
    target_metadata = Base.metadata
    logger.info("Successfully imported models and set metadata")
except Exception as e:
    logger.error(f"Error importing models: {str(e)}")
    raise

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    logger.info("Running migrations offline")
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    logger.info("Running migrations online")
    try:
        connectable = create_engine(DATABASE_URL)
        logger.info("Created database engine")

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )
            logger.info("Configured alembic context")

            with context.begin_transaction():
                context.run_migrations()
                logger.info("Completed migrations")

    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
