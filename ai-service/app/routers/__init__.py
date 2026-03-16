"""
路由模块

职责：
    1. 定义AI服务的API路由
    2. 处理HTTP请求和响应
    3. 路由注册和配置

路由列表：
    - chat: AI对话路由 (/ai/chat)
    - knowledge: RAG知识库路由 (/ai/rag)
    - agent: 用例生成路由 (/ai/agent)
"""

from app.routers import chat, knowledge, agent

__all__ = ["chat", "knowledge", "agent"]
