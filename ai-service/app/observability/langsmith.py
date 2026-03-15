"""
LangSmith配置模块

职责：
    1. 初始化LangSmith环境变量
    2. 配置追踪参数
    3. 提供LangSmith客户端

LangSmith说明：
    LangSmith是LangChain提供的LLM应用观测平台，支持：
    - 全链路追踪
    - 性能监控
    - 调试分析
    - 数据集管理

环境变量：
    - LANGSMITH_API_KEY: API密钥
    - LANGSMITH_PROJECT: 项目名称
    - LANGSMITH_TRACING: 是否启用追踪

使用示例：
    from app.observability.langsmith import get_langsmith_client
    client = get_langsmith_client()
"""

import os
from typing import Optional

from langsmith import Client

from app.config import config
from app.observability import app_logger


def setup_langsmith() -> None:
    """
    设置LangSmith环境变量

    从配置中读取LangSmith配置并设置环境变量。
    如果未配置API Key，则不启用追踪。
    """
    # 设置API Key
    if config.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = config.langsmith_api_key
        os.environ["LANGCHAIN_API_KEY"] = config.langsmith_api_key

    # 设置项目名称
    if config.langsmith_project:
        os.environ["LANGSMITH_PROJECT"] = config.langsmith_project
        os.environ["LANGCHAIN_PROJECT"] = config.langsmith_project

    # 设置追踪开关
    os.environ["LANGSMITH_TRACING"] = "true" if config.langsmith_tracing else "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "true" if config.langsmith_tracing else "false"

    if config.langsmith_tracing and config.langsmith_api_key:
        app_logger.info(
            "LangSmith追踪已启用: project={}",
            config.langsmith_project
        )
    else:
        app_logger.info("LangSmith追踪未启用")


_langsmith_client: Optional[Client] = None


def get_langsmith_client() -> Optional[Client]:
    """
    获取LangSmith客户端（单例）

    @return: LangSmith客户端实例或None
    """
    global _langsmith_client

    if _langsmith_client is None and config.langsmith_api_key:
        try:
            _langsmith_client = Client()
            app_logger.info("LangSmith客户端初始化成功")
        except Exception as e:
            app_logger.error("LangSmith客户端初始化失败: {}", str(e))

    return _langsmith_client


if __name__ == "__main__":
    """LangSmith配置调试"""
    print("=" * 60)
    print("LangSmith配置调试")
    print("=" * 60)

    print("\n1. 配置信息:")
    print(f"   API Key: {'已配置' if config.langsmith_api_key else '未配置'}")
    print(f"   Project: {config.langsmith_project}")
    print(f"   Tracing: {config.langsmith_tracing}")

    print("\n2. 环境变量:")
    setup_langsmith()
    print(f"   LANGSMITH_API_KEY: {'已设置' if os.getenv('LANGSMITH_API_KEY') else '未设置'}")
    print(f"   LANGSMITH_PROJECT: {os.getenv('LANGSMITH_PROJECT', '未设置')}")
    print(f"   LANGSMITH_TRACING: {os.getenv('LANGSMITH_TRACING', '未设置')}")

    print("\n3. 客户端状态:")
    client = get_langsmith_client()
    print(f"   客户端: {'已初始化' if client else '未初始化'}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
