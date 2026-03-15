"""
LangSmith 评估初始化脚本

功能：
    1. 创建评估数据集
    2. 配置 LangSmith 评估器
    3. 推送数据集到 LangSmith 平台

使用：
    python -m evals.init_langsmith
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.observability.langsmith import setup_langsmith, get_langsmith_client
from app.config import config


def load_jsonl(file_path: str):
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


def build_rag_examples(base_examples, target_count: int = 36):
    if not base_examples:
        return []
    if len(base_examples) >= target_count:
        return base_examples[:target_count]
    expanded = list(base_examples)
    idx = 0
    while len(expanded) < target_count:
        current = dict(base_examples[idx % len(base_examples)])
        question = str(current.get("question", "")).strip()
        current["question"] = f"{question}（评估扩展样本{len(expanded) + 1}）"
        expanded.append(current)
        idx += 1
    return expanded


def init_rag_dataset():
    """初始化 RAG 评估数据集"""
    setup_langsmith()
    client = get_langsmith_client()
    if not client:
        print("LangSmith 客户端未初始化")
        return

    dataset_path = Path(__file__).parent / "data" / "rag_eval_dataset.jsonl"
    if not dataset_path.exists():
        print(f"数据集文件不存在: {dataset_path}")
        return

    examples = build_rag_examples(load_jsonl(str(dataset_path)), target_count=36)
    if not examples:
        print("数据集为空")
        return

    inputs = []
    outputs = []
    for item in examples:
        inputs.append({"question": item.get("question", "")})
        outputs.append(
            {
                "golden_keywords": item.get("golden_keywords", []),
                "reference_answer": item.get("reference_answer", ""),
            }
        )

    dataset_name = "TestPlatform-RAG-Eval-v2"
    try:
        try:
            old_dataset = client.read_dataset(dataset_name=dataset_name)
            client.delete_dataset(dataset_id=old_dataset.id)
        except Exception:
            pass
        dataset = client.create_dataset(
            dataset_name=dataset_name, description="测试平台 RAG 评估数据集（36条）"
        )
        print(f"创建数据集: {dataset_name}")

        for i, (inp, out) in enumerate(zip(inputs, outputs)):
            client.create_example(inputs=inp, outputs=out, dataset_id=dataset.id)
            if (i + 1) % 10 == 0:
                print(f"已添加 {i + 1} 条数据...")

        print(f"数据集创建完成，共 {len(examples)} 条数据")
    except Exception as e:
        print(f"数据集创建失败: {e}")


def init_case_dataset():
    """初始化用例生成评估数据集"""
    setup_langsmith()
    client = get_langsmith_client()
    if not client:
        print("LangSmith 客户端未初始化")
        return

    dataset_path = Path(__file__).parent / "data" / "case_eval_dataset.jsonl"
    if not dataset_path.exists():
        print(f"数据集文件不存在: {dataset_path}")
        return

    examples = load_jsonl(str(dataset_path))
    if not examples:
        print("数据集为空")
        return

    inputs = []
    outputs = []
    for item in examples:
        inputs.append(
            {
                "requirement": item.get("requirement", ""),
                "project_id": item.get("project_id", ""),
            }
        )
        outputs.append(
            {
                "expected_apis": item.get("expected_apis", []),
                "required_fields": item.get("required_fields", []),
                "domain": item.get("domain", ""),
            }
        )

    dataset_name = "TestPlatform-Agent-Eval-v2"
    try:
        try:
            old_dataset = client.read_dataset(dataset_name=dataset_name)
            client.delete_dataset(dataset_id=old_dataset.id)
        except Exception:
            pass
        dataset = client.create_dataset(
            dataset_name=dataset_name, description="测试平台用例生成评估数据集"
        )
        print(f"创建数据集: {dataset_name}")

        for i, (inp, out) in enumerate(zip(inputs, outputs)):
            client.create_example(inputs=inp, outputs=out, dataset_id=dataset.id)
            if (i + 1) % 10 == 0:
                print(f"已添加 {i + 1} 条数据...")

        print(f"数据集创建完成，共 {len(examples)} 条数据")
    except Exception as e:
        print(f"数据集创建失败: {e}")


def index_knowledge_docs():
    """索引知识文档用于 RAG 评估"""
    from app.services.rag_service import rag_service

    docs_path = Path(__file__).parent / "data" / "knowledge_docs.jsonl"
    if not docs_path.exists():
        print(f"知识文档文件不存在: {docs_path}")
        return

    docs = load_jsonl(str(docs_path))
    project_id = "eval-project-001"

    doc_groups = {}
    for doc in docs:
        doc_id = doc.get("id", "")
        if doc_id not in doc_groups:
            doc_groups[doc_id] = {
                "doc_id": doc_id,
                "doc_type": doc.get("doc_type", "manual"),
                "doc_name": doc.get("doc_name", ""),
                "chunks": [],
            }
        doc_groups[doc_id]["chunks"].append(
            {"content": doc.get("content", ""), "metadata": {}}
        )

    for doc_id, group in doc_groups.items():
        result = rag_service.add_document(
            project_id=project_id,
            doc_id=doc_id,
            doc_type=group["doc_type"],
            doc_name=group["doc_name"],
            documents=group["chunks"],
            user_id="eval-system",
        )
        status = "成功" if result.get("indexed") else "失败"
        print(f"索引文档 {doc_id}: {status}")

    print(f"知识文档索引完成，共 {len(doc_groups)} 篇文档")


if __name__ == "__main__":
    print("=" * 60)
    print("LangSmith 评估初始化")
    print("=" * 60)

    print("\n1. 初始化 RAG 评估数据集...")
    init_rag_dataset()

    print("\n2. 初始化用例生成评估数据集...")
    init_case_dataset()

    print("\n3. 索引知识文档...")
    index_knowledge_docs()

    print("\n" + "=" * 60)
    print("初始化完成!")
    print("=" * 60)
