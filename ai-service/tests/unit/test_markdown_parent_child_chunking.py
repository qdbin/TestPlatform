from app.utils.markdown_parent_child_chunking import markdown_parent_child_chunker


def test_markdown_parent_child_chunking_should_keep_parent_metadata():
    content = "# 登录接口\n\n## 成功\n返回token\n\n## 失败\n返回401"
    chunks = markdown_parent_child_chunker.split(content)
    assert chunks
    first = chunks[0]
    assert "content" in first
    assert "metadata" in first
    assert "parent_id" in first["metadata"]
    assert "parent_content" in first["metadata"]
