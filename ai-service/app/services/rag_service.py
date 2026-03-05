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
import httpx
from app.config import config


class OpenAIEmbeddingFunction:
    """使用OpenAI兼容API的Embedding函数（支持OpenAI、Ollama等）"""
    
    def __init__(self, api_key: str = "", base_url: str = "https://api.openai.com/v1", model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """生成文档向量"""
        embeddings = []
        for text in input:
            try:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = httpx.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json={"model": self.model, "input": text},
                    timeout=60.0
                )
                if response.status_code == 200:
                    data = response.json()
                    embedding = data.get("data", [{}])[0].get("embedding", [])
                    embeddings.append(embedding)
                else:
                    print(f"Embedding API错误: {response.status_code} - {response.text[:200]}")
                    return []
            except Exception as e:
                print(f"Embedding失败: {e}")
                return []
        return embeddings
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self(documents)
    
    def embed_query(self, query: str) -> List[float]:
        result = self([query])
        return result[0] if result else []


class OllamaEmbeddingFunction:
    """使用Ollama的Embedding函数（本地部署，完全免费）"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """生成文档向量"""
        embeddings = []
        for text in input:
            try:
                response = httpx.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=60.0
                )
                if response.status_code == 200:
                    data = response.json()
                    embedding = data.get("embedding", [])
                    embeddings.append(embedding)
                else:
                    print(f"Ollama Embedding错误: {response.status_code}")
                    return []
            except Exception as e:
                print(f"Ollama Embedding失败: {e}，请确保Ollama已启动")
                return []
        return embeddings
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self(documents)
    
    def embed_query(self, query: str) -> List[float]:
        result = self([query])
        return result[0] if result else []


class RAGService:
    """RAG服务类"""

    def __init__(self):
        self._embedding_func = None
        self._client = None
        self._fallback_docs = None
        self._embedding_init_failed = False
        self._embedding_warning_logged = False

    def _init_components(self) -> None:
        """延迟初始化向量存储组件"""
        if self._embedding_func is None and not self._embedding_init_failed:
            provider = config.get("embedding.provider", "ollama")
            
            if provider == "openai":
                try:
                    api_key = config.get("embedding.openai_api_key", "")
                    base_url = config.get("embedding.openai_base_url", "https://api.openai.com/v1")
                    model = config.get("embedding.openai_model", "text-embedding-3-small")
                    if not api_key:
                        raise ValueError("未配置OpenAI API Key")
                    self._embedding_func = OpenAIEmbeddingFunction(api_key, base_url, model)
                    self._embedding_init_failed = False
                    print(f"Embedding模型加载成功: OpenAI兼容API ({model}) @ {base_url}")
                except Exception as e:
                    print(f"OpenAI Embedding加载失败: {e}")
                    self._embedding_func = None
                    self._embedding_init_failed = True
            elif provider == "ollama":
                try:
                    ollama_url = config.get("embedding.ollama_url", "http://localhost:11434")
                    ollama_model = config.get("embedding.ollama_model", "nomic-embed-text")
                    self._embedding_func = OllamaEmbeddingFunction(ollama_url, ollama_model)
                    self._embedding_init_failed = False
                    print(f"Embedding模型加载成功: Ollama ({ollama_model})")
                except Exception as e:
                    print(f"Ollama Embedding加载失败: {e}")
                    self._embedding_func = None
                    self._embedding_init_failed = True
            else:
                print(f"未知的Embedding provider: {provider}，使用关键词匹配检索")
                self._embedding_func = None
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

    def _delete_fallback_docs(self, project_id: str, knowledge_id: str) -> bool:
        project_id = str(project_id)
        knowledge_id = str(knowledge_id)
        store = self._load_fallback_docs()
        project_docs = store.get(project_id)
        if isinstance(project_docs, dict) and knowledge_id in project_docs:
            project_docs.pop(knowledge_id, None)
            store[project_id] = project_docs
            self._fallback_docs = store
            self._save_fallback_docs()
            return True
        return False

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
    ) -> Dict[str, Any]:
        """添加文档到知识库"""
        project_id = str(project_id)
        knowledge_id = str(knowledge_id)
        if not documents:
            return {"indexed": False, "degraded": False, "vector_count": 0, "error": "empty_documents"}
        
        self._init_components()
        self._upsert_fallback_docs(project_id, knowledge_id, documents)
        
        if self._embedding_func is None:
            return {"indexed": True, "degraded": True, "vector_count": len(documents), "error": "embedding_unavailable"}
        
        try:
            embeddings = self._embedding_func.embed_documents(documents)
            collection = self._get_or_create_collection(project_id)
            ids = [f"{knowledge_id}_{i}" for i in range(len(documents))]
            metadatas = [{"knowledge_id": knowledge_id, "chunk_index": i} for i in range(len(documents))]
            
            try:
                collection.upsert(embeddings=embeddings, documents=documents, ids=ids, metadatas=metadatas)
            except AttributeError:
                collection.add(embeddings=embeddings, documents=documents, ids=ids, metadatas=metadatas)
            
            return {"indexed": True, "degraded": False, "vector_count": len(ids), "error": ""}
        except Exception as e:
            print(f"向量索引失败: {e}")
            return {"indexed": True, "degraded": True, "vector_count": len(documents), "error": str(e)}

    def search(
        self, project_id: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """知识库检索"""
        project_id = str(project_id)
        self._init_components()
        
        if self._embedding_func is None:
            return self._fallback_search(project_id, query, top_k)
        
        try:
            query_embedding = self._embedding_func.embed_query(query)
            collection = self._client.get_collection(name=self._get_collection_name(project_id))
            results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
            
            formatted_results = []
            if results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "distance": results["distances"][0][i] if results.get("distances") else 0,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    })
            
            if not formatted_results:
                return self._fallback_search(project_id, query, top_k)
            
            filtered = [item for item in formatted_results if not isinstance(item.get("distance"), (int, float)) or float(item.get("distance")) <= 1.5]
            return filtered if filtered else self._fallback_search(project_id, query, top_k)
        except Exception as e:
            print(f"向量检索失败: {e}")
            return self._fallback_search(project_id, query, top_k)

    def delete_knowledge(self, project_id: str, knowledge_id: str) -> Dict[str, Any]:
        """删除知识库文档"""
        project_id = str(project_id)
        knowledge_id = str(knowledge_id)
        fallback_deleted = self._delete_fallback_docs(project_id, knowledge_id)
        vector_deleted = 0
        try:
            self._init_components()
            if self._client is None:
                return {"status": "success", "vector_deleted": vector_deleted, "fallback_deleted": fallback_deleted}

            collection_name = self._get_collection_name(project_id)
            try:
                collection = self._client.get_collection(name=collection_name)
            except ValueError:
                return {"status": "success", "vector_deleted": vector_deleted, "fallback_deleted": fallback_deleted}

            ids_to_delete: List[str] = []
            try:
                existing = collection.get(where={"knowledge_id": knowledge_id})
                if isinstance(existing, dict) and isinstance(existing.get("ids"), list):
                    ids_to_delete = [str(item) for item in existing.get("ids") if item]
            except TypeError:
                existing = collection.get()
                all_ids = existing.get("ids") if isinstance(existing, dict) else []
                all_meta = existing.get("metadatas") if isinstance(existing, dict) else []
                if isinstance(all_ids, list) and isinstance(all_meta, list):
                    for idx, current_id in enumerate(all_ids):
                        metadata = all_meta[idx] if idx < len(all_meta) else {}
                        if isinstance(metadata, dict) and str(metadata.get("knowledge_id")) == knowledge_id:
                            ids_to_delete.append(str(current_id))
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                vector_deleted = len(ids_to_delete)
            return {"status": "success", "vector_deleted": vector_deleted, "fallback_deleted": fallback_deleted}
        except Exception as e:
            print(f"Chroma删除失败: {e}")
            return {"status": "error", "vector_deleted": vector_deleted, "fallback_deleted": fallback_deleted, "error": str(e)}

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
