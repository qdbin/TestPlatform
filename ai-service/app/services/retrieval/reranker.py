"""
本地BGE Reranker精排模块。
"""

from __future__ import annotations

from typing import List, Dict, Any
import httpx

from sentence_transformers import CrossEncoder

from app.config import config


class LocalBGEReranker:
    def __init__(self):
        self.mode = config.get("reranker.mode", "local_model")
        self.model_name = config.get("reranker.model", "BAAI/bge-reranker-v2-m3")
        self.base_url = config.get("reranker.base_url", "http://localhost:11434")
        self.timeout = int(config.get("reranker.timeout", 20))
        self._model = None

    def _get_model(self):
        if self._model is None:
            self._model = CrossEncoder(self.model_name)
        return self._model

    def _rerank_by_http(self, query: str, docs: List[str]) -> List[float]:
        payload = {"model": self.model_name, "query": query, "documents": docs}
        response = httpx.post(
            f"{self.base_url.rstrip('/')}/api/rerank",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json() or {}
        scores = []
        for item in data.get("results", []):
            scores.append(float(item.get("relevance_score") or 0.0))
        return scores if len(scores) == len(docs) else [0.0 for _ in docs]

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        if not candidates:
            return []
        docs = [str(item.get("content") or "") for item in candidates]
        try:
            if self.mode == "http":
                scores = self._rerank_by_http(query, docs)
            else:
                model = self._get_model()
                pairs = [[query, doc] for doc in docs]
                scores = [float(score) for score in model.predict(pairs)]
        except Exception:
            for item in candidates:
                item["rerank_score"] = float(item.get("hybrid_score") or 0.0)
            return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_k]
        for idx, item in enumerate(candidates):
            item["rerank_score"] = scores[idx] if idx < len(scores) else 0.0
        return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_k]


reranker = LocalBGEReranker()
