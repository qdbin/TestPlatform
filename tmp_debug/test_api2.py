"""测试AI对话API - 带登录"""
import requests
import json

BASE_URL = "http://localhost:8080"
AI_SERVICE_URL = "http://localhost:8001"

# 测试AI服务
print("=== 测试AI服务 ===")
try:
    resp = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
    print(f"AI服务状态: {resp.status_code}")
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"AI服务连接失败: {e}")

# 先获取token - 测试项目列表
print("\n=== 测试获取Token ===")
try:
    # 尝试直接获取项目列表
    resp = requests.get(f"{BASE_URL}/autotest/project/list", timeout=5)
    print(f"项目列表状态: {resp.status_code}")
    print(f"响应: {resp.text[:300]}")
except Exception as e:
    print(f"请求失败: {e}")

# 测试AI聊天接口
print("\n=== 测试AI聊天接口 ===")
try:
    # 先调用后端登录接口获取token
    login_data = {
        "username": "admin",
        "password": "123456"
    }
    login_resp = requests.post(f"{BASE_URL}/autotest/user/login", json=login_data, timeout=5)
    print(f"登录状态: {login_resp.status_code}")
    print(f"登录响应: {login_resp.text}")
    
    token = None
    if login_resp.status_code == 200:
        try:
            token = login_resp.json().get("token")
            print(f"Token: {token[:30]}..." if token and len(token) > 30 else f"Token: {token}")
        except:
            pass
    
    # 使用token调用AI聊天接口
    chat_data = {
        "projectId": "1",
        "userId": "1",
        "message": "你好",
        "useRag": True
    }
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["token"] = token
    
    chat_resp = requests.post(
        f"{BASE_URL}/autotest/ai/chat",
        json=chat_data,
        headers=headers,
        timeout=60
    )
    print(f"AI聊天状态: {chat_resp.status_code}")
    print(f"AI聊天响应: {chat_resp.text}")
    
except Exception as e:
    print(f"AI聊天测试失败: {e}")
    import traceback
    traceback.print_exc()
