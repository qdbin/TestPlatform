from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageItem(BaseModel):
    role: str
    content: str


class ChatRequestModel(BaseModel):
    project_id: str
    user_id: Optional[str] = ""
    message: str
    use_rag: bool = True
    messages: List[MessageItem] = Field(default_factory=list)


class RagAddRequestModel(BaseModel):
    project_id: str
    user_id: Optional[str] = ""
    doc_id: str
    doc_type: str
    doc_name: str
    content: str


class RagQueryRequestModel(BaseModel):
    project_id: str
    user_id: Optional[str] = ""
    question: str
    top_k: int = 5
    messages: List[MessageItem] = Field(default_factory=list)


class RagDeleteRequestModel(BaseModel):
    project_id: str
    doc_id: str


class GenerateCaseRequestModel(BaseModel):
    project_id: str
    user_id: Optional[str] = ""
    user_requirement: str
    selected_apis: List[str] = Field(default_factory=list)
    messages: List[MessageItem] = Field(default_factory=list)


class ApiSelectionResult(BaseModel):
    api_ids: List[str] = Field(default_factory=list)
    reason: str = ""


class CaseApiStepModel(BaseModel):
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
