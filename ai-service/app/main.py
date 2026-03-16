"""
架构说明：
    - 前端(Vue) → 后端(SpringBoot) → AI服务(FastAPI)
    - AI服务通过HTTP与SpringBoot后端通信
    - 使用SSE实现流式对话响应
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.observability import app_logger, setup_langsmith
from app.routers import chat, knowledge, agent


# ==================== FastAPI 应用初始化 ====================
# 初始化LangSmith追踪配置
setup_langsmith()

# 创建FastAPI应用实例
app = FastAPI(
    title="AI智能测试助手服务",
    description="为测试平台提供AI对话、Rag智能问答和用例生成功能",
    version="1.0.0",  # 服务版本：用于健康检查与部署核对
)

# ==================== CORS 中间件配置 ====================
# 配置跨域资源共享，允许前端应用访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,  # 允许的源地址列表
    allow_credentials=True,  # 允许携带凭证（cookie等）
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# ==================== 路由注册 ====================
app.include_router(chat.router, prefix="/ai", tags=["AI对话"])
app.include_router(knowledge.router, prefix="/ai/rag", tags=["RAG"])
app.include_router(agent.router, prefix="/ai/agent", tags=["用例生成"])


# ==================== 健康检查接口 ====================
@app.get("/")
async def root():
    app_logger.info("health_root_called")
    return {"status": "ok", "service": "AI智能测试助手", "version": "1.0.0"}


@app.get("/health")
async def health():
    app_logger.info("health_probe_called")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("AI智能测试助手服务启动")
    print("=" * 60)
    print(f"服务地址: http://{config.server_host}:{config.server_port}")
    print(f"文档地址: http://{config.server_host}:{config.server_port}/docs")
    print(f"LLM Provider: {config.llm_provider}")
    print(f"LLM Model: {config.llm_model}")
    print(f"平台地址: {config.platform_base_url}")
    print("=" * 60)

    uvicorn.run(
        "main:app", host=config.server_host, port=config.server_port, reload=True
    )
