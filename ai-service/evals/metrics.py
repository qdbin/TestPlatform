"""
RAG检索评估指标模块

职责：
    1. 计算检索任务的核心指标（召回率、精确率、MRR）
    2. 提供关键词匹配评分功能
    3. 支持多查询批量评估

核心指标说明：
    - Recall（召回率）：预测命中的文档数 / 标准文档总数，衡量检索覆盖面
    - Precision（精确率）：预测命中的文档数 / 预测的文档总数，衡量检索准确性
    - MRR（平均倒数排名）：首个命中文档的排名倒数平均值，衡量检索排序质量
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass
class RetrievalMetrics:
    """
    检索评估结果容器

    字段说明：
        - recall: 召回率（0~1），预测命中的文档数占标准文档总数的比例
        - precision: 精确率（0~1），预测命中的文档数占预测文档总数的比例
        - mrr: 平均倒数排名（0~1），首个命中文档排名倒数的平均值
    """

    recall: float
    precision: float
    mrr: float


def _safe_div(a: float, b: float) -> float:
    """
    安全除法，避免除零错误

    @param a: 被除数
    @param b: 除数
    @return: a/b 当 b>0，否则返回 0.0
    """
    return a / b if b else 0.0


def compute_retrieval_metrics(
    predicted_doc_ids: Sequence[Sequence[str]],
    golden_doc_ids: Sequence[Sequence[str]],
) -> RetrievalMetrics:
    """
    计算检索评估指标

    实现步骤：
        1. 遍历每个查询的预测结果和标准结果
        2. 对每个查询计算命中数、召回、精确
        3. 累加 MRR（首个命中文档的排名倒数）
        4. 返回平均值

    @param predicted_doc_ids: 预测的文档ID列表（外层列表为查询，内层列表为该查询的检索结果）
    @param golden_doc_ids: 标准文档ID列表（外层列表为查询，内层列表为该查询的真实相关文档）
    @return: RetrievalMetrics 对象（包含 recall/precision/mrr）

    示例：
        predicted = [["doc1", "doc2"], ["doc3"]]
        golden = [["doc1", "doc3"], ["doc3"]]
        # 第一个查询：命中 doc1，召回=1/2=0.5，精确=1/2=0.5，排名=1，MRR=1
        # 第二个查询：命中 doc3，召回=1/1=1，精确=1/1=1，排名=1，MRR=1
        # 平均：recall=0.75, precision=0.75, mrr=1.0
    """
    recall_sum = 0.0
    precision_sum = 0.0
    mrr_sum = 0.0
    total = len(golden_doc_ids)
    for preds, golds in zip(predicted_doc_ids, golden_doc_ids):
        pred_set = [str(i) for i in preds]
        gold_set = set(str(i) for i in golds)
        hit_count = len([i for i in pred_set if i in gold_set])
        recall_sum += _safe_div(hit_count, len(gold_set))
        precision_sum += _safe_div(hit_count, len(pred_set))
        rank = 0
        for idx, doc_id in enumerate(pred_set, start=1):
            if doc_id in gold_set:
                rank = idx
                break
        mrr_sum += _safe_div(1.0, rank)
    return RetrievalMetrics(
        recall=_safe_div(recall_sum, total),
        precision=_safe_div(precision_sum, total),
        mrr=_safe_div(mrr_sum, total),
    )


def keyword_match_score(answer: str, keywords: Iterable[str]) -> float:
    """
    关键词匹配评分

    计算答案中包含的关键词比例，用于评估答案与标准关键词的匹配程度

    @param answer: 待评估的答案文本
    @param keywords: 标准关键词列表
    @return: 匹配得分（0~1），命中的关键词数 / 关键词总数

    示例：
        answer = "登录需要用户名和密码"
        keywords = ["登录", "用户名", "密码", "验证码"]
        # 命中：登录、用户名、密码 = 3个
        # 得分：3/4 = 0.75
    """
    text = str(answer or "")
    keys = [str(k) for k in keywords if str(k)]
    if not keys:
        return 0.0
    hits = sum(1 for k in keys if k in text)
    return _safe_div(hits, len(keys))
