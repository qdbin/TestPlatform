"""测试AI对话API - 修正API路径"""
import requests
import json

BASE_URL = "http://localhost:8080"
AI_SERVICE_URL = "http://localhost:8001"

def main():
    session = requests.Session()
    
    # 测试AI服务
    print("=== 测试AI服务 ===")
    try:
        resp = session.get(f"{AI_SERVICE_URL}/health", timeout=5)
        print(f"AI服务状态: {resp.status_code}")
        print(f"响应: {resp.text}")
    except Exception as e:
        print(f"AI服务连接失败: {e}")
        return
    
    # 1. 先调用正确的登录接口获取token
    print("\n=== 步骤1: 登录获取Token ===")
    import base64
    login_data = {
        "account": "admin",
        "password": base64.b64encode("123456".encode()).decode()
    }
    try:
        login_resp = session.post(f"{BASE_URL}/autotest/login", json=login_data, timeout=10)
        print(f"登录状态: {login_resp.status_code}")
        
        if login_resp.status_code != 200:
            print("登录失败，无法继续测试")
            return
            
        token = login_resp.headers.get("token")
        print(f"获取到的Token: {token[:50]}..." if token and len(token) > 50 else f"获取到的Token: {token}")
        
    except Exception as e:
        print(f"登录请求失败: {e}")
        return
    
    if not token:
        print("无法获取token，登录可能失败")
        return
    
    headers = {"token": token}
    
    # 2. 使用token调用项目列表 - 正确的路径
    print("\n=== 步骤2: 测试项目列表 ===")
    try:
        # POST方式，路径是 /autotest/project/list/{goPage}/{pageSize}
        project_resp = session.post(f"{BASE_URL}/autotest/project/list/1/10", headers=headers, timeout=10)
        print(f"项目列表状态: {project_resp.status_code}")
        print(f"响应: {project_resp.text[:500]}")
    except Exception as e:
        print(f"项目列表请求失败: {e}")
    
    # 3. 测试AI聊天接口（非流式）
    print("\n=== 步骤3: 测试AI对话 ===")
    chat_data = {
        "projectId": "1",
        "userId": "1", 
        "message": "你好",
        "useRag": True
    }
    
    try:
        chat_resp = session.post(
            f"{BASE_URL}/autotest/ai/chat",
            json=chat_data,
            headers=headers,
            timeout=60
        )
        print(f"AI聊天状态: {chat_resp.status_code}")
        print(f"AI聊天响应: {chat_resp.text[:1000]}")
    except Exception as e:
        print(f"AI聊天测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
