#!/bin/bash

# 设置错误时退出
set -e

echo "开始回滚..."

# 检查必要的环境变量
if [ -z "$DEPLOY_ENV" ]; then
    echo "错误: 未设置DEPLOY_ENV环境变量"
    exit 1
fi

# 检查回滚版本参数
if [ -z "$1" ]; then
    echo "错误: 请指定要回滚的版本(git commit hash)"
    exit 1
fi

ROLLBACK_VERSION=$1

# 根据环境选择配置文件
if [ "$DEPLOY_ENV" = "prod" ]; then
    COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"
elif [ "$DEPLOY_ENV" = "dev" ]; then
    COMPOSE_FILE="docker-compose.yml -f docker-compose.dev.yml"
else
    echo "错误: DEPLOY_ENV必须是 'prod' 或 'dev'"
    exit 1
fi

# 备份当前数据库
echo "备份当前数据库..."
python tools/scripts/db/backup.py

# 切换到指定版本
echo "切换到指定版本: $ROLLBACK_VERSION"
git checkout $ROLLBACK_VERSION

# 重新构建和启动容器
echo "重新构建和启动Docker容器..."
docker-compose -f $COMPOSE_FILE up -d --build

# 执行数据库迁移
echo "执行数据库迁移..."
python tools/scripts/db/migrate.py

echo "回滚完成!"
