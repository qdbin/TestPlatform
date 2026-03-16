"""
文本分块模块

职责：
    1. 使用LangChain的RecursiveCharacterTextSplitter进行通用文本分块
    2. 支持多种分隔符配置
    3. 支持重叠区域保持上下文连贯性

分块策略：
    1. 递归分块：按分隔符层级递归分割
    2. 重叠分块：相邻块有重叠，保持上下文
    3. 语义优先：优先按段落/句子分割，保持语义完整

使用示例：
    from app.utils.chunking import text_chunker

    chunks = text_chunker.split(long_text)
    for chunk in chunks:
        print(f"长度: {len(chunk)}, 内容: {chunk[:50]}...")
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """
    通用文本分块器

    职责：
        - 使用RecursiveCharacterTextSplitter进行智能分块
        - 保持语义完整性，优先按段落分割
        - 支持重叠区域配置

    参数说明：
        - chunk_size: 每个块的最大字符数（默认500）
        - chunk_overlap: 相邻块重叠字符数（默认50）
        - separators: 分隔符优先级列表（默认按段落、句子、单词）
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "；", " ", ""]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            keep_separator=True,
        )

    def split(self, text: str) -> List[str]:
        """
        分割文本为字符串列表

        实现步骤：
            1. 检查文本是否为空
            2. 使用RecursiveCharacterTextSplitter分割
            3. 返回字符串列表

        @param text: 输入文本
        @return: 文本块列表（字符串）
        """
        if not text:
            return []

        return self.splitter.split_text(text)

    def split_documents(self, texts: List[str]) -> List[Document]:
        """
        分割多个文本为Document列表

        适用于已按段落/文档分隔的批量文本处理

        @param texts: 文本列表
        @return: Document列表
        """
        if not texts:
            return []

        docs = [Document(page_content=text) for text in texts]
        return self.splitter.split_documents(docs)

    def split_with_metadata(
        self, text: str, source: str = "", metadata: dict = None
    ) -> List[Document]:
        """
        分割文本并添加元数据

        方便追踪每个块的内容来源

        @param text: 输入文本
        @param source: 来源标识
        @param metadata: 其他元数据
        @return: 包含元数据的Document列表
        """
        if not text:
            return []

        docs = self.splitter.split_text(text)
        base_metadata = metadata or {}
        if source:
            base_metadata["source"] = source

        return [
            Document(page_content=doc, metadata=base_metadata.copy()) for doc in docs
        ]


text_chunker = TextChunker()


if __name__ == "__main__":
    print("=" * 60)
    print("文本分块器调试")
    print("=" * 60)

    test_text = """
# 登录接口文档

## 常规说明
### 接口说明
用户登录接口，用于用户身份验证。

### 请求参数
- username: 用户名，必填，字符串类型
- password: 密码，必填，字符串类型

### 响应参数
- code: 状态码，200表示成功
- message: 提示信息
- data: 用户数据，包含token等信息

### 错误码
- 400: 参数错误
- 401: 认证失败
- 500: 服务器错误

## 接口示例

### 请求示例
```json
{
    "username": "user123",
    "password": "pass456"
}
```

### 响应示例
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "token": "abc123xyz",
        "user_id": 12345
    }
}
```
"""

    print("\n1. 通用文本分块:")
    chunker = TextChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.split(test_text)
    print(f"   原文长度: {len(test_text)} 字符")
    print(f"   分块数量: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"   块{i}长度: {len(chunk)} 字符")
        print(f"   内容预览:")
        print(chunk)
        print("\n" + "=" * 60)

    print("\n2. Markdown分块:")
    from markdown_parent_child_chunking import markdown_parent_child_chunker

    docs = markdown_parent_child_chunker.split(test_text)
    print(f"   分块数量: {len(docs)}")
    for i, doc in enumerate(docs, 1):
        print(f"   块{i} H1: {doc.metadata.get('H1', 'N/A')}")
        print(f"   块{i} H2: {doc.metadata.get('H2', 'N/A')}")
        print(f"   内容: ")
        print(doc.page_content)
        print("\n" + "=" * 60)

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
