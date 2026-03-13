"""
BM25关键词检索模块

核心功能：
    - 经典BM25算法实现
    - 支持中英文混合分词
    - 输出排序结果与分数

BM25参数：
    - k1: 词频饱和参数，默认1.5
    - b: 文档长度归一化参数，默认0.75
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Any


class BM25KeywordRetriever:
    """
    BM25关键词检索器

    职责：
        - 实现经典BM25相关性评分算法
        - 支持中英文混合文本分词
        - 返回按相关性排序的检索结果
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def _tokenize(self, text: str) -> List[str]:
        """
        中英文混合分词

        处理策略：
            1. 转小写
            2. 英文按字母数字分割
            3. 中文按字符分割，并生成二元组

        @param text: 待分词文本
        @return: token列表
        """
        lowered = str(text or "").lower()
        base_tokens = [
            token for token in re.split(r"[^\w\u4e00-\u9fff]+", lowered) if token
        ]
        enriched: List[str] = []
        for token in base_tokens:
            enriched.append(token)
            enriched.extend(re.findall(r"[a-z0-9]+", token))
            chinese_chars = re.findall(r"[\u4e00-\u9fff]", token)
            enriched.extend(chinese_chars)
            if len(chinese_chars) >= 2:
                for idx in range(len(chinese_chars) - 1):
                    enriched.append(chinese_chars[idx] + chinese_chars[idx + 1])
        return [item for item in enriched if item]

    def search(
        self,
        query: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        BM25检索

        实现步骤：
            1. 对查询和文档集分词
            2. 计算IDF和文档长度
            3. 对每个文档计算BM25分数
            4. 排序并返回Top-K结果

        @param query: 用户查询
        @param documents: 文档列表
        @param metadatas: 文档元数据列表
        @param top_k: 召回数量
        @return: [{"content": "...", "distance": 0.5, "metadata": {...}, "bm25_score": 1.5}, ...]
        """
        # 边界检查
        if not documents:
            return []
        # 步骤1：对查询和文档集分词
        corpus_tokens = [self._tokenize(doc) for doc in documents]
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        # 步骤2：计算IDF和文档长度
        avg_doc_len = sum(len(tokens) for tokens in corpus_tokens) / max(
            1, len(corpus_tokens)
        )
        doc_freq: Dict[str, int] = {}
        for tokens in corpus_tokens:
            for token in set(tokens):
                doc_freq[token] = doc_freq.get(token, 0) + 1
        total_docs = len(corpus_tokens)

        # 步骤3：对每个文档计算BM25分数
        scores: List[tuple[int, float]] = []
        for idx, tokens in enumerate(corpus_tokens):
            tf_map: Dict[str, int] = {}
            for token in tokens:
                tf_map[token] = tf_map.get(token, 0) + 1
            doc_len = len(tokens)
            score = 0.0
            # 计算每个查询词的BM25分数
            for token in query_tokens:
                if token not in tf_map:
                    continue
                df = doc_freq.get(token, 0)
                idf = math.log(1 + ((total_docs - df + 0.5) / (df + 0.5)))
                tf = tf_map[token]
                denominator = tf + self.k1 * (
                    1 - self.b + self.b * doc_len / max(1.0, avg_doc_len)
                )
                score += idf * ((tf * (self.k1 + 1)) / max(1e-8, denominator))
            if score > 0:
                scores.append((idx, score))
        # 步骤4：排序并返回Top-K
        scores.sort(key=lambda item: item[1], reverse=True)
        output: List[Dict[str, Any]] = []
        for rank, (idx, score) in enumerate(scores[:top_k]):
            meta = metadatas[idx] if idx < len(metadatas) else {}
            output.append(
                {
                    "content": documents[idx],
                    "distance": max(0.0, 1.0 - min(1.0, score / 10.0)),
                    "metadata": meta,
                    "bm25_score": score,
                    "rank": rank + 1,
                }
            )
        return output


if __name__ == "__main__":
    """
    BM25检索器调试代码

    调试说明：
        1. 测试分词
        2. 测试检索
    """
    print("=" * 60)
    print("BM25检索器调试")
    print("=" * 60)

    retriever = BM25KeywordRetriever()

    # 测试1：分词
    print("\n1. 分词测试:")
    test_text = "登录接口API user login"
    tokens = retriever._tokenize(test_text)
    print(f"   文本: {test_text}")
    print(f"   Tokens: {tokens}")

    # 测试2：检索
    print("\n2. 检索测试:")
    docs = [
        "用户登录接口说明",
        "注册接口文档",
        "用户管理接口",
        "登录API接口文档",
    ]
    metas = [{"doc_id": f"d{i}"} for i in range(len(docs))]
    results = retriever.search("登录接口", docs, metas, top_k=3)
    print(f"   查询: 登录接口")
    print(f"   结果数量: {len(results)}")
    for r in results:
        print(
            f"   - rank={r['rank']}, score={r['bm25_score']:.2f}, content={r['content'][:20]}..."
        )

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
