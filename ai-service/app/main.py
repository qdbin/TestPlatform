"""
AI智能测试助手服务入口
FastAPI主应用配置和启动
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import config

# 路由导入
from app.routers import chat, knowledge, agent

# 创建FastAPI应用py
app = FastAPI(
    title="AI智能测试助手服务",
    description="为流马测试平台提供AI对话、知识库管理和用例生成功能",
    version="1.0.0",
)

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/ai", tags=["AI对话"])
app.include_router(knowledge.router, prefix="/ai/knowledge", tags=["知识库管理"])
app.include_router(agent.router, prefix="/ai/agent", tags=["用例生成"])


@app.get("/")
async def root():
    """根路径健康检查"""
    return {"status": "ok", "service": "AI智能测试助手", "version": "1.0.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=config.server_host, port=config.server_port, reload=True
    )
