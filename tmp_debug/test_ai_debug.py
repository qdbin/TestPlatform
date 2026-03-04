"""直接在运行的服务中添加调试"""
import requests
import json

AI_SERVICE_URL = "http://localhost:8001"

# 添加知识库文档测试
print("=== 测试1: 检查LLM服务配置 ===")
# 调用一个会触发异常的接口来获取调试信息
chat_data = {
    "project_id": "1",
    "message": "测试",
    "use_rag": False  # 关闭RAG
}

try:
    resp = requests.post(f"{AI_SERVICE_URL}/ai/chat", json=chat_data, timeout=30)
    print(f"响应: {resp.text[:500]}")
except Exception as e:
    print(f"错误: {e}")
