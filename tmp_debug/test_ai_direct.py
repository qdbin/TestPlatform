"""直接测试AI服务"""
import requests
import json

AI_SERVICE_URL = "http://localhost:8001"

def main():
    # 1. 测试AI服务健康状态
    print("=== 测试AI服务健康检查 ===")
    try:
        resp = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        print(f"状态: {resp.status_code}, 响应: {resp.text}")
    except Exception as e:
        print(f"失败: {e}")
        return
    
    # 2. 直接测试AI聊天接口
    print("\n=== 直接测试AI聊天接口 ===")
    chat_data = {
        "project_id": "1",
        "message": "你好",
        "use_rag": True
    }
    
    try:
        chat_resp = requests.post(
            f"{AI_SERVICE_URL}/ai/chat",
            json=chat_data,
            timeout=60
        )
        print(f"状态: {chat_resp.status_code}")
        print(f"响应: {chat_resp.text[:1000]}")
    except Exception as e:
        print(f"失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
