"""
AI对话路由
处理AI聊天相关请求，支持SSE流式输出
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from app.services.agent_service import agent_service

router = APIRouter()


class ChatRequest(BaseModel):
    """
    聊天请求模型。
    messages示例: [{"role":"user","content":"上个问题"}, {"role":"assistant","content":"上个回答"}]
    """
    project_id: str
    message: str
    use_rag: bool = True
    messages: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    content: str


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
            messages=request.messages or [],
        )

        return {
            "content": result.get("reply", ""),
            "case": result.get("case"),
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
            for event in agent_service.stream_chat(
                project_id=request.project_id,
                token=token,
                message=request.message,
                use_rag=request.use_rag,
                messages=request.messages or [],
            ):
                # SSE标准帧：每个事件以双换行结尾，前端按 \n\n 分帧消费。
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            # 正常收尾事件，前端据此停止读取。
            yield f"data: {json.dumps({'type': 'end'}, ensure_ascii=False)}\n\n"

        except Exception as e:
            # 异常也按SSE事件输出，避免前端读流阻塞。
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
