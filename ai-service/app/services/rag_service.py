"""
RAG服务模块
负责向量存储、检索等RAG相关功能
"""

from typing import List, Dict, Any, Optional
import os
import json
import re
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import config


class RAGService:
    """RAG服务类"""

    def __init__(self):
        self._embeddings = None
        self._client = None
        self._fallback_docs = None
        self._embedding_init_failed = False
        self._embedding_warning_logged = False

    def _init_components(self) -> None:
        """延迟初始化向量存储组件"""
        if self._embeddings is None and not self._embedding_init_failed:
            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=config.embedding_model,
                    model_kwargs={"device": config.embedding_device},
                )
                self._embedding_init_failed = False
            except Exception as e:
                print(f"Embedding模型加载失败: {e}")
                self._embeddings = None
                self._embedding_init_failed = True

        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=config.chroma_persist_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )

    def _get_collection_name(self, project_id: str) -> str:
        """获取项目对应的collection名称"""
        return f"{config.chroma_prefix}{str(project_id)}"

    def _get_fallback_store_path(self) -> str:
        os.makedirs(config.chroma_persist_dir, exist_ok=True)
        return os.path.join(config.chroma_persist_dir, "fallback_docs.json")

    def _load_fallback_docs(self) -> Dict[str, Dict[str, List[str]]]:
        if self._fallback_docs is not None:
            return self._fallback_docs
        path = self._get_fallback_store_path()
        if not os.path.exists(path):
            self._fallback_docs = {}
            return self._fallback_docs
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._fallback_docs = data if isinstance(data, dict) else {}
        except Exception:
            self._fallback_docs = {}
        return self._fallback_docs

    def _save_fallback_docs(self) -> None:
        path = self._get_fallback_store_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._fallback_docs or {}, f, ensure_ascii=False)

    def _upsert_fallback_docs(
        self, project_id: str, knowledge_id: str, documents: List[str]
    ) -> None:
        project_id = str(project_id)
        knowledge_id = str(knowledge_id)
        store = self._load_fallback_docs()
        project_docs = store.get(project_id)
        if not isinstance(project_docs, dict):
            project_docs = {}
        project_docs[knowledge_id] = documents
        store[project_id] = project_docs
        self._fallback_docs = store
        self._save_fallback_docs()

    def _delete_fallback_docs(self, project_id: str, knowledge_id: str) -> None:
        project_id = str(project_id)
        knowledge_id = str(knowledge_id)
        store = self._load_fallback_docs()
        project_docs = store.get(project_id)
        if isinstance(project_docs, dict) and knowledge_id in project_docs:
            project_docs.pop(knowledge_id, None)
            store[project_id] = project_docs
            self._fallback_docs = store
            self._save_fallback_docs()

    def _fallback_search(
        self, project_id: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        project_id = str(project_id)
        store = self._load_fallback_docs()
        project_docs = store.get(project_id)
        if not isinstance(project_docs, dict):
            return []
        raw_terms = re.findall(r"[\u4e00-\u9fffA-Za-z0-9_]+", query or "")
        terms: List[str] = []
        for token in raw_terms:
            token = token.strip()
            if not token:
                continue
            terms.append(token)
            if re.search(r"[\u4e00-\u9fff]", token) and len(token) > 2:
                for i in range(len(token) - 1):
                    terms.append(token[i : i + 2])
        if not terms and query:
            terms = [query]
        scored: List[Dict[str, Any]] = []
        for knowledge_id, docs in project_docs.items():
            if not isinstance(docs, list):
                continue
            for index, doc in enumerate(docs):
                text = str(doc or "")
                score = sum(text.count(term) for term in terms) if terms else 0
                if score <= 0 and query and query not in text:
                    continue
                scored.append(
                    {
                        "content": text,
                        "distance": 0,
                        "metadata": {
                            "knowledge_id": knowledge_id,
                            "chunk_index": index,
                            "fallback": True,
                        },
                        "score": score,
                    }
                )
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        return [
            {
                "content": item.get("content"),
                "distance": item.get("distance"),
                "metadata": item.get("metadata"),
            }
            for item in scored[:top_k]
        ]

    def _get_or_create_collection(self, project_id: str):
        """获取或创建项目的向量集合"""
        if self._client is None:
            self._init_components()
        collection_name = self._get_collection_name(project_id)
        return self._client.get_or_create_collection(
            name=collection_name, metadata={"project_id": project_id}
        )

    def add_documents(
        self, project_id: str, knowledge_id: str, documents: List[str]
    ) -> None:
        """添加文档到知识库"""
        project_id = str(project_id)
        knowledge_id = str(knowledge_id)
        if not documents:
            return
        self._upsert_fallback_docs(project_id, knowledge_id, documents)

        self._init_components()

        if self._embeddings is None:
            if not self._embedding_warning_logged:
                print("警告：Embedding模型未加载，已写入回退检索存储")
                self._embedding_warning_logged = True
            return

        embeddings = self._embeddings.embed_documents(documents)

        collection = self._get_or_create_collection(project_id)

        ids = [f"{knowledge_id}_{i}" for i in range(len(documents))]

        metadatas = [
            {"knowledge_id": knowledge_id, "chunk_index": i}
            for i in range(len(documents))
        ]

        try:
            collection.upsert(
                embeddings=embeddings, documents=documents, ids=ids, metadatas=metadatas
            )
        except AttributeError:
            collection.add(
                embeddings=embeddings, documents=documents, ids=ids, metadatas=metadatas
            )

    def search(
        self, project_id: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """知识库检索"""
        project_id = str(project_id)
        self._init_components()

        if self._embeddings is None:
            if not self._embedding_warning_logged:
                print("警告：Embedding模型未加载，使用回退检索")
                self._embedding_warning_logged = True
            return self._fallback_search(project_id, query, top_k)

        query_embedding = self._embeddings.embed_query(query)

        try:
            collection = self._client.get_collection(
                name=self._get_collection_name(project_id)
            )
        except Exception:
            return self._fallback_search(project_id, query, top_k)

        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

        formatted_results = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append(
                    {
                        "content": doc,
                        "distance": (
                            results["distances"][0][i]
                            if results.get("distances")
                            else 0
                        ),
                        "metadata": (
                            results["metadatas"][0][i]
                            if results.get("metadatas")
                            else {}
                        ),
                    }
                )

        if not formatted_results:
            return self._fallback_search(project_id, query, top_k)
        filtered = [
            item
            for item in formatted_results
            if not isinstance(item.get("distance"), (int, float))
            or float(item.get("distance")) <= 1.2
        ]
        if filtered:
            return filtered
        return self._fallback_search(project_id, query, top_k)

    def delete_knowledge(self, project_id: str, knowledge_id: str) -> None:
        """删除知识库文档"""
        project_id = str(project_id)
        knowledge_id = str(knowledge_id)
        self._delete_fallback_docs(project_id, knowledge_id)
        try:
            self._init_components()
            if self._client is None: return
            
            collection_name = self._get_collection_name(project_id)
            try:
                collection = self._client.get_collection(name=collection_name)
            except Exception:
                return

            # 使用 where 过滤器直接删除，比先 get 再 delete 更高效且准确
            collection.delete(where={"knowledge_id": knowledge_id})
            
        except Exception as e:
            print(f"Chroma删除失败: {e}")

    def get_collection_stats(self, project_id: str) -> Dict[str, Any]:
        """获取知识库统计信息"""
        project_id = str(project_id)
        try:
            self._init_components()
            collection = self._client.get_collection(
                name=self._get_collection_name(project_id)
            )
            return {
                "count": collection.count(),
                "project_id": project_id,
                "collection_name": self._get_collection_name(project_id),
            }
        except Exception:
            return {
                "count": 0,
                "project_id": project_id,
                "collection_name": self._get_collection_name(project_id),
            }


rag_service = RAGService()
