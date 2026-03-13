"""
文档分块工具
支持多种分块策略
"""

from typing import List
import re


class TextChunker:
    """
    文本分块器。
    职责：将长文按标题/段落/句子切分为适合RAG索引的片段。
    """

    @staticmethod
    def chunk_markdown_by_heading(text: str, chunk_size: int = 1200) -> List[str]:
        """
        按 Markdown 标题优先切片。
        @param text: 原始文档
        @param chunk_size: 单片最大字符数
        @return: 切片结果
        """
        if not text:
            return []
        lines = text.splitlines()
        sections: List[str] = []
        current: List[str] = []
        for line in lines:
            if re.match(r"^\s{0,3}#{1,6}\s+", line) and current:  # 新标题触发新分段
                sections.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current).strip())
        normalized_sections: List[str] = []
        for section in sections:
            if not section:
                continue
            if len(section) <= chunk_size:  # 小段直接保留，减少语义断裂
                normalized_sections.append(section)
                continue
            paragraphs = [item for item in section.split("\n\n") if item.strip()]
            if not paragraphs:
                normalized_sections.append(section)
                continue
            block = ""
            for paragraph in paragraphs:
                candidate = paragraph.strip()
                if not candidate:
                    continue
                if block and len(block) + len(candidate) + 2 > chunk_size:
                    normalized_sections.append(block.strip())
                    block = candidate
                else:
                    block = f"{block}\n\n{candidate}".strip() if block else candidate
            if block:
                normalized_sections.append(block.strip())
        return normalized_sections

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
    
    实现策略：
        1. 优先使用标题分块（保持语义完整）
        2. 无标题时回退段落分块
    
    Args:
        text: 原始文本
        chunk_size: 块大小
        overlap: 重叠大小

    Returns:
        分块后的文本列表
    """
    chunks = TextChunker.chunk_markdown_by_heading(
        text, max(chunk_size, 800)
    )
    if chunks:
        return chunks
    return TextChunker.chunk_by_paragraph(
        text, chunk_size, overlap
    )


if __name__ == "__main__":
    """
    文本分块工具调试代码
    
    调试说明：
        1. 测试按标题分块
        2. 测试按段落分块
        3. 测试按句子分块
        4. 测试固定大小分块
    """
    print("=" * 60)
    print("文本分块工具调试")
    print("=" * 60)
    
    test_text = """# 登录接口文档

## 接口说明
这是一个用户登录接口，用于验证用户身份。

## 请求参数
- username: 用户名
- password: 密码

## 响应示例
```json
{"code": 200, "message": "success"}
```

## 注意事项
1. 用户名区分大小写
2. 密码需要加密传输
3. 登录失败返回错误码401
"""
    
    # 测试1：按标题分块
    print("\n1. 按标题分块测试:")
    chunks = TextChunker.chunk_markdown_by_heading(test_text, chunk_size=500)
    print(f"   分块数量: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"   - 块{i+1}: {chunk[:50]}...")
    
    # 测试2：按段落分块
    print("\n2. 按段落分块测试:")
    chunks = TextChunker.chunk_by_paragraph(test_text, chunk_size=200)
    print(f"   分块数量: {len(chunks)}")
    
    # 测试3：按句子分块
    print("\n3. 按句子分块测试:")
    chunks = TextChunker.chunk_by_sentence(test_text, chunk_size=100)
    print(f"   分块数量: {len(chunks)}")
    
    # 测试4：固定大小分块
    print("\n4. 固定大小分块测试:")
    chunks = TextChunker.chunk_fixed(test_text, chunk_size=100)
    print(f"   分块数量: {len(chunks)}")
    
    # 测试5：主函数
    print("\n5. 主函数测试:")
    chunks = chunk_text(test_text)
    print(f"   分块数量: {len(chunks)}")
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
