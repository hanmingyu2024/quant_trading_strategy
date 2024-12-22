# 创建一个测试文件来验证导入
try:
    from backend.app.config import settings
    from backend.app.models.user import User
    from backend.app.schemas.user import UserCreate
    from backend.app.utils.database import get_db
    from backend.app.utils.security import create_access_token
    
    print("所有模块导入成功！")
except Exception as e:
    print(f"导入错误: {str(e)}") 