"""
BGE Reranker精排模块

核心功能：
    - BGE-reranker-v2-m3 模型调用
    - 支持本地模型和HTTP两种模式
    - 对候选文档进行相关性重排序

配置项：
    - reranker.mode: local_model / http
    - reranker.model: 模型名称
    - reranker.base_url: HTTP模式服务地址
"""

from __future__ import annotations

from typing import List, Dict, Any
import httpx

from sentence_transformers import CrossEncoder

from app.config import config


class LocalBGEReranker:
    """
    BGE Reranker 精排器

    职责：
        - 加载 BGE 重排序模型
        - 对混合检索候选结果进行精排
        - 支持本地模型和 HTTP 两种调用模式
    """

    def __init__(self):
        self.mode = config.get("reranker.mode", "local_model")
        self.model_name = config.get("reranker.model", "BAAI/bge-reranker-v2-m3")
        self.base_url = config.get("reranker.base_url", "http://localhost:11434")
        self.timeout = int(config.get("reranker.timeout", 20))
        self._model = None

    def _get_model(self):
        """获取本地CrossEncoder模型"""
        if self._model is None:
            self._model = CrossEncoder(self.model_name)
        return self._model

    def _rerank_by_http(self, query: str, docs: List[str]) -> List[float]:
        """
        HTTP模式调用reranker服务

        @param query: 查询文本
        @param docs: 文档列表
        @return: 相关性分数列表
        """
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

    def rerank(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        """
        精排主入口

        实现步骤：
            1. 提取候选文档内容
            2. 根据模式选择本地模型或HTTP调用
            3. 计算相关性分数
            4. 排序并返回Top-K结果

        @param query: 用户查询
        @param candidates: 候选文档列表（来自混合检索）
        @param top_k: 返回数量
        @return: 重排序后的文档列表

        示例：
            输入：query="如何登录", candidates=[{content: "..."}, ...], top_k=3
            输出：[{content: "...", rerank_score: 0.95}, ...]
        """
        # 边界检查
        if not candidates:
            return []
        # 提取文档内容
        docs = [str(item.get("content") or "") for item in candidates]
        try:
            # 根据模式选择调用方式
            if self.mode == "http":
                scores = self._rerank_by_http(query, docs)
            else:
                # 本地模型模式
                model = self._get_model()
                pairs = [[query, doc] for doc in docs]
                scores = [float(score) for score in model.predict(pairs)]
        except Exception:
            # 异常降级：使用混合得分
            for item in candidates:
                item["rerank_score"] = float(item.get("hybrid_score") or 0.0)
            return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[
                :top_k
            ]
        # 设置重排分数
        for idx, item in enumerate(candidates):
            item["rerank_score"] = scores[idx] if idx < len(scores) else 0.0
        # 排序并返回Top-K
        return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_k]


reranker = LocalBGEReranker()


if __name__ == "__main__":
    """
    BGE Reranker调试代码

    调试说明：
        1. 测试精排功能
    """
    print("=" * 60)
    print("BGE Reranker调试")
    print("=" * 60)

    # 测试精排
    print("\n1. 精排测试:")
    candidates = [
        {"content": "用户登录接口说明，验证用户名密码", "hybrid_score": 0.8},
        {"content": "注册接口文档，创建新用户", "hybrid_score": 0.6},
        {"content": "登录API接口，返回token", "hybrid_score": 0.9},
        {"content": "忘记密码接口，重置密码", "hybrid_score": 0.5},
    ]
    result = reranker.rerank("登录接口", candidates, top_k=3)
    print(f"   查询: 登录接口")
    print(f"   精排结果:")
    for i, item in enumerate(result):
        print(
            f"   - {i+1}. score={item.get('rerank_score', 0):.3f}, content={item['content'][:20]}..."
        )

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
