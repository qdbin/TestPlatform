"""
AI服务数据模型定义

职责：
    1. 定义前后端交互的请求/响应数据结构
    2. 使用 Pydantic 进行数据校验
    3. 为 Agent 用例生成提供 Schema 约束

核心模型：
    - ChatRequestModel: AI对话请求
    - RagAddRequestModel: 知识库文档添加请求
    - GenerateCaseRequestModel: 用例生成请求
    - CaseRequestModel: 用例数据结构（符合平台后端规范）

数据模型关系：
    CaseRequestModel
    ├── CaseApiStepModel (步骤详情)
    └── MessageItem (对话消息)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageItem(BaseModel):
    """
    对话消息项

    字段说明：
        - role: 消息角色（user/assistant/system）
        - content: 消息内容

    示例：
        {"role": "user", "content": "你好"}
        {"role": "assistant", "content": "您好！有什么可以帮助您的？"}
    """

    role: str
    content: str


class ChatRequestModel(BaseModel):
    """
    AI对话请求模型

    请求示例：
        {
            "project_id": "test-project",
            "message": "你好",
            "use_rag": true,
            "messages": [{"role": "user", "content": "你好"}]
        }
    """

    project_id: str
    user_id: Optional[str] = ""
    message: str
    use_rag: bool = True
    messages: List[MessageItem] = Field(default_factory=list)


class RagAddRequestModel(BaseModel):
    """
    RAG知识库文档添加请求模型

    请求示例：
        {
            "project_id": "test-project",
            "user_id": "user-001",
            "doc_id": "doc-001",
            "doc_type": "manual",
            "doc_name": "登录接口文档",
            "content": "# 登录接口\\n\\n## 请求参数\\n..."
        }
    """

    project_id: str
    user_id: Optional[str] = ""
    doc_id: str
    doc_type: str
    doc_name: str
    content: str


class RagQueryRequestModel(BaseModel):
    """
    RAG知识库检索请求模型

    请求示例：
        {
            "project_id": "test-project",
            "question": "登录接口需要哪些参数？",
            "top_k": 3
        }
    """

    project_id: str
    user_id: Optional[str] = ""
    question: str
    top_k: int = 5
    messages: List[MessageItem] = Field(default_factory=list)


class RagDeleteRequestModel(BaseModel):
    """
    RAG知识库文档删除请求模型

    字段说明：
        - project_id: 项目ID（必填）
        - doc_id: 文档ID（必填）

    请求示例：
        {
            "project_id": "test-project",
            "doc_id": "doc-001"
        }
    """

    project_id: str
    doc_id: str


class GenerateCaseRequestModel(BaseModel):
    """
    用例生成请求模型

    字段说明：
        - project_id: 项目ID（必填）
        - user_id: 用户ID（可选）
        - user_requirement: 用户需求描述（必填）
        - selected_apis: 预选接口ID列表（可选）
        - messages: 历史对话消息（可选）

    请求示例：
        {
            "project_id": "test-project",
            "user_requirement": "设计登录+注册的完整测试流程",
            "selected_apis": [],
            "messages": []
        }
    """

    project_id: str
    user_id: Optional[str] = ""
    user_requirement: str
    selected_apis: List[str] = Field(default_factory=list)
    messages: List[MessageItem] = Field(default_factory=list)


class ApiSelectionResult(BaseModel):
    """
    接口选择结果模型

    字段说明：
        - api_ids: 选中的接口ID列表
        - reason: 选择原因说明

    返回示例：
        {
            "api_ids": ["api-001", "api-002"],
            "reason": "登录接口和注册接口是用户登录流程的核心接口"
        }
    """

    api_ids: List[str] = Field(default_factory=list)
    reason: str = ""


class CaseApiStepModel(BaseModel):
    """
    用例步骤模型（CaseApiRequest）

    字段说明：
        - id: 步骤ID（后端生成，可空）
        - index: 步骤序号（从1开始）
        - caseId: 用例ID（后端生成，可空）
        - apiId: 接口ID（必填）
        - description: 步骤描述
        - header/query/rest: 参数列表（每项仅保留name/value/required）
        - body: 请求体（type/form/json/raw/file五字段）
        - assertion: 断言列表
        - relation: 依赖关系（前置接口）
        - controller: 前置/后置处理
        - apiMethod/apiName/apiPath: 接口元信息

    body格式示例：
        {
            "type": "json",
            "form": [],
            "json": "{\\"username\\":\\"test\\"}",
            "raw": "",
            "file": []
        }
    """

    model_config = ConfigDict(extra="forbid")  # 禁止额外字段，确保数据严格
    id: str = ""
    index: int = 0
    caseId: str = ""
    apiId: str
    description: str = ""
    header: List[Any] = Field(default_factory=list)
    body: Dict[str, Any] = Field(default_factory=dict)
    query: List[Any] = Field(default_factory=list)
    rest: List[Any] = Field(default_factory=list)
    assertion: List[Any] = Field(default_factory=list)
    relation: List[Any] = Field(default_factory=list)
    controller: List[Any] = Field(default_factory=list)
    apiMethod: str = ""
    apiName: str = ""
    apiPath: str = ""


class CaseRequestModel(BaseModel):
    """
    完整用例模型（CaseRequest）

    字段说明：
        - id: 用例ID（后端生成，可空）
        - num: 用例编号
        - name: 用例名称（必填）
        - level: 用例等级（P0/P1/P2/P3）
        - moduleId/moduleName: 模块信息
        - projectId: 项目ID（必填，用于数据隔离）
        - type: 用例类型（API/Web/App）
        - thirdParty: 第三方集成标识
        - description: 用例描述
        - environmentIds: 适用环境列表
        - system: 系统类型（web/ios/android）
        - commonParam: 公共参数（functions/params/header/proxy）
        - status: 用例状态（Normal/Disabled）
        - caseApis: API测试步骤列表（必填）
        - caseWebs: Web测试步骤列表
        - caseApps: App测试步骤列表

    完整示例：
        {
            "id": "",
            "num": 0,
            "name": "用户登录流程测试",
            "level": "P0",
            "moduleId": "m1",
            "moduleName": "用户模块",
            "projectId": "p1",
            "type": "API",
            "caseApis": [...]
        }
    """

    model_config = ConfigDict(extra="forbid")  # 禁止额外字段
    id: str = ""
    num: int = 0
    name: str
    level: str = "P0"
    moduleId: str
    moduleName: str
    projectId: str
    type: str = "API"
    thirdParty: str = ""
    description: str = ""
    environmentIds: List[Any] = Field(default_factory=list)
    system: str = "web"
    commonParam: Dict[str, Any] = Field(default_factory=dict)
    status: str = "Normal"
    caseApis: List[CaseApiStepModel]
    caseWebs: List[Any] = Field(default_factory=list)
    caseApps: List[Any] = Field(default_factory=list)
