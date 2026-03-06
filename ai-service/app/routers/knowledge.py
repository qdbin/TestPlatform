from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.rag_service import rag_service
from app.utils.chunking import chunk_text

router = APIRouter()


class RagAddRequest(BaseModel):
    project_id: str
    doc_id: str
    doc_type: str
    doc_name: str
    content: str


class RagQueryRequest(BaseModel):
    project_id: str
    question: str
    top_k: int = 5
    messages: List[Dict[str, Any]] = []


class RagDeleteRequest(BaseModel):
    doc_id: str


@router.post("/add")
async def add_document(request: RagAddRequest):
    try:
        chunks = chunk_text(request.content, chunk_size=1200, overlap=80)
        if not chunks:
            return {
                "status": "success",
                "indexed": False,
                "degraded": False,
                "vector_count": 0,
                "error": "empty_documents",
            }
        index_result = rag_service.add_document(
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
    try:
        result = rag_service.delete_document(request.doc_id)
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error") or "删除失败")
        return {"status": "success", "vector_deleted": result.get("vector_deleted", 0)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/query")
async def query_knowledge(request: RagQueryRequest):
    try:
        results = rag_service.search(
            project_id=request.project_id,
            query=request.question,
            top_k=request.top_k,
        )
        if not results:
            return {
                "status": "success",
                "data": [],
                "answer": "未找到相关文档",
                "has_context": False,
            }
        context = "\n\n".join([str(item.get("content") or "") for item in results if item])
        return {
            "status": "success",
            "data": results,
            "answer": context,
            "has_context": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.get("/stats/{project_id}")
async def get_stats(project_id: str):
    try:
        stats = rag_service.get_collection_stats(project_id)
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")
