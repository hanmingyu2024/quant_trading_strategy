"""
测试管理接口
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 先登录获取token
def get_auth_token():
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/users/login", json=login_data)
    return response.json().get("access_token")

def test_admin_endpoints():
    # 获取认证token
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试各个端点
    endpoints = [
        "/admin/email/stats",
        "/admin/email/queue",
        "/admin/alerts/stats",
        "/admin/alerts/rules"
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"\n测试 {endpoint}:")
        print(response.json())

if __name__ == "__main__":
    test_admin_endpoints() 