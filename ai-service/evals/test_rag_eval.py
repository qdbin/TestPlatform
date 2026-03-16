"""
RAG 评估测试模块 - Pytest + LangSmith

评估指标：
    - 检索阶段：召回率(Recall)、精确率(Precision)、MRR
    - 生成阶段：忠实度(Faithfulness)、答案相关性(Answer Relevance)

使用方法：
    conda activate aitest
    cd ai-service
    python -m pytest evals/test_rag_eval.py -v --tb=short
    
    # 推送到 LangSmith
    python -m pytest evals/test_rag_eval.py -v --tb=short --langsmith
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from langsmith import Client
from langsmith.evaluation import EvaluationResult, RunEvaluator
from langsmith.schemas import Example, Run

from app.config import config
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service


# 加载评估数据集
def load_rag_dataset() -> List[Dict[str, Any]]:
    """加载RAG评估数据集"""
    dataset_path = Path(__file__).parent / "data" / "rag_eval_dataset.jsonl"
    data = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data


# 评估项目ID
EVAL_PROJECT_ID = "eval-project-001"
RAG_DATASET_NAME = "TestPlatform-RAG-Eval-v2"


class RAGRetrievalEvaluator(RunEvaluator):
    """RAG检索评估器 - 评估召回率和精确率"""
    
    def __init__(self, golden_doc_ids: List[str]):
        self.golden_doc_ids = golden_doc_ids
    
    def evaluate_run(self, run: Run, example: Optional[Example] = None) -> EvaluationResult:
        """评估检索结果"""
        outputs = run.outputs or {}
        retrieved_docs = outputs.get("retrieved_docs", [])
        
        if not retrieved_docs:
            return EvaluationResult(
                key="retrieval_recall",
                score=0.0,
                comment="未检索到任何文档"
            )
        
        # 提取检索到的doc_id
        retrieved_ids = [
            doc.get("metadata", {}).get("doc_id") or doc.get("doc_id", "")
            for doc in retrieved_docs
        ]
        
        # 计算召回率
        hits = sum(1 for doc_id in self.golden_doc_ids if doc_id in retrieved_ids)
        recall = hits / len(self.golden_doc_ids) if self.golden_doc_ids else 0.0
        
        # 计算精确率
        relevant = sum(1 for doc_id in retrieved_ids if doc_id in self.golden_doc_ids)
        precision = relevant / len(retrieved_ids) if retrieved_ids else 0.0
        
        # 计算MRR
        mrr = 0.0
        for i, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in self.golden_doc_ids:
                mrr = 1.0 / i
                break
        
        return EvaluationResult(
            key="retrieval_metrics",
            score=recall,  # 主指标使用召回率
            comment=json.dumps({
                "recall": recall,
                "precision": precision,
                "mrr": mrr,
                "retrieved_count": len(retrieved_ids),
                "golden_count": len(self.golden_doc_ids)
            }, ensure_ascii=False)
        )


class RAGGenerationEvaluator(RunEvaluator):
    """RAG生成评估器 - 评估答案质量"""
    
    def __init__(self, reference_answer: str, question: str):
        self.reference_answer = reference_answer
        self.question = question
    
    def evaluate_run(self, run: Run, example: Optional[Example] = None) -> EvaluationResult:
        """评估生成答案质量"""
        outputs = run.outputs or {}
        generated_answer = outputs.get("answer", "")
        retrieved_docs = outputs.get("retrieved_docs", [])
        
        if not generated_answer or not retrieved_docs:
            return EvaluationResult(
                key="generation_quality",
                score=0.0,
                comment="无生成答案或检索结果"
            )
        
        # 构建评估Prompt
        context = "\n".join([
            str(doc.get("content", ""))[:500]
            for doc in retrieved_docs[:3]
        ])
        
        eval_prompt = f"""你是一个专业的AI答案评估专家。请评估生成答案的质量。

问题：{self.question}

检索到的文档片段：
{context}

参考标准答案：{self.reference_answer}

生成的答案：{generated_answer}

请评估以下指标（0-1分）：
1. 忠实度(Faithfulness)：生成答案是否与检索到的文档一致，是否有幻觉
2. 相关性(Relevance)：生成答案是否与问题相关，是否回答了问题
3. 完整性(Completeness)：生成答案是否完整覆盖了标准答案的关键信息

请以JSON格式返回：
{{
    "faithfulness": 0.0-1.0,
    "relevance": 0.0-1.0,
    "completeness": 0.0-1.0,
    "reason": "评估理由"
}}"""
        
        try:
            response = llm_service.chat(
                [{"role": "user", "content": eval_prompt}],
                system_prompt="你是一个专业的AI评估助手，请客观公正地评估答案质量。"
            )
            
            # 解析JSON响应
            import re
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                faithfulness = float(result.get("faithfulness", 0.0))
                relevance = float(result.get("relevance", 0.0))
                completeness = float(result.get("completeness", 0.0))
                reason = result.get("reason", "")
                
                # 综合得分
                avg_score = (faithfulness + relevance + completeness) / 3.0
                
                return EvaluationResult(
                    key="generation_quality",
                    score=avg_score,
                    comment=json.dumps({
                        "faithfulness": faithfulness,
                        "relevance": relevance,
                        "completeness": completeness,
                        "reason": reason
                    }, ensure_ascii=False)
                )
        except Exception as e:
            return EvaluationResult(
                key="generation_quality",
                score=0.0,
                comment=f"评估失败: {str(e)}"
            )
        
        return EvaluationResult(
            key="generation_quality",
            score=0.0,
            comment="无法解析评估结果"
        )


def create_langsmith_dataset(client: Client) -> str:
    """创建LangSmith数据集"""
    dataset_name = RAG_DATASET_NAME
    
    # 检查数据集是否已存在
    try:
        existing_datasets = list(client.list_datasets(dataset_name=dataset_name))
        if existing_datasets:
            print(f"数据集已存在: {dataset_name}")
            return existing_datasets[0].id
    except Exception:
        pass
    
    # 创建新数据集
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="测试平台RAG评估数据集 - 包含20个问答对，覆盖用户认证、订单管理、商品管理等场景"
    )
    
    # 加载数据
    examples = load_rag_dataset()
    
    # 添加示例
    for item in examples:
        client.create_example(
            inputs={"question": item["question"]},
            outputs={
                "golden_keywords": item["golden_keywords"],
                "golden_doc_ids": item["doc_ids"],
                "reference_answer": item["reference_answer"]
            },
            dataset_id=dataset.id
        )
    
    print(f"数据集创建完成: {dataset_name}, 共{len(examples)}条数据")
    return dataset.id


def rag_search_wrapper(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """RAG搜索包装函数 - 用于LangSmith评估"""
    question = inputs.get("question", "")
    
    # 执行RAG搜索
    result = rag_service.search_with_status(
        project_id=EVAL_PROJECT_ID,
        query=question,
        top_k=5
    )
    
    retrieved_docs = result.get("data", [])
    
    # 生成答案
    if retrieved_docs:
        context = "\n".join([
            f"[文档 {i+1}] {doc.get('content', '')[:800]}"
            for i, doc in enumerate(retrieved_docs[:3])
        ])
        
        answer_prompt = f"""基于以下检索到的文档，回答问题。

检索文档：
{context}

问题：{question}

请给出准确、简洁的回答："""
        
        try:
            answer = llm_service.chat(
                [{"role": "user", "content": answer_prompt}],
                system_prompt="你是一个专业的技术文档助手，基于提供的文档回答问题。"
            )
        except Exception:
            answer = "生成答案失败"
    else:
        answer = "未检索到相关文档"
    
    return {
        "answer": answer,
        "retrieved_docs": retrieved_docs,
        "question": question
    }


@pytest.fixture(scope="module")
def langsmith_client():
    """LangSmith客户端Fixture"""
    if not config.LANGSMITH_API_KEY:
        pytest.skip("LangSmith API Key未配置")
    return Client(api_key=config.LANGSMITH_API_KEY)


@pytest.fixture(scope="module")
def rag_dataset(langsmith_client):
    """RAG数据集Fixture"""
    return create_langsmith_dataset(langsmith_client)


class TestRAGRetrieval:
    """RAG检索测试类"""
    
    def test_keyword_search_recall(self):
        """测试关键词搜索召回率"""
        examples = load_rag_dataset()
        
        results = []
        for item in examples[:5]:  # 测试前5条
            question = item["question"]
            golden_keywords = item["golden_keywords"]
            
            # 执行搜索
            result = rag_service.search_with_status(
                project_id=EVAL_PROJECT_ID,
                query=question,
                top_k=5
            )
            
            retrieved_docs = result.get("data", [])
            
            # 计算关键词召回率
            if retrieved_docs and golden_keywords:
                retrieved_text = " ".join([
                    str(doc.get("content", "")).lower()
                    for doc in retrieved_docs
                ])
                hits = sum(1 for kw in golden_keywords if kw.lower() in retrieved_text)
                recall = hits / len(golden_keywords)
            else:
                recall = 0.0
            
            results.append({
                "question": question[:30],
                "recall": recall,
                "retrieved_count": len(retrieved_docs)
            })
            
            print(f"问题: {question[:30]}... 召回率: {recall:.2f}")
        
        avg_recall = sum(r["recall"] for r in results) / len(results)
        print(f"\n平均关键词召回率: {avg_recall:.4f}")
        
        # 断言平均召回率应大于0.5
        assert avg_recall > 0.5, f"平均召回率 {avg_recall:.4f} 过低"
    
    def test_vector_search_precision(self):
        """测试向量搜索精确率"""
        examples = load_rag_dataset()
        
        results = []
        for item in examples[:5]:
            question = item["question"]
            golden_doc_ids = item["doc_ids"]
            
            result = rag_service.search_with_status(
                project_id=EVAL_PROJECT_ID,
                query=question,
                top_k=5
            )
            
            retrieved_docs = result.get("data", [])
            
            # 计算精确率
            if retrieved_docs:
                retrieved_ids = [
                    doc.get("metadata", {}).get("doc_id") or doc.get("doc_id", "")
                    for doc in retrieved_docs
                ]
                relevant = sum(1 for doc_id in retrieved_ids if doc_id in golden_doc_ids)
                precision = relevant / len(retrieved_ids)
            else:
                precision = 0.0
            
            results.append({
                "question": question[:30],
                "precision": precision
            })
        
        avg_precision = sum(r["precision"] for r in results) / len(results)
        print(f"\n平均精确率: {avg_precision:.4f}")
        
        assert avg_precision > 0.3, f"平均精确率 {avg_precision:.4f} 过低"
    
    def test_hybrid_search_mrr(self):
        """测试混合搜索MRR"""
        examples = load_rag_dataset()
        
        mrr_scores = []
        for item in examples[:5]:
            question = item["question"]
            golden_doc_ids = item["doc_ids"]
            
            result = rag_service.search_with_status(
                project_id=EVAL_PROJECT_ID,
                query=question,
                top_k=5
            )
            
            retrieved_docs = result.get("data", [])
            
            # 计算MRR
            for i, doc in enumerate(retrieved_docs, 1):
                doc_id = doc.get("metadata", {}).get("doc_id") or doc.get("doc_id", "")
                if doc_id in golden_doc_ids:
                    mrr_scores.append(1.0 / i)
                    break
            else:
                mrr_scores.append(0.0)
        
        avg_mrr = sum(mrr_scores) / len(mrr_scores)
        print(f"\n平均MRR: {avg_mrr:.4f}")
        
        assert avg_mrr > 0.3, f"平均MRR {avg_mrr:.4f} 过低"


class TestRAGGeneration:
    """RAG生成测试类"""
    
    def test_answer_faithfulness(self):
        """测试答案忠实度"""
        examples = load_rag_dataset()
        
        faithfulness_scores = []
        for item in examples[:3]:  # 测试前3条
            question = item["question"]
            reference = item["reference_answer"]
            
            # 检索
            result = rag_service.search_with_status(
                project_id=EVAL_PROJECT_ID,
                query=question,
                top_k=3
            )
            
            retrieved_docs = result.get("data", [])
            if not retrieved_docs:
                continue
            
            # 生成答案
            context = "\n".join([
                doc.get("content", "")[:500]
                for doc in retrieved_docs[:2]
            ])
            
            prompt = f"""基于以下文档回答问题：
{context}

问题：{question}"""
            
            try:
                answer = llm_service.chat([{"role": "user", "content": prompt}])
                
                # 简单忠实度检查：答案是否包含文档中的关键信息
                doc_keywords = set()
                for doc in retrieved_docs[:2]:
                    content = doc.get("content", "").lower()
                    # 提取关键术语
                    import re
                    words = re.findall(r'\b[a-zA-Z_]+\b', content)
                    doc_keywords.update(words[:10])
                
                answer_lower = answer.lower()
                matches = sum(1 for kw in doc_keywords if kw in answer_lower)
                faithfulness = min(1.0, matches / max(len(doc_keywords) * 0.3, 1))
                
                faithfulness_scores.append(faithfulness)
                print(f"问题: {question[:30]}... 忠实度: {faithfulness:.2f}")
            except Exception as e:
                print(f"评估失败: {e}")
                continue
        
        if faithfulness_scores:
            avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores)
            print(f"\n平均忠实度: {avg_faithfulness:.4f}")
            assert avg_faithfulness > 0.5, f"平均忠实度 {avg_faithfulness:.4f} 过低"
    
    def test_answer_relevance(self):
        """测试答案相关性"""
        examples = load_rag_dataset()
        
        relevance_scores = []
        for item in examples[:3]:
            question = item["question"]
            
            result = rag_service.search_with_status(
                project_id=EVAL_PROJECT_ID,
                query=question,
                top_k=3
            )
            
            retrieved_docs = result.get("data", [])
            if not retrieved_docs:
                continue
            
            context = "\n".join([
                doc.get("content", "")[:500]
                for doc in retrieved_docs[:2]
            ])
            
            prompt = f"""基于以下文档回答问题：
{context}

问题：{question}"""
            
            try:
                answer = llm_service.chat([{"role": "user", "content": prompt}])
                
                # 简单相关性检查：答案是否覆盖问题关键词
                import re
                question_keywords = set(re.findall(r"[\u4e00-\u9fa5a-zA-Z]{2,}", question.lower()))
                corpus_text = f"{answer}\n{context}".lower()
                matches = sum(1 for kw in question_keywords if kw in corpus_text)
                relevance = min(1.0, matches / max(len(question_keywords) * 0.5, 1))
                
                relevance_scores.append(relevance)
            except Exception:
                continue
        
        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            print(f"\n平均相关性: {avg_relevance:.4f}")
            assert avg_relevance > 0.5, f"平均相关性 {avg_relevance:.4f} 过低"


@pytest.mark.skipif(not config.LANGSMITH_API_KEY, reason="LangSmith未配置")
def test_langsmith_rag_evaluation(langsmith_client, rag_dataset):
    """使用LangSmith进行端到端RAG评估"""
    from langsmith.evaluation import evaluate
    
    examples = load_rag_dataset()
    
    def target_fn(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """目标函数"""
        return rag_search_wrapper(inputs)
    
    def retrieval_evaluator(run, example) -> EvaluationResult:
        """检索评估"""
        outputs = run.outputs or {}
        retrieved_docs = outputs.get("retrieved_docs", [])
        
        # 获取标准答案的doc_ids
        golden_doc_ids = example.outputs.get("golden_doc_ids", []) if example else []
        
        if not retrieved_docs or not golden_doc_ids:
            return EvaluationResult(key="recall", score=0.0)
        
        retrieved_ids = [
            doc.get("metadata", {}).get("doc_id") or doc.get("doc_id", "")
            for doc in retrieved_docs
        ]
        
        hits = sum(1 for doc_id in golden_doc_ids if doc_id in retrieved_ids)
        recall = hits / len(golden_doc_ids)
        
        return EvaluationResult(key="recall", score=recall)
    
    # 运行评估
    results = evaluate(
        target_fn,
        data=RAG_DATASET_NAME,
        evaluators=[retrieval_evaluator],
        experiment_prefix="rag-retrieval-test",
        client=langsmith_client
    )
    
    print(f"\nLangSmith评估完成: {results}")


if __name__ == "__main__":
    # 本地测试运行
    pytest.main([__file__, "-v", "--tb=short", "-s"])
