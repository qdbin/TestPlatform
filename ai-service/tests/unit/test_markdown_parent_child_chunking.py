from pathlib import Path

from app.utils.markdown_parent_child_chunking import markdown_parent_child_chunker


def test_markdown_parent_child_chunking_should_keep_parent_child_strategy():
    content = "# 登录接口\n\n简介\n\n## 成功\n返回token\n\n### 示例\nok\n\n## 失败\n返回401"
    chunks = markdown_parent_child_chunker.split(content)
    assert chunks
    parents = [
        item for item in chunks if item.get("metadata", {}).get("chunk_role") == "parent"
    ]
    children = [
        item for item in chunks if item.get("metadata", {}).get("chunk_role") == "child"
    ]
    assert parents
    assert children
    assert parents[0]["content"].startswith("# 登录接口")
    assert any("## 成功" in item["content"] for item in children)
    assert any("## 示例" in item["content"] for item in children)
    assert all(item["metadata"].get("parent_chunk_id") for item in children)
    assert all("parent_id" in item["metadata"] for item in children)
    assert all("parent_content" in item["metadata"] for item in children)


def test_markdown_parent_child_chunking_should_work_for_real_files():
    base = Path(
        r"c:\Users\hanbin\main\Core\DevHome\m2.5\TestPlatform\platform-backend\assets\backend相关说明(按需了解即可)"
    )
    targets = [
        base / "接口说明.md",
        base / "系统功能结构图.md",
        base / "PRD.md",
    ]
    for file_path in targets:
        content = file_path.read_text(encoding="utf-8")
        chunks = markdown_parent_child_chunker.split(content)
        assert chunks, str(file_path)
        assert all("content" in item and "metadata" in item for item in chunks)
        assert any(
            item.get("metadata", {}).get("chunk_role") == "parent" for item in chunks
        )
        assert any(
            item.get("metadata", {}).get("chunk_role") == "child" for item in chunks
        )
        assert all(
            item.get("metadata", {}).get("level") in (1, 2) for item in chunks
        )
