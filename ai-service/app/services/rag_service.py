"""
RAG服务模块
负责向量存储、检索等RAG相关功能
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import config


class RAGService:
    """RAG服务类"""

    def __init__(self):
        self._embeddings = None
        self._client = None

    def _init_components(self) -> None:
        """延迟初始化向量存储组件"""
        if self._embeddings is None:
            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=config.embedding_model,
                    model_kwargs={"device": config.embedding_device},
                )
            except Exception as e:
                print(f"Embedding模型加载失败: {e}")
                self._embeddings = None

        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=config.chroma_persist_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )

    def _get_collection_name(self, project_id: str) -> str:
        """获取项目对应的collection名称"""
        return f"{config.chroma_prefix}{project_id}"

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
        if not documents:
            return

        self._init_components()

        if self._embeddings is None:
            print("警告：Embedding模型未加载，跳过索引")
            return

        embeddings = self._embeddings.embed_documents(documents)

        collection = self._get_or_create_collection(project_id)

        ids = [f"{knowledge_id}_{i}" for i in range(len(documents))]

        metadatas = [
            {"knowledge_id": knowledge_id, "chunk_index": i}
            for i in range(len(documents))
        ]

        collection.add(
            embeddings=embeddings, documents=documents, ids=ids, metadatas=metadatas
        )

    def search(
        self, project_id: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """知识库检索"""
        self._init_components()

        if self._embeddings is None:
            print("警告：Embedding模型未加载，返回空结果")
            return []

        query_embedding = self._embeddings.embed_query(query)

        try:
            collection = self._client.get_collection(
                name=self._get_collection_name(project_id)
            )
        except Exception:
            return []

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

        return formatted_results

    def delete_knowledge(self, project_id: str, knowledge_id: str) -> None:
        """删除知识库文档"""
        try:
            self._init_components()
            collection = self._client.get_collection(
                name=self._get_collection_name(project_id)
            )

            result = collection.get()
            if result and result.get("ids"):
                ids_to_delete = [
                    id_val
                    for i, meta in enumerate(result.get("metadatas", []))
                    if meta.get("knowledge_id") == knowledge_id
                ]
                if ids_to_delete:
                    collection.delete(ids=ids_to_delete)
        except Exception:
            pass

    def get_collection_stats(self, project_id: str) -> Dict[str, Any]:
        """获取知识库统计信息"""
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
