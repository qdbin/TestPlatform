"""
RAG检索评估脚本

职责：
    - 加载RAG测试数据集
    - 调用知识库检索API
    - 评估检索结果（召回率、精确率、MRR）
    - 输出评估指标

评估指标：
    - retrieval_recall: 召回率
    - retrieval_precision: 精确率
    - retrieval_mrr: 平均倒数排名
    - answer_relevance: 答案相关性
    - faithfulness: 答案可信度
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests
from langsmith import Client

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from metrics import compute_retrieval_metrics, keyword_match_score


DATASET = ROOT / "data" / "rag_eval_dataset.jsonl"
API_BASE = "http://localhost:8001"


def load_dataset() -> List[Dict[str, Any]]:
    """
    加载RAG评估数据集

    数据格式（JSONL，每行一个JSON对象）：
        {
            "id": "p1-doc-001",           // 测试用例唯一标识
            "project_id": "p1",           // 项目ID（用于匹配向量库）
            "question": "登录接口需要哪些参数？",  // 用户问题
            "doc_ids": ["doc1", "doc2"],  // 标准相关文档ID列表
            "golden_keywords": ["登录", "参数", "username", "password"],  // 答案应包含的关键词
            "reference_answer": "..."     // 参考答案（用于答案准确性评估）
        }

    @return: 测试数据列表
    """
    rows: List[Dict[str, Any]] = []
    with DATASET.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def run_single(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行单条RAG评估

    评估流程：
        1. 构建检索请求payload，包含project_id、question、top_k等参数
        2. 调用RAG查询API `/ai/rag/query`
        3. 解析响应，提取检索到的文档列表和生成答案
        4. 从文档metadata中提取predicted_doc_ids
        5. 使用keyword_match_score计算答案相关性

    @param item: 测试数据项（包含 id, question, doc_ids, golden_keywords, reference_answer）
    @return: 评估结果字典，包含字段：
        - id: 测试用例ID
        - predicted_doc_ids: 检索到的文档ID列表
        - golden_doc_ids: 标准相关文档ID列表
        - answer_relevance: 关键词匹配得分（0~1）
        - faithfulness: 答案可信度（同 answer_relevance）
        - answer_accuracy: 答案准确性得分

    API响应示例：
        {
            "data": [
                {"content": "...", "metadata": {"doc_id": "doc1", ...}},
                {"content": "...", "metadata": {"doc_id": "doc2", ...}}
            ],
            "answer": "登录接口需要username和password参数..."
        }
    """
    payload = {
        "project_id": (
            item["id"].split("-")[0]
            if item.get("project_id") is None
            else item["project_id"]
        ),
        "question": item["question"],
        "top_k": 5,
        "messages": [],
    }
    resp = requests.post(f"{API_BASE}/ai/rag/query", json=payload, timeout=60)
    data = resp.json() if resp.ok else {"data": [], "answer": ""}
    docs = data.get("data") or []
    predicted_doc_ids = [
        str((doc.get("metadata") or {}).get("doc_id") or "")
        for doc in docs
        if isinstance(doc, dict)
    ]
    answer = data.get("answer") or ""
    relevance = keyword_match_score(answer, item.get("golden_keywords") or [])
    return {
        "id": item["id"],
        "predicted_doc_ids": predicted_doc_ids,
        "golden_doc_ids": item.get("doc_ids") or [],
        "answer_relevance": relevance,
        "faithfulness": relevance,
        "answer_accuracy": (
            1.0
            if keyword_match_score(answer, [item.get("reference_answer") or ""]) > 0
            else relevance
        ),
    }


def main() -> None:
    """
    RAG评估主入口

    执行流程：
        1. 加载数据集
        2. 执行每条检索评估
        3. 计算检索指标（召回/精确/MRR）
        4. 计算答案质量指标
        5. 输出JSON结果
    """
    client = Client()
    rows = load_dataset()
    records = [run_single(item) for item in rows]
    retrieval = compute_retrieval_metrics(
        [x["predicted_doc_ids"] for x in records],
        [x["golden_doc_ids"] for x in records],
    )
    avg_relevance = sum(x["answer_relevance"] for x in records) / len(records)
    avg_faithfulness = sum(x["faithfulness"] for x in records) / len(records)
    avg_accuracy = sum(x["answer_accuracy"] for x in records) / len(records)
    summary = {
        "retrieval_recall": retrieval.recall,
        "retrieval_precision": retrieval.precision,
        "retrieval_mrr": retrieval.mrr,
        "answer_relevance": avg_relevance,
        "faithfulness": avg_faithfulness,
        "answer_accuracy": avg_accuracy,
        "sample_count": len(records),
    }
    project_name = "test-platform-ai-rag-eval"
    try:
        client.list_projects(limit=1)
    except Exception:
        pass
    print(
        json.dumps(
            {"project": project_name, "summary": summary, "records": records},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
