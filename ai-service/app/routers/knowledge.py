"""
RAG知识库路由
处理知识文档的增删改查

核心功能：
    1. POST /ai/rag/add - 新增知识文档
    2. POST /ai/rag/delete - 删除知识文档
    3. POST /ai/rag/query - 知识检索
    4. GET /ai/rag/stats/{project_id} - 获取统计信息

数据隔离：
    - 项目级隔离：通过 project_id 元数据过滤
    - 文档级隔离：通过 doc_id 标识每个文档
"""

from fastapi import APIRouter, HTTPException
from app.schemas import RagAddRequestModel, RagDeleteRequestModel, RagQueryRequestModel
from app.services.rag_service import rag_service
from app.utils.markdown_parent_child_chunking import markdown_parent_child_chunker

router = APIRouter()

# ==================== 知识文档接口 ====================


@router.post("/add")
async def add_document(request: RagAddRequestModel):
    """
    新增/重建知识文档索引

    实现步骤：
        1. 使用 markdown_parent_child_chunker 解析文档内容
        2. 调用 rag_service.add_document() 写入向量库
        3. 返回索引结果（含降级状态）

    @return: {status, indexed, degraded, vector_count, error}
    """
    try:
        # 步骤1：文档切片 - 按 Markdown 标题层级分块
        chunks = markdown_parent_child_chunker.split(request.content)
        if not chunks:
            return {
                "status": "success",
                "indexed": False,
                "degraded": False,
                "vector_count": 0,
                "error": "empty_documents",
            }

        # 步骤2：RAG写入 - embedding + upsert 到 Chroma
        index_result = rag_service.add_document(
            project_id=request.project_id,
            doc_id=request.doc_id,
            doc_type=request.doc_type,
            doc_name=request.doc_name,
            documents=chunks,
            user_id=request.user_id or "",
        )
        return {"status": "success", **index_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"新增文档失败: {str(e)}")


@router.post("/delete")
async def delete_document(request: RagDeleteRequestModel):
    """
    删除知识文档对应向量分片

    @return: {status, vector_deleted}
    """
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
async def query_knowledge(request: RagQueryRequestModel):
    """
    查询知识库并返回上下文答案

    实现步骤：
        1. 调用 rag_service.search_with_status() 执行混合检索
        2. 根据检索状态返回对应结果
        3. 无结果时提供友好的错误提示

    @return: {status, data, answer, has_context, rag_status}

    rag_status 状态说明：
        - success: 检索成功
        - no_context: 无相关文档
        - embedding_unavailable: Embedding服务不可用
        - vector_error: 向量库异常
    """
    try:
        search_result = rag_service.search_with_status(
            project_id=request.project_id,
            query=request.question,
            top_k=request.top_k,
            user_id=request.user_id or "",
        )
        results = search_result.get("data", [])

        # 无结果时的状态处理
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

        # 有结果时组装上下文
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
    """
    获取项目维度知识库统计信息

    @param project_id: 项目ID
    @return: {status, data: {count, project_id, collection_name}}
    """
    try:
        stats = rag_service.get_collection_stats(project_id)
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


if __name__ == "__main__":
    """
    知识库路由调试代码

    调试说明：
        1. 新增文档：POST /ai/rag/add
        2. 知识检索：POST /ai/rag/query
        3. 删除文档：POST /ai/rag/delete
        4. 获取统计：GET /ai/rag/stats/{project_id}

    测试命令示例：

    # 1. 新增文档
    curl -X POST http://localhost:8001/ai/rag/add \
      -H "Content-Type: application/json" \
      -d '{
        "project_id": "test-project",
        "doc_id": "doc-001",
        "doc_type": "manual",
        "doc_name": "登录接口文档",
        "content": "# 登录接口\n\n## 请求参数\n- username: 用户名\n- password: 密码"
      }'

    # 2. 知识检索
    curl -X POST http://localhost:8001/ai/rag/query \
      -H "Content-Type: application/json" \
      -d '{
        "project_id": "test-project",
        "question": "登录接口需要哪些参数？",
        "top_k": 3
      }'

    # 3. 删除文档
    curl -X POST http://localhost:8001/ai/rag/delete \
      -H "Content-Type: application/json" \
      -d '{
        "project_id": "test-project",
        "doc_id": "doc-001"
      }'

    # 4. 获取统计
    curl http://localhost:8001/ai/rag/stats/test-project
    """
    print("=" * 60)
    print("RAG知识库路由调试")
    print("=" * 60)
    print("\n接口列表：")
    print("  1. POST /ai/rag/add - 新增知识文档")
    print("  2. POST /ai/rag/query - 知识检索")
    print("  3. POST /ai/rag/delete - 删除知识文档")
    print("  4. GET /ai/rag/stats/{project_id} - 获取统计")
    print("\n数据隔离策略：")
    print("  - 项目隔离：project_id 元数据过滤")
    print("  - 文档隔离：doc_id 标识每个文档")
    print("=" * 60)
