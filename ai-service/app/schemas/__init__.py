"""
数据模型模块

职责：
    1. 定义Pydantic数据模型
    2. 请求/响应数据校验
    3. 用例生成Schema定义

核心模型：
    - ChatRequestModel: AI对话请求
    - RagAddRequestModel: 知识库添加请求
    - GenerateCaseRequestModel: 用例生成请求
    - CaseRequestModel: 用例数据结构
    - ApiSelectionResult: 接口选择结果
"""

from app.schemas.ai_models import (
    MessageItem,
    ChatRequestModel,
    RagAddRequestModel,
    RagQueryRequestModel,
    RagDeleteRequestModel,
    GenerateCaseRequestModel,
    ApiSelectionResult,
    CaseApiStepModel,
    CaseRequestModel,
)

__all__ = [
    "MessageItem",
    "ChatRequestModel",
    "RagAddRequestModel",
    "RagQueryRequestModel",
    "RagDeleteRequestModel",
    "GenerateCaseRequestModel",
    "ApiSelectionResult",
    "CaseApiStepModel",
    "CaseRequestModel",
]
