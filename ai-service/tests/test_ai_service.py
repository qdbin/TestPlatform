import os
import sys
from typing import List

import pytest
from fastapi.testclient import TestClient


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DummyEmbeddings:
    def embed_documents(self, texts: List[str]):
        return [[float(i), 0.0, 0.0] for i in range(len(texts))]

    def embed_query(self, text: str):
        return [0.0, 0.0, 0.0]


class FakeCollection:
    def __init__(self):
        self.docs = []
        self.ids = []
        self.metadatas = []
        self.embeddings = []

    def add(self, embeddings, documents, ids, metadatas):
        self.embeddings.extend(embeddings)
        self.docs.extend(documents)
        self.ids.extend(ids)
        self.metadatas.extend(metadatas)

    def upsert(self, embeddings, documents, ids, metadatas):
        current = {id_val: i for i, id_val in enumerate(self.ids)}
        for i, id_val in enumerate(ids):
            if id_val in current:
                idx = current[id_val]
                self.embeddings[idx] = embeddings[i]
                self.docs[idx] = documents[i]
                self.metadatas[idx] = metadatas[i]
            else:
                self.embeddings.append(embeddings[i])
                self.docs.append(documents[i])
                self.ids.append(id_val)
                self.metadatas.append(metadatas[i])

    def query(self, query_embeddings, n_results=5):
        top_docs = self.docs[:n_results]
        top_meta = self.metadatas[:n_results]
        top_distance = [0.0 for _ in top_docs]
        return {
            "documents": [top_docs],
            "metadatas": [top_meta],
            "distances": [top_distance],
        }

    def count(self):
        return len(self.ids)

    def get(self, where=None):
        if not where:
            return {"ids": self.ids, "metadatas": self.metadatas}
        knowledge_id = str(where.get("knowledge_id")) if isinstance(where, dict) else ""
        matched = [
            (id_val, meta)
            for id_val, meta in zip(self.ids, self.metadatas)
            if isinstance(meta, dict) and str(meta.get("knowledge_id")) == knowledge_id
        ]
        return {"ids": [x[0] for x in matched], "metadatas": [x[1] for x in matched]}

    def delete(self, ids=None, where=None):
        if ids is None and where is not None:
            knowledge_id = str(where.get("knowledge_id")) if isinstance(where, dict) else ""
            ids = [
                id_val
                for id_val, meta in zip(self.ids, self.metadatas)
                if isinstance(meta, dict) and str(meta.get("knowledge_id")) == knowledge_id
            ]
        ids = ids or []
        remain = [
            (d, i, m, e)
            for d, i, m, e in zip(self.docs, self.ids, self.metadatas, self.embeddings)
            if i not in set(ids)
        ]
        self.docs = [x[0] for x in remain]
        self.ids = [x[1] for x in remain]
        self.metadatas = [x[2] for x in remain]
        self.embeddings = [x[3] for x in remain]


class FakeClient:
    def __init__(self):
        self.collections = {}

    def get_or_create_collection(self, name, metadata=None):
        if name not in self.collections:
            self.collections[name] = FakeCollection()
        return self.collections[name]

    def get_collection(self, name):
        if name not in self.collections:
            raise ValueError("collection not exists")
        return self.collections[name]


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
    rag_service._client = FakeClient()

    results = rag_service.search("project_x", "登录接口", top_k=3)
    assert results == []


def test_rag_add_and_search(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embeddings = DummyEmbeddings()
    rag_service._client = FakeClient()

    project_id = "test_project"
    knowledge_id = "k1"
    docs = ["用户登录接口说明", "登录接口返回token字段"]
    rag_service.add_documents(project_id, knowledge_id, docs)

    results = rag_service.search(project_id, "登录", top_k=2)
    assert isinstance(results, list)
    assert len(results) > 0


def test_rag_reindex_same_knowledge(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embeddings = DummyEmbeddings()
    rag_service._client = FakeClient()

    project_id = "test_project_reindex"
    knowledge_id = "k_reindex"
    rag_service.add_documents(project_id, knowledge_id, ["登录接口V1"])
    rag_service.add_documents(project_id, knowledge_id, ["登录接口V2"])
    stats = rag_service.get_collection_stats(project_id)
    assert stats["count"] == 1


def test_rag_project_isolation(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embeddings = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._fallback_docs = {}

    rag_service.add_documents("p_a", "k1", ["登录接口A"])
    rag_service.add_documents("p_b", "k2", ["支付接口B"])

    results_a = rag_service.search("p_a", "登录", top_k=5)
    results_b = rag_service.search("p_b", "支付", top_k=5)
    assert any("登录接口A" in item.get("content", "") for item in results_a)
    assert all("支付接口B" not in item.get("content", "") for item in results_a)
    assert any("支付接口B" in item.get("content", "") for item in results_b)


def test_rag_fallback_search_when_embedding_unavailable(monkeypatch):
    from app.services.rag_service import rag_service

    monkeypatch.setattr(rag_service, "_init_components", lambda: None)
    rag_service._embeddings = None
    rag_service._client = FakeClient()
    rag_service._fallback_docs = {}
    rag_service._upsert_fallback_docs("p_fallback", "k1", ["韩斌简历：自动化测试工程师"])
    results = rag_service.search("p_fallback", "韩斌", top_k=3)
    assert isinstance(results, list)
    assert len(results) >= 1


def test_rag_delete_knowledge(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embeddings = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._fallback_docs = {}
    rag_service.add_documents("p_del", "k_del", ["删除前文档"])
    delete_result = rag_service.delete_knowledge("p_del", "k_del")
    assert delete_result.get("status") == "success"
    results = rag_service.search("p_del", "删除前文档", top_k=5)
    assert results == []


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

    def fake_stream_chat(project_id: str, token: str, message: str, use_rag: bool, conversation_id: str = "", history_messages=None):
        yield {"type": "content", "delta": "O"}
        yield {"type": "content", "delta": "K"}
        yield {"type": "case", "case": {"name": "demo"}}

    monkeypatch.setattr(agent_service_module.agent_service, "stream_chat", fake_stream_chat)

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


def test_agent_chat_case_via_executor(monkeypatch):
    from app.services.agent_service import agent_service

    class FakeExecutor:
        def invoke(self, payload):
            return {
                "output": '{"reply":"已生成草稿","case":{"name":"登录接口用例"}}'
            }

    monkeypatch.setattr(agent_service, "_build_executor", lambda p, t, r: FakeExecutor())

    result = agent_service.chat(
        project_id="p1",
        token="tok",
        message="请帮我生成登录接口测试用例",
        use_rag=True,
    )
    assert result.get("reply") == "已生成草稿"
    assert isinstance(result.get("case"), dict)


def test_generate_case_json_repair(monkeypatch):
    from app.services import agent_service as agent_service_module
    from app.services.agent_service import agent_service
    from app.services import llm_service as llm_service_module
    from app.services import rag_service as rag_service_module

    class FakePlatformClient:
        def get_api_list(self, project_id: str):
            return [{"id": "api_1"}]

        def get_api_detail(self, api_id: str):
            return {
                "id": api_id,
                "name": "登录接口",
                "path": "/login",
                "method": "POST",
                "moduleId": "m1",
                "moduleName": "登录模块",
            }

    monkeypatch.setattr(agent_service_module, "get_platform_client", lambda token: FakePlatformClient())
    monkeypatch.setattr(rag_service_module.rag_service, "search", lambda project_id, query, top_k=5: [])
    monkeypatch.setattr(
        llm_service_module.llm_service,
        "chat",
        lambda messages: '{"name":"登录用例","type":"API","caseApis":[{"name":"步骤1",}],}',
    )

    result = agent_service.generate_case(
        project_id="p1",
        token="tok",
        user_requirement="生成登录接口测试用例",
        selected_apis=["api_1"],
    )
    assert result.get("status") == "success"
    assert isinstance(result.get("case"), dict)
    assert result["case"].get("name") == "登录用例"
    assert result["case"].get("projectId") == "p1"


def test_generate_case_needs_api_create(monkeypatch):
    from app.services import agent_service as agent_service_module
    from app.services.agent_service import agent_service

    class EmptyPlatformClient:
        def get_api_list(self, project_id: str):
            return []

        def get_api_detail(self, api_id: str):
            return None
        
        def save_api(self, project_id: str, api_data):
            return None

    monkeypatch.setattr(agent_service_module, "get_platform_client", lambda token: EmptyPlatformClient())
    monkeypatch.setattr(
        agent_service,
        "_generate_interface_candidates",
        lambda project_id, requirement: [{"name": "登录接口", "path": "/login", "method": "POST", "description": ""}],
    )
    result = agent_service.generate_case(
        project_id="p2",
        token="tok",
        user_requirement="生成登录用例",
        selected_apis=[],
    )
    assert result.get("status") == "needs_api_create"
    assert isinstance(result.get("interfaces"), list)
    assert result["interfaces"][0]["path"] == "/login"


def test_generate_case_auto_create_api(monkeypatch):
    from app.services import agent_service as agent_service_module
    from app.services.agent_service import agent_service
    from app.services import llm_service as llm_service_module
    from app.services import rag_service as rag_service_module

    class AutoCreateClient:
        def __init__(self):
            self.saved_ids = ["api_created_1"]

        def get_api_list(self, project_id: str):
            return []

        def get_api_detail(self, api_id: str):
            if api_id == "api_created_1":
                return {
                    "id": "api_created_1",
                    "name": "注册接口",
                    "path": "/register",
                    "method": "POST",
                    "moduleId": "0",
                    "moduleName": "默认模块",
                }
            return None

        def save_api(self, project_id: str, api_data):
            return "api_created_1"

    monkeypatch.setattr(agent_service_module, "get_platform_client", lambda token: AutoCreateClient())
    monkeypatch.setattr(
        agent_service,
        "_generate_interface_candidates",
        lambda project_id, requirement: [{"name": "注册接口", "path": "/register", "method": "POST", "description": ""}],
    )
    monkeypatch.setattr(rag_service_module.rag_service, "search", lambda project_id, query, top_k=5: [])
    monkeypatch.setattr(
        llm_service_module.llm_service,
        "chat",
        lambda messages: '{"name":"注册流程用例","type":"API","caseApis":[{"apiId":"api_created_1","description":"步骤1"}]}',
    )
    result = agent_service.generate_case(
        project_id="p3",
        token="tok",
        user_requirement="基于注册接口生成用例",
        selected_apis=[],
    )
    assert result.get("status") == "success"
    assert "api_created_1" in result.get("created_api_ids", [])

