"""
AI服务数据模型定义

职责：
    - 定义前后端交互的请求/响应数据结构
    - 使用 Pydantic 进行数据校验
    - 为 Agent 用例生成提供 Schema 约束

核心模型：
    - ChatRequestModel: AI对话请求
    - RagAddRequestModel: 知识库文档添加请求
    - GenerateCaseRequestModel: 用例生成请求
    - CaseRequestModel: 用例数据结构（符合平台后端规范）
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

    字段说明：
        - project_id: 项目ID（隔离主键）
        - doc_id: 文档ID（用于重建索引）
        - doc_type: 文档类型（manual/api_doc等）
        - doc_name: 文档名（用于关键词召回）
        - content: 文档内容
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
    """
    project_id: str
    user_id: Optional[str] = ""
    question: str
    top_k: int = 5
    messages: List[MessageItem] = Field(default_factory=list)


class RagDeleteRequestModel(BaseModel):
    """
    RAG知识库文档删除请求模型
    """
    project_id: str
    doc_id: str


class GenerateCaseRequestModel(BaseModel):
    """
    用例生成请求模型

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
    """
    api_ids: List[str] = Field(default_factory=list)
    reason: str = ""


class CaseApiStepModel(BaseModel):
    """
    用例步骤模型（CaseApiRequest）

    字段说明：
        - id: 步骤ID（后端生成，可空）
        - index: 步骤序号
        - caseId: 用例ID
        - apiId: 接口ID（必填）
        - description: 步骤描述
        - header/query/rest: 参数列表（每项仅保留name/value/required）
        - body: 请求体（type/form/json/raw/file五字段）
        - assertion: 断言列表
        - relation: 依赖关系（前置接口）
        - controller: 前置/后置处理
        - apiMethod/apiName/apiPath: 接口元信息
    """
    model_config = ConfigDict(extra="forbid")
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
        - name: 用例名称
        - level: 用例等级（P0/P1/P2/P3）
        - moduleId/moduleName: 模块信息
        - projectId: 项目ID（必填，用于数据隔离）
        - type: 用例类型（API/Web/App）
        - thirdParty: 第三方集成标识
        - description: 用例描述
        - environmentIds: 适用环境列表
        - system: 系统类型（web/ios/android）
        - commonParam: 公共参数（functions/params/header/proxy）
        - status: 用例状态（正常/禁用）
        - caseApis: API测试步骤列表
        - caseWebs: Web测试步骤列表
        - caseApps: App测试步骤列表
    """
    model_config = ConfigDict(extra="forbid")
    id: str = ""
    num: int = 0
    name: str
    level: str = "P1"
    moduleId: str
    moduleName: str
    projectId: str
    type: str = "API"
    thirdParty: str = ""
    description: str = ""
    environmentIds: List[Any] = Field(default_factory=list)
    system: str = "web"
    commonParam: Dict[str, Any] = Field(default_factory=dict)
    status: str = "正常"
    caseApis: List[CaseApiStepModel]
    caseWebs: List[Any] = Field(default_factory=list)
    caseApps: List[Any] = Field(default_factory=list)
