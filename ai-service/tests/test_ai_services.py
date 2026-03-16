"""
AI 服务单元测试

功能：
    1. LLM 服务测试
    2. RAG 服务测试
    3. Agent 服务测试

使用：
    pytest tests/test_ai_services.py -v
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLLMService:
    """LLM 服务测试"""

    @pytest.fixture
    def llm_service(self):
        from app.services.llm_service import llm_service

        return llm_service

    def test_chat(self, llm_service):
        """测试普通对话"""
        messages = [{"role": "user", "content": "你好"}]
        with patch.object(llm_service, "_get_llm") as mock_llm:
            mock_response = Mock()
            mock_response.content = "你好，我是AI助手"
            mock_llm.return_value.invoke.return_value = mock_response

            result = llm_service.chat(messages)
            assert result == "你好，我是AI助手"

    def test_chat_json(self, llm_service):
        """测试 JSON 模式对话"""
        messages = [{"role": "user", "content": "返回JSON格式"}]
        with patch.object(llm_service, "_get_llm") as mock_llm:
            mock_response = Mock()
            mock_response.content = '{"name": "test"}'
            mock_llm.return_value.bind.return_value.invoke.return_value = mock_response

            result = llm_service.chat_json(messages)
            assert "name" in result

    def test_build_messages(self, llm_service):
        """测试消息格式转换"""
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好"},
        ]
        result = llm_service._build_langchain_messages(messages, None)
        assert len(result) == 2


class TestRAGService:
    """RAG 服务测试"""

    @pytest.fixture
    def rag_service(self):
        from app.services.rag_service import rag_service

        return rag_service

    def test_add_document(self, rag_service):
        """测试文档添加"""
        documents = [{"content": "测试文档内容", "metadata": {}}]
        with patch.object(rag_service, "_init_components"):
            with patch.object(
                rag_service, "_get_or_create_collection"
            ) as mock_collection:
                mock_collection.return_value = Mock()

                result = rag_service.add_document(
                    project_id="test-project",
                    doc_id="doc1",
                    doc_type="test",
                    doc_name="测试文档",
                    documents=documents,
                )
                assert result is not None

    def test_search(self, rag_service):
        """测试检索"""
        with patch.object(rag_service, "_init_components"):
            with patch.object(rag_service, "_query_rewrite_and_expand") as mock_rewrite:
                mock_rewrite.return_value = ["测试查询"]

                with patch.object(rag_service, "_keyword_search") as mock_keyword:
                    mock_keyword.return_value = []

                    with patch.object(rag_service, "_vector_search") as mock_vector:
                        mock_vector.return_value = ("success", [])

                        result = rag_service.search_with_status(
                            project_id="test-project", query="测试查询", top_k=5
                        )
                        assert result is not None
                        assert "status" in result
                        assert "data" in result


class TestAgentService:
    """Agent 服务测试"""

    @pytest.fixture
    def agent_service(self):
        from app.services.agent_service import agent_service

        return agent_service

    def test_is_case_request(self):
        """测试用例需求识别"""
        from app.services.agent_service import _is_case_request

        assert _is_case_request("帮我生成一个登录测试用例") == True
        assert _is_case_request("如何登录系统？") == False
        assert _is_case_request("编写测试场景") == True

    def test_normalize_messages(self):
        """测试消息标准化"""
        from app.services.agent_service import _normalize_messages

        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好"},
            {"role": "user", "content": ""},
            "invalid",
        ]
        result = _normalize_messages(messages)
        assert len(result) == 2

    def test_build_chat_prompt(self, agent_service):
        """测试对话 Prompt 构建"""
        result = agent_service._build_chat_prompt(
            message="测试问题", rag_docs=[{"content": "文档内容"}], rag_status="success"
        )
        assert "测试问题" in result


class TestQueryRewriter:
    """查询改写器测试"""

    def test_rewrite(self):
        from app.services.retrieval.query_rewrite import query_rewriter

        result = query_rewriter.rewrite_and_expand("登录")
        assert isinstance(result, list)
        assert len(result) > 0


class TestReranker:
    """重排序器测试"""

    def test_rerank(self):
        from app.services.retrieval.reranker import reranker

        candidates = [
            {"content": "第一个文档", "hybrid_score": 0.8},
            {"content": "第二个文档", "hybrid_score": 0.6},
            {"content": "第三个文档", "hybrid_score": 0.9},
        ]

        result = reranker.rerank("测试查询", candidates, top_k=2)
        assert len(result) <= 2
        assert all("rerank_score" in item for item in result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
