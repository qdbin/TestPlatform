"""
AI服务单元测试
"""

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfig:
    """配置测试"""

    def test_config_load(self):
        """测试配置加载"""
        from app.config import config

        assert config.llm_provider is not None
        assert config.embedding_model is not None
        print(f"LLM Provider: {config.llm_provider}")
        print(f"Embedding Model: {config.embedding_model}")


class TestChunker:
    """文本分块测试"""

    def test_chunk_by_paragraph(self):
        """测试按段落分块"""
        from app.utils.chunking import chunk_text

        text = "这是第一段内容。\n\n这是第二段内容，包含一些详细描述。"
        chunks = chunk_text(text, chunk_size=50, overlap=10)

        assert len(chunks) > 0
        print(f"分块结果: {chunks}")

    def test_chunk_empty_text(self):
        """测试空文本"""
        from app.utils.chunking import chunk_text

        chunks = chunk_text("", chunk_size=50)
        assert len(chunks) == 0

        chunks = chunk_text(None, chunk_size=50)
        assert len(chunks) == 0


class TestLLMService:
    """LLM服务测试"""

    @pytest.mark.skipif(
        not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="需要配置API Key",
    )
    def test_llm_chat(self):
        """测试LLM对话"""
        from app.services.llm_service import llm_service

        messages = [{"role": "user", "content": "你好，请介绍一下自己"}]
        response = llm_service.chat(messages)

        assert response is not None
        assert len(response) > 0
        print(f"LLM响应: {response[:100]}...")


class TestRAGService:
    """RAG服务测试"""

    def test_rag_init(self):
        """测试RAG服务初始化"""
        from app.services.rag_service import rag_service

        assert rag_service._embeddings is not None
        assert rag_service._client is not None
        print("RAG服务初始化成功")

    def test_rag_search_empty(self):
        """测试空项目检索"""
        from app.services.rag_service import rag_service

        results = rag_service.search("test_project_not_exist", "测试查询", top_k=3)
        assert isinstance(results, list)
        print(f"检索结果: {results}")

    def test_rag_stats(self):
        """测试统计信息"""
        from app.services.rag_service import rag_service

        stats = rag_service.get_collection_stats("test_project")
        assert "count" in stats
        assert "project_id" in stats
        print(f"统计信息: {stats}")


class TestPlatformClient:
    """平台客户端测试"""

    def test_client_init(self):
        """测试客户端初始化"""
        from app.tools.platform_tools import platform_client

        assert platform_client.base_url is not None
        print(f"平台地址: {platform_client.base_url}")

    def test_get_api_list(self):
        """测试获取接口列表"""
        from app.tools.platform_tools import PlatformClient

        # 使用不存在的项目测试
        client = PlatformClient()
        result = client.get_api_list("test_project_id")

        assert isinstance(result, list)
        print(f"接口列表: {result}")


class TestAgentService:
    """Agent服务测试"""

    def test_agent_init(self):
        """测试Agent初始化"""
        from app.services.agent_service import agent_service

        assert agent_service is not None
        print("Agent服务初始化成功")


class TestAPIs:
    """API接口测试"""

    def test_root(self):
        """测试根路径"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print(f"根路径响应: {data}")

    def test_health(self):
        """测试健康检查"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        print(f"健康检查: {response.json()}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
