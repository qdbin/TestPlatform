"""测试后端 + AI服务的完整流程"""
import requests
import json
import base64

BASE_URL = "http://localhost:8080"
AI_SERVICE_URL = "http://localhost:8001"

def main():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    print("=== 1. 登录获取token ===")
    login_data = {
        "account": "admin",
        "password": base64.b64encode("123456".encode()).decode()
    }
    login_resp = session.post(f"{BASE_URL}/autotest/user/login", json=login_data)
    print(f"登录状态: {login_resp.status_code}")
    print(f"响应: {login_resp.text[:200]}")
    
    token = login_resp.headers.get("token")
    if not token:
        print("未获取到token")
        return
    print(f"Token: {token[:30]}...")
    
    session.headers.update({"token": token})
    
    print("\n=== 2. 测试AI聊天接口 (非流式) ===")
    chat_data = {
        "projectId": "1",
        "userId": "1", 
        "message": "你好",
        "useRag": False
    }
    
    chat_resp = session.post(f"{BASE_URL}/autotest/ai/chat", json=chat_data)
    print(f"聊天状态: {chat_resp.status_code}")
    print(f"响应: {chat_resp.text[:500]}")
    
    print("\n=== 3. 测试AI聊天流式接口 ===")
    try:
        stream_resp = session.post(
            f"{BASE_URL}/autotest/ai/chat/stream", 
            json=chat_data,
            stream=True,
            timeout=30
        )
        print(f"流式状态: {stream_resp.status_code}")
        
        if stream_resp.status_code == 200:
            for line in stream_resp.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        print(f"收到: {line[:100]}")
        else:
            print(f"错误: {stream_resp.text[:200]}")
    except Exception as e:
        print(f"流式请求失败: {e}")

if __name__ == "__main__":
    main()
