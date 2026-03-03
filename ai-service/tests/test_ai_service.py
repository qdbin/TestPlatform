import os
import sys
from typing import List

import chromadb
import pytest
from fastapi.testclient import TestClient


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DummyEmbeddings:
    def embed_documents(self, texts: List[str]):
        return [[float(i), 0.0, 0.0] for i in range(len(texts))]

    def embed_query(self, text: str):
        return [0.0, 0.0, 0.0]


@pytest.fixture()
def client():
    from app.main import app

    return TestClient(app)


def test_config_load():
    from app.config import config

    assert isinstance(config.llm_provider, str)
    assert isinstance(config.embedding_model, str)
    assert isinstance(config.chroma_persist_dir, str)


def test_chunking_basic():
    from app.utils.chunking import chunk_text

    text = "这是第一段内容。\n\n这是第二段内容，包含一些详细描述。"
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) > 0


def test_rag_search_empty(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embeddings = DummyEmbeddings()
    rag_service._client = chromadb.EphemeralClient()

    results = rag_service.search("project_x", "登录接口", top_k=3)
    assert results == []


def test_rag_add_and_search(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embeddings = DummyEmbeddings()
    rag_service._client = chromadb.EphemeralClient()

    project_id = "test_project"
    knowledge_id = "k1"
    docs = ["用户登录接口说明", "登录接口返回token字段"]
    rag_service.add_documents(project_id, knowledge_id, docs)

    results = rag_service.search(project_id, "登录", top_k=2)
    assert isinstance(results, list)
    assert len(results) > 0


def test_platform_client_headers():
    from app.tools.platform_tools import get_platform_client

    c = get_platform_client("t123")
    headers = c._get_headers()
    assert headers.get("token") == "t123"


def test_chat_api_uses_agent(monkeypatch, client: TestClient):
    from app.services import agent_service as agent_service_module

    def fake_chat(project_id: str, token: str, message: str, use_rag: bool):
        return {"reply": "你好", "case": {"name": "demo"}}

    monkeypatch.setattr(agent_service_module.agent_service, "chat", fake_chat)

    resp = client.post(
        "/ai/chat",
        json={"project_id": "p1", "message": "测试", "use_rag": True, "conversation_id": ""},
        headers={"token": "tok"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["content"] == "你好"
    assert data["case"]["name"] == "demo"


def test_chat_stream_sse_format(monkeypatch, client: TestClient):
    from app.services import agent_service as agent_service_module

    def fake_chat(project_id: str, token: str, message: str, use_rag: bool):
        return {"reply": "OK", "case": {"name": "demo"}}

    monkeypatch.setattr(agent_service_module.agent_service, "chat", fake_chat)

    resp = client.post(
        "/ai/chat/stream",
        json={"project_id": "p1", "message": "测试", "use_rag": True, "conversation_id": ""},
        headers={"token": "tok"},
    )
    assert resp.status_code == 200
    text = resp.text
    assert "data:" in text
    assert '"type": "case"' in text
    assert '"type": "end"' in text

