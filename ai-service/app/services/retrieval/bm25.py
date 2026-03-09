"""
BM25关键词检索模块。
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Any


class BM25KeywordRetriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def _tokenize(self, text: str) -> List[str]:
        lowered = str(text or "").lower()
        base_tokens = [token for token in re.split(r"[^\w\u4e00-\u9fff]+", lowered) if token]
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
        if not documents:
            return []
        corpus_tokens = [self._tokenize(doc) for doc in documents]
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        avg_doc_len = sum(len(tokens) for tokens in corpus_tokens) / max(1, len(corpus_tokens))
        doc_freq: Dict[str, int] = {}
        for tokens in corpus_tokens:
            for token in set(tokens):
                doc_freq[token] = doc_freq.get(token, 0) + 1
        total_docs = len(corpus_tokens)

        scores: List[tuple[int, float]] = []
        for idx, tokens in enumerate(corpus_tokens):
            tf_map: Dict[str, int] = {}
            for token in tokens:
                tf_map[token] = tf_map.get(token, 0) + 1
            doc_len = len(tokens)
            score = 0.0
            for token in query_tokens:
                if token not in tf_map:
                    continue
                df = doc_freq.get(token, 0)
                idf = math.log(1 + ((total_docs - df + 0.5) / (df + 0.5)))
                tf = tf_map[token]
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / max(1.0, avg_doc_len))
                score += idf * ((tf * (self.k1 + 1)) / max(1e-8, denominator))
            if score > 0:
                scores.append((idx, score))
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
