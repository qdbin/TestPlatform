"""
AI对话路由
处理AI聊天相关请求，支持SSE流式输出

核心功能：
    1. POST /ai/chat/stream - SSE流式对话接口
    2. 自动识别用例需求并分流处理

请求格式：
    {
        "project_id": "项目ID",
        "message": "用户消息",
        "use_rag": true,  // 是否启用知识库检索
        "messages": [{"role": "user/assistant", "content": "..."}]
    }

响应格式（SSE事件流）：
    {"type": "content", "delta": "..."}
    {"type": "case", "case": {...}, "api_ids": [...]}
    {"type": "error", "message": "..."}
    {"type": "end"}

SSE协议说明：
    - Content-Type: text/event-stream
    - 每个事件以 data: {...}\n\n 格式发送
    - 前端按 \n\n 分帧消费
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import json

from app.schemas import ChatRequestModel
from app.services.agent_service import agent_service

router = APIRouter()


@router.post("/chat/stream")
async def chat_stream(request: ChatRequestModel, raw_request: Request):
    """
    AI对话接口（SSE流式输出）

    功能说明：
        - 接收用户消息，返回AI回复的SSE流
        - 自动识别用例生成需求并分流处理
        - 支持RAG知识库检索增强回答

    @param request: 聊天请求体，包含项目ID、消息、配置
    @param raw_request: 原始HTTP请求，用于提取token
    @return: text/event-stream 响应

    实现步骤：
        1. 从请求头获取token用于平台鉴权
        2. 调用 agent_service.stream_chat() 获取SSE事件流
        3. 将事件转换为SSE格式并返回
        4. 捕获异常并转换为错误事件
    """

    async def generate():
        try:
            # 步骤1：从请求头获取token用于平台API鉴权
            token = raw_request.headers.get("token") or ""

            # 步骤2：调用Agent服务获取流式响应
            # Agent层负责流式事件编排，区分问答/用例生成
            async for event in agent_service.stream_chat(
                project_id=request.project_id,
                token=token,
                message=request.message,
                use_rag=request.use_rag,
                messages=[item.model_dump() for item in request.messages],
                user_id=request.user_id or "",
            ):
                # SSE标准帧格式：每个事件以双换行结尾\n\n
                # 前端按 \n\n 分帧消费
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        except Exception as e:
            # 异常也按SSE事件输出，避免前端读流阻塞
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    # 返回StreamingResponse，设置SSE所需响应头
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",  # 禁用缓存
            "Connection": "keep-alive",  # 保持长连接
            "X-Accel-Buffering": "no",  # 禁用Nginx缓冲，确保实时推送
        },
    )
