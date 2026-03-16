"""
BM25关键词检索模块

职责：
    1. 基于BM25算法实现关键词检索
    2. 作为向量检索的补充，提高召回率
    3. 支持中文分词和停用词过滤

BM25算法说明：
    BM25是一种基于概率模型的信息检索算法，
    通过词频(TF)和逆文档频率(IDF)计算文档与查询的相关性。

    核心公式：
        score = Σ IDF(q_i) * (f(q_i) * (k1 + 1)) / (f(q_i) + k1 * (1 - b + b * |D| / avgdl))
        其中：
            - q_i: 查询词
            - f(q_i): 词频
            - IDF: 逆文档频率
            - k1, b: 调节参数
            - |D|: 文档长度
            - avgdl: 平均文档长度
"""

import re
import math
from typing import List, Dict, Any, Set, Tuple
from collections import Counter


class BM25KeywordRetriever:
    """
    BM25关键词检索器

    职责：
        - 构建文档索引
        - 执行BM25检索
        - 返回Top-K相关文档

    使用示例：
        retriever = BM25KeywordRetriever()
        results = retriever.search("登录接口", documents, metadatas, top_k=5)
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        初始化BM25检索器

        @param k1: 词频饱和度参数（通常1.2-2.0）
        @param b: 文档长度归一化参数（通常0.75）
        """
        self.k1 = k1
        self.b = b
        self.stopwords: Set[str] = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也",
            "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那",
            "个", "为", "之", "与", "及", "等", "或", "但", "而", "因", "于", "则", "即", "若", "虽",
            "故", "乃", "既", "以", "所", "被", "把", "给", "让", "向", "往", "从", "自", "到", "在",
            "关于", "对于", "由于", "根据", "按照", "通过", "经过", "随着", "除了", "除", "除了",
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "have", "has",
            "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must",
            "shall", "can", "need", "dare", "ought", "used", "to", "of", "in", "for", "on", "with",
            "at", "by", "from", "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then", "once", "here", "there",
            "when", "where", "why", "how", "all", "each", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just",
            "and", "but", "if", "or", "because", "until", "while", "this", "that", "these", "those"
        }

    def _tokenize(self, text: str) -> List[str]:
        """
        中文分词

        实现：
            1. 按非中文字符分割
            2. 提取2-4字的中文词组
            3. 过滤停用词和单字

        @param text: 输入文本
        @return: 分词结果列表
        """
        if not text:
            return []

        # 统一转换为小写并清理
        text = str(text).lower().strip()

        # 提取中文词汇（2-4字词组）
        tokens = []

        # 匹配中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
        for chars in chinese_chars:
            # 提取2-4字词组
            for length in range(2, min(5, len(chars) + 1)):
                for i in range(len(chars) - length + 1):
                    token = chars[i:i + length]
                    if token not in self.stopwords:
                        tokens.append(token)

        # 提取英文单词
        english_words = re.findall(r'[a-zA-Z]+', text)
        for word in english_words:
            if len(word) > 1 and word not in self.stopwords:
                tokens.append(word)

        return tokens

    def _calculate_idf(self, term: str, documents: List[List[str]]) -> float:
        """
        计算逆文档频率(IDF)

        @param term: 查询词
        @param documents: 文档分词列表
        @return: IDF值
        """
        # 包含该词的文档数
        doc_count = sum(1 for doc in documents if term in doc)
        if doc_count == 0:
            return 0

        # IDF公式: log((N - n + 0.5) / (n + 0.5) + 1)
        N = len(documents)
        idf = math.log((N - doc_count + 0.5) / (doc_count + 0.5) + 1)
        return idf

    def _calculate_bm25_score(
        self,
        query_tokens: List[str],
        doc_tokens: List[str],
        idf_dict: Dict[str, float],
        avgdl: float
    ) -> float:
        """
        计算BM25分数

        @param query_tokens: 查询词列表
        @param doc_tokens: 文档词列表
        @param idf_dict: IDF字典
        @param avgdl: 平均文档长度
        @return: BM25分数
        """
        score = 0.0
        doc_len = len(doc_tokens)
        doc_counter = Counter(doc_tokens)

        for term in query_tokens:
            if term not in idf_dict:
                continue

            # 词频
            tf = doc_counter.get(term, 0)
            if tf == 0:
                continue

            # IDF
            idf = idf_dict[term]

            # BM25计算公式
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / avgdl)
            score += idf * numerator / denominator

        return score

    def search(
        self,
        query: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        执行BM25检索

        实现步骤：
            1. 对查询和文档进行分词
            2. 计算每个词的IDF
            3. 计算每个文档的BM25分数
            4. 按分数排序返回Top-K

        @param query: 查询字符串
        @param documents: 文档列表
        @param metadatas: 文档元数据列表
        @param top_k: 返回结果数量
        @return: 检索结果列表

        返回格式：
            [
                {
                    "content": "文档内容",
                    "metadata": {...},
                    "score": 1.234,
                    "source": "keyword"
                },
                ...
            ]
        """
        if not documents:
            return []

        # 分词
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        doc_tokens_list = [self._tokenize(doc) for doc in documents]

        # 计算IDF
        unique_terms = set(query_tokens)
        idf_dict = {
            term: self._calculate_idf(term, doc_tokens_list)
            for term in unique_terms
        }

        # 计算平均文档长度
        total_len = sum(len(tokens) for tokens in doc_tokens_list)
        avgdl = total_len / len(doc_tokens_list) if doc_tokens_list else 1

        # 计算每个文档的分数
        scored_docs: List[Tuple[int, float]] = []
        for idx, doc_tokens in enumerate(doc_tokens_list):
            score = self._calculate_bm25_score(
                query_tokens, doc_tokens, idf_dict, avgdl
            )
            if score > 0:
                scored_docs.append((idx, score))

        # 按分数排序
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # 构建结果
        results = []
        for idx, score in scored_docs[:top_k]:
            result = {
                "content": documents[idx],
                "metadata": metadatas[idx] if idx < len(metadatas) else {},
                "score": score,
                "source": "keyword",
            }
            results.append(result)

        return results


if __name__ == "__main__":
    """BM25检索器调试"""
    print("=" * 60)
    print("BM25关键词检索器调试")
    print("=" * 60)

    # 测试数据
    documents = [
        "用户登录接口，用于用户身份验证",
        "用户注册接口，用于创建新用户账号",
        "获取用户信息接口，查询用户详细资料",
        "修改密码接口，用于更新用户密码",
        "订单查询接口，查询用户订单列表",
    ]
    metadatas = [
        {"id": "api-1", "name": "登录接口"},
        {"id": "api-2", "name": "注册接口"},
        {"id": "api-3", "name": "用户信息接口"},
        {"id": "api-4", "name": "修改密码接口"},
        {"id": "api-5", "name": "订单查询接口"},
    ]

    retriever = BM25KeywordRetriever()

    # 测试分词
    print("\n1. 分词测试:")
    text = "用户登录接口测试"
    tokens = retriever._tokenize(text)
    print(f"   原文: {text}")
    print(f"   分词: {tokens}")

    # 测试检索
    print("\n2. 检索测试:")
    queries = ["登录", "用户", "密码", "订单"]
    for query in queries:
        results = retriever.search(query, documents, metadatas, top_k=3)
        print(f"\n   查询: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['metadata']['name']} (score: {result['score']:.3f})")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
