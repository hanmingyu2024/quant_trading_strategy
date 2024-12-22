"""
主程序入口模块
"""
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import psutil
import platform
import time
from backend.app.utils.logger import setup_logger
from backend.app.utils.database import warm_up_pool, engine
from contextlib import asynccontextmanager
from backend.app.api.endpoints import health
from fastapi.routing import APIRoute
from starlette.routing import Mount  # 添加 Mount 导入
from fastapi.security import OAuth2PasswordBearer

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# 使用 Path 对象处理路径
project_root = Path(project_root)  # 转换为 Path 对象
log_dir = project_root / 'logs'    # 现在可以使用 / 运算符

# 或者使用 os.path.join
log_dir = os.path.join(project_root, 'logs')  # 这也是可行的

print(f"项目根目录: {project_root}")
print(f"日志目录: {log_dir}")

logger = setup_logger(__name__)

logger.info(f"应用启动，日志目录: {log_dir}")

# 导入其他模块
from backend.app.core.config import settings
from backend.app.middlewares.logging_middleware import LoggingMiddleware
from backend.app.middlewares.rate_limit_middleware import RateLimitMiddleware
from backend.app.middlewares.auth_middleware import AuthMiddleware
from backend.app.middlewares.exception_handler_middleware import ExceptionHandlerMiddleware
from backend.app.middlewares.security import SecurityMiddleware
from backend.app.api.v1 import auth, users, password_reset, admin
from backend.app.utils.database import engine, get_db

# 在应用启动时确保日志目录存在
log_dir = Path(__file__).parent.parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# 添加数据库连接统计函数
def get_connection_stats():
    """获取数据库连接统计信息"""
    try:
        return {
            "pool_size": engine.pool.size(),
            "active_connections": len(engine.pool._in_use),
            "total_connections": engine.pool.checkedin() + engine.pool.checkedout(),
            "connection_errors": 0,
            "last_connection_time": time.time(),
        }
    except Exception as e:
        logger.error(f"数据库连接错误: {e}")
        return {
            "pool_size": 0,
            "active_connections": 0,
            "total_connections": 0,
            "connection_errors": 1,
            "last_connection_time": 0,
        }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        logger.info("正在启动应用...")
        # 使用集合记录已注册的路由路径
        registered_paths = set()
        
        for route in app.routes:
            if isinstance(route, APIRoute):
                path = route.path
                methods = ','.join(sorted(route.methods))
                
                # 跳过不带 api/v1 前缀的健康检查和状态路由
                if path in ['/health', '/stats', '/test']:
                    continue
                    
                route_key = f"{path}:{methods}"
                if route_key not in registered_paths:
                    registered_paths.add(route_key)
                    logger.info(f"注册 API 路由: {path} [{route.methods}]")
            elif isinstance(route, Mount):
                logger.info(f"注册挂载路由: {route.path}")
            else:
                logger.info(f"注册其他路由: {route.path}")
        yield
    finally:
        logger.info("正在关闭应用...")

# 创建 FastAPI 应用
app = FastAPI(
    title="量化交易策略系统",
    description="API 文档",
    version="1.0.0",
    lifespan=lifespan
)

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# 添加中间件（按照处理顺序）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityMiddleware)  # 安全中间件
app.add_middleware(LoggingMiddleware)   # 日志中间件
app.add_middleware(RateLimitMiddleware, requests_limit=100, window_size=60)  # 速率限制
app.add_middleware(AuthMiddleware)      # 认证中间件
app.add_middleware(ExceptionHandlerMiddleware)  # 异常处理

# 配置静态文件
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

# 注册路由
app.include_router(
    auth.router,
    prefix=settings.API_V1_STR,
    tags=["认证"]
)
app.include_router(
    users.router,
    prefix=settings.API_V1_STR,
    tags=["用户"]
)
app.include_router(
    password_reset.router,
    prefix=settings.API_V1_STR,
    tags=["密码重置"]
)
app.include_router(
    admin.router,
    prefix=settings.API_V1_STR,
    tags=["管理"]
)
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"]
)

@app.get("/")
async def root(token: str = Depends(oauth2_scheme)):
    """根路由 - 可选认证"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "API 服务正常运行",
        "authenticated": token is not None
    }

@app.get("/health")
async def health_check():
    """健康检查 - 无需认证"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats")
async def get_stats():
    """系统状态 - 无需认证"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    path = request.url.path
    logger.info(f"收到请求: {request.method} {path}")
    
    try:
        response = await call_next(request)
        logger.info(f"请求完成: {request.method} {path} - {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"请求异常: {request.method} {path} - {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",  # 使用导入字符串
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
