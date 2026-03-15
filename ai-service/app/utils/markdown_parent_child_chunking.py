"""
Markdown父子分块模块

职责：
    1. 解析Markdown文档结构
    2. 按标题层级分块
    3. 维护父子关系
    4. 支持元数据提取

分块策略：
    1. 按标题层级分块：# ## ###
    2. 父子关系维护：子块包含父块标题
    3. 元数据提取：提取标题、层级等信息

使用示例：
    chunker = MarkdownParentChildChunker()
    chunks = chunker.split(markdown_text)
    # chunks = [{"content": "...", "metadata": {"level": 1, "title": "..."}}]
"""

from typing import List, Dict, Any, Tuple
import re


class MarkdownParentChildChunker:
    """
    Markdown父子分块器

    职责：
        - 解析Markdown文档结构
        - 按标题层级分块
        - 维护父子关系
        - 提取元数据

    分块规则：
        1. 按# ## ###等标题分割
        2. 子块包含父块标题作为上下文
        3. 提取标题层级和名称作为元数据
    """

    def __init__(self, max_chunk_size: int = 1000):
        """
        初始化Markdown分块器

        @param max_chunk_size: 最大块大小
        """
        self.max_chunk_size = max_chunk_size
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def split(self, text: str) -> List[Dict[str, Any]]:
        """
        分割Markdown文本

        实现步骤：
            1. 解析所有标题
            2. 按标题分割内容
            3. 构建父子关系
            4. 生成带元数据的块

        @param text: Markdown文本
        @return: 块列表（包含content和metadata）

        返回格式：
            [
                {
                    "content": "块内容",
                    "metadata": {
                        "level": 2,
                        "title": "标题",
                        "parent_titles": ["父标题"]
                    }
                }
            ]
        """
        if not text:
            return []

        # 解析标题
        headings = self._parse_headings(text)

        if not headings:
            # 没有标题，整个文本作为一个块
            return [{"content": text.strip(), "metadata": {"level": 0, "title": ""}}]

        # 按标题分割
        sections = self._split_by_headings(text, headings)

        # 构建带父子关系的块
        chunks = self._build_chunks_with_hierarchy(sections)

        return chunks

    def _parse_headings(self, text: str) -> List[Tuple[int, str, int]]:
        """
        解析所有标题

        @param text: Markdown文本
        @return: [(层级, 标题, 位置), ...]
        """
        headings = []
        for match in self.heading_pattern.finditer(text):
            level = len(match.group(1))
            title = match.group(2).strip()
            position = match.start()
            headings.append((level, title, position))
        return headings

    def _split_by_headings(
        self, text: str, headings: List[Tuple[int, str, int]]
    ) -> List[Dict[str, Any]]:
        """按标题分割文本"""
        sections = []

        for i, (level, title, position) in enumerate(headings):
            # 确定当前部分的结束位置
            if i + 1 < len(headings):
                end_pos = headings[i + 1][2]
            else:
                end_pos = len(text)

            # 提取内容
            content = text[position:end_pos].strip()

            sections.append({
                "level": level,
                "title": title,
                "content": content,
            })

        return sections

    def _build_chunks_with_hierarchy(
        self, sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """构建带层级关系的块"""
        chunks = []
        parent_stack: List[Tuple[int, str]] = []  # (层级, 标题)

        for section in sections:
            level = section["level"]
            title = section["title"]
            content = section["content"]

            # 更新父标题栈
            while parent_stack and parent_stack[-1][0] >= level:
                parent_stack.pop()

            # 构建父标题列表
            parent_titles = [p[1] for p in parent_stack]

            # 构建完整内容（包含父标题上下文）
            if parent_titles:
                context = " > ".join(parent_titles)
                full_content = f"上下文: {context}\n\n{content}"
            else:
                full_content = content

            # 如果内容过长，进一步分割
            if len(full_content) > self.max_chunk_size:
                sub_chunks = self._split_large_content(
                    full_content, level, title, parent_titles
                )
                chunks.extend(sub_chunks)
            else:
                chunks.append({
                    "content": full_content,
                    "metadata": {
                        "level": level,
                        "title": title,
                        "parent_titles": parent_titles,
                    },
                })

            # 将当前标题加入父栈
            parent_stack.append((level, title))

        return chunks

    def _split_large_content(
        self,
        content: str,
        level: int,
        title: str,
        parent_titles: List[str],
    ) -> List[Dict[str, Any]]:
        """分割过大的内容"""
        chunks = []

        # 按段落分割
        paragraphs = content.split('\n\n')
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > self.max_chunk_size:
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": {
                            "level": level,
                            "title": title,
                            "parent_titles": parent_titles,
                        },
                    })
                current_chunk = para
            else:
                current_chunk += '\n\n' + para if current_chunk else para

        # 添加最后一个块
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": {
                    "level": level,
                    "title": title,
                    "parent_titles": parent_titles,
                },
            })

        return chunks


# 全局分块器实例
markdown_parent_child_chunker = MarkdownParentChildChunker()


if __name__ == "__main__":
    """Markdown分块器调试"""
    print("=" * 60)
    print("Markdown父子分块器调试")
    print("=" * 60)

    # 测试数据
    test_markdown = """
# API文档

## 用户模块

### 登录接口
用户登录接口说明。

请求参数：
- username: 用户名
- password: 密码

响应参数：
- token: 认证令牌
- userId: 用户ID

### 注册接口
用户注册接口说明。

## 订单模块

### 创建订单
创建订单接口说明。

### 查询订单
查询订单接口说明。
"""

    # 测试分块
    print("\n1. Markdown分块测试:")
    chunker = MarkdownParentChildChunker(max_chunk_size=500)
    chunks = chunker.split(test_markdown)

    print(f"   原文长度: {len(test_markdown)} 字符")
    print(f"   分块数量: {len(chunks)}")

    for i, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        print(f"\n   块{i}:")
        print(f"      标题: {metadata['title']}")
        print(f"      层级: {metadata['level']}")
        print(f"      父标题: {metadata['parent_titles']}")
        print(f"      内容长度: {len(chunk['content'])} 字符")
        print(f"      内容预览: {chunk['content'][:60]}...")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
