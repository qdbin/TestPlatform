from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
import httpx
from app.config import config


class OpenAIEmbeddingFunction:
    """使用OpenAI兼容API的Embedding函数（支持OpenAI、Ollama等）"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.openai.com/v1",
        model: str = "text-embedding-3-small",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
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
                    timeout=60.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    embedding = data.get("data", [{}])[0].get("embedding", [])
                    embeddings.append(embedding)
                else:
                    print(
                        f"Embedding API错误: {response.status_code} - {response.text[:200]}"
                    )
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

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def __call__(self, input: List[str]) -> List[List[float]]:
        """生成文档向量"""
        embeddings = []
        for text in input:
            try:
                embedding = []
                legacy_resp = httpx.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=60.0,
                )
                if legacy_resp.status_code == 200:
                    legacy_data = legacy_resp.json() or {}
                    embedding = legacy_data.get("embedding", []) or []
                elif legacy_resp.status_code == 404:
                    new_resp = httpx.post(
                        f"{self.base_url}/api/embed",
                        json={"model": self.model, "input": text},
                        timeout=60.0,
                    )
                    if new_resp.status_code == 200:
                        new_data = new_resp.json() or {}
                        values = new_data.get("embeddings")
                        if isinstance(values, list) and values:
                            first = values[0]
                            embedding = first if isinstance(first, list) else []
                    else:
                        return []
                else:
                    return []
                if not embedding:
                    return []
                embeddings.append(embedding)
            except Exception as e:
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
                    base_url = config.get(
                        "embedding.openai_base_url", "https://api.openai.com/v1"
                    )
                    model = config.get(
                        "embedding.openai_model", "text-embedding-3-small"
                    )
                    if not api_key:
                        raise ValueError("未配置OpenAI API Key")
                    self._embedding_func = OpenAIEmbeddingFunction(
                        api_key, base_url, model
                    )
                    self._embedding_init_failed = False
                    print(
                        f"Embedding模型加载成功: OpenAI兼容API ({model}) @ {base_url}"
                    )
                except Exception as e:
                    print(f"OpenAI Embedding加载失败: {e}")
                    self._embedding_func = None
                    self._embedding_init_failed = True
            elif provider == "ollama":
                try:
                    ollama_url = config.get(
                        "embedding.ollama_url", "http://localhost:11434"
                    )
                    ollama_model = config.get(
                        "embedding.ollama_model", "nomic-embed-text"
                    )
                    self._embedding_func = OllamaEmbeddingFunction(
                        ollama_url, ollama_model
                    )
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

    def _fallback_embed(self, text: str, dims: int = 768) -> List[float]:
        values = [0.0] * dims
        source = str(text or "")
        if not source:
            return values
        for i, ch in enumerate(source):
            values[i % dims] += (ord(ch) % 997) / 997.0
        length = max(1, len(source))
        return [item / length for item in values]

    def _embed_documents_with_fallback(
        self, documents: List[str]
    ) -> Tuple[List[List[float]], bool]:
        if self._embedding_func is not None:
            try:
                vectors = self._embedding_func.embed_documents(documents)
                if vectors and len(vectors) == len(documents):
                    return vectors, False
            except Exception:
                pass
        return [self._fallback_embed(item) for item in documents], True

    def _embed_query_with_fallback(self, query: str) -> Tuple[List[float], bool]:
        if self._embedding_func is not None:
            try:
                vector = self._embedding_func.embed_query(query)
                if vector:
                    return vector, False
            except Exception:
                pass
        return self._fallback_embed(query), True

    def _format_chunk_document(self, doc_name: str, doc_type: str, chunk: str) -> str:
        title = str(doc_name or "").strip()
        dtype = str(doc_type or "").strip()
        body = str(chunk or "").strip()
        if title and dtype:
            return f"文档名：{title}\n文档类型：{dtype}\n\n{body}"
        if title:
            return f"文档名：{title}\n\n{body}"
        return body

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
        normalized_docs = [
            self._format_chunk_document(doc_name, doc_type, item)
            for item in documents
            if str(item or "").strip()
        ]
        if not normalized_docs:
            return {
                "indexed": False,
                "degraded": False,
                "vector_count": 0,
                "error": "empty_documents",
            }
        self._init_components()
        try:
            collection = self._get_or_create_collection()
            collection.delete(where=self._doc_where(project_id, doc_id))
            embeddings, used_fallback = self._embed_documents_with_fallback(
                normalized_docs
            )
            ids = [f"{project_id}_{doc_id}_{i}" for i in range(len(normalized_docs))]
            metadatas = [
                {
                    "project_id": project_id,
                    "doc_id": doc_id,
                    "doc_type": doc_type,
                    "doc_name": doc_name,
                    "chunk_index": i,
                }
                for i in range(len(normalized_docs))
            ]
            collection.upsert(
                embeddings=embeddings,
                documents=normalized_docs,
                ids=ids,
                metadatas=metadatas,
            )
            return {
                "indexed": True,
                "degraded": False,
                "vector_count": len(normalized_docs),
                "error": "fallback_embedding" if used_fallback else "",
            }
        except Exception as e:
            print(f"向量索引失败: {e}")
            return {
                "indexed": False,
                "degraded": True,
                "vector_count": 0,
                "error": str(e),
            }

    def _safe_collection_get(self, collection, where: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return collection.get(where=where, include=["documents", "metadatas"])
        except TypeError:
            return collection.get(where=where)

    def _doc_where(self, project_id: str, doc_id: str) -> Dict[str, Any]:
        return {"$and": [{"project_id": str(project_id)}, {"doc_id": str(doc_id)}]}

    def _vector_search(
        self, project_id: str, query: str, top_k: int
    ) -> Tuple[str, List[Dict[str, Any]]]:
        query_embedding, used_fallback = self._embed_query_with_fallback(query)
        if not query_embedding:
            return "embedding_unavailable", []
        collection = self._get_or_create_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"project_id": project_id},
        )
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
        return ("fallback" if used_fallback else "success"), formatted_results

    def _keyword_search(
        self, project_id: str, query: str, top_k: int
    ) -> List[Dict[str, Any]]:
        collection = self._get_or_create_collection()
        source = self._safe_collection_get(collection, {"project_id": project_id})
        documents = source.get("documents") or []
        metadatas = source.get("metadatas") or []
        if not isinstance(documents, list):
            documents = []
        if not isinstance(metadatas, list):
            metadatas = []
        terms = [
            item.strip().lower() for item in str(query or "").split() if item.strip()
        ]
        if not terms and query:
            terms = [str(query).strip().lower()]
        query_text = str(query or "").strip().lower()
        if query_text and query_text not in terms:
            terms.append(query_text)
        ranked: List[Dict[str, Any]] = []
        for idx, doc in enumerate(documents):
            text = str(doc or "")
            content_lc = text.lower()
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            metadata_text = " ".join(
                [
                    str(metadata.get("doc_name") or ""),
                    str(metadata.get("doc_type") or ""),
                ]
            ).lower()
            score = 0
            for term in terms:
                if not term:
                    continue
                if term in content_lc:
                    score += content_lc.count(term)
                if metadata_text and term in metadata_text:
                    score += 3
            if score <= 0:
                continue
            ranked.append(
                {
                    "content": text,
                    "distance": max(0.0, 1.0 - min(1.0, score / 10.0)),
                    "metadata": metadata,
                    "score": score,
                }
            )
        ranked.sort(key=lambda item: item.get("score", 0), reverse=True)
        return [
            {
                "content": item["content"],
                "distance": item["distance"],
                "metadata": item["metadata"],
            }
            for item in ranked[:top_k]
        ]

    def search_with_status(
        self, project_id: str, query: str, top_k: int = 5
    ) -> Dict[str, Any]:
        project_id = str(project_id)
        self._init_components()
        try:
            keyword_hits = self._keyword_search(project_id, query, top_k)
            vector_status, vector_hits = self._vector_search(project_id, query, top_k)
            merged: List[Dict[str, Any]] = []
            seen = set()
            for item in keyword_hits + vector_hits:
                key = (str(item.get("content") or ""), str(item.get("metadata") or ""))
                if key in seen:
                    continue
                seen.add(key)
                merged.append(item)
                if len(merged) >= top_k:
                    break
            if merged:
                return {"status": "success", "data": merged}
            if vector_status == "embedding_unavailable":
                return {"status": "embedding_unavailable", "data": []}
            return {"status": "no_context", "data": []}
        except Exception as e:
            print(f"向量检索失败: {e}")
            return {"status": "vector_error", "data": [], "error": str(e)}

    def search(
        self, project_id: str, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        return self.search_with_status(project_id, query, top_k).get("data", [])

    def delete_document(self, project_id: str, doc_id: str) -> Dict[str, Any]:
        project_id = str(project_id)
        doc_id = str(doc_id)
        try:
            self._init_components()
            collection = self._get_or_create_collection()
            existing = self._safe_collection_get(
                collection, self._doc_where(project_id, doc_id)
            )
            ids = existing.get("ids") if isinstance(existing, dict) else []
            delete_count = len(ids) if isinstance(ids, list) else 0
            collection.delete(where=self._doc_where(project_id, doc_id))
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
