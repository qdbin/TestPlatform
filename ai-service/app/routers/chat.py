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

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service

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
async def chat(request: ChatRequest):
    """
    AI对话接口（非流式）
    """
    try:
        # 构建消息列表
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        # 如果启用RAG，检索相关知识
        context = ""
        if request.use_rag:
            # 检索知识库
            docs = rag_service.search(request.project_id, request.message, top_k=3)
            if docs:
                context = "\n\n".join([f"参考知识：{doc['content']}" for doc in docs])
        
        # 构建完整prompt
        full_prompt = request.message
        if context:
            full_prompt = f"{context}\n\n用户问题：{request.message}\n\n请根据以上知识库内容回答用户问题。"
        
        # 调用LLM
        messages = [{"role": "user", "content": full_prompt}]
        response = llm_service.chat(messages, system_prompt=SYSTEM_PROMPT)
        
        return {
            "content": response,
            "conversation_id": request.conversation_id or ""
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    AI对话接口（SSE流式输出）
    """
    async def generate():
        try:
            # 构建消息
            messages = [
                {"role": "user", "content": request.message}
            ]
            
            # 如果启用RAG，检索知识
            context = ""
            if request.use_rag:
                docs = rag_service.search(request.project_id, request.message, top_k=3)
                if docs:
                    context = "\n\n".join([f"参考知识：{doc['content']}" for doc in docs])
            
            # 构建完整prompt
            full_prompt = request.message
            if context:
                full_prompt = f"{context}\n\n用户问题：{request.message}\n\n请根据以上知识库内容回答用户问题。"
            
            messages = [{"role": "user", "content": full_prompt}]
            
            # 流式输出
            full_response = ""
            for chunk in llm_service.chat_with_stream(messages, system_prompt=SYSTEM_PROMPT):
                content = chunk.content
                full_response += content
                # SSE格式发送
                yield f"data: {json.dumps({'type': 'content', 'delta': content})}\n\n"
                await asyncio.sleep(0.01)
            
            # 发送结束标记
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """
    获取会话历史
    """
    # TODO: 从数据库获取会话历史
    return {"conversation_id": conversation_id, "messages": []}
