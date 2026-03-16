"""
AI 服务冒烟测试脚本

功能：
    1. 测试后端健康检查
    2. 测试 AI 服务健康检查
    3. 测试 RAG 知识库功能
    4. 测试用例生成功能
    5. 测试流式对话功能

使用：
    python tests/smoke_test.py
"""

import json
import sys
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8080"
AI_BASE_URL = "http://localhost:8001"

PROJECT_ID = "test-project-001"
TEST_TOKEN = ""


class SmokeTest:
    """冒烟测试类"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        prefix = {
            "INFO": "[INFO]",
            "PASS": "[PASS]",
            "FAIL": "[FAIL]",
            "ERROR": "[ERROR]"
        }.get(level, "[INFO]")
        print(f"{prefix} {message}")

    def assert_result(self, name: str, success: bool, message: str = ""):
        """记录测试结果"""
        self.results.append({"name": name, "success": success, "message": message})
        if success:
            self.passed += 1
            self.log(f"✓ {name}", "PASS")
        else:
            self.failed += 1
            self.log(f"✗ {name}: {message}", "FAIL")

    def test_backend_health(self):
        """测试后端健康检查"""
        try:
            response = requests.get(f"{BASE_URL}/autotest/health", timeout=5)
            success = response.status_code == 200
            self.assert_result("后端健康检查", success, str(response.status_code))
        except Exception as e:
            self.assert_result("后端健康检查", False, str(e))

    def test_ai_health(self):
        """测试 AI 服务健康检查"""
        try:
            response = requests.get(f"{AI_BASE_URL}/health", timeout=5)
            success = response.status_code == 200
            self.assert_result("AI服务健康检查", success, str(response.status_code))
        except Exception as e:
            self.assert_result("AI服务健康检查", False, str(e))

    def test_rag_knowledge_add(self):
        """测试 RAG 知识添加"""
        try:
            url = f"{AI_BASE_URL}/ai/rag/add"
            payload = {
                "projectId": PROJECT_ID,
                "docType": "test",
                "docName": "测试文档",
                "content": "这是测试文档内容，用于验证RAG功能",
                "userId": "test-user"
            }
            response = requests.post(url, json=payload, timeout=30)
            data = response.json()
            success = response.status_code == 200 and data.get("success") == True
            self.assert_result("RAG知识添加", success, json.dumps(data))
        except Exception as e:
            self.assert_result("RAG知识添加", False, str(e))

    def test_rag_knowledge_query(self):
        """测试 RAG 知识检索"""
        try:
            url = f"{AI_BASE_URL}/ai/rag/query"
            params = {
                "projectId": PROJECT_ID,
                "query": "测试文档",
                "topK": 3
            }
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            success = response.status_code == 200 and len(data.get("data", [])) > 0
            self.assert_result("RAG知识检索", success, json.dumps(data)[:200])
        except Exception as e:
            self.assert_result("RAG知识检索", False, str(e))

    def test_chat_stream(self):
        """测试流式对话"""
        try:
            url = f"{AI_BASE_URL}/ai/chat/stream"
            headers = {"Content-Type": "application/json"}
            payload = {
                "projectId": PROJECT_ID,
                "message": "你好，请介绍一下你自己",
                "useRag": False,
                "messages": []
            }

            response = requests.post(url, json=payload, headers=headers, 
                                   stream=True, timeout=60)

            chunks = []
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data)
                            if chunk_data.get("type") == "content":
                                chunks.append(chunk_data.get("delta", ""))
                        except:
                            pass

            success = len(chunks) > 0
            full_content = "".join(chunks)
            self.assert_result("流式对话", success, full_content[:100] if full_content else "无内容")
        except Exception as e:
            self.assert_result("流式对话", False, str(e))

    def test_case_generation(self):
        """测试用例生成"""
        try:
            url = f"{AI_BASE_URL}/ai/generate-case"
            headers = {"Content-Type": "application/json"}
            payload = {
                "projectId": PROJECT_ID,
                "userRequirement": "生成一个用户登录测试用例",
                "selectedApis": [],
                "messages": []
            }

            response = requests.post(url, json=payload, headers=headers, timeout=120)
            data = response.json()

            success = (response.status_code == 200 and 
                      (data.get("status") == "success" or data.get("case") is not None))

            case_name = ""
            if data.get("case"):
                case_name = data.get("case").get("name", "")
            elif data.get("message"):
                case_name = data.get("message", "")[:50]

            self.assert_result("用例生成", success, case_name)
        except Exception as e:
            self.assert_result("用例生成", False, str(e))

    def test_api_list(self):
        """测试获取接口列表"""
        try:
            url = f"{AI_BASE_URL}/ai/agent/api-list/{PROJECT_ID}"
            headers = {"Content-Type": "application/json"}
            response = requests.get(url, headers=headers, timeout=30)

            success = response.status_code == 200
            data = response.json() if success else {}

            api_count = len(data.get("apiList", [])) if isinstance(data.get("apiList"), list) else 0

            self.assert_result("获取接口列表", success, f"接口数量: {api_count}")
        except Exception as e:
            self.assert_result("获取接口列表", False, str(e))

    def print_summary(self):
        """打印测试汇总"""
        print("\n" + "=" * 60)
        print("冒烟测试结果汇总")
        print("=" * 60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")
        print("=" * 60)

        if self.failed == 0:
            print("🎉 所有测试通过!")
        else:
            print(f"⚠️  {self.failed} 项测试失败")

        print("\n失败详情:")
        for result in self.results:
            if not result["success"]:
                print(f"  - {result['name']}: {result['message']}")


def run_smoke_tests():
    """运行冒烟测试"""
    test = SmokeTest()

    print("=" * 60)
    print("AI 服务冒烟测试")
    print("=" * 60)

    test.test_backend_health()
    test.test_ai_health()
    test.test_rag_knowledge_add()
    time.sleep(1)
    test.test_rag_knowledge_query()
    test.test_api_list()
    test.test_chat_stream()
    test.test_case_generation()

    test.print_summary()

    return test.failed == 0


if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
