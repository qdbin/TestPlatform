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
    rows: List[Dict[str, Any]] = []
    with DATASET.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def run_single(item: Dict[str, Any]) -> Dict[str, Any]:
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
