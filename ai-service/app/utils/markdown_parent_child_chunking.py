"""
Markdown文档分块模块

职责：
    1. 实现动态父子层级分块
    2. 自动检测文档标题层级并确定父子关系
    3. 适配项目RAG服务的父子召回策略

层级判断规则：
    | 检测到的标题层级 | 父子设置 |
    |----------------|---------|
    | 2级（H1+H2） | H2作为父块 |
    | 3级（H1+H2+H3） | H2作为父块，H3作为子块 |
    | 4级（H1+H2+H3+H4） | H2作为父块，H3作为子块（含H4） |

元数据字段：
    - chunk_role: 块角色（parent=父块，child=子块）
    - parent_chunk_id: 父块ID（子块专用）
    - chunk_id: 块唯一ID
    - H1/H2/H3/H4: 对应层级标题内容

使用示例：
    from app.utils.markdown_parent_child_chunking import markdown_parent_child_chunker

    chunks = markdown_parent_child_chunker.split(markdown_text)
    for chunk in chunks:
        print(f"角色: {chunk.metadata['chunk_role']}")
        print(f"标题: {chunk.metadata.get('H2') or chunk.metadata.get('H3')}")
"""

import hashlib
from typing import List, Optional, Set
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter


class MarkdownParentChunker:
    """
    Markdown动态父子分块器

    核心特性：
        - 自动检测文档标题层级
        - 动态确定父子关系
        - 支持H1-H4任意组合

    层级判断：
        - 2级标题：H1+H2 → H2为父块
        - 3级标题：H1+H2+H3 → H2为父，H3为子
        - 4级标题：H1+H2+H3+H4 → H2为父，H3为子（含H4）
    """

    def __init__(
        self,
        headers_to_split_on: Optional[List[tuple]] = None,
    ):
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "H1"),
            ("##", "H2"),
            ("###", "H3"),
            ("####", "H4"),
        ]

        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False,
        )

    def _detect_header_levels(self, raw_docs: List[Document]) -> Set[str]:
        """检测文档中实际存在的标题层级"""
        levels = set()
        for doc in raw_docs:
            metadata = doc.metadata
            for level in ["H1", "H2", "H3", "H4"]:
                if metadata.get(level):
                    levels.add(level)
        return levels

    def _determine_parent_child_levels(self, levels: Set[str]) -> tuple:
        """
        根据检测到的层级确定父子关系

        @param levels: 检测到的标题层级集合
        @return: (父层级, 子层级)
        """
        sorted_levels = sorted(levels, key=lambda x: int(x[1:]))

        if len(sorted_levels) >= 3:
            return ("H2", "H3")
        elif "H2" in sorted_levels:
            return ("H2", None)
        elif "H1" in sorted_levels:
            return ("H1", None)
        else:
            return (None, None)

    def split(self, text: str) -> List[Document]:
        """
        分割Markdown文档

        实现逻辑：
            1. 使用LangChain解析Markdown
            2. 检测实际标题层级
            3. 动态确定父子关系
            4. 构建块结构

        @param text: Markdown原始文本
        @return: Document列表（父块+子块）
        """
        if not text or not text.strip():
            return []

        raw_docs = self.splitter.split_text(text)

        levels = self._detect_header_levels(raw_docs)
        parent_level, child_level = self._determine_parent_child_levels(levels)

        chunks: List[Document] = []
        current_h1 = ""
        current_h2 = ""
        current_h3 = ""
        current_parent_content_parts: List[str] = []
        parent_chunk_id = ""

        def _make_chunk_id(*args) -> str:
            seed = "|".join(str(a)[:50] for a in args).encode("utf-8", errors="ignore")
            return hashlib.md5(seed).hexdigest()[:16]

        def _flush_parent():
            """输出当前父块"""
            nonlocal chunks, current_parent_content_parts, parent_chunk_id
            if not parent_chunk_id:
                return

            parent_content = "\n\n".join(current_parent_content_parts).strip()
            if parent_content:
                chunks.append(
                    Document(
                        page_content=parent_content,
                        metadata={
                            "chunk_role": "parent",
                            "parent_chunk_id": "",
                            "chunk_id": parent_chunk_id,
                            "H1": current_h1,
                            "H2": current_h2,
                            "H3": "",
                        },
                    )
                )

            parent_chunk_id = ""
            current_parent_content_parts = []

        for doc in raw_docs:
            metadata = doc.metadata.copy()
            content = doc.page_content.strip()

            h1 = metadata.get("H1", "")
            h2 = metadata.get("H2", "")
            h3 = metadata.get("H3", "")
            h4 = metadata.get("H4", "")

            if h1:
                _flush_parent()
                current_h1 = h1
                current_h2 = ""
                current_h3 = ""

            if parent_level == "H2":
                if h2:
                    _flush_parent()
                    current_h2 = h2
                    parent_chunk_id = _make_chunk_id(current_h1, h2, "", content)
                    current_parent_content_parts = [content]

                elif h3 and child_level == "H3":
                    if not current_h2:
                        current_h2 = "全文"
                        parent_chunk_id = _make_chunk_id(
                            current_h1, "全文", "", content
                        )

                    child_content = f"### {h3}\n\n{content}" if h4 else content
                    child_id = _make_chunk_id(current_h1, current_h2, h3, content)

                    chunks.append(
                        Document(
                            page_content=content,
                            metadata={
                                "chunk_role": "child",
                                "parent_chunk_id": parent_chunk_id,
                                "chunk_id": child_id,
                                "H1": current_h1,
                                "H2": current_h2,
                                "H3": h3,
                            },
                        )
                    )
                    current_parent_content_parts.append(child_content)

                elif content:
                    if current_h2:
                        current_parent_content_parts.append(content)
                    elif current_h1:
                        current_parent_content_parts.append(content)
                    else:
                        current_h1 = "未命名文档"
                        current_parent_content_parts.append(content)

            elif parent_level == "H1":
                if h1:
                    if current_h1 and current_parent_content_parts:
                        _flush_parent()
                    if not current_h1:
                        current_h1 = h1
                        parent_chunk_id = _make_chunk_id(h1, "", "", content)
                        current_parent_content_parts = [content]
                    else:
                        current_parent_content_parts.append(content)
                elif content:
                    current_parent_content_parts.append(content)

            else:
                if content:
                    current_h1 = current_h1 or "未命名文档"
                    if not parent_chunk_id:
                        parent_chunk_id = _make_chunk_id(current_h1, "", "", content)
                    current_parent_content_parts.append(content)

        _flush_parent()

        if not chunks and current_parent_content_parts:
            parent_content = "\n\n".join(current_parent_content_parts).strip()
            if parent_content:
                chunks.append(
                    Document(
                        page_content=parent_content,
                        metadata={
                            "chunk_role": "parent",
                            "parent_chunk_id": "",
                            "chunk_id": _make_chunk_id(
                                current_h1, "", "", parent_content
                            ),
                            "H1": current_h1,
                            "H2": "",
                            "H3": "",
                        },
                    )
                )

        return chunks


markdown_chunker = MarkdownParentChunker()
markdown_parent_child_chunker = markdown_chunker
