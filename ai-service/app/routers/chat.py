"""
AI对话路由
处理AI聊天相关请求，支持SSE流式输出
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio

from app.services.agent_service import agent_service

router = APIRouter()


class ChatRequest(BaseModel):
    """对话请求"""

    project_id: str
    message: str
    use_rag: bool = True
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """对话响应"""

    content: str
    conversation_id: str


# 系统提示词
SYSTEM_PROMPT = """你是一个专业的API测试助手，专注于帮助用户进行API测试。

你可以：
1. 回答关于API测试的问题
2. 帮助用户理解接口文档
3. 提供测试用例设计建议
4. 解释测试结果和错误

请用简洁、专业的语言回答问题。"""


@router.post("/chat")
async def chat(request: ChatRequest, raw_request: Request):
    """
    AI对话接口（非流式）
    """
    try:
        token = raw_request.headers.get("token") or ""
        result = agent_service.chat(
            project_id=request.project_id,
            token=token,
            message=request.message,
            use_rag=request.use_rag,
        )

        return {
            "content": result.get("reply", ""),
            "case": result.get("case"),
            "conversation_id": request.conversation_id or "",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, raw_request: Request):
    """
    AI对话接口（SSE流式输出）
    """

    async def generate():
        try:
            token = raw_request.headers.get("token") or ""
            result = agent_service.chat(
                project_id=request.project_id,
                token=token,
                message=request.message,
                use_rag=request.use_rag,
            )

            reply = str(result.get("reply") or "")
            for ch in reply:
                yield f"data: {json.dumps({'type': 'content', 'delta': ch}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.002)

            if result.get("case") is not None:
                yield f"data: {json.dumps({'type': 'case', 'case': result.get('case')}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """
    获取会话历史
    """
    # TODO: 从数据库获取会话历史
    return {"conversation_id": conversation_id, "messages": []}
