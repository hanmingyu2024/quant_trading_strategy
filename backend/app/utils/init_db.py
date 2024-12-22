from backend.app.models import Base
from backend.app.utils.database import engine
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User
from sqlalchemy.orm import Session

def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建测试管理员用户
    from backend.app.utils.database import SessionLocal
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员用户
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=AuthService.get_password_hash("admin123"),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("管理员用户创建成功！")
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成！") 