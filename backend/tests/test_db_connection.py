import logging
from sqlalchemy import create_engine, text
import urllib.parse

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_USER = "hanmingyushanbaoyue"
DB_PASSWORD = urllib.parse.quote_plus("hanmingyu@208521")  # URL编码密码
DB_HOST = "rm-bp1on391pisu4c2msuo.mysql.rds.aliyuncs.com"
DB_PORT = "3306"
DB_NAME = "reinforcementlearningbot"

def test_connection():
    """测试数据库连接"""
    try:
        # 构建数据库URL
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        print("\n=== 数据库连接测试 ===")
        print(f"主机: {DB_HOST}")
        print(f"端口: {DB_PORT}")
        print(f"数据库: {DB_NAME}")
        print(f"用户: {DB_USER}")
        
        # 创建引擎并测试连接
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("\n✅ 数据库连接成功!")
            print(f"测试查询结果: {result.fetchone()}")
            
    except Exception as e:
        print(f"\n❌ 数据库连接失败!")
        print(f"错误信息: {str(e)}")
        print("\n可能的原因:")
        print("1. 数据库凭据错误")
        print("2. 数据库未启动")
        print("3. 网络连接问题")
        print("4. 防火墙设置")

if __name__ == "__main__":
    test_connection() 