from typing import List, Dict, Any, Optional
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
    def __init__(self):
        self._embedding_func = None
        self._client = None
        self._collection = None
        self._embedding_init_failed = False

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

    def _get_or_create_collection(self):
        if self._client is None:
            self._init_components()
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=config.chroma_collection_name,
                metadata={"scope": "all_projects"},
            )
        return self._collection

    def add_document(
        self,
        project_id: str,
        doc_id: str,
        doc_type: str,
        doc_name: str,
        documents: List[str],
    ) -> Dict[str, Any]:
        project_id = str(project_id)
        doc_id = str(doc_id)
        doc_type = str(doc_type or "manual")
        doc_name = str(doc_name or "")
        if not documents:
            return {
                "indexed": False,
                "degraded": False,
                "vector_count": 0,
                "error": "empty_documents",
            }
        self._init_components()
        if self._embedding_func is None:
            return {
                "indexed": False,
                "degraded": True,
                "vector_count": 0,
                "error": "embedding_unavailable",
            }
        try:
            collection = self._get_or_create_collection()
            collection.delete(where={"doc_id": doc_id})
            embeddings = self._embedding_func.embed_documents(documents)
            if not embeddings or len(embeddings) != len(documents):
                return {
                    "indexed": False,
                    "degraded": True,
                    "vector_count": 0,
                    "error": "embedding_failed",
                }
            ids = [f"{project_id}_{doc_id}_{i}" for i in range(len(documents))]
            metadatas = [
                {
                    "project_id": project_id,
                    "doc_id": doc_id,
                    "doc_type": doc_type,
                    "doc_name": doc_name,
                    "chunk_index": i,
                }
                for i in range(len(documents))
            ]
            collection.upsert(
                embeddings=embeddings,
                documents=documents,
                ids=ids,
                metadatas=metadatas,
            )
            return {
                "indexed": True,
                "degraded": False,
                "vector_count": len(documents),
                "error": "",
            }
        except Exception as e:
            print(f"向量索引失败: {e}")
            return {
                "indexed": False,
                "degraded": True,
                "vector_count": 0,
                "error": str(e),
            }

    def search(
        self, project_id: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        project_id = str(project_id)
        self._init_components()
        if self._embedding_func is None:
            return []
        try:
            query_embedding = self._embedding_func.embed_query(query)
            if not query_embedding:
                return []
            collection = self._get_or_create_collection()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"project_id": project_id},
            )
            formatted_results = []
            if results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "content": doc,
                        "distance": results["distances"][0][i] if results.get("distances") else 0,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    })
            return formatted_results
        except Exception as e:
            print(f"向量检索失败: {e}")
            return []

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        doc_id = str(doc_id)
        try:
            self._init_components()
            collection = self._get_or_create_collection()
            existing = collection.get(where={"doc_id": doc_id})
            ids = existing.get("ids") if isinstance(existing, dict) else []
            delete_count = len(ids) if isinstance(ids, list) else 0
            collection.delete(where={"doc_id": doc_id})
            return {"status": "success", "vector_deleted": delete_count}
        except Exception as e:
            print(f"Chroma删除失败: {e}")
            return {"status": "error", "vector_deleted": 0, "error": str(e)}

    def get_collection_stats(self, project_id: str) -> Dict[str, Any]:
        project_id = str(project_id)
        try:
            self._init_components()
            collection = self._get_or_create_collection()
            result = collection.get(where={"project_id": project_id})
            ids = result.get("ids") if isinstance(result, dict) else []
            return {
                "count": len(ids) if isinstance(ids, list) else 0,
                "project_id": project_id,
                "collection_name": config.chroma_collection_name,
            }
        except Exception:
            return {
                "count": 0,
                "project_id": project_id,
                "collection_name": config.chroma_collection_name,
            }


rag_service = RAGService()
