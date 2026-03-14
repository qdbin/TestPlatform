"""
文档分块工具模块

职责：
    1. 提供多种文本分块策略（标题分块、段落分块、句子分块、固定大小分块）
    2. 支持 Markdown 文档语义感知分块
    3. 为 RAG 系统提供合适大小的文本片段

核心类：
    - TextChunker: 文本分块器

主要方法：
    - chunk_markdown_by_heading(): 按Markdown标题切片
    - chunk_by_paragraph(): 按段落分块
    - chunk_by_sentence(): 按句子分块
    - chunk_fixed(): 固定大小分块
    - chunk_text(): 智能分块入口（自动选择最佳策略）
"""

from typing import List
import re


class TextChunker:
    """
    文本分块器。

    职责：
        - 将长文本按标题/段落/句子切分为适合RAG索引的片段
        - 优先保持语义完整性
        - 支持重叠区域以保持上下文连贯性

    分块策略优先级：
        1. 标题分块（保持语义完整）
        2. 段落分块（自然断点）
        3. 句子分块（细粒度）
        4. 固定分块（兜底策略）
    """

    @staticmethod
    def chunk_markdown_by_heading(text: str, chunk_size: int = 1200) -> List[str]:
        """
        按 Markdown 标题优先切片

        实现步骤：
            1. 按行分割文本
            2. 识别 Markdown 标题（# ~ ######）
            3. 遇到新标题时，将之前内容作为一个分段
            4. 对每个分段，如果超过 chunk_size，进一步按段落分割

        @param text: 原始Markdown文档
        @param chunk_size: 单片最大字符数（默认1200）
        @return: 分块后的文本列表

        示例：
            输入：# 标题1\n内容1\n\n# 标题2\n内容2
            输出：["# 标题1\n内容1", "# 标题2\n内容2"]
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

        实现步骤：
            1. 按双换行符分割段落
            2. 遍历段落，累加到当前块
            3. 当前块超过 chunk_size 时，保存当前块并开启新块
            4. 新块包含 overlap 长度的前一块内容（保持上下文连贯）

        @param text: 原始文本
        @param chunk_size: 块大小（字符数），默认500
        @param overlap: 重叠字符数，默认50（保持上下文连贯性）
        @return: 分块后的文本列表

        示例：
            text = "段落1内容...\n\n段落2内容...\n\n段落3内容..."
            chunk_size = 20, overlap = 5
            输出：["段落1内容...段落2", "段落2内容...段落3", "段落3内容..."]
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

        实现步骤：
            1. 按标点符号（。！？.!?）分割句子
            2. 重新组合句子和标点符号
            3. 累加句子到当前块，超过 chunk_size 时分割
            4. 新块包含 overlap 长度的前一块内容

        @param text: 原始文本
        @param chunk_size: 块大小（字符数），默认300
        @param overlap: 重叠字符数，默认20
        @return: 分块后的文本列表
        """
        if not text:
            return []

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

        实现步骤：
            1. 从文本开头开始，每次取 chunk_size 大小的片段
            2. 下一个片段起点 = 上一个片段终点 - overlap
            3. 重复直到文本结束

        @param text: 原始文本
        @param chunk_size: 块大小（字符数），默认500
        @param overlap: 重叠字符数，默认50
        @return: 分块后的文本列表

        示例：
            text = "abcdefghij", chunk_size = 3, overlap = 1
            输出：["abc", "cde", "efg", "ghi", "ij"]
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
    文本分块主函数（智能策略选择）

    实现策略：
        1. 优先使用标题分块（保持语义完整）
        2. 无标题时回退段落分块

    @param text: 原始文本
    @param chunk_size: 块大小（默认500）
    @param overlap: 重叠大小（默认50）
    @return: 分块后的文本列表
    """
    chunks = TextChunker.chunk_markdown_by_heading(text, max(chunk_size, 800))
    if chunks:
        return chunks
    return TextChunker.chunk_by_paragraph(text, chunk_size, overlap)


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
