"""
RAG检索服务模块 - LangChain 1.x LCEL版本

职责：
    1. 管理 Embedding 组件与 Chroma 向量库连接
    2. 将文档分片写入向量库并维护 project/doc 级隔离
    3. 执行"查询改写 + 向量检索 + 关键词召回 + 重排序"混合检索
    4. 集成 LangSmith 全链路追踪
    5. 使用LCEL构建可组合的检索链路

核心类：
    - RAGService: RAG核心服务（检索增强生成）
    - OpenAIEmbeddingFunction: OpenAI 兼容 Embedding 适配器
    - OllamaEmbeddingFunction: Ollama 本地 Embedding 适配器

检索流程：
    1. 查询改写（Query Rewriting）
    2. 并行执行向量检索 + 关键词检索
    3. 结果融合与去重
    4. 重排序（Reranking）
    5. 返回最终结果
"""

from typing import List, Dict, Any, Tuple, Optional
import asyncio
import json
import time
import chromadb
from chromadb.config import Settings
import httpx
from langchain_core.runnables import RunnableLambda, RunnableParallel

from app.config import config
from app.observability import app_logger
from app.observability.traceable import traceable
from app.services.retrieval import BM25KeywordRetriever, query_rewriter, reranker


class OpenAIEmbeddingFunction:
    """
    OpenAI 兼容 Embedding 适配器。
    适用场景：接入 OpenAI / DeepSeek 兼容网关的 embedding 接口。

    使用示例：
        embed_fn = OpenAIEmbeddingFunction(api_key="sk-xxx")
        vectors = embed_fn(["文本1", "文本2"])
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
        """批量文本向量化"""
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

    使用示例：
        embed_fn = OllamaEmbeddingFunction(base_url="http://localhost:11434")
        vectors = embed_fn(["文本1", "文本2"])
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
                # 尝试旧版API
                legacy_resp = httpx.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=60.0,
                )
                if legacy_resp.status_code == 200:
                    legacy_data = legacy_resp.json() or {}
                    embedding = legacy_data.get("embedding", []) or []
                elif legacy_resp.status_code == 404:
                    # 回退到新版API
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
    RAG核心服务（检索增强生成）- LangChain 1.x实现

    主要职责：
        - Embedding 管理（支持OpenAI/Ollama/降级）
        - 向量写入与维护（Chroma）
        - 混合检索（查询改写 + 向量 + 关键词 + 重排序）
        - 状态回传（success/no_context/embedding_unavailable等）
        - 全链路LangSmith追踪

    检索流程：
        1. 查询改写与扩写
        2. 并行向量检索 + 关键词检索
        3. 结果融合与去重（RRF）
        4. BGE重排序
        5. 返回Top-K结果

    数据隔离：
        - 项目级：通过 project_id 元数据过滤
        - 文档级：通过 doc_id 元数据标识
    """

    def __init__(self):
        self._embedding_func = None
        self._client = None
        self._collection = None
        self._embedding_init_failed = False
        self._bm25_retriever = BM25KeywordRetriever()

    def _init_components(self) -> None:
        """
        延迟初始化 Embedding 与 Chroma 组件

        支持的Embedding Provider：
            - openai: OpenAI兼容API
            - ollama: 本地Ollama服务
        """
        if self._embedding_func is None and not self._embedding_init_failed:
            provider = config.embedding_provider

            if provider == "openai":
                try:
                    api_key = config.embedding_openai_api_key
                    base_url = config.embedding_openai_base_url
                    model = config.embedding_openai_model
                    if not api_key:
                        raise ValueError("未配置OpenAI API Key")

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

            elif provider == "ollama":
                try:
                    ollama_url = config.embedding_ollama_url
                    ollama_model = config.embedding_ollama_model

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

        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=config.chroma_persist_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )

    def _get_or_create_collection(self):
        """获取或创建Chroma集合"""
        if self._client is None:
            self._init_components()
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=config.chroma_collection_name,
                metadata={"scope": "all_projects"},
            )
        return self._collection

    def _fallback_embed(self, text: str, dims: int = 768) -> List[float]:
        """
        降级向量算法（哈希分桶）

        当Embedding服务不可用时，使用简单的哈希算法生成向量。
        虽然语义效果差，但能保证系统可用性。
        """
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
        """文档向量化（含降级）"""
        if self._embedding_func is not None:
            try:
                vectors = self._embedding_func.embed_documents(documents)
                if vectors and len(vectors) == len(documents):
                    return vectors, False
            except Exception:
                pass
        return [self._fallback_embed(item) for item in documents], True

    def _embed_query_with_fallback(self, query: str) -> Tuple[List[float], bool]:
        """查询向量化（含降级）"""
        if self._embedding_func is not None:
            try:
                vector = self._embedding_func.embed_query(query)
                if vector:
                    return vector, False
            except Exception:
                pass
        return self._fallback_embed(query), True

    def _format_chunk_document(self, doc_name: str, doc_type: str, chunk: str) -> str:
        """格式化文档块（添加元信息）"""
        title = str(doc_name or "").strip()
        dtype = str(doc_type or "").strip()
        body = str(chunk or "").strip()
        if title and dtype:
            return f"文档名：{title}\n文档类型：{dtype}\n\n{body}"
        if title:
            return f"文档名：{title}\n\n{body}"
        return body

    def _normalize_metadata_value(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)):
            if isinstance(value, str):
                return value[:1000]
            return value
        if value is None:
            return ""
        if isinstance(value, list):
            if not value:
                return ""
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, dict):
            if not value:
                return ""
            return json.dumps(value, ensure_ascii=False)
        return str(value)[:1000]

    def _build_metadata(
        self,
        project_id: str,
        doc_id: str,
        doc_type: str,
        doc_name: str,
        user_id: str,
        timestamp: int,
        chunk_index: int,
        extra_meta: Dict[str, Any],
    ) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            "project_id": project_id,
            "doc_id": doc_id,
            "doc_type": doc_type,
            "doc_name": doc_name,
            "user_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            "chunk_index": chunk_index,
        }
        for key, value in (extra_meta or {}).items():
            metadata[str(key)] = self._normalize_metadata_value(value)
        return metadata

    @traceable(name="rag_add_document", run_type="retriever")
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
        写入知识文档分片到向量库

        实现步骤：
            1. 规范化文档格式
            2. 生成向量（含降级处理）
            3. 构建元数据（project_id/doc_id隔离）
            4. 写入Chroma集合

        @param project_id: 项目ID（隔离）
        @param doc_id: 文档ID
        @param doc_type: 文档类型
        @param doc_name: 文档名称
        @param documents: 文档块列表
        @param user_id: 用户ID
        @return: {indexed, degraded, vector_count, error}
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

        # 规范化文档
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
            # 删除旧数据
            collection.delete(where=self._doc_where(project_id, doc_id))

            # 生成向量
            embeddings, used_fallback = self._embed_documents_with_fallback(
                normalized_docs
            )

            # 构建ID和元数据
            ids = [f"{project_id}_{doc_id}_{i}" for i in range(len(normalized_docs))]
            metadatas = []
            for i in range(len(normalized_docs)):
                current_meta = chunk_metas[i] if i < len(chunk_metas) else {}
                metadatas.append(
                    self._build_metadata(
                        project_id=project_id,
                        doc_id=doc_id,
                        doc_type=doc_type,
                        doc_name=doc_name,
                        user_id=user_id,
                        timestamp=timestamp,
                        chunk_index=i,
                        extra_meta=current_meta,
                    )
                )

            # 写入向量库
            collection.upsert(
                embeddings=embeddings,
                documents=normalized_docs,
                ids=ids,
                metadatas=metadatas,
            )

            app_logger.info(
                "rag_document_indexed project={} doc_id={} chunks={} degraded={}",
                project_id,
                doc_id,
                len(normalized_docs),
                used_fallback
            )

            return {
                "indexed": True,
                "degraded": used_fallback,
                "vector_count": len(normalized_docs),
                "error": "",
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
        """安全获取集合数据"""
        try:
            return collection.get(where=where, include=["documents", "metadatas"])
        except TypeError:
            return collection.get(where=where)

    def _doc_where(self, project_id: str, doc_id: str) -> Dict[str, Any]:
        """构建文档查询条件"""
        return {"$and": [{"project_id": str(project_id)}, {"doc_id": str(doc_id)}]}

    def _build_merge_key(self, item: Dict[str, Any]) -> str:
        """构建结果合并键（用于去重）"""
        metadata = (
            item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        )
        doc_id = str(metadata.get("doc_id") or "")
        chunk_index = str(metadata.get("chunk_index") or "")
        if doc_id and chunk_index:
            return f"{doc_id}:{chunk_index}"
        return str(item.get("content") or "")[:200]

    @traceable(name="rag_vector_search", run_type="retriever")
    def _vector_search(
        self, project_id: str, query: str, top_k: int
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        纯向量语义检索

        @param project_id: 项目ID（隔离）
        @param query: 查询字符串
        @param top_k: 返回数量
        @return: (状态, 结果列表)

        状态说明：
            - success: 检索成功
            - fallback: 使用了降级向量
            - embedding_unavailable: Embedding服务不可用
        """
        query_embedding, used_fallback = self._embed_query_with_fallback(query)
        if not query_embedding:
            return "embedding_unavailable", []

        collection = self._get_or_create_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,  # 检索更多，供后续融合
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
                        "source": "vector",
                    }
                )
        return ("fallback" if used_fallback else "success"), formatted_results

    @traceable(name="rag_keyword_search", run_type="retriever")
    def _keyword_search(
        self, project_id: str, query: str, top_k: int
    ) -> List[Dict[str, Any]]:
        """关键词召回（BM25）"""
        collection = self._get_or_create_collection()
        source = self._safe_collection_get(collection, {"project_id": project_id})
        documents = source.get("documents") or []
        metadatas = source.get("metadatas") or []

        if not isinstance(documents, list):
            documents = []
        if not isinstance(metadatas, list):
            metadatas = []

        results = self._bm25_retriever.search(query, documents, metadatas, top_k=top_k * 2)
        # 标记来源
        for r in results:
            r["source"] = "keyword"
        return results

    @traceable(name="rag_fuse_results", run_type="retriever")
    def _fuse_results(
        self,
        keyword_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        融合关键词和向量检索结果

        使用RRF (Reciprocal Rank Fusion)算法融合结果：
            score = Σ(1 / (rank + k))
            其中k为常数（通常取60）

        @param keyword_results: 关键词检索结果
        @param vector_results: 向量检索结果
        @param top_k: 返回数量
        @return: 融合后的结果列表
        """
        merged_map: Dict[str, Dict[str, Any]] = {}

        # 关键词结果打分 (RRF)
        for rank, item in enumerate(keyword_results):
            key = self._build_merge_key(item)
            score = 1.0 / (rank + 1 + 60)  # RRF公式: 1/(k+60)
            if key in merged_map:
                merged_map[key]["score"] += score
            else:
                merged_map[key] = {"item": item, "score": score}

        # 向量结果打分 (RRF + 相似度)
        for rank, item in enumerate(vector_results):
            key = self._build_merge_key(item)
            distance = float(item.get("distance") or 0.0)
            similarity = max(0.0, 1.0 - distance)
            # RRF分数 + 相似度加权
            score = (1.0 / (rank + 1 + 60)) + (similarity * 0.5)

            if key in merged_map:
                merged_map[key]["score"] += score
                # 更新距离为最小值
                existing_dist = merged_map[key]["item"].get("distance", 1.0)
                merged_map[key]["item"]["distance"] = min(existing_dist, distance)
            else:
                merged_map[key] = {"item": item, "score": score}

        # 按分数排序
        ranked = sorted(
            merged_map.values(),
            key=lambda x: x["score"],
            reverse=True,
        )

        # 构建最终结果
        results = []
        for entry in ranked[:top_k * 2]:  # 取更多供重排序
            item = entry["item"]
            item["hybrid_score"] = entry["score"]
            results.append(item)

        return results

    def _retrieve_for_query(
        self, project_id: str, current_query: str, top_k: int
    ) -> Dict[str, Any]:
        parallel = RunnableParallel(
            keyword=RunnableLambda(
                lambda x: self._keyword_search(project_id, x["query"], top_k)
            ),
            vector=RunnableLambda(
                lambda x: self._vector_search(project_id, x["query"], top_k)
            ),
        )
        retrieval = parallel.invoke({"query": current_query})
        keyword_hits = retrieval.get("keyword") if isinstance(retrieval, dict) else []
        vector_result = (
            retrieval.get("vector") if isinstance(retrieval, dict) else ("no_context", [])
        )
        status = "no_context"
        vector_hits: List[Dict[str, Any]] = []
        if isinstance(vector_result, tuple) and len(vector_result) == 2:
            status = str(vector_result[0] or "no_context")
            if isinstance(vector_result[1], list):
                vector_hits = vector_result[1]
        return {
            "query": current_query,
            "keyword_hits": keyword_hits if isinstance(keyword_hits, list) else [],
            "vector_status": status,
            "vector_hits": vector_hits,
        }

    def _load_parent_chunks(
        self, project_id: str, parent_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        if not parent_ids:
            return {}
        collection = self._get_or_create_collection()
        source = self._safe_collection_get(collection, {"project_id": project_id})
        documents = source.get("documents") or []
        metadatas = source.get("metadatas") or []
        parent_map: Dict[str, Dict[str, Any]] = {}
        for idx, doc in enumerate(documents):
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            if not isinstance(metadata, dict):
                continue
            role = str(metadata.get("chunk_role") or "")
            parent_id = str(metadata.get("parent_chunk_id") or "")
            if role != "parent" or not parent_id or parent_id not in parent_ids:
                continue
            parent_map[parent_id] = {
                "content": str(doc or ""),
                "metadata": metadata,
                "source": "parent",
                "distance": 0.0,
                "hybrid_score": 0.0,
                "rerank_score": 0.0,
            }
        return parent_map

    @traceable(name="rag_parent_strategy", run_type="retriever")
    def _apply_parent_document_strategy(
        self, project_id: str, reranked_results: List[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        if not reranked_results:
            return []
        parent_score_map: Dict[str, float] = {}
        for item in reranked_results:
            metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
            parent_id = str(metadata.get("parent_chunk_id") or "")
            if not parent_id:
                continue
            score = float(item.get("rerank_score") or item.get("hybrid_score") or 0.0)
            parent_score_map[parent_id] = max(parent_score_map.get(parent_id, 0.0), score)
        ranked_parent_ids = [
            entry[0]
            for entry in sorted(parent_score_map.items(), key=lambda x: x[1], reverse=True)
        ]
        parent_chunks = self._load_parent_chunks(project_id, ranked_parent_ids[:top_k])
        merged: List[Dict[str, Any]] = []
        for parent_id in ranked_parent_ids:
            if parent_id in parent_chunks:
                merged.append(parent_chunks[parent_id])
        merged.extend(reranked_results)
        deduped: List[Dict[str, Any]] = []
        seen_keys: set = set()
        for item in merged:
            key = self._build_merge_key(item)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(item)
            if len(deduped) >= top_k:
                break
        return deduped[:top_k]

    @traceable(name="rag_search", run_type="retriever")
    def search_with_status(
        self,
        project_id: str,
        query: str,
        top_k: int = 5,
        user_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        混合检索总入口 - 完整流程

        检索流程：
            1. 查询改写与扩写（Query Rewriting）
            2. 对每个改写查询执行并行检索（向量+关键词）
            3. 结果融合（RRF）
            4. BGE重排序
            5. 返回Top-K结果

        @param project_id: 项目ID（隔离）
        @param query: 查询字符串
        @param top_k: 返回结果数量
        @param user_id: 用户ID
        @return: {"status": "success/no_context/...", "data": [...]}

        状态说明：
            - success: 检索成功
            - no_context: 无相关文档
            - embedding_unavailable: Embedding服务不可用
            - error: 检索异常
        """
        project_id = str(project_id)
        original_query = query.strip()

        if not original_query:
            return {"status": "empty_query", "data": []}

        self._init_components()

        try:
            # 步骤1：查询改写与扩写
            expanded_queries = query_rewriter.rewrite_and_expand(
                original_query,
                max_variants=3,
                messages=messages,
            )
            app_logger.info(
                "rag_query_expanded original='{}' expanded_count={}",
                original_query[:50],
                len(expanded_queries)
            )

            all_keyword_results: List[Dict] = []
            all_vector_results: List[Dict] = []
            vector_status = "no_context"
            query_results = []
            try:
                async def _run_queries() -> List[Dict[str, Any]]:
                    tasks = [
                        asyncio.to_thread(
                            self._retrieve_for_query,
                            project_id,
                            current_query,
                            top_k,
                        )
                        for current_query in expanded_queries
                    ]
                    return await asyncio.gather(*tasks)

                query_results = asyncio.run(_run_queries())
            except RuntimeError:
                for current_query in expanded_queries:
                    query_results.append(
                        self._retrieve_for_query(project_id, current_query, top_k)
                    )

            for entry in query_results:
                keyword_hits = entry.get("keyword_hits") or []
                all_keyword_results.extend(keyword_hits)
                current_status = str(entry.get("vector_status") or "no_context")
                if current_status in ("success", "fallback", "embedding_unavailable"):
                    vector_status = current_status
                vector_hits = entry.get("vector_hits") or []
                all_vector_results.extend(vector_hits)

            # 步骤3：结果融合（RRF）
            fused_results = self._fuse_results(
                all_keyword_results, all_vector_results, top_k * 2
            )

            # 步骤4：BGE重排序
            reranked_results = reranker.rerank(
                original_query, fused_results, top_k=top_k
            )
            final_results = self._apply_parent_document_strategy(
                project_id=project_id,
                reranked_results=reranked_results,
                top_k=top_k,
            )

            app_logger.info(
                "rag_search_complete project={} query='{}' "
                "expanded={} keyword_hits={} vector_hits={} final={}",
                project_id,
                original_query[:50],
                len(expanded_queries),
                len(all_keyword_results),
                len(all_vector_results),
                len(final_results)
            )

            if final_results:
                return {"status": "success", "data": final_results}

            if vector_status == "embedding_unavailable":
                return {"status": "embedding_unavailable", "data": []}

            return {"status": "no_context", "data": []}

        except Exception as e:
            app_logger.error("RAG检索失败: {}", str(e))
            return {"status": "error", "data": [], "error": str(e)}

    def search(
        self, project_id: str, query: str, top_k: int = 5, user_id: str = ""
    ) -> List[Dict[str, Any]]:
        """简单检索入口（仅返回数据）"""
        return self.search_with_status(project_id, query, top_k, user_id=user_id).get(
            "data", []
        )

    @traceable(name="rag_delete_document", run_type="retriever")
    def delete_document(self, project_id: str, doc_id: str) -> Dict[str, Any]:
        """删除文档对应向量分片"""
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

            app_logger.info(
                "rag_document_deleted project={} doc_id={} deleted={}",
                project_id,
                doc_id,
                delete_count
            )

            return {"status": "success", "vector_deleted": delete_count}
        except Exception as e:
            app_logger.error("Chroma删除失败: {}", str(e))
            return {"status": "error", "vector_deleted": 0, "error": str(e)}

    def get_collection_stats(self, project_id: str) -> Dict[str, Any]:
        """获取项目向量统计信息"""
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


# 全局RAG服务实例
rag_service = RAGService()
