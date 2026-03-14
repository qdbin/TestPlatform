from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass
class RetrievalMetrics:
    recall: float
    precision: float
    mrr: float


def _safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def compute_retrieval_metrics(
    predicted_doc_ids: Sequence[Sequence[str]],
    golden_doc_ids: Sequence[Sequence[str]],
) -> RetrievalMetrics:
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
    text = str(answer or "")
    keys = [str(k) for k in keywords if str(k)]
    if not keys:
        return 0.0
    hits = sum(1 for k in keys if k in text)
    return _safe_div(hits, len(keys))
