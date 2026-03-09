from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.rag_service import rag_service
from app.utils.markdown_parent_child_chunking import markdown_parent_child_chunker

router = APIRouter()


class RagAddRequest(BaseModel):
    """
    知识文档入库请求。
    Schema示例：
    {"project_id":"p1","doc_id":"d1","doc_type":"manual","doc_name":"登录文档","content":"..."}
    """

    project_id: str
    doc_id: str
    doc_type: str
    doc_name: str
    content: str


class RagQueryRequest(BaseModel):
    """知识检索请求。messages预留给后续多轮检索增强。"""

    project_id: str  # 项目ID：控制检索隔离范围
    question: str  # 用户问题：作为检索query
    top_k: int = 5  # 召回数量：通常5条足够拼装上下文
    messages: List[Dict[str, Any]] = []  # 预留字段：后续可做多轮检索重写


class RagDeleteRequest(BaseModel):
    project_id: str
    doc_id: str


@router.post("/add")
async def add_document(request: RagAddRequest):
    """新增/重建知识文档索引。先切片再写入向量库。"""
    try:
        chunks = markdown_parent_child_chunker.split(request.content)
        if not chunks:
            return {
                "status": "success",
                "indexed": False,
                "degraded": False,
                "vector_count": 0,
                "error": "empty_documents",
            }
        index_result = rag_service.add_document(  # RAG写入：embedding + upsert
            project_id=request.project_id,
            doc_id=request.doc_id,
            doc_type=request.doc_type,
            doc_name=request.doc_name,
            documents=chunks,
        )
        return {"status": "success", **index_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"新增文档失败: {str(e)}")


@router.post("/delete")
async def delete_document(request: RagDeleteRequest):
    """删除知识文档对应向量分片。"""
    try:
        result = rag_service.delete_document(request.project_id, request.doc_id)
        if result.get("status") != "success":
            raise HTTPException(
                status_code=500, detail=result.get("error") or "删除失败"
            )
        return {"status": "success", "vector_deleted": result.get("vector_deleted", 0)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/query")
async def query_knowledge(request: RagQueryRequest):
    """
    查询知识库并返回上下文答案。
    返回中的 rag_status 用于前端区分无结果/服务异常等状态。
    """
    try:
        search_result = rag_service.search_with_status(
            project_id=request.project_id,
            query=request.question,
            top_k=request.top_k,
        )
        results = search_result.get("data", [])
        if not results:
            status = str(search_result.get("status") or "")
            if status == "embedding_unavailable":
                answer = "知识库服务异常，请稍后重试"
            elif status == "vector_error":
                answer = "知识库服务异常，请稍后重试"
            else:
                answer = "未找到相关文档"
            return {
                "status": "success",
                "data": [],
                "answer": answer,
                "has_context": False,
                "rag_status": status or "no_context",
            }
        context = "\n\n".join(
            [str(item.get("content") or "") for item in results if item]
        )
        return {
            "status": "success",
            "data": results,
            "answer": context,
            "has_context": True,
            "rag_status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.get("/stats/{project_id}")
async def get_stats(project_id: str):
    """获取项目维度知识库统计（分片数量等）。"""
    try:
        stats = rag_service.get_collection_stats(project_id)
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")
