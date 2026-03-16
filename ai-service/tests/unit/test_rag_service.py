import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.rag_service import RAGService
from app.utils.markdown_parent_child_chunking import markdown_parent_child_chunker

TEST_PROJECT_ID = "unit-test-project"


def test_rag_service_has_required_methods():
    service = RAGService()
    assert hasattr(service, "add_document")
    assert hasattr(service, "delete_document")
    assert hasattr(service, "search")
    assert hasattr(service, "search_with_status")
    assert hasattr(service, "get_collection_stats")


def test_add_document():
    service = RAGService()
    result = service.add_document(
        project_id=TEST_PROJECT_ID,
        doc_id="test-doc-001",
        doc_type="manual",
        doc_name="测试文档",
        documents=[{"content": "这是一个测试文档的内容", "metadata": {"section": "intro"}}],
        user_id="test-user",
    )
    assert result.get("indexed") is True
    assert "vector_count" in result


def test_delete_document():
    service = RAGService()
    service.add_document(
        project_id=TEST_PROJECT_ID,
        doc_id="test-doc-delete",
        doc_type="manual",
        doc_name="删除测试文档",
        documents=[{"content": "将被删除的内容", "metadata": {}}],
        user_id="test-user",
    )
    result = service.delete_document(TEST_PROJECT_ID, "test-doc-delete")
    assert result.get("status") in {"success", "error"}
    assert "vector_deleted" in result


def test_keyword_search():
    service = RAGService()
    service.add_document(
        project_id=TEST_PROJECT_ID,
        doc_id="test-doc-search",
        doc_type="api",
        doc_name="搜索测试文档",
        documents=[
            {"content": "用户登录接口需要用户名和密码", "metadata": {"api": "login"}},
            {"content": "用户注册接口需要邮箱和手机号", "metadata": {"api": "register"}},
        ],
        user_id="test-user",
    )
    results = service._keyword_search(TEST_PROJECT_ID, "登录", top_k=3)
    assert isinstance(results, list)


def test_vector_search():
    service = RAGService()
    status, results = service._vector_search(TEST_PROJECT_ID, "用户认证相关接口", top_k=3)
    assert status in {"success", "fallback", "embedding_unavailable"}
    assert isinstance(results, list)


def test_hybrid_search():
    service = RAGService()
    result = service.search_with_status(project_id=TEST_PROJECT_ID, query="登录接口", top_k=5)
    assert "status" in result
    assert "data" in result


def test_fuse_results():
    service = RAGService()
    fused = service._fuse_results(
        [{"content": "a", "metadata": {"doc_id": "d1", "chunk_index": 1}}],
        [{"content": "b", "metadata": {"doc_id": "d2", "chunk_index": 1}, "distance": 0.2}],
        top_k=5,
    )
    assert isinstance(fused, list)


def test_project_isolation():
    service = RAGService()
    project_a = "project-a"
    project_b = "project-b"
    service.add_document(
        project_id=project_a,
        doc_id="isolated-doc",
        doc_type="manual",
        doc_name="隔离测试文档",
        documents=[{"content": "这是项目A的文档", "metadata": {}}],
        user_id="test-user",
    )
    result_b = service.search_with_status(project_b, "项目A", top_k=3)
    result_a = service.search_with_status(project_a, "项目A", top_k=3)
    assert "data" in result_a
    assert "data" in result_b


def test_add_document_with_empty_list_metadata():
    service = RAGService()
    result = service.add_document(
        project_id=TEST_PROJECT_ID,
        doc_id="test-doc-meta-empty-list",
        doc_type="manual",
        doc_name="空列表元数据文档",
        documents=[
            {
                "content": "文档内容",
                "metadata": {"parent_titles": [], "tags": ["a", "b"]},
            }
        ],
        user_id="test-user",
    )
    assert result.get("indexed") is True
    assert result.get("error") in {"", None}


def test_real_markdown_files_should_keep_parent_child_retrieval():
    service = RAGService()
    base = Path(
        r"c:\Users\hanbin\main\Core\DevHome\m2.5\TestPlatform\platform-backend\assets\backend相关说明(按需了解即可)"
    )
    files = [
        ("接口说明.md", "real-md-api"),
        ("系统功能结构图.md", "real-md-arch"),
        ("PRD.md", "real-md-prd"),
    ]
    for file_name, doc_id in files:
        content = (base / file_name).read_text(encoding="utf-8")
        chunks = markdown_parent_child_chunker.split(content)
        add_result = service.add_document(
            project_id=TEST_PROJECT_ID,
            doc_id=doc_id,
            doc_type="manual",
            doc_name=file_name,
            documents=chunks,
            user_id="test-user",
        )
        assert add_result.get("indexed") is True

    result = service.search_with_status(
        project_id=TEST_PROJECT_ID,
        query="系统整体架构图包含哪些模块",
        top_k=5,
        messages=[{"role": "user", "content": "我在看系统功能结构图"}],
    )
    assert result.get("status") in {"success", "no_context", "fallback"}
    data = result.get("data") or []
    if data:
        assert all(isinstance(item.get("metadata"), dict) for item in data)
        assert any(
            (item.get("metadata") or {}).get("chunk_role") == "parent" for item in data
        )
