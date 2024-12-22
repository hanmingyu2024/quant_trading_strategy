from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
def health_check():
    """健康检查端点 - 使用同步函数而不是异步"""
    try:
        logger.info("执行健康检查...")
        return {
            "status": "ok",
            "timestamp": str(datetime.now()),
            "message": "服务正常运行"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"健康检查失败: {str(e)}"
        )

@router.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    stats = get_connection_stats()
    return {
        "database": {
            "connections": stats,
            "performance": {
                "error_rate": f"{(stats['connection_errors'] / max(1, stats['total_connections'])) * 100:.2f}%",
                "active_rate": f"{(stats['active_connections'] / max(1, stats['pool_size'])) * 100:.2f}%"
            }
        },
        "timestamp": datetime.now().isoformat()
    } 