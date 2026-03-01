"""
知识库管理路由
处理知识库文档的索引、检索等请求
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.rag_service import rag_service
from app.utils.chunking import chunk_text

router = APIRouter()


class IndexRequest(BaseModel):
    """索引请求"""
    knowledge_id: str
    project_id: str
    name: str
    content: str


class SearchRequest(BaseModel):
    """检索请求"""
    project_id: str
    query: str
    top_k: int = 5


@router.post("/index")
async def index_document(request: IndexRequest):
    """
    索引知识库文档
    """
    try:
        # 文档分块
        chunks = chunk_text(request.content, chunk_size=500, overlap=50)
        
        if not chunks:
            return {"status": "success", "message": "文档为空，无需索引"}
        
        # 添加到向量库
        rag_service.add_documents(
            project_id=request.project_id,
            knowledge_id=request.knowledge_id,
            documents=chunks
        )
        
        return {
            "status": "success",
            "message": f"索引成功，共{len(chunks)}个文档块"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引失败: {str(e)}")


@router.delete("/index/{knowledge_id}")
async def delete_index(project_id: str, knowledge_id: str):
    """
    删除知识库索引
    """
    try:
        rag_service.delete_knowledge(project_id, knowledge_id)
        return {"status": "success", "message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/search")
async def search_knowledge(request: SearchRequest):
    """
    知识库检索
    """
    try:
        results = rag_service.search(
            project_id=request.project_id,
            query=request.query,
            top_k=request.top_k
        )
        
        return {
            "status": "success",
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.get("/stats/{project_id}")
async def get_stats(project_id: str):
    """
    获取知识库统计信息
    """
    try:
        stats = rag_service.get_collection_stats(project_id)
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.post("/sync/api")
async def sync_api(project_id: str, apis: List[Dict[str, Any]]):
    """
    同步项目接口到知识库
    将API信息转换为文档格式并索引
    """
    try:
        for api in apis:
            # 构建接口文档内容
            content = f"""
# {api.get('name', '未命名接口')}

## 基本信息
- 接口路径：{api.get('path', '')}
- 请求方法：{api.get('method', '')}
- 接口描述：{api.get('description', '')}

## 请求参数
{api.get('query', '')}

## 请求体
{api.get('body', '')}

## 响应示例
{api.get('response', '')}
"""
            # 分块
            chunks = chunk_text(content, chunk_size=500, overlap=50)
            
            # 索引
            rag_service.add_documents(
                project_id=project_id,
                knowledge_id=f"api_{api.get('id', '')}",
                documents=chunks
            )
        
        return {
            "status": "success",
            "message": f"同步成功，共处理{len(apis)}个接口"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")
