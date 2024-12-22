"""
这是一个重置 Alembic 迁移工具的脚本文件。
主要功能包括:
1. 删除数据库中的 alembic_version 表
2. 清理 versions 目录下的迁移文件
3. 重置 Alembic 迁移状态

使用场景:
- 需要重新开始数据库迁移时
- 迁移历史出现问题需要重置时
- 开发环境重新初始化数据库时
"""

from sqlalchemy import create_engine, text
import urllib.parse
import os
import shutil

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("开始重置 Alembic...")

# 1. 删除数据库中的 alembic_version 表
print("正在检查数据库...")
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        print("成功删除 alembic_version 表（如果存在）")
except Exception as e:
    print(f"删除表时出错：{str(e)}")

# 2. 删除 versions 目录中的所有文件
versions_dir = os.path.join('alembic', 'versions')
if os.path.exists(versions_dir):
    print("正在清理 versions 目录...")
    for file in os.listdir(versions_dir):
        if file.endswith('.py'):
            os.remove(os.path.join(versions_dir, file))
    print("已清理 versions 目录")

print("重置完成！现在可以重新运行 alembic revision --autogenerate -m 'Initial migration'") 