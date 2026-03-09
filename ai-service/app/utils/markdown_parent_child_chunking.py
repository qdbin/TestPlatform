"""
Markdown Parent-Child 切片模块。
"""

from __future__ import annotations

from typing import List, Dict, Any

from langchain.text_splitter import MarkdownTextSplitter, RecursiveCharacterTextSplitter


class MarkdownParentChildChunker:
    def __init__(self, parent_size: int = 1200, child_size: int = 400, overlap: int = 60):
        self.parent_splitter = MarkdownTextSplitter(chunk_size=parent_size, chunk_overlap=overlap)
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_size, chunk_overlap=max(20, overlap // 2)
        )

    def split(self, content: str) -> List[Dict[str, Any]]:
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
