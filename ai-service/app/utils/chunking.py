"""
文档分块工具
支持多种分块策略
"""

from typing import List


class TextChunker:
    """文本分块器"""

    @staticmethod
    def chunk_by_paragraph(
        text: str, chunk_size: int = 500, overlap: int = 50
    ) -> List[str]:
        """
        按段落分块

        Args:
            text: 原始文本
            chunk_size: 块大小（字符数）
            overlap: 重叠字符数

        Returns:
            分块后的文本列表
        """
        if not text:
            return []

        # 按段落分割
        paragraphs = text.split("\n\n")

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 如果当前块加上新段落超过大小，先保存当前块
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # 保留overlap长度的内容
                current_chunk = (
                    current_chunk[-overlap:] + "\n\n" + para if overlap > 0 else para
                )
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # 添加最后一个块
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    @staticmethod
    def chunk_by_sentence(
        text: str, chunk_size: int = 300, overlap: int = 20
    ) -> List[str]:
        """
        按句子分块

        Args:
            text: 原始文本
            chunk_size: 块大小（字符数）
            overlap: 重叠句子数

        Returns:
            分块后的文本列表
        """
        if not text:
            return []

        # 简单按句号、问号、感叹号分割
        import re

        sentences = re.split(r"([。！？.!?])", text)

        # 重新组合句子和标点
        recombined_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                recombined_sentences.append(sentences[i] + sentences[i + 1])
            else:
                recombined_sentences.append(sentences[i])

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = (
                    sentence[-overlap:] + sentence if overlap > 0 else sentence
                )
            else:
                current_chunk += sentence

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    @staticmethod
    def chunk_fixed(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        固定大小分块

        Args:
            text: 原始文本
            chunk_size: 块大小
            overlap: 重叠大小

        Returns:
            分块后的文本列表
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap

        return chunks


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    文本分块主函数

    Args:
        text: 原始文本
        chunk_size: 块大小
        overlap: 重叠大小

    Returns:
        分块后的文本列表
    """
    return TextChunker.chunk_by_paragraph(text, chunk_size, overlap)
