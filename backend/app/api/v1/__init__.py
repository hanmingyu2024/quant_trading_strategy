import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from backend.app.api.v1.auth import router as auth_router

__all__ = ["auth_router"]
