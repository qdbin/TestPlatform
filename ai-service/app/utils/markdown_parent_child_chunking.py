"""
Markdown Parent-Child 切片模块

核心功能：
    - Parent块：保留完整标题语义
    - Child块：细粒度检索单元
    - 层级关系：通过 metadata.parent_id 关联

使用示例：
    chunker = MarkdownParentChildChunker(parent_size=1200, child_size=400)
    chunks = chunker.split(markdown_text)
"""

from __future__ import annotations

from typing import List, Dict, Any

from langchain.text_splitter import MarkdownTextSplitter, RecursiveCharacterTextSplitter


class MarkdownParentChildChunker:
    """
    Markdown父子切片器
    
    职责：
        - 按Markdown标题层级切分Parent块（保留完整语义）
        - 在Parent块内进一步细分子块（适合精确检索）
        - 通过metadata维护父子关系
    """

    def __init__(self, parent_size: int = 1200, child_size: int = 400, overlap: int = 60):
        self.parent_splitter = MarkdownTextSplitter(chunk_size=parent_size, chunk_overlap=overlap)
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_size, chunk_overlap=max(20, overlap // 2)
        )

    def split(self, content: str) -> List[Dict[str, Any]]:
        """
        执行父子切片
        
        实现步骤：
            1. 使用MarkdownTextSplitter按标题切分为Parent块
            2. 对每个Parent块使用RecursiveCharacterTextSplitter切分为Child块
            3. 返回带父子关系元数据的块列表
        
        @param content: Markdown格式文档内容
        @return: [{"content": "...", "metadata": {...}}, ...]
        
        返回格式示例：
            {
                "content": "子块内容",
                "metadata": {
                    "parent_id": "p0",
                    "parent_index": 0,
                    "child_index": 0,
                    "parent_content": "父块内容摘要"
                }
            }
        """
        text = str(content or "").strip()
        if not text:
            return []
        parent_docs = self.parent_splitter.create_documents([text])
        chunks: List[Dict[str, Any]] = []
        for parent_idx, parent_doc in enumerate(parent_docs):
            parent_text = str(parent_doc.page_content or "").strip()
            if not parent_text:
                continue
            child_docs = self.child_splitter.create_documents([parent_text])
            for child_idx, child_doc in enumerate(child_docs):
                child_text = str(child_doc.page_content or "").strip()
                if not child_text:
                    continue
                chunks.append(
                    {
                        "content": child_text,
                        "metadata": {
                            "parent_id": f"p{parent_idx}",
                            "parent_index": parent_idx,
                            "child_index": child_idx,
                            "parent_content": parent_text[:2000],
                        },
                    }
                )
        return chunks


markdown_parent_child_chunker = MarkdownParentChildChunker()


if __name__ == "__main__":
    """
    Markdown父子切片器调试代码
    
    调试说明：
        1. 测试父子切片
        2. 验证层级关系
    """
    print("=" * 60)
    print("Markdown父子切片器调试")
    print("=" * 60)
    
    test_markdown = """# 登录接口

## 接口说明
用户登录接口，验证用户名密码。

## 请求参数
- username: 用户名
- password: 密码

## 响应示例
```json
{"code": 0, "message": "success"}
```

## 错误码
- 401: 用户名或密码错误
- 500: 服务器异常
"""
    
    # 测试切片
    print("\n1. 父子切片测试:")
    chunks = markdown_parent_child_chunker.split(test_markdown)
    print(f"   切片数量: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):
        print(f"   - 块{i+1}: {chunk['content'][:50]}...")
        print(f"     parent_id: {chunk['metadata'].get('parent_id')}")
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
