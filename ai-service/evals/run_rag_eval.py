"""
RAG 评估运行脚本

功能：
    1. 运行 RAG 检索评估
    2. 计算召回率、精确率、MRR
    3. 计算生成质量指标
    4. 推送评估结果到 LangSmith

评估指标：
    - 召回率 (Recall): 检索到的相关文档比例
    - 精确率 (Precision): 检索结果中相关文档的比例
    - MRR (Mean Reciprocal Rank): 平均倒数排名
    - 忠实度 (Faithfulness): 生成答案与检索文档的一致性
    - 相关性 (Relevance): 生成答案与问题的相关性

使用：
    python -m evals.run_rag_eval
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.observability.langsmith import setup_langsmith, get_langsmith_client
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """加载 JSONL 文件"""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return data


def calculate_keyword_recall(
    retrieved_docs: List[Dict], golden_keywords: List[str]
) -> float:
    """计算关键词召回率"""
    if not golden_keywords or not retrieved_docs:
        return 0.0

    retrieved_text = " ".join(
        [str(doc.get("content", "")).lower() for doc in retrieved_docs]
    )

    hits = sum(1 for kw in golden_keywords if kw.lower() in retrieved_text)
    return hits / len(golden_keywords)


def calculate_precision(retrieved_docs: List[Dict], golden_doc_ids: List[str]) -> float:
    """计算精确率"""
    if not retrieved_docs:
        return 0.0

    relevant = sum(
        1
        for doc in retrieved_docs
        if doc.get("metadata", {}).get("doc_id") in golden_doc_ids
    )
    return relevant / len(retrieved_docs)


def calculate_mrr(retrieved_docs: List[Dict], golden_doc_ids: List[str]) -> float:
    """计算 MRR"""
    for i, doc in enumerate(retrieved_docs):
        if doc.get("metadata", {}).get("doc_id") in golden_doc_ids:
            return 1.0 / (i + 1)
    return 0.0


def evaluate_rag_generation(
    question: str, retrieved_docs: List[Dict], reference_answer: str
) -> Dict[str, float]:
    """评估 RAG 生成质量"""
    if not retrieved_docs:
        return {"faithfulness": 0.0, "relevance": 0.0}

    context = "\n".join(
        [str(doc.get("content", ""))[:500] for doc in retrieved_docs[:3]]
    )

    prompt = f"""你是一个评估专家。请根据以下检索到的文档片段评估AI生成答案的质量。

检索到的文档：
{context}

参考标准答案：{reference_answer}

请评估以下指标（0-1分）：
1. 忠实度(Faithfulness)：生成答案是否与检索文档一致
2. 相关性(Relevance)：生成答案是否与问题相关

请返回JSON格式：
{{
    "faithfulness": 0.0-1.0,
    "relevance": 0.0-1.0,
    "reason": "简短评估理由"
}}
"""

    try:
        response = llm_service.chat_json(
            [{"role": "user", "content": prompt}],
            system_prompt="你是一个专业的AI评估助手",
        )
        result = json.loads(response)
        return {
            "faithfulness": float(result.get("faithfulness", 0.0)),
            "relevance": float(result.get("relevance", 0.0)),
            "reason": result.get("reason", ""),
        }
    except Exception as e:
        print(f"生成评估失败: {e}")
        return {"faithfulness": 0.0, "relevance": 0.0, "reason": str(e)}


def run_rag_eval():
    """运行 RAG 评估"""
    setup_langsmith()
    client = get_langsmith_client()

    dataset_path = Path(__file__).parent / "data" / "rag_eval_dataset.jsonl"
    if not dataset_path.exists():
        print(f"数据集文件不存在: {dataset_path}")
        return

    examples = load_jsonl(str(dataset_path))
    if not examples:
        print("数据集为空")
        return

    project_id = "eval-project-001"
    results = []

    print("=" * 60)
    print("RAG 评估开始")
    print("=" * 60)

    for i, item in enumerate(examples):
        question = item.get("question", "")
        golden_keywords = item.get("golden_keywords", [])
        golden_doc_ids = item.get("doc_ids", [])
        reference_answer = item.get("reference_answer", "")

        print(f"\n[{i+1}/{len(examples)}] 问题: {question[:30]}...")

        search_result = rag_service.search_with_status(
            project_id=project_id, query=question, top_k=5
        )

        retrieved_docs = search_result.get("data", [])

        recall = calculate_keyword_recall(retrieved_docs, golden_keywords)
        precision = calculate_precision(retrieved_docs, golden_doc_ids)
        mrr = calculate_mrr(retrieved_docs, golden_doc_ids)

        generation_eval = evaluate_rag_generation(
            question, retrieved_docs, reference_answer
        )

        result = {
            "question": question,
            "golden_keywords": golden_keywords,
            "golden_doc_ids": golden_doc_ids,
            "retrieved_count": len(retrieved_docs),
            "recall": recall,
            "precision": precision,
            "mrr": mrr,
            "faithfulness": generation_eval.get("faithfulness", 0.0),
            "relevance": generation_eval.get("relevance", 0.0),
        }
        results.append(result)

        print(f"  召回率: {recall:.2f}, 精确率: {precision:.2f}, MRR: {mrr:.2f}")
        print(
            f"  忠实度: {generation_eval.get('faithfulness', 0):.2f}, 相关性: {generation_eval.get('relevance', 0):.2f}"
        )

        if client and (i + 1) % 5 == 0:
            try:
                client.create_example(
                    inputs={"question": question},
                    outputs={
                        "recall": recall,
                        "precision": precision,
                        "mrr": mrr,
                        "faithfulness": generation_eval.get("faithfulness", 0),
                        "relevance": generation_eval.get("relevance", 0),
                    },
                    dataset_name="TestPlatform-RAG-Eval",
                )
            except Exception as e:
                print(f"  推送 LangSmith 失败: {e}")

    avg_recall = sum(r["recall"] for r in results) / len(results)
    avg_precision = sum(r["precision"] for r in results) / len(results)
    avg_mrr = sum(r["mrr"] for r in results) / len(results)
    avg_faithfulness = sum(r["faithfulness"] for r in results) / len(results)
    avg_relevance = sum(r["relevance"] for r in results) / len(results)

    print("\n" + "=" * 60)
    print("RAG 评估结果汇总")
    print("=" * 60)
    print(f"平均召回率 (Recall):    {avg_recall:.4f}")
    print(f"平均精确率 (Precision): {avg_precision:.4f}")
    print(f"平均 MRR:              {avg_mrr:.4f}")
    print(f"平均忠实度 (Faithfulness): {avg_faithfulness:.4f}")
    print(f"平均相关性 (Relevance):   {avg_relevance:.4f}")
    print("=" * 60)

    results_file = Path(__file__).parent / "data" / "rag_eval_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "summary": {
                    "avg_recall": avg_recall,
                    "avg_precision": avg_precision,
                    "avg_mrr": avg_mrr,
                    "avg_faithfulness": avg_faithfulness,
                    "avg_relevance": avg_relevance,
                },
                "details": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n评估结果已保存到: {results_file}")


if __name__ == "__main__":
    run_rag_eval()
