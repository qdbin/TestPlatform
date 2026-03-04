"""测试AI对话API"""
import requests
import json

# 测试AI服务
print("=== 测试AI服务 ===")
try:
    resp = requests.get("http://localhost:8001/health", timeout=5)
    print(f"AI服务状态: {resp.status_code}")
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"AI服务连接失败: {e}")

# 测试后端服务
print("\n=== 测试后端服务 ===")
try:
    resp = requests.get("http://localhost:8080/autotest/project/list", timeout=5)
    print(f"后端服务状态: {resp.status_code}")
    print(f"响应: {resp.text[:200]}")
except Exception as e:
    print(f"后端服务连接失败: {e}")

# 测试AI对话接口
print("\n=== 测试AI对话接口 ===")
try:
    # 先获取token
    login_data = {
        "username": "admin",
        "password": "123456"
    }
    login_resp = requests.post("http://localhost:8080/autotest/user/login", json=login_data, timeout=5)
    print(f"登录状态: {login_resp.status_code}")
    
    token = None
    if login_resp.status_code == 200:
        try:
            token = login_resp.json().get("token")
            print(f"Token: {token[:20]}..." if token and len(token) > 20 else f"Token: {token}")
        except:
            pass
    
    # 测试AI聊天接口（非流式）
    chat_data = {
        "projectId": "1",
        "userId": "1",
        "message": "你好，测试一下",
        "useRag": True
    }
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["token"] = token
    
    chat_resp = requests.post(
        "http://localhost:8080/autotest/ai/chat",
        json=chat_data,
        headers=headers,
        timeout=30
    )
    print(f"AI聊天状态: {chat_resp.status_code}")
    print(f"AI聊天响应: {chat_resp.text[:500]}")
    
except Exception as e:
    print(f"AI聊天测试失败: {e}")
