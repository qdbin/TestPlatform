import os
import sys
import time
from typing import List, Dict, Any

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

    def query(self, query_embeddings, n_results=5, where=None):
        pairs = list(zip(self.docs, self.metadatas))
        if isinstance(where, dict):
            for key, value in where.items():
                pairs = [
                    item
                    for item in pairs
                    if isinstance(item[1], dict) and str(item[1].get(key)) == str(value)
                ]
        top_docs = [item[0] for item in pairs[:n_results]]
        top_meta = [item[1] for item in pairs[:n_results]]
        top_distance = [0.0 for _ in top_docs]
        return {
            "documents": [top_docs],
            "metadatas": [top_meta],
            "distances": [top_distance],
        }

    def count(self):
        return len(self.ids)

    def get(self, where=None, include=None):
        if not isinstance(where, dict):
            return {"ids": self.ids, "metadatas": self.metadatas}

        def matches(meta, expr):
            if not isinstance(expr, dict):
                return False
            if "$and" in expr and isinstance(expr["$and"], list):
                return all(matches(meta, item) for item in expr["$and"])
            for key, value in expr.items():
                if key.startswith("$"):
                    continue
                if str(meta.get(key)) != str(value):
                    return False
            return True

        matched = []
        for id_val, meta in zip(self.ids, self.metadatas):
            if not isinstance(meta, dict):
                continue
            if matches(meta, where):
                matched.append((id_val, meta))
        return {"ids": [x[0] for x in matched], "metadatas": [x[1] for x in matched]}

    def delete(self, ids=None, where=None):
        if ids is None and isinstance(where, dict):

            def matches(meta, expr):
                if not isinstance(expr, dict):
                    return False
                if "$and" in expr and isinstance(expr["$and"], list):
                    return all(matches(meta, item) for item in expr["$and"])
                for key, value in expr.items():
                    if key.startswith("$"):
                        continue
                    if str(meta.get(key)) != str(value):
                        return False
                return True

            ids = []
            for id_val, meta in zip(self.ids, self.metadatas):
                if not isinstance(meta, dict):
                    continue
                if matches(meta, where):
                    ids.append(id_val)
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

    text = "# 标题1\n第一段\n\n## 标题2\n第二段"
    chunks = chunk_text(text, chunk_size=80, overlap=10)
    assert len(chunks) > 0


def test_rag_search_empty(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    results = rag_service.search("project_x", "登录接口", top_k=3)
    assert results == []


def test_rag_add_and_search(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    project_id = "test_project"
    doc_id = "k1"
    docs = ["用户登录接口说明", "登录接口返回token字段"]
    rag_service.add_document(project_id, doc_id, "manual", "登录文档", docs)

    results = rag_service.search(project_id, "登录", top_k=2)
    assert isinstance(results, list)
    assert len(results) > 0


def test_rag_reindex_same_knowledge(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    project_id = "test_project_reindex"
    doc_id = "k_reindex"
    rag_service.add_document(project_id, doc_id, "manual", "登录文档", ["登录接口V1"])
    rag_service.add_document(project_id, doc_id, "manual", "登录文档", ["登录接口V2"])
    stats = rag_service.get_collection_stats(project_id)
    assert stats["count"] == 1


def test_rag_project_isolation(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    rag_service.add_document("p_a", "k1", "manual", "a", ["登录接口A"])
    rag_service.add_document("p_b", "k2", "manual", "b", ["支付接口B"])

    results_a = rag_service.search("p_a", "登录", top_k=5)
    results_b = rag_service.search("p_b", "支付", top_k=5)
    assert any("登录接口A" in item.get("content", "") for item in results_a)
    assert all("支付接口B" not in item.get("content", "") for item in results_a)
    assert any("支付接口B" in item.get("content", "") for item in results_b)


def test_rag_delete_knowledge(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None
    rag_service.add_document("p_del", "k_del", "manual", "删除文档", ["删除前文档"])
    delete_result = rag_service.delete_document("p_del", "k_del")
    assert delete_result.get("status") == "success"
    results = rag_service.search("p_del", "删除前文档", top_k=5)
    assert results == []


def test_platform_client_headers():
    from app.tools.platform_tools import get_platform_client

    c = get_platform_client("t123")
    headers = c._get_headers()
    assert headers.get("token") == "t123"


def test_chat_stream_sse_format(monkeypatch, client: TestClient):
    from app.services import agent_service as agent_service_module

    def fake_stream_chat(
        project_id: str, token: str, message: str, use_rag: bool, messages=None
    ):
        yield {"type": "content", "delta": "O"}
        yield {"type": "content", "delta": "K"}
        yield {"type": "case", "case": {"name": "demo"}}

    monkeypatch.setattr(
        agent_service_module.agent_service, "stream_chat", fake_stream_chat
    )

    resp = client.post(
        "/ai/chat/stream",
        json={"project_id": "p1", "message": "测试", "use_rag": True, "messages": []},
        headers={"token": "tok"},
    )
    assert resp.status_code == 200
    text = resp.text
    assert "data:" in text
    assert '"type": "case"' in text
    assert '"type": "end"' in text


def test_chat_stream_should_flush_first_event_without_waiting(
    monkeypatch, client: TestClient
):
    from app.services import agent_service as agent_service_module

    def fake_stream_chat(
        project_id: str, token: str, message: str, use_rag: bool, messages=None
    ):
        yield {"type": "content", "delta": "正在思考，请稍候..."}
        time.sleep(0.25)
        yield {"type": "content", "delta": "后续内容"}

    monkeypatch.setattr(
        agent_service_module.agent_service, "stream_chat", fake_stream_chat
    )
    start = time.time()
    with client.stream(
        "POST",
        "/ai/chat/stream",
        json={"project_id": "p1", "message": "测试", "use_rag": True, "messages": []},
        headers={"token": "tok"},
    ) as resp:
        assert resp.status_code == 200
        for line in resp.iter_lines():
            if line and line.startswith("data:"):
                first_delay = time.time() - start
                assert first_delay < 0.35
                assert "正在思考" in line
                break


def test_agent_chat_case_via_executor(monkeypatch):
    from app.services.agent_service import agent_service

    monkeypatch.setattr(
        agent_service,
        "generate_case",
        lambda project_id, token, user_requirement, selected_apis=None, messages=None: {
            "status": "success",
            "case": {"name": "登录接口用例"},
        },
    )

    result = agent_service.chat(
        project_id="p1",
        token="tok",
        message="请帮我生成登录接口测试用例",
        use_rag=True,
    )
    assert result.get("reply") == "已生成用例预览，请确认后手动保存。"
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

        def get_case_schema(self, project_id: str):
            return {"CaseRequest": {"type": "object"}}

    monkeypatch.setattr(
        agent_service_module, "get_platform_client", lambda token: FakePlatformClient()
    )
    monkeypatch.setattr(
        rag_service_module.rag_service, "search", lambda project_id, query, top_k=5: []
    )
    monkeypatch.setattr(
        llm_service_module.llm_service,
        "chat_json",
        lambda messages, system_prompt=None: '{"name":"登录用例","caseApis":[{"apiId":"api_1","description":"步骤1"},{"apiId":"api_1","description":"步骤2"}],}',
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


def test_generate_case_without_api_should_fail(monkeypatch):
    from app.services import agent_service as agent_service_module
    from app.services.agent_service import agent_service

    class EmptyClient:
        def get_api_list(self, project_id: str):
            return []

    monkeypatch.setattr(
        agent_service_module, "get_platform_client", lambda token: EmptyClient()
    )
    result = agent_service.generate_case(
        project_id="p2",
        token="tok",
        user_requirement="生成登录用例",
        selected_apis=[],
    )
    assert result.get("status") == "error"
    assert "接口" in str(result.get("message") or "")


def test_case_intent_should_require_action():
    from app.services.agent_service import _is_case_request

    assert _is_case_request("帮我生成登录注册流程用例") is True
    assert _is_case_request("接口测试是什么") is False


def test_chat_prompt_no_context_private_vs_public():
    from app.services.agent_service import agent_service

    private_prompt = agent_service._build_chat_prompt(
        "当前项目登录失败怎么排查", [], "no_context"
    )
    public_prompt = agent_service._build_chat_prompt(
        "周杰伦有哪些经典歌曲", [], "no_context"
    )
    assert "未检索到证据" in private_prompt
    assert "不要提及知识库未命中" in public_prompt


def test_chat_prompt_should_include_context():
    from app.services.agent_service import agent_service

    prompt = agent_service._build_chat_prompt(
        "登录接口如何断言",
        [{"content": "登录成功返回token"}],
        "success",
    )
    assert "知识片段" in prompt
    assert "登录成功返回token" in prompt


def test_dependency_relations_should_link_auth_flow():
    from app.services.agent_service import agent_service

    api_details = [
        {"id": "api_login", "path": "/auth/login", "method": "POST"},
        {"id": "api_profile", "path": "/user/profile", "method": "GET"},
    ]
    relations = agent_service._build_dependency_relations(api_details)
    assert "api_profile" in relations
    assert "api_login" in relations.get("api_profile", [])


def test_normalize_case_should_complete_flow_steps():
    from app.services.agent_service import agent_service

    api_details = [
        {
            "id": "api_1",
            "name": "登录",
            "path": "/auth/login",
            "method": "POST",
            "moduleId": "m1",
            "moduleName": "鉴权",
        },
        {
            "id": "api_2",
            "name": "用户信息",
            "path": "/user/profile",
            "method": "GET",
            "moduleId": "m1",
            "moduleName": "鉴权",
        },
    ]
    case_obj = {"name": "链路用例", "caseApis": [{"apiId": "api_1"}]}
    normalized = agent_service._normalize_case(
        "p1",
        case_obj,
        api_details,
        api_relations={"api_2": ["api_1"]},
    )
    steps = normalized.get("caseApis") or []
    assert len(steps) >= 2
    assert steps[0].get("apiId") == "api_1"
    assert any(step.get("apiId") == "api_2" for step in steps)


def test_rag_router_add_query_delete(monkeypatch, client: TestClient):
    from app.services import rag_service as rag_service_module

    monkeypatch.setattr(
        rag_service_module.rag_service,
        "add_document",
        lambda project_id, doc_id, doc_type, doc_name, documents: {
            "indexed": True,
            "degraded": False,
            "vector_count": len(documents),
            "error": "",
        },
    )
    monkeypatch.setattr(
        rag_service_module.rag_service,
        "search_with_status",
        lambda project_id, query, top_k=5: {
            "status": "success",
            "data": [{"content": "命中内容", "metadata": {"project_id": project_id}}],
        },
    )
    monkeypatch.setattr(
        rag_service_module.rag_service,
        "delete_document",
        lambda project_id, doc_id: {"status": "success", "vector_deleted": 2},
    )
    add_resp = client.post(
        "/ai/rag/add",
        json={
            "project_id": "p1",
            "doc_id": "d1",
            "doc_type": "manual",
            "doc_name": "文档",
            "content": "# H1\n内容",
        },
    )
    assert add_resp.status_code == 200
    query_resp = client.post(
        "/ai/rag/query",
        json={"project_id": "p1", "question": "登录", "top_k": 3, "messages": []},
    )
    assert query_resp.status_code == 200
    assert query_resp.json().get("has_context") is True
    delete_resp = client.post(
        "/ai/rag/delete", json={"project_id": "p1", "doc_id": "d1"}
    )
    assert delete_resp.status_code == 200


def test_platform_client_get_api_list_supports_pager_list(monkeypatch):
    from app.tools.platform_tools import PlatformClient

    class FakeResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {
                "status": 0,
                "message": "成功",
                "data": {
                    "list": [
                        {
                            "id": "a1",
                            "name": "登录接口",
                            "path": "/auth/login",
                            "method": "POST",
                        },
                        {
                            "id": "a2",
                            "name": "查询用户",
                            "path": "/user/info",
                            "method": "GET",
                        },
                    ],
                    "total": 2,
                },
            }

    class FakeClientCtx:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def post(self, url, json=None, headers=None):
            return FakeResponse()

    monkeypatch.setattr("app.tools.platform_tools.httpx.Client", FakeClientCtx)
    client = PlatformClient(base_url="http://localhost:8080", api_key="tok")
    items = client.get_api_list("p1")
    assert len(items) == 2
    assert items[0]["id"] == "a1"


def test_rag_doc_name_should_be_searchable(monkeypatch):
    from app.services.rag_service import rag_service

    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    rag_service.add_document("p_doc", "d_name", "manual", "韩斌", ["身高和其他信息"])
    results = rag_service.search("p_doc", "韩斌", top_k=5)
    assert len(results) > 0
    assert any("韩斌" in str(item.get("content") or "") for item in results)


def test_stream_chat_case_should_emit_first_chunk_immediately(monkeypatch):
    from app.services.agent_service import agent_service

    def slow_generate_case(
        project_id, token, user_requirement, selected_apis=None, messages=None
    ):
        time.sleep(0.25)
        return {
            "status": "success",
            "case": {"name": "登录用例"},
            "existing_api_ids": [],
        }

    monkeypatch.setattr(agent_service, "generate_case", slow_generate_case)
    stream = agent_service.stream_chat(
        project_id="p1",
        token="tok",
        message="请生成登录用例",
        use_rag=True,
        messages=[],
    )
    start = time.time()
    first = next(stream)
    elapsed = time.time() - start
    assert elapsed < 0.12
    assert first.get("type") == "content"
    assert "正在生成用例" in str(first.get("delta") or "")


def test_stream_chat_should_split_large_delta(monkeypatch):
    from app.services.agent_service import agent_service
    from app.services import llm_service as llm_service_module

    monkeypatch.setattr(
        llm_service_module.llm_service,
        "chat_with_stream",
        lambda messages, system_prompt=None: iter(["A" * 45]),
    )
    stream = agent_service.stream_chat(
        project_id="p1",
        token="tok",
        message="解释登录接口断言",
        use_rag=False,
        messages=[],
    )
    parts = [evt.get("delta", "") for evt in stream if evt.get("type") == "content"]
    assert parts[0] == "正在思考，请稍候..."
    merged = "".join([part for part in parts if part and part.strip()])
    assert "A" * 45 in merged


def test_stream_chat_non_case_should_emit_first_chunk_immediately(monkeypatch):
    from app.services.agent_service import agent_service
    from app.services import llm_service as llm_service_module

    def delayed_stream(messages, system_prompt=None):
        time.sleep(0.35)
        yield "测试流式内容"

    monkeypatch.setattr(
        llm_service_module.llm_service, "chat_with_stream", delayed_stream
    )
    stream = agent_service.stream_chat(
        project_id="p1",
        token="tok",
        message="什么是接口测试",
        use_rag=False,
        messages=[],
    )
    start = time.time()
    first = next(stream)
    elapsed = time.time() - start
    assert elapsed < 0.12
    assert first.get("type") == "content"
    assert "正在思考" in str(first.get("delta") or "")
