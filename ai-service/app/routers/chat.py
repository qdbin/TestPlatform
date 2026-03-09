"""
AI对话路由
处理AI聊天相关请求，支持SSE流式输出
"""

from fastapi import APIRouter, Request
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
    use_rag=True 表示启用知识检索增强。
    """

    project_id: str
    message: str
    use_rag: bool = True
    messages: Optional[List[Dict[str, Any]]] = None


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, raw_request: Request):
    """
    AI对话接口（SSE流式输出）
    @param request: 聊天请求体
    @param raw_request: 原始HTTP请求（读取token）
    @return: text/event-stream 响应
    """

    def generate():
        try:
            token = raw_request.headers.get("token") or ""
            for event in agent_service.stream_chat(  # Agent层负责流式事件编排
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
