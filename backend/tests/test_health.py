import requests
import json

def test_health():
    """测试健康检查接口"""
    try:
        # 发送请求
        response = requests.get("http://localhost:8000/health")
        
        # 打印详细信息
        print("\n=== 健康检查测试 ===")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        # 尝试解析 JSON
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON 数据: {data}")
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {str(e)}")
        else:
            print(f"请求失败: HTTP {response.status_code}")
            
    except requests.RequestException as e:
        print(f"请求异常: {str(e)}")

if __name__ == "__main__":
    test_health() 