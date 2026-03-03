"""测试AI对话API - 调试Token传递"""
import requests
import json

BASE_URL = "http://localhost:8080"

def main():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    # 1. 登录获取token
    print("=== 步骤1: 登录 ===")
    import base64
    login_data = {
        "account": "admin",
        "password": base64.b64encode("123456".encode()).decode()
    }
    
    login_resp = session.post(f"{BASE_URL}/autotest/login", json=login_data)
    print(f"登录状态: {login_resp.status_code}")
    
    # 打印所有响应头
    print(f"响应头: {dict(login_resp.headers)}")
    
    token = login_resp.headers.get("token")
    print(f"Token: {token[:30]}..." if token else "No token")
    
    if not token:
        print("登录失败!")
        return
    
    # 设置token到session headers - 确保每次请求都带token
    session.headers.update({"token": token})
    print(f"当前session headers: {dict(session.headers)}")
    
    # 2. 测试AI接口
    print("\n=== 步骤2: 测试AI接口 ===")
    chat_data = {
        "projectId": "1",
        "userId": "1", 
        "message": "你好",
        "useRag": True
    }
    
    # 直接用session发送
    chat_resp = session.post(f"{BASE_URL}/autotest/ai/chat", json=chat_data)
    print(f"AI聊天状态: {chat_resp.status_code}")
    print(f"AI聊天响应: {chat_resp.text[:1000]}")

if __name__ == "__main__":
    main()
