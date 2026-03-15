"""
文本分块模块

职责：
    1. 将长文本分割成适当大小的块
    2. 支持多种分块策略
    3. 保持文本语义完整性

分块策略：
    1. 固定长度分块：按字符数分割
    2. 语义分块：按段落/句子分割
    3. 重叠分块：相邻块有重叠，保持上下文

使用示例：
    chunker = TextChunker(chunk_size=500, overlap=50)
    chunks = chunker.split(long_text)
"""

from typing import List
import re


class TextChunker:
    """
    文本分块器

    职责：
        - 将长文本分割成适当大小的块
        - 支持多种分块策略
        - 保持语义完整性

    参数说明：
        - chunk_size: 每个块的最大字符数
        - overlap: 相邻块之间的重叠字符数
        - separators: 优先分割符列表
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        separators: List[str] = None,
    ):
        """
        初始化文本分块器

        @param chunk_size: 块大小（字符数）
        @param overlap: 重叠大小（字符数）
        @param separators: 优先分割符列表
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = separators or ["\n\n", "\n", "。", "；", " "]

    def split(self, text: str) -> List[str]:
        """
        分割文本

        实现步骤：
            1. 尝试按分隔符分割
            2. 如果块太大，递归分割
            3. 添加重叠内容

        @param text: 输入文本
        @return: 文本块列表
        """
        if not text:
            return []

        # 如果文本长度小于块大小，直接返回
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        current_chunk = ""

        # 按分隔符分割
        parts = self._split_by_separators(text)

        for part in parts:
            # 如果当前块加上新部分不超过限制，直接添加
            if len(current_chunk) + len(part) <= self.chunk_size:
                current_chunk += part
            else:
                # 保存当前块
                if current_chunk:
                    chunks.append(current_chunk)

                # 如果单个部分超过块大小，需要进一步分割
                if len(part) > self.chunk_size:
                    sub_chunks = self._split_large_part(part)
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1]
                else:
                    current_chunk = part

        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)

        # 添加重叠
        return self._add_overlap(chunks)

    def _split_by_separators(self, text: str) -> List[str]:
        """按分隔符分割文本"""
        parts = [text]

        for separator in self.separators:
            new_parts = []
            for part in parts:
                if len(part) > self.chunk_size:
                    # 按当前分隔符分割
                    split_parts = part.split(separator)
                    # 保留分隔符
                    for i, split_part in enumerate(split_parts[:-1]):
                        new_parts.append(split_part + separator)
                    new_parts.append(split_parts[-1])
                else:
                    new_parts.append(part)
            parts = new_parts

        return [p for p in parts if p.strip()]

    def _split_large_part(self, part: str) -> List[str]:
        """分割过大的部分"""
        chunks = []
        for i in range(0, len(part), self.chunk_size - self.overlap):
            chunk = part[i : i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks

    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """添加重叠内容"""
        if not chunks or self.overlap <= 0:
            return chunks

        result = [chunks[0]]

        for i in range(1, len(chunks)):
            # 从前一个块末尾取重叠内容
            prev_chunk = chunks[i - 1]
            overlap_text = prev_chunk[-self.overlap :] if len(prev_chunk) > self.overlap else prev_chunk

            # 添加到当前块开头
            current_chunk = overlap_text + chunks[i]
            result.append(current_chunk)

        return result


if __name__ == "__main__":
    """文本分块器调试"""
    print("=" * 60)
    print("文本分块器调试")
    print("=" * 60)

    # 测试数据
    test_text = """
# 登录接口文档

## 接口说明
用户登录接口，用于用户身份验证。

## 请求参数
- username: 用户名，必填，字符串类型
- password: 密码，必填，字符串类型

## 响应参数
- code: 状态码，200表示成功
- message: 提示信息
- data: 用户数据，包含token等信息

## 错误码
- 400: 参数错误
- 401: 认证失败
- 500: 服务器错误

## 示例
请求：
{
    "username": "admin",
    "password": "123456"
}

响应：
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "token": "xxx",
        "userId": "123"
    }
}
"""

    # 测试分块
    print("\n1. 固定长度分块:")
    chunker = TextChunker(chunk_size=200, overlap=20)
    chunks = chunker.split(test_text)
    print(f"   原文长度: {len(test_text)} 字符")
    print(f"   分块数量: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"   块{i}长度: {len(chunk)} 字符")
        print(f"   内容预览: {chunk[:50]}...")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
