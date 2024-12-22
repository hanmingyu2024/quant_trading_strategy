import requests

def test_api():
    """测试API是否正常工作"""
    print("\n=== 开始API测试 ===")
    
    # 1. 测试健康检查
    response = requests.get("http://localhost:8000/health")
    print(f"\n1. 健康检查: {response.json()}")
    
    # 2. 测试用户注册
    response = requests.post(
        "http://localhost:8000/api/v1/users/register",
        json={"username": "test", "password": "test123"}
    )
    print(f"\n2. 用户注册: {response.json()}")
    
    # 3. 测试用户登录
    response = requests.post(
        "http://localhost:8000/api/v1/users/login",
        json={"username": "test", "password": "test123"}
    )
    print(f"\n3. 用户登录: {response.json()}")

if __name__ == "__main__":
    test_api() 