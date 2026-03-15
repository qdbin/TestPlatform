"""
重排序模块 (BGE Reranker)

职责：
    1. 对混合检索结果进行精排序
    2. 提高检索结果的相关性
    3. 基于BGE模型计算查询-文档相关性分数

BGE Reranker说明：
    BGE (BAAI General Embedding) 是北京智源研究院开源的Embedding模型系列。
    Reranker用于对候选文档进行精排序，计算查询与文档的匹配度。

    使用场景：
        1. 向量检索召回Top-K后，使用Reranker精排
        2. 混合检索结果融合后，使用Reranker精排
        3. 提高最终返回结果的相关性

实现特点：
    - 使用BGE模型计算查询-文档对的相关性
    - 支持批量处理提高效率
    - 提供降级机制（当模型不可用时使用原始分数）
"""

from typing import List, Dict, Any, Optional
import os

from app.observability import app_logger


class BGEReranker:
    """
    BGE重排序器

    职责：
        - 加载BGE Reranker模型
        - 计算查询-文档相关性分数
        - 对结果进行精排序

    模型说明：
        - 默认模型: BAAI/bge-reranker-base
        - 输入: (query, document) 对
        - 输出: 相关性分数 (0-1)

    使用示例：
        reranker = BGEReranker()
        results = reranker.rerank("查询", candidates, top_k=5)
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """
        初始化BGE重排序器

        @param model_name: BGE模型名称
        """
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self._load_error = None

    def _load_model(self) -> bool:
        """
        延迟加载BGE模型

        @return: 是否加载成功
        """
        if self._model is not None:
            return True

        try:
            # 尝试导入transformers
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            # 加载模型和tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name
            )
            self._model.eval()

            app_logger.info("BGE Reranker模型加载成功: {}", self.model_name)
            return True

        except ImportError:
            self._load_error = "transformers库未安装，跳过BGE重排序"
            app_logger.warning(self._load_error)
            return False

        except Exception as e:
            self._load_error = f"BGE模型加载失败: {str(e)}"
            app_logger.error(self._load_error)
            return False

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
        batch_size: int = 8,
    ) -> List[Dict[str, Any]]:
        """
        对候选结果进行重排序

        实现步骤：
            1. 加载模型（如果未加载）
            2. 批量计算相关性分数
            3. 按分数排序
            4. 返回Top-K结果

        @param query: 查询字符串
        @param candidates: 候选结果列表
        @param top_k: 返回结果数量
        @param batch_size: 批处理大小
        @return: 重排序后的结果列表

        降级策略：
            如果模型加载失败，使用原始分数排序
        """
        if not candidates:
            return []

        # 尝试加载模型
        if not self._load_model():
            # 降级：使用原始分数排序
            return self._fallback_sort(candidates, top_k)

        try:
            import torch

            # 准备输入
            pairs = []
            for candidate in candidates:
                content = str(candidate.get("content") or "")
                pairs.append([query, content])

            # 批量计算分数
            scores = []
            for i in range(0, len(pairs), batch_size):
                batch_pairs = pairs[i : i + batch_size]

                # Tokenize
                inputs = self._tokenizer(
                    batch_pairs,
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                    max_length=512,
                )

                # 计算分数
                with torch.no_grad():
                    outputs = self._model(**inputs)
                    batch_scores = outputs.logits.squeeze(-1).tolist()
                    if isinstance(batch_scores, float):
                        batch_scores = [batch_scores]
                    scores.extend(batch_scores)

            # 添加分数到结果
            for i, candidate in enumerate(candidates):
                candidate["rerank_score"] = scores[i] if i < len(scores) else 0.0

            # 按重排序分数排序
            sorted_candidates = sorted(
                candidates,
                key=lambda x: x.get("rerank_score", 0),
                reverse=True,
            )

            return sorted_candidates[:top_k]

        except Exception as e:
            app_logger.error("BGE重排序失败: {}", str(e))
            return self._fallback_sort(candidates, top_k)

    def _fallback_sort(
        self, candidates: List[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        """
        降级排序（当模型不可用时）

        使用原始分数（hybrid_score或distance）进行排序。

        @param candidates: 候选结果
        @param top_k: 返回数量
        @return: 排序后的结果
        """
        # 使用混合分数或距离分数排序
        sorted_candidates = sorted(
            candidates,
            key=lambda x: x.get("hybrid_score", 1.0 - x.get("distance", 1.0)),
            reverse=True,
        )

        # 标记为降级结果
        for candidate in sorted_candidates:
            candidate["rerank_score"] = candidate.get("hybrid_score", 0.0)
            candidate["rerank_fallback"] = True

        return sorted_candidates[:top_k]


# 全局重排序器实例
reranker = BGEReranker()


if __name__ == "__main__":
    """BGE重排序器调试"""
    print("=" * 60)
    print("BGE重排序器调试")
    print("=" * 60)

    # 测试数据
    candidates = [
        {
            "content": "用户登录接口文档，包含用户名和密码参数",
            "metadata": {"id": "doc-1"},
            "hybrid_score": 0.85,
        },
        {
            "content": "订单查询接口，支持按时间范围查询",
            "metadata": {"id": "doc-2"},
            "hybrid_score": 0.75,
        },
        {
            "content": "用户注册接口，用于创建新用户账号",
            "metadata": {"id": "doc-3"},
            "hybrid_score": 0.80,
        },
    ]

    reranker = BGEReranker()

    # 测试重排序
    print("\n1. 重排序测试:")
    query = "登录接口参数"
    results = reranker.rerank(query, candidates, top_k=3)

    print(f"\n   查询: {query}")
    print("   重排序结果:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['metadata']['id']}")
        print(f"      内容: {result['content'][:30]}...")
        print(f"      分数: hybrid={result.get('hybrid_score', 0):.3f}, "
              f"rerank={result.get('rerank_score', 0):.3f}")
        if result.get('rerank_fallback'):
            print(f"      (降级排序)")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
