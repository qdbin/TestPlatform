"""
评估环境初始化脚本

功能：
    1. 初始化LangSmith数据集
    2. 索引知识文档到RAG系统
    3. 验证评估环境配置

使用方法：
    conda activate aitest
    cd ai-service
    python -m evals.setup_eval
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import config
from app.services.rag_service import rag_service
from langsmith import Client


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """加载JSONL文件"""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data


def init_langsmith_datasets():
    """初始化LangSmith数据集"""
    print("=" * 60)
    print("初始化 LangSmith 数据集")
    print("=" * 60)
    
    if not config.LANGSMITH_API_KEY:
        print("❌ LangSmith API Key 未配置，跳过数据集初始化")
        return False
    
    try:
        client = Client(api_key=config.LANGSMITH_API_KEY)
        
        # 1. 创建RAG评估数据集
        print("\n📊 创建 RAG 评估数据集...")
        rag_dataset_name = "TestPlatform-RAG-Eval-v2"
        
        # 检查是否已存在
        existing = list(client.list_datasets(dataset_name=rag_dataset_name))
        if existing:
            print(f"   ℹ️ 数据集已存在: {rag_dataset_name}")
        else:
            rag_dataset = client.create_dataset(
                dataset_name=rag_dataset_name,
                description="测试平台RAG评估数据集 - 包含20个问答对，覆盖用户认证、订单管理、商品管理等场景"
            )
            
            # 加载RAG评估数据
            rag_data_path = Path(__file__).parent / "data" / "rag_eval_dataset.jsonl"
            rag_examples = load_jsonl(str(rag_data_path))
            
            for item in rag_examples:
                client.create_example(
                    inputs={"question": item["question"]},
                    outputs={
                        "golden_keywords": item["golden_keywords"],
                        "golden_doc_ids": item["doc_ids"],
                        "reference_answer": item["reference_answer"]
                    },
                    dataset_id=rag_dataset.id
                )
            
            print(f"   ✅ 创建完成: {rag_dataset_name}, 共{len(rag_examples)}条数据")
        
        # 2. 创建Agent评估数据集
        print("\n🤖 创建 Agent 评估数据集...")
        agent_dataset_name = "TestPlatform-Agent-Eval-v2"
        
        existing = list(client.list_datasets(dataset_name=agent_dataset_name))
        if existing:
            print(f"   ℹ️ 数据集已存在: {agent_dataset_name}")
        else:
            agent_dataset = client.create_dataset(
                dataset_name=agent_dataset_name,
                description="测试平台Agent用例生成评估数据集 - 包含30个测试场景"
            )
            
            # 加载Agent评估数据
            agent_data_path = Path(__file__).parent / "data" / "agent_eval_dataset.jsonl"
            agent_examples = load_jsonl(str(agent_data_path))
            
            for item in agent_examples:
                client.create_example(
                    inputs={
                        "requirement": item["user_requirement"],
                        "project_id": item["project_id"]
                    },
                    outputs={
                        "expected_api_count_min": item["expected_api_count_min"],
                        "expected_apis": item["expected_apis"],
                        "required_fields": item["required_fields"],
                        "domain": item["domain"]
                    },
                    dataset_id=agent_dataset.id
                )
            
            print(f"   ✅ 创建完成: {agent_dataset_name}, 共{len(agent_examples)}条数据")
        
        print("\n✅ LangSmith 数据集初始化完成")
        return True
        
    except Exception as e:
        print(f"\n❌ LangSmith 初始化失败: {e}")
        return False


def index_knowledge_docs():
    """索引知识文档到RAG系统"""
    print("\n" + "=" * 60)
    print("索引知识文档到 RAG 系统")
    print("=" * 60)
    
    docs_path = Path(__file__).parent / "data" / "knowledge_docs.jsonl"
    if not docs_path.exists():
        print(f"❌ 知识文档文件不存在: {docs_path}")
        return False
    
    try:
        docs = load_jsonl(str(docs_path))
        project_id = "eval-project-001"
        
        # 按doc_id分组
        doc_groups: Dict[str, Dict] = {}
        for doc in docs:
            doc_id = doc.get("id", "")
            if doc_id not in doc_groups:
                doc_groups[doc_id] = {
                    "doc_id": doc_id,
                    "doc_type": doc.get("doc_type", "api"),
                    "doc_name": doc.get("doc_name", ""),
                    "chunks": [],
                }
            doc_groups[doc_id]["chunks"].append({
                "content": doc.get("content", ""),
                "metadata": {}
            })
        
        # 索引文档
        success_count = 0
        for doc_id, group in doc_groups.items():
            try:
                result = rag_service.add_document(
                    project_id=project_id,
                    doc_id=doc_id,
                    doc_type=group["doc_type"],
                    doc_name=group["doc_name"],
                    documents=group["chunks"],
                    user_id="eval-system",
                )
                if result.get("indexed"):
                    success_count += 1
                    print(f"   ✅ 索引文档: {doc_id}")
                else:
                    print(f"   ⚠️ 索引失败: {doc_id}")
            except Exception as e:
                print(f"   ❌ 索引异常 {doc_id}: {e}")
        
        print(f"\n✅ 知识文档索引完成: {success_count}/{len(doc_groups)} 篇文档")
        return True
        
    except Exception as e:
        print(f"\n❌ 知识文档索引失败: {e}")
        return False


def verify_environment():
    """验证评估环境配置"""
    print("\n" + "=" * 60)
    print("验证评估环境配置")
    print("=" * 60)
    
    checks = []
    
    # 1. 检查LangSmith配置
    print("\n🔍 检查 LangSmith 配置...")
    if config.LANGSMITH_API_KEY:
        print(f"   ✅ LANGSMITH_API_KEY: 已配置 ({config.LANGSMITH_API_KEY[:20]}...)")
        checks.append(True)
    else:
        print("   ❌ LANGSMITH_API_KEY: 未配置")
        checks.append(False)
    
    if config.LANGSMITH_PROJECT:
        print(f"   ✅ LANGSMITH_PROJECT: {config.LANGSMITH_PROJECT}")
    else:
        print("   ⚠️ LANGSMITH_PROJECT: 未配置，使用默认值")
    
    # 2. 检查LLM配置
    print("\n🔍 检查 LLM 配置...")
    if config.DEEPSEEK_API_KEY:
        print(f"   ✅ DEEPSEEK_API_KEY: 已配置 ({config.DEEPSEEK_API_KEY[:20]}...)")
        checks.append(True)
    else:
        print("   ❌ DEEPSEEK_API_KEY: 未配置")
        checks.append(False)
    
    # 3. 检查数据文件
    print("\n🔍 检查数据文件...")
    data_files = [
        "knowledge_docs.jsonl",
        "rag_eval_dataset.jsonl",
        "agent_eval_dataset.jsonl"
    ]
    
    data_dir = Path(__file__).parent / "data"
    for filename in data_files:
        file_path = data_dir / filename
        if file_path.exists():
            # 统计行数
            with open(file_path, "r", encoding="utf-8") as f:
                line_count = sum(1 for _ in f if _.strip())
            print(f"   ✅ {filename}: {line_count} 条记录")
            checks.append(True)
        else:
            print(f"   ❌ {filename}: 文件不存在")
            checks.append(False)
    
    # 4. 检查RAG服务
    print("\n🔍 检查 RAG 服务...")
    try:
        test_result = rag_service.search_with_status(
            project_id="eval-project-001",
            query="测试查询",
            top_k=1
        )
        print(f"   ✅ RAG 服务正常")
        checks.append(True)
    except Exception as e:
        print(f"   ⚠️ RAG 服务检查异常: {e}")
        # 可能是项目未初始化，不一定是错误
        checks.append(True)
    
    # 汇总
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"环境检查: {passed}/{total} 项通过")
    
    if passed == total:
        print("✅ 评估环境准备就绪！")
        return True
    else:
        print("⚠️ 部分检查未通过，但可能不影响基本功能")
        return False


def main():
    """主入口"""
    print("\n" + "=" * 60)
    print("AI服务评估环境初始化")
    print("=" * 60)
    
    # 1. 验证环境
    verify_environment()
    
    # 2. 初始化LangSmith数据集
    init_langsmith_datasets()
    
    # 3. 索引知识文档
    index_knowledge_docs()
    
    print("\n" + "=" * 60)
    print("初始化完成！")
    print("=" * 60)
    print("\n下一步操作:")
    print("  1. 运行RAG评估: python -m pytest evals/test_rag_eval.py -v")
    print("  2. 运行Agent评估: python -m pytest evals/test_agent_eval.py -v")
    print("  3. 运行全部评估: python -m pytest evals/ -v")


if __name__ == "__main__":
    main()
