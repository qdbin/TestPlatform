"""
冒烟测试 - 使用requests进行接口自动化测试

测试范围：
    - 健康检查接口
    - RAG知识库接口
    - Agent用例生成接口
    - 流式对话接口

使用方法：
    conda activate aitest
    cd ai-service
    python -m pytest tests/integration/test_smoke_requests.py -v
    
    # 或作为脚本直接运行
    python tests/integration/test_smoke_requests.py
"""

import json
import sys
import time
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# API基础配置
BASE_URL = "http://localhost:8001"
TEST_PROJECT_ID = "smoke-test-project"
TEST_TOKEN = "smoke-test-token"


class TestHealthCheck:
    """健康检查测试"""
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "status" in data
        print(f"✅ 根路径测试通过: {data.get('message', data.get('status'))}")
    
    def test_health_endpoint(self):
        """测试健康检查接口"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy"
            print(f"✅ 健康检查通过: {data}")
        except requests.exceptions.ConnectionError:
            pytest.skip("AI服务未启动")


class TestRAGEndpoints:
    """RAG接口测试"""
    
    def test_add_document(self):
        """测试添加文档"""
        url = f"{BASE_URL}/ai/rag/add"
        payload = {
            "project_id": TEST_PROJECT_ID,
            "user_id": "smoke-user",
            "doc_id": "smoke-doc-001",
            "doc_type": "manual",
            "doc_name": "冒烟测试文档",
            "content": "这是一个用于冒烟测试的文档内容",
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            assert response.status_code in [200, 201]
            data = response.json()
            assert data.get("status") == "success"
            print(f"✅ 添加文档测试通过")
        except requests.exceptions.ConnectionError:
            pytest.skip("AI服务未启动")
    
    def test_search_documents(self):
        """测试文档搜索"""
        url = f"{BASE_URL}/ai/rag/query"
        payload = {
            "project_id": TEST_PROJECT_ID,
            "user_id": "smoke-user",
            "question": "测试",
            "top_k": 3,
            "messages": []
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            print(f"✅ 文档搜索测试通过，返回{len(data.get('data', []))}条结果")
        except requests.exceptions.ConnectionError:
            pytest.skip("AI服务未启动")
    
    def test_list_documents(self):
        """测试文档统计"""
        url = f"{BASE_URL}/ai/rag/stats/{TEST_PROJECT_ID}"
        
        try:
            response = requests.get(url, timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "success"
            print(f"✅ 文档列表测试通过")
        except requests.exceptions.ConnectionError:
            pytest.skip("AI服务未启动")


class TestAgentEndpoints:
    """Agent接口测试"""
    
    def test_generate_case(self):
        """测试用例生成"""
        url = f"{BASE_URL}/ai/agent/generate-case"
        payload = {
            "project_id": TEST_PROJECT_ID,
            "user_requirement": "设计一个用户登录测试用例",
            "selected_apis": [],
            "messages": []
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            print(f"✅ 用例生成测试通过，状态: {data.get('status')}")
        except requests.exceptions.ConnectionError:
            pytest.skip("AI服务未启动")
    
class TestChatEndpoints:
    """对话接口测试"""
    
    def test_chat_stream(self):
        """测试流式对话"""
        url = f"{BASE_URL}/ai/chat/stream"
        payload = {
            "project_id": TEST_PROJECT_ID,
            "message": "你好",
            "use_rag": False,
            "stream": True
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                stream=True,
                timeout=60,
                headers={"token": TEST_TOKEN}
            )
            assert response.status_code == 200
            
            assert response.headers.get("content-type", "").startswith("text/event-stream")
            chunks = []
            for line in response.iter_lines():
                if line:
                    chunks.append(line.decode('utf-8'))
                    if len(chunks) >= 3:
                        break
            
            assert len(chunks) > 0, "流式响应为空"
            print(f"✅ 流式对话测试通过，收到{len(chunks)}个数据块")
        except requests.exceptions.ConnectionError:
            pytest.skip("AI服务未启动")


def run_smoke_tests():
    """运行所有冒烟测试"""
    import pytest
    
    print("\n" + "=" * 60)
    print("AI服务冒烟测试")
    print("=" * 60)
    print(f"测试地址: {BASE_URL}")
    print("=" * 60 + "\n")
    
    # 检查服务是否可连接
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ AI服务已启动 (状态码: {response.status_code})\n")
    except requests.exceptions.ConnectionError:
        print(f"❌ AI服务未启动，请确保服务运行在 {BASE_URL}")
        print("   启动命令: python -m app.main")
        return False
    
    # 运行pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    return exit_code == 0


if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
