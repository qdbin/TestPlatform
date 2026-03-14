"""
RAG检索服务模块

职责：
    1. 管理 Embedding 组件与 Chroma 向量库连接
    2. 将文档分片写入向量库并维护 project/doc 级隔离
    3. 执行"关键词 + 向量"混合检索并输出统一状态码

核心类：
    - RAGService: RAG核心服务（检索增强生成）
    - OpenAIEmbeddingFunction: OpenAI 兼容 Embedding 适配器
    - OllamaEmbeddingFunction: Ollama 本地 Embedding 适配器
"""

from typing import List, Dict, Any, Tuple
import re
import time
import chromadb
from chromadb.config import Settings
import httpx
from app.config import config
from app.observability import app_logger
from app.services.retrieval import BM25KeywordRetriever, query_rewriter, reranker


class OpenAIEmbeddingFunction:
    """
    OpenAI 兼容 Embedding 适配器。
    适用场景：接入 OpenAI / DeepSeek 兼容网关的 embedding 接口。
    """

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
        """
        批量文本向量化。
        @param input: 待向量化文本列表
        @return: 向量列表（顺序与 input 一致）
        """
        embeddings = []
        for text in input:
            try:
                headers = {"Content-Type": "application/json"}  # OpenAI 兼容 JSON 协议
                if self.api_key:
                    headers["Authorization"] = (
                        f"Bearer {self.api_key}"  # 鉴权头（私有部署可为空）
                    )

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
                    app_logger.error(
                        "Embedding API错误 status={} body={}",
                        response.status_code,
                        response.text[:200],
                    )
                    return []
            except Exception as e:
                app_logger.error("Embedding失败: {}", str(e))
                return []
        return embeddings

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self(documents)

    def embed_query(self, query: str) -> List[float]:
        result = self([query])
        return result[0] if result else []


class OllamaEmbeddingFunction:
    """
    Ollama Embedding 适配器（本地模型）。
    兼容 /api/embeddings（旧）与 /api/embed（新）两套接口。
    """

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
    """
    RAG核心服务（检索增强生成）。
    主要职责：Embedding 管理、向量写入、混合检索、状态回传。
    """

    def __init__(self):
        self._embedding_func = None
        self._client = None
        self._collection = None
        self._embedding_init_failed = False
        self._bm25_retriever = BM25KeywordRetriever()

    def _init_components(self) -> None:
        """
        延迟初始化 Embedding 与 Chroma 组件。
        实现阶段：
        1) 按配置选择 provider（openai/ollama）。
        2) 初始化 embedding 函数并记录降级状态。
        3) 初始化 Chroma PersistentClient。
        """
        # 检查是否需要初始化
        if self._embedding_func is None and not self._embedding_init_failed:
            # 获取Embedding provider配置
            provider = config.get("embedding.provider", "ollama")

            # OpenAI兼容模式初始化
            if provider == "openai":
                try:
                    # 读取OpenAI配置
                    api_key = config.get("embedding.openai_api_key", "")
                    base_url = config.get(
                        "embedding.openai_base_url", "https://api.openai.com/v1"
                    )
                    model = config.get(
                        "embedding.openai_model", "text-embedding-3-small"
                    )
                    # 检查API Key
                    if not api_key:
                        raise ValueError("未配置OpenAI API Key")
                    # 创建Embedding函数
                    self._embedding_func = OpenAIEmbeddingFunction(
                        api_key, base_url, model
                    )
                    self._embedding_init_failed = False
                    app_logger.info(
                        "Embedding模型加载成功: OpenAI兼容API {} @ {}",
                        model,
                        base_url,
                    )
                except Exception as e:
                    app_logger.error("OpenAI Embedding加载失败: {}", str(e))
                    self._embedding_func = None
                    self._embedding_init_failed = True
            # Ollama本地模式初始化
            elif provider == "ollama":
                try:
                    # 读取Ollama配置
                    ollama_url = config.get(
                        "embedding.ollama_url", "http://localhost:11434"
                    )
                    ollama_model = config.get(
                        "embedding.ollama_model", "nomic-embed-text"
                    )
                    # 创建Embedding函数
                    self._embedding_func = OllamaEmbeddingFunction(
                        ollama_url, ollama_model
                    )
                    self._embedding_init_failed = False
                    app_logger.info("Embedding模型加载成功: Ollama {}", ollama_model)
                except Exception as e:
                    app_logger.error("Ollama Embedding加载失败: {}", str(e))
                    self._embedding_func = None
                    self._embedding_init_failed = True
            else:
                app_logger.warning(
                    "未知的Embedding provider: {}，使用关键词匹配检索", provider
                )
                self._embedding_func = None
                self._embedding_init_failed = True

        # 初始化Chroma客户端
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=config.chroma_persist_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )

    def _get_or_create_collection(self):
        """获取或创建Chroma集合"""
        # 确保组件已初始化
        if self._client is None:
            self._init_components()
        # 获取或创建集合
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=config.chroma_collection_name,
                metadata={"scope": "all_projects"},
            )
        return self._collection

    def _fallback_embed(self, text: str, dims: int = 768) -> List[float]:
        """
        降级向量算法（哈希分桶）。

        @param text: 原始文本
        @param dims: 向量维度，默认 768（兼容主流 embedding 维度）
        @return: 归一化后的伪向量
        """
        # 初始化向量数组
        values = [0.0] * dims
        source = str(text or "")
        # 空文本直接返回零向量
        if not source:
            return values
        # 字符哈希累加
        for i, ch in enumerate(source):
            values[i % dims] += (ord(ch) % 997) / 997.0
        # 归一化处理
        length = max(1, len(source))
        return [item / length for item in values]

    def _embed_documents_with_fallback(
        self, documents: List[str]
    ) -> Tuple[List[List[float]], bool]:
        """
        文档向量化（含降级）。

        返回值: (embeddings, used_fallback)
        """
        # 优先使用真实Embedding
        if self._embedding_func is not None:
            try:
                vectors = self._embedding_func.embed_documents(documents)
                if vectors and len(vectors) == len(documents):
                    return vectors, False
            except Exception:
                pass
        # 降级：使用哈希伪向量
        return [self._fallback_embed(item) for item in documents], True

    def _embed_query_with_fallback(self, query: str) -> Tuple[List[float], bool]:
        """
        查询向量化（含降级）。

        @param query: 用户检索问题
        @return: (query_vector, used_fallback)
        """
        # 优先使用真实Embedding
        if self._embedding_func is not None:
            try:
                vector = self._embedding_func.embed_query(query)
                if vector:
                    return vector, False
            except Exception:
                pass
        # 降级：使用哈希伪向量
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
        documents: List[Any],
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        写入知识文档分片到向量库。
        @param project_id: 项目ID（跨项目隔离主键）
        @param doc_id: 文档ID（重建索引时会覆盖）
        @param doc_type: 文档类型（manual/api_doc 等）
        @param doc_name: 文档名（用于关键词召回增强）
        @param documents: 文档分片文本列表
        @return: {indexed,degraded,vector_count,error}

        示例：
        输入：project_id=p1, doc_id=d1, documents=['登录说明1','登录说明2']
        输出：{"indexed":true,"vector_count":2,"error":""}

        Schema示例：
        - metadata: {"project_id":"p1","doc_id":"d1","doc_type":"manual","doc_name":"登录规范","chunk_index":0}
        - id: "p1_d1_0"
        """
        project_id = str(project_id)
        doc_id = str(doc_id)
        doc_type = str(doc_type or "manual")
        doc_name = str(doc_name or "")
        user_id = str(user_id or "")
        timestamp = int(time.time() * 1000)
        if not documents:
            return {
                "indexed": False,
                "degraded": False,
                "vector_count": 0,
                "error": "empty_documents",
            }
        normalized_docs: List[str] = []
        chunk_metas: List[Dict[str, Any]] = []
        for item in documents:
            if isinstance(item, dict):
                content = str(item.get("content") or "").strip()
                extra_meta = (
                    item.get("metadata")
                    if isinstance(item.get("metadata"), dict)
                    else {}
                )
            else:
                content = str(item or "").strip()
                extra_meta = {}
            if not content:
                continue
            normalized_docs.append(
                self._format_chunk_document(doc_name, doc_type, content)
            )
            chunk_metas.append(extra_meta)
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
            # 关键阶段：先删后写，保证重建索引不残留旧向量。
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
                    "user_id": user_id,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "chunk_index": i,
                    **(chunk_metas[i] if i < len(chunk_metas) else {}),
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
            app_logger.error("向量索引失败: {}", str(e))
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

    def _build_merge_key(self, item: Dict[str, Any]) -> str:
        metadata = (
            item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        )
        doc_id = str(metadata.get("doc_id") or "")
        chunk_index = str(metadata.get("chunk_index") or "")
        parent_id = str(metadata.get("parent_id") or "")
        if doc_id and chunk_index:
            return f"{doc_id}:{chunk_index}:{parent_id}"
        return str(item.get("content") or "")[:200]

    def _extract_chunk_body(self, content: str) -> str:
        text = str(content or "").strip()
        if not text:
            return ""
        if "\n\n" not in text:
            return text
        parts = [part.strip() for part in text.split("\n\n") if part.strip()]
        if not parts:
            return text
        return parts[-1]

    def _build_parent_fragment(
        self, parent_content: str, child_content: str, query: str
    ) -> str:
        source = str(parent_content or "").strip()
        if not source:
            return ""
        max_chars = int(config.get("rag.parent_backfill_max_chars", 360))
        window = int(config.get("rag.parent_backfill_window", 120))
        child_body = self._extract_chunk_body(child_content)
        anchors = [child_body[:90], str(query or "").strip()]
        idx = -1
        for anchor in anchors:
            anchor = str(anchor or "").strip()
            if not anchor:
                continue
            idx = source.find(anchor)
            if idx >= 0:
                break
        if idx < 0:
            for token in re.split(r"[^\w\u4e00-\u9fff]+", str(query or "").lower()):
                if len(token) < 2:
                    continue
                low_source = source.lower()
                low_idx = low_source.find(token)
                if low_idx >= 0:
                    idx = low_idx
                    break
        if idx < 0:
            idx = 0
        start = max(0, idx - window)
        end = min(len(source), start + max_chars)
        fragment = source[start:end].strip()
        if start > 0:
            fragment = "..." + fragment
        if end < len(source):
            fragment = fragment + "..."
        return fragment

    def _apply_parent_backfill(
        self, items: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        if not config.get("rag.parent_backfill_enabled", True):
            return items
        merged: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            metadata = (
                item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
            )
            parent_content = str(metadata.get("parent_content") or "").strip()
            content = str(item.get("content") or "").strip()
            if not parent_content or not content:
                merged.append(item)
                continue
            if parent_content in content:
                merged.append(item)
                continue
            fragment = self._build_parent_fragment(parent_content, content, query)
            if not fragment:
                merged.append(item)
                continue
            enriched = dict(item)
            enriched["parent_context"] = fragment
            enriched["content"] = f"{content}\n\n上文片段：\n{fragment}"
            merged.append(enriched)
        return merged

    def _vector_search(
        self, project_id: str, query: str, top_k: int
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        纯向量检索。

        返回值status:
        - success: 正常Embedding检索
        - fallback: 使用降级Embedding检索
        - embedding_unavailable: 无可用向量
        """
        # 阶段1：查询向量化
        query_embedding, used_fallback = self._embed_query_with_fallback(query)
        # 向量为空时直接返回
        if not query_embedding:
            return "embedding_unavailable", []
        # 执行向量检索
        collection = self._get_or_create_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"project_id": project_id},
        )
        # 阶段2：格式统一
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
        """
        关键词召回。

        目的：在 embedding 不稳定或语义向量未命中时提供可解释兜底。
        """
        # 获取集合
        collection = self._get_or_create_collection()
        # 获取项目文档
        source = self._safe_collection_get(collection, {"project_id": project_id})
        documents = source.get("documents") or []
        metadatas = source.get("metadatas") or []
        # 类型检查
        if not isinstance(documents, list):
            documents = []
        if not isinstance(metadatas, list):
            metadatas = []
        return self._bm25_retriever.search(query, documents, metadatas, top_k=top_k)

    def search_with_status(
        self, project_id: str, query: str, top_k: int = 5, user_id: str = ""
    ) -> Dict[str, Any]:
        """
        混合检索总入口：关键词检索 + 向量检索去重融合。
        状态语义：
        - success/no_context/embedding_unavailable/vector_error
        """
        project_id = str(project_id)
        self._init_components()
        try:
            # 对每个查询词分别进行关键词和向量检索
            expanded_queries = query_rewriter.rewrite_and_expand(query)
            keyword_hits: List[Dict[str, Any]] = []
            vector_hits: List[Dict[str, Any]] = []
            vector_status = "no_context"
            # 遍历展开后的查询词
            for current_query in expanded_queries:
                # 关键词检索
                keyword_hits.extend(
                    self._keyword_search(project_id, current_query, top_k)
                )
                # 向量检索
                current_status, current_vector_hits = self._vector_search(
                    project_id, current_query, top_k
                )
                if current_status in {"success", "fallback"}:
                    vector_status = current_status
                vector_hits.extend(current_vector_hits)
            # 合并去重：关键词结果
            merged_map: Dict[str, Dict[str, Any]] = {}
            for rank, item in enumerate(keyword_hits):
                key = self._build_merge_key(item)
                base = merged_map.get(key, {"item": item, "score": 0.0})
                base["score"] += 1.0 / (rank + 1)
                merged_map[key] = base
            # 合并去重：向量结果（加权融合）
            for rank, item in enumerate(vector_hits):
                key = self._build_merge_key(item)
                distance = float(item.get("distance") or 0.0)
                similarity = max(0.0, 1.0 - distance)
                base = merged_map.get(key, {"item": item, "score": 0.0})
                base["score"] += (1.0 / (rank + 1)) + similarity
                if "item" in base and isinstance(base["item"], dict):
                    base["item"]["distance"] = min(
                        float(base["item"].get("distance") or 1.0), distance
                    )
                merged_map[key] = base
            # 按得分排序
            ranked = sorted(
                merged_map.values(),
                key=lambda value: float(value.get("score") or 0),
                reverse=True,
            )
            # 扩展候选集
            merged = []
            for entry in ranked[: max(top_k * 3, top_k)]:
                item = entry["item"]
                item["hybrid_score"] = float(entry.get("score") or 0)
                merged.append(item)
            # 精排重排
            reranked = reranker.rerank(query, merged, top_k=top_k)
            app_logger.info(
                "rag_search project={} query={} expanded={} hybrid_candidates={} final={}",
                project_id,
                query[:80],
                len(expanded_queries),
                len(merged),
                len(reranked),
            )
            # 父文档回填
            merged = self._apply_parent_backfill(reranked, query)
            # 返回结果
            if merged:
                return {"status": "success", "data": merged}
            if vector_status == "embedding_unavailable":
                return {"status": "embedding_unavailable", "data": []}
            return {"status": "no_context", "data": []}
        except Exception as e:
            app_logger.error("向量检索失败: {}", str(e))
            return {"status": "vector_error", "data": [], "error": str(e)}

    def search(
        self, project_id: str, query: str, top_k: int = 5, user_id: str = ""
    ) -> List[Dict[str, Any]]:
        return self.search_with_status(project_id, query, top_k, user_id=user_id).get(
            "data", []
        )

    def delete_document(self, project_id: str, doc_id: str) -> Dict[str, Any]:
        """
        删除文档对应向量分片。
        @param project_id: 项目ID
        @param doc_id: 文档ID
        @return: 删除状态与删除数量
        """
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
            app_logger.error("Chroma删除失败: {}", str(e))
            return {"status": "error", "vector_deleted": 0, "error": str(e)}

    def get_collection_stats(self, project_id: str) -> Dict[str, Any]:
        """
        获取项目向量统计信息。
        @param project_id: 项目ID
        @return: count/project_id/collection_name
        """
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
