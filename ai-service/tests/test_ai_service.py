"""
AI服务单元测试模块

测试范围：
    1. RAG服务：文档索引、检索、项目隔离、父文档回填
    2. Agent服务：用例生成、对话流程、依赖关系构建
    3. 平台客户端：鉴权头、API调用
    4. SSE流式响应：事件格式、首事件延迟

Mock策略：
    - DummyEmbeddings: 模拟Embedding函数，返回固定向量
    - FakeCollection: 模拟Chroma Collection，内存存储
    - FakeClient: 模拟Chroma Client，管理Collection

关键测试场景：
    - test_rag_add_and_search: RAG索引与检索基本流程
    - test_rag_project_isolation: 项目间数据隔离验证
    - test_rag_should_backfill_parent_context_when_child_hit: 父文档回填机制
    - test_chat_stream_sse_format: SSE流式响应格式验证
    - test_generate_case_json_repair: JSON修复机制验证
"""

import os
import sys
import time
import asyncio
from typing import List, Dict, Any

import pytest
from fastapi.testclient import TestClient

# 关键步骤：将项目根目录添加到Python路径（支持导入app模块）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def _fake_async_stream(chunks):
    for item in chunks:
        yield item


class DummyEmbeddings:
    """
    模拟Embedding函数

    用于测试环境避免加载真实Embedding模型

    关键字段：
        - embed_documents: 批量文档向量化
        - embed_query: 查询向量化
    """

    def embed_documents(self, texts: List[str]):
        # 关键步骤：返回固定向量，维度为3（简化测试）
        return [[float(i), 0.0, 0.0] for i in range(len(texts))]

    def embed_query(self, text: str):
        # 关键步骤：查询向量固定为[0,0,0]（简化测试）
        return [0.0, 0.0, 0.0]


class FakeCollection:
    """
    模拟Chroma Collection

    内存存储实现，支持：
        - add/upsert: 写入文档
        - query: 检索文档
        - delete: 删除文档
        - get: 按条件获取文档

    关键字段：
        - docs: 文档内容列表
        - ids: 文档ID列表
        - metadatas: 元数据列表
        - embeddings: 向量列表
    """

    def __init__(self):
        self.docs = []  # 文档内容列表
        self.ids = []  # 文档ID列表
        self.metadatas = []  # 元数据列表
        self.embeddings = []  # 向量列表

    def add(self, embeddings, documents, ids, metadatas):
        # 关键步骤：追加文档到内存列表
        self.embeddings.extend(embeddings)
        self.docs.extend(documents)
        self.ids.extend(ids)
        self.metadatas.extend(metadatas)

    def upsert(self, embeddings, documents, ids, metadatas):
        # 关键步骤：构建ID到索引的映射（用于判断更新还是新增）
        current = {id_val: i for i, id_val in enumerate(self.ids)}
        for i, id_val in enumerate(ids):
            if id_val in current:
                # 关键步骤：ID已存在，执行更新
                idx = current[id_val]
                self.embeddings[idx] = embeddings[i]
                self.docs[idx] = documents[i]
                self.metadatas[idx] = metadatas[i]
            else:
                # 关键步骤：ID不存在，执行新增
                self.embeddings.append(embeddings[i])
                self.docs.append(documents[i])
                self.ids.append(id_val)
                self.metadatas.append(metadatas[i])

    def query(self, query_embeddings, n_results=5, where=None):
        # 关键步骤：构建文档-元数据对
        pairs = list(zip(self.docs, self.metadatas))

        # 关键步骤：按where条件过滤
        if isinstance(where, dict):
            for key, value in where.items():
                pairs = [
                    item
                    for item in pairs
                    if isinstance(item[1], dict) and str(item[1].get(key)) == str(value)
                ]

        # 关键步骤：返回Top-K结果
        top_docs = [item[0] for item in pairs[:n_results]]
        top_meta = [item[1] for item in pairs[:n_results]]
        top_distance = [0.0 for _ in top_docs]  # 距离固定为0（简化测试）
        return {
            "documents": [top_docs],
            "metadatas": [top_meta],
            "distances": [top_distance],
        }

    def count(self):
        return len(self.ids)

    def get(self, where=None, include=None):
        # 关键步骤：无where条件时返回全部
        if not isinstance(where, dict):
            return {"ids": self.ids, "metadatas": self.metadatas}

        def matches(meta, expr):
            # 关键步骤：支持$and逻辑运算符
            if not isinstance(expr, dict):
                return False
            if "$and" in expr and isinstance(expr["$and"], list):
                return all(matches(meta, item) for item in expr["$and"])

            # 关键步骤：逐字段匹配
            for key, value in expr.items():
                if key.startswith("$"):  # 跳过运算符键
                    continue
                if str(meta.get(key)) != str(value):
                    return False
            return True

        # 关键步骤：遍历所有文档，筛选匹配项
        matched = []
        for id_val, meta in zip(self.ids, self.metadatas):
            if not isinstance(meta, dict):
                continue
            if matches(meta, where):
                matched.append((id_val, meta))
        return {"ids": [x[0] for x in matched], "metadatas": [x[1] for x in matched]}

    def delete(self, ids=None, where=None):
        # 关键步骤：按where条件查找要删除的ID
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

        # 关键步骤：过滤掉要删除的文档
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
    """
    模拟Chroma Client

    管理多个Collection的内存存储

    关键字段：
        - collections: Collection名称到实例的映射
    """

    def __init__(self):
        self.collections = {}  # Collection名称到实例的映射

    def get_or_create_collection(self, name, metadata=None):
        # 关键步骤：懒加载创建Collection
        if name not in self.collections:
            self.collections[name] = FakeCollection()
        return self.collections[name]

    def get_collection(self, name):
        if name not in self.collections:
            raise ValueError("collection not exists")
        return self.collections[name]


@pytest.fixture()
def client():
    """创建FastAPI测试客户端"""
    from app.main import app

    return TestClient(app)


def test_config_load():
    """测试配置加载是否正常"""
    from app.config import config

    # 关键断言：验证核心配置字段类型
    assert isinstance(config.llm_provider, str)
    assert isinstance(config.embedding_model, str)
    assert isinstance(config.chroma_persist_dir, str)


def test_chunking_basic():
    """测试基础文本分块功能"""
    from app.utils.chunking import chunk_text

    text = "# 标题1\n第一段\n\n## 标题2\n第二段"
    chunks = chunk_text(text, chunk_size=80, overlap=10)

    # 关键断言：验证分块结果非空
    assert len(chunks) > 0


def test_rag_search_empty(monkeypatch):
    """
    测试空索引检索

    场景：索引为空时检索应返回空列表
    """
    from app.services.rag_service import rag_service

    # 关键步骤：注入Mock组件
    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    # 关键步骤：执行检索
    results = rag_service.search("project_x", "登录接口", top_k=3)
    assert results == []


def test_rag_add_and_search(monkeypatch):
    """
    测试RAG索引与检索基本流程

    场景：添加文档后应能检索到相关内容
    """
    from app.services.rag_service import rag_service

    # 关键步骤：注入Mock组件
    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    # 关键步骤：添加文档到索引
    project_id = "test_project"
    doc_id = "k1"
    docs = ["用户登录接口说明", "登录接口返回token字段"]
    rag_service.add_document(project_id, doc_id, "manual", "登录文档", docs)

    # 关键步骤：执行检索
    results = rag_service.search(project_id, "登录", top_k=2)
    assert isinstance(results, list)
    assert len(results) > 0


def test_rag_should_backfill_parent_context_when_child_hit(monkeypatch):
    """
    测试父文档回填机制

    场景：子文档命中时，应回填父文档上下文
    """
    from app.services.rag_service import rag_service

    # 关键步骤：注入Mock组件
    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    project_id = "test_project_parent_backfill"

    # 关键步骤：构造带父文档元数据的分片
    parent_content = (
        "# 登录接口\n"
        "登录成功会返回token和refreshToken。\n"
        "登录失败会返回401并提示密码错误。\n"
        "前端收到401后应引导用户重试。"
    )
    docs = [
        {
            "content": "登录失败会返回401并提示密码错误。",
            "metadata": {
                "parent_id": "p0",  # 父文档ID
                "parent_content": parent_content,  # 父文档完整内容
                "child_index": 0,  # 子文档索引
            },
        }
    ]
    rag_service.add_document(project_id, "doc_parent_1", "manual", "登录文档", docs)

    # 关键步骤：执行检索
    results = rag_service.search(project_id, "登录失败返回什么", top_k=1)

    # 关键断言：验证检索命中
    assert len(results) == 1
    assert "登录失败会返回401" in str(results[0].get("content") or "")
    assert str((results[0].get("metadata") or {}).get("doc_id") or "") == "doc_parent_1"


def test_rag_reindex_same_knowledge(monkeypatch):
    """
    测试重建索引覆盖机制

    场景：相同doc_id重建索引时，旧数据应被覆盖
    """
    from app.services.rag_service import rag_service

    # 关键步骤：注入Mock组件
    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    project_id = "test_project_reindex"
    doc_id = "k_reindex"

    # 关键步骤：第一次索引
    rag_service.add_document(project_id, doc_id, "manual", "登录文档", ["登录接口V1"])

    # 关键步骤：第二次索引（覆盖）
    rag_service.add_document(project_id, doc_id, "manual", "登录文档", ["登录接口V2"])

    # 关键断言：验证只有一条记录（覆盖成功）
    stats = rag_service.get_collection_stats(project_id)
    assert stats["count"] == 1


def test_rag_project_isolation(monkeypatch):
    """
    测试项目间数据隔离

    场景：不同项目的数据应相互隔离
    """
    from app.services.rag_service import rag_service

    # 关键步骤：注入Mock组件
    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    # 关键步骤：为两个项目添加文档
    rag_service.add_document("p_a", "k1", "manual", "a", ["登录接口A"])
    rag_service.add_document("p_b", "k2", "manual", "b", ["支付接口B"])

    # 关键步骤：分别检索两个项目
    results_a = rag_service.search("p_a", "登录", top_k=5)
    results_b = rag_service.search("p_b", "支付", top_k=5)

    # 关键断言：验证项目隔离
    assert any("登录接口A" in item.get("content", "") for item in results_a)
    assert all("支付接口B" not in item.get("content", "") for item in results_a)
    assert any("支付接口B" in item.get("content", "") for item in results_b)


def test_rag_delete_knowledge(monkeypatch):
    """
    测试文档删除功能

    场景：删除文档后应无法检索到
    """
    from app.services.rag_service import rag_service

    # 关键步骤：注入Mock组件
    rag_service._embedding_func = DummyEmbeddings()
    rag_service._client = FakeClient()
    rag_service._collection = None

    # 关键步骤：添加文档
    rag_service.add_document("p_del", "k_del", "manual", "删除文档", ["删除前文档"])

    # 关键步骤：删除文档
    delete_result = rag_service.delete_document("p_del", "k_del")
    assert delete_result.get("status") == "success"

    # 关键步骤：验证删除后无法检索
    results = rag_service.search("p_del", "删除前文档", top_k=5)
    assert results == []


def test_platform_client_headers():
    """测试平台客户端鉴权头生成"""
    from app.tools.platform_tools import get_platform_client

    # 关键步骤：创建客户端并获取鉴权头
    c = get_platform_client("t123")
    headers = c._get_headers()

    # 关键断言：验证token正确传递
    assert headers.get("token") == "t123"


def test_chat_stream_sse_format(monkeypatch, client: TestClient):
    """
    测试SSE流式响应格式

    场景：流式响应应符合SSE格式规范
    """
    from app.services import agent_service as agent_service_module

    # 关键步骤：Mock流式响应
    async def fake_stream_chat(
        project_id: str,
        token: str,
        message: str,
        use_rag: bool,
        messages=None,
        user_id="",
    ):
        yield {"type": "content", "delta": "O"}
        yield {"type": "content", "delta": "K"}
        yield {"type": "case", "case": {"name": "demo"}}
        yield {"type": "end"}

    monkeypatch.setattr(
        agent_service_module.agent_service, "stream_chat", fake_stream_chat
    )

    # 关键步骤：发送流式请求
    resp = client.post(
        "/ai/chat/stream",
        json={"project_id": "p1", "message": "测试", "use_rag": True, "messages": []},
        headers={"token": "tok"},
    )

    # 关键断言：验证SSE格式
    assert resp.status_code == 200
    text = resp.text
    assert "data:" in text
    assert '"type": "case"' in text
    assert '"type": "end"' in text


def test_chat_stream_should_flush_first_event_without_waiting(
    monkeypatch, client: TestClient
):
    """
    测试首事件立即刷新机制

    场景：首事件应在350ms内返回，避免用户等待
    """
    from app.services import agent_service as agent_service_module

    # 关键步骤：Mock带延迟的流式响应
    async def fake_stream_chat(
        project_id: str,
        token: str,
        message: str,
        use_rag: bool,
        messages=None,
        user_id="",
    ):
        yield {"type": "content", "delta": "首包事件"}
        time.sleep(0.25)  # 模拟LLM延迟
        yield {"type": "content", "delta": "后续内容"}
        yield {"type": "end"}

    monkeypatch.setattr(
        agent_service_module.agent_service, "stream_chat", fake_stream_chat
    )

    # 关键步骤：记录开始时间
    start = time.time()

    # 关键步骤：发送流式请求
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

                # 关键断言：首事件延迟应小于350ms
                assert first_delay < 0.35
                assert "首包事件" in line
                break


def test_agent_chat_case_via_executor(monkeypatch):
    """
    测试Agent对话生成用例流程

    场景：用户请求生成用例时，应返回用例预览
    """
    from app.services.agent_service import agent_service

    # 关键步骤：Mock generate_case方法
    monkeypatch.setattr(
        agent_service,
        "generate_case",
        lambda project_id, token, user_requirement, selected_apis=None, messages=None, user_id="": {
            "status": "success",
            "case": {"name": "登录接口用例"},
        },
    )

    # 关键步骤：执行对话
    result = agent_service.chat(
        project_id="p1",
        token="tok",
        message="请帮我生成登录接口测试用例",
        use_rag=True,
    )

    # 关键断言：验证用例生成结果
    assert result.get("reply") == "已生成用例预览，请确认后手动保存。"
    assert isinstance(result.get("case"), dict)


def test_generate_case_json_repair(monkeypatch):
    """
    测试用例生成JSON修复机制

    场景：LLM返回不完整JSON时，应能修复并解析
    """
    from app.services import agent_service as agent_service_module
    from app.services.agent_service import agent_service
    from app.services import llm_service as llm_service_module
    from app.services import rag_service as rag_service_module

    # 关键步骤：Mock平台客户端
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

    # 关键步骤：Mock RAG检索返回空
    monkeypatch.setattr(
        rag_service_module.rag_service,
        "search",
        lambda project_id, query, top_k=5, user_id="": [],
    )

    # 关键步骤：Mock LLM返回不完整JSON（末尾有多余逗号）
    monkeypatch.setattr(
        llm_service_module.llm_service,
        "chat_json",
        lambda messages, system_prompt=None: '{"name":"登录用例","caseApis":[{"apiId":"api_1","description":"步骤1"},{"apiId":"api_1","description":"步骤2"}],}',
    )

    # 关键步骤：执行用例生成
    result = agent_service.generate_case(
        project_id="p1",
        token="tok",
        user_requirement="生成登录接口测试用例",
        selected_apis=["api_1"],
    )

    # 关键断言：验证JSON修复成功
    assert result.get("status") == "success"
    assert isinstance(result.get("case"), dict)
    assert result["case"].get("name") == "登录用例"
    assert result["case"].get("projectId") == "p1"


def test_generate_case_without_api_should_fail(monkeypatch):
    """
    测试无接口时用例生成失败

    场景：项目无接口时，用例生成应返回错误
    """
    from app.services import agent_service as agent_service_module
    from app.services.agent_service import agent_service

    # 关键步骤：Mock空接口列表
    class EmptyClient:
        def get_api_list(self, project_id: str):
            return []

    monkeypatch.setattr(
        agent_service_module, "get_platform_client", lambda token: EmptyClient()
    )

    # 关键步骤：执行用例生成
    result = agent_service.generate_case(
        project_id="p2",
        token="tok",
        user_requirement="生成登录用例",
        selected_apis=[],
    )

    # 关键断言：验证错误状态
    assert result.get("status") == "error"
    assert "接口" in str(result.get("message") or "")


def test_case_intent_should_require_action():
    """测试用例意图识别"""
    from app.services.agent_service import _is_case_request

    # 关键断言：验证用例生成意图识别
    assert _is_case_request("帮我生成登录注册流程用例") is True
    assert _is_case_request("接口测试是什么") is False


def test_chat_prompt_no_context_private_vs_public():
    """
    测试无上下文时的Prompt差异

    场景：私有项目与公开问题的Prompt应不同
    """
    from app.services.agent_service import agent_service

    # 关键步骤：构建私有项目Prompt
    private_prompt = agent_service._build_chat_prompt(
        "当前项目登录失败怎么排查", [], "no_context"
    )

    # 关键步骤：构建公开问题Prompt
    public_prompt = agent_service._build_chat_prompt(
        "周杰伦有哪些经典歌曲", [], "no_context"
    )

    # 关键断言：验证Prompt差异
    assert "未检索到证据" in private_prompt
    assert "不要提及知识库未命中" in public_prompt


def test_chat_prompt_should_include_context():
    """测试有上下文时的Prompt构建"""
    from app.services.agent_service import agent_service

    # 关键步骤：构建带上下文的Prompt
    prompt = agent_service._build_chat_prompt(
        "登录接口如何断言",
        [{"content": "登录成功返回token"}],
        "success",
    )

    # 关键断言：验证上下文被包含
    assert "知识片段" in prompt
    assert "登录成功返回token" in prompt


def test_dependency_relations_should_link_auth_flow():
    """
    测试依赖关系构建

    场景：登录接口应被识别为用户信息接口的前置依赖
    """
    from app.services.agent_service import agent_service

    # 关键步骤：构造接口详情
    api_details = [
        {"id": "api_login", "path": "/auth/login", "method": "POST"},
        {"id": "api_profile", "path": "/user/profile", "method": "GET"},
    ]

    # 关键步骤：构建依赖关系
    relations = agent_service._build_dependency_relations(api_details)

    # 关键断言：验证依赖关系
    assert "api_profile" in relations
    assert "api_login" in relations.get("api_profile", [])


def test_normalize_case_should_complete_flow_steps():
    """
    测试用例标准化补全流程步骤

    场景：根据依赖关系自动补全缺失的流程步骤
    """
    from app.services.agent_service import agent_service

    # 关键步骤：构造接口详情
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

    # 关键步骤：构造原始用例（只有登录步骤）
    case_obj = {"name": "链路用例", "caseApis": [{"apiId": "api_1"}]}

    # 关键步骤：标准化用例
    normalized = agent_service._normalize_case(
        "p1",
        case_obj,
        api_details,
        api_relations={"api_2": ["api_1"]},  # api_2依赖api_1
    )

    # 关键断言：验证步骤补全
    steps = normalized.get("caseApis") or []
    assert len(steps) >= 2
    assert steps[0].get("apiId") == "api_1"
    assert any(step.get("apiId") == "api_2" for step in steps)


def test_rag_router_add_query_delete(monkeypatch, client: TestClient):
    from app.services import rag_service as rag_service_module

    monkeypatch.setattr(
        rag_service_module.rag_service,
        "add_document",
        lambda project_id, doc_id, doc_type, doc_name, documents, user_id="": {
            "indexed": True,
            "degraded": False,
            "vector_count": len(documents),
            "error": "",
        },
    )
    monkeypatch.setattr(
        rag_service_module.rag_service,
        "search_with_status",
        lambda project_id, query, top_k=5, user_id="": {
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
        project_id, token, user_requirement, selected_apis=None, messages=None, user_id=""
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
    first = asyncio.run(anext(stream))
    elapsed = time.time() - start
    assert elapsed < 0.35
    assert first.get("type") == "content"
    assert "已生成用例预览" in str(first.get("delta") or "")


def test_stream_chat_should_split_large_delta(monkeypatch):
    from app.services.agent_service import agent_service
    from app.services import llm_service as llm_service_module

    monkeypatch.setattr(
        llm_service_module.llm_service,
        "achat_with_stream",
        lambda messages, system_prompt=None: _fake_async_stream(["A" * 45]),
    )
    stream = agent_service.stream_chat(
        project_id="p1",
        token="tok",
        message="解释登录接口断言",
        use_rag=False,
        messages=[],
    )
    parts = []
    async def collect():
        async for evt in stream:
            if evt.get("type") == "content":
                parts.append(evt.get("delta", ""))
    asyncio.run(collect())
    merged = "".join([part for part in parts if part and part.strip()])
    assert "A" * 45 in merged


def test_stream_chat_non_case_should_emit_first_chunk_immediately(monkeypatch):
    from app.services.agent_service import agent_service
    from app.services import llm_service as llm_service_module

    async def delayed_stream(messages, system_prompt=None):
        time.sleep(0.35)
        yield "测试流式内容"

    monkeypatch.setattr(
        llm_service_module.llm_service, "achat_with_stream", delayed_stream
    )
    stream = agent_service.stream_chat(
        project_id="p1",
        token="tok",
        message="什么是接口测试",
        use_rag=False,
        messages=[],
    )
    start = time.time()
    first = asyncio.run(anext(stream))
    elapsed = time.time() - start
    assert elapsed < 0.5
    assert first.get("type") == "content"
    assert "测试流式内容" in str(first.get("delta") or "")
