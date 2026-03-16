"""
评估模块

提供RAG和Agent的自动化评估能力

使用方法：
    # 初始化评估环境
    python -m evals.setup_eval
    
    # 运行RAG评估
    python -m pytest evals/test_rag_eval.py -v
    
    # 运行Agent评估
    python -m pytest evals/test_agent_eval.py -v
"""

from evals.metrics import (
    RetrievalMetrics,
    compute_retrieval_metrics,
    keyword_match_score,
)

__all__ = [
    "RetrievalMetrics",
    "compute_retrieval_metrics",
    "keyword_match_score",
]
