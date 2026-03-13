"""
Agent核心编排模块

职责：
    1. 基于 LangChain ReAct 工具链选择项目接口
    2. 融合 RAG 证据、Schema 约束和历史消息生成可保存用例
    3. 提供普通问答与 SSE 流式输出统一入口

核心类说明：
    - AgentService: 主服务类，负责对话/用例生成流程编排
    - CaseRequestModel: 用例请求数据模型（Pydantic）
    - CaseApiStepModel: 用例步骤模型

主要流程：
    1. 对话流程：识别用例需求 -> RAG检索 -> LLM回答
    2. 用例生成流程：选接口 -> 读详情 -> 融合RAG -> LLM生成 -> 校验
"""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, ValidationError, ConfigDict

try:
    from json_repair import repair_json
except Exception:

    def repair_json(text: str, return_objects: bool = False):
        return re.sub(r",\s*([}\]])", r"\1", text or "")


from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.case_workflow import CaseGenerationWorkflow, CaseWorkflowContext
from app.observability import app_logger
from app.tools.platform_tools import get_platform_client


# ==================== 系统提示词 ====================
ASSISTANT_ROLE_PROMPT = """你是接口自动化测试平台的AI智能助手，专注于帮助用户进行接口测试和用例设计。

## 核心职责
1. **知识问答**：回答接口测试、自动化测试、测试设计相关问题
2. **用例生成**：基于项目已有接口，生成结构化测试用例JSON
3. **问题排查**：提供接口调试、测试执行问题的排查建议

## 回答规则
1. **准确性优先**：只回答确定的内容，不确定时明确说明
2. **结构化输出**：用例生成必须输出严格符合Schema的JSON
3. **项目隔离**：只能使用当前项目已有接口，禁止虚构接口
4. **知识库优先**：回答项目相关问题时优先引用知识库证据

## 用例生成规则
1. 只能使用已存在的apiId，不得创建新接口
2. 输出必须是纯JSON格式，不包含Markdown标记
3. 每个步骤必须包含apiId、apiMethod、apiPath、apiName
4. 至少生成2个步骤（正向场景+异常场景）
5. 流程类需求需串联多个相关接口
6. 禁止输出草稿、提案、伪代码、自然语言步骤
7. 禁止补充数据库不存在的接口、字段或路径"""

CHAT_ROLE_PROMPT = """你是接口测试助手。
要求：
1. 直接回答，先给结论再给要点；
2. 避免冗长铺垫，优先短句；
3. 不确定时明确说明不确定。"""


# ==================== 数据模型定义 ====================


class CaseApiStepModel(BaseModel):
    """
    用例步骤模型（API接口）

    字段说明：
        - apiId: 关联的接口ID
        - apiMethod: HTTP方法
        - apiPath: 接口路径
        - apiName: 接口名称
        - description: 步骤描述
        - header/query/body: 请求参数
        - assertion: 断言配置
    """

    model_config = ConfigDict(extra="forbid")
    id: str = ""
    index: int = 0
    caseId: str = ""
    apiId: str
    description: str = ""
    header: List[Any] = []
    body: Dict[str, Any] = {}
    query: List[Any] = []
    rest: List[Any] = []
    assertion: List[Any] = []
    relation: List[Any] = []
    controller: List[Any] = []
    apiMethod: str = ""
    apiName: str = ""
    apiPath: str = ""


class CaseRequestModel(BaseModel):
    """
    测试用例请求模型

    顶层字段：
        - name: 用例名称
        - projectId: 项目ID
        - moduleId/moduleName: 模块信息
        - caseApis: 用例步骤列表
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
    environmentIds: List[Any] = []
    system: str = "web"
    commonParam: Dict[str, Any] = {}
    status: str = "正常"
    caseApis: List[CaseApiStepModel]
    caseWebs: List[Any] = []
    caseApps: List[Any] = []


class ApiIdInput(BaseModel):
    """ReAct Agent 工具输入模型"""

    api_id: str


# ==================== 工具函数 ====================


def _try_parse_json_object(text: str) -> Optional[Dict[str, Any]]:
    """
    尝试解析 JSON 对象

    实现策略：
        1. 直接尝试解析
        2. 使用 json_repair 修复后解析
        3. 正则提取 JSON 片段后解析

    @param text: 待解析文本
    @return: 解析后的字典，失败返回 None
    """
    if not text:
        return None
    source = text.strip()
    if not source:
        return None
    for candidate in [source, repair_json(source, return_objects=False)]:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    match = re.search(r"\{[\s\S]*\}", source)
    if not match:
        return None
    try:
        parsed = json.loads(repair_json(match.group(0), return_objects=False))
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None
    return None


def _normalize_messages(
    messages: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, str]]:
    """
    规范化消息格式

    过滤规则：
        - 只保留 role 为 user/assistant 的消息
        - 跳过空内容
        - 转换为 LangChain 所需格式

    @param messages: 原始消息列表
    @return: 规范化后的消息列表
    """
    if not isinstance(messages, list):
        return []
    result: List[Dict[str, str]] = []
    for item in messages:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "")
        content = str(item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            result.append({"role": role, "content": content})
    return result


def _is_case_request(message: str) -> bool:
    """
    判断是否为用例生成需求

    识别规则：
        - 包含"用例/测试点/测试场景"等关键词
        - 包含"生成/设计/编写/创建"等动作词

    @param message: 用户消息
    @return: 是否为用例需求
    """
    text = (message or "").lower()
    case_terms = ["用例", "测试点", "测试场景", "测试步骤", "test case", "case"]
    action_terms = ["生成", "设计", "编写", "创建", "输出", "规划", "帮我", "给我"]
    has_case = any(item in text for item in case_terms)
    has_action = any(item in text for item in action_terms)
    return has_case and has_action


def _is_project_private_query(message: str) -> bool:
    """
    判断是否为项目私有问题

    识别规则：
        - 包含项目相关关键词（接口/API/环境等）
        - 包含 URL 路径格式

    @param message: 用户消息
    @return: 是否为私有问题
    """
    text = (message or "").lower()
    private_keywords = [
        "当前项目",
        "本项目",
        "我们系统",
        "我们项目",
        "私有",
        "内部",
        "公司",
        "接口",
        "api",
        "数据库",
        "环境",
        "配置",
        "上线",
        "日志",
        "报错",
        "token",
        "login",
        "register",
        "auth",
        "endpoint",
        "path",
        "url",
    ]
    if any(keyword in text for keyword in private_keywords):
        return True
    if re.search(r"/[a-zA-Z0-9_\-/]+", text):
        return True
    return False


class AgentService:
    """
    AgentService（AI助手核心服务）

    主要职责：
        - ReAct选接口：使用LangChain Agent选择项目接口
        - RAG增强：融合知识库检索结果
        - Case标准化：Pydantic模型校验生成用例
        - SSE事件编排：流式输出支持
    """

    def __init__(self):
        # 初始化用例生成工作流
        self.case_workflow = CaseGenerationWorkflow(
            get_platform_client=lambda token: get_platform_client(token),
            select_api_ids=self._select_api_ids,
            build_dependency_relations=self._build_dependency_relations,
            build_case_prompt=self._build_case_prompt,
            normalize_case=self._normalize_case,
            parse_json_object=_try_parse_json_object,
            case_model=CaseRequestModel,
            assistant_role_prompt=ASSISTANT_ROLE_PROMPT,
        )

    def _extract_path_tokens(self, api_item: Dict[str, Any]) -> Set[str]:
        """
        从API路径提取语义token

        实现步骤：
            1. 获取path/URL字段并转小写
            2. 按分隔符拆分token
            3. 过滤停用词和数字

        @param api_item: 接口详情字典
        @return: 有意义的token集合
        """
        path = str(api_item.get("path") or api_item.get("url") or "").lower()
        raw_tokens = re.split(r"[/_\-\{\}\.\s]+", path)
        stop_words = {"api", "v1", "v2", "v3", "rest", "openapi"}
        return {
            token
            for token in raw_tokens
            if token
            and len(token) > 1
            and not token.isdigit()
            and token not in stop_words
        }

    def _build_dependency_relations(
        self, api_details: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        构建接口依赖关系图

        依赖识别规则：
            1. 路径token重叠度
            2. 认证接口优先（login/auth/token）
            3. 注册→登录链路

        @param api_details: 接口详情列表
        @return: {api_id: [依赖api_id列表]}
        """
        if not api_details:
            return {}
        relations: Dict[str, List[str]] = {}
        auth_cues = {"login", "signin", "auth", "token", "oauth"}
        register_cues = {"register", "signup", "user", "account"}

        # 阶段1：提取所有接口的token
        api_tokens = {
            str(item.get("id")): self._extract_path_tokens(item)
            for item in api_details
            if isinstance(item, dict) and item.get("id")
        }

        # 阶段2：计算接口间依赖分数
        for current in api_details:
            if not isinstance(current, dict):
                continue
            current_id = str(current.get("id") or "")
            if not current_id:
                continue
            current_tokens = api_tokens.get(current_id, set())
            current_method = str(current.get("method") or "").upper()
            scored: List[Dict[str, Any]] = []

            for candidate in api_details:
                if not isinstance(candidate, dict):
                    continue
                candidate_id = str(candidate.get("id") or "")
                if not candidate_id or candidate_id == current_id:
                    continue
                candidate_tokens = api_tokens.get(candidate_id, set())

                # token重叠度
                overlap = len(current_tokens & candidate_tokens)
                score = overlap

                # 认证接口加权
                if current_method in {"GET", "PUT", "DELETE"} and (
                    candidate_tokens & auth_cues
                ):
                    score += 2
                # 注册→登录链路
                if (current_tokens & register_cues) and (candidate_tokens & auth_cues):
                    score += 1

                if score > 0:
                    scored.append({"id": candidate_id, "score": score})

            # 排序取Top3
            scored.sort(key=lambda x: x.get("score", 0), reverse=True)
            relations[current_id] = [item["id"] for item in scored[:3]]
        return relations

    def _build_chat_prompt(
        self, message: str, rag_docs: List[Dict[str, Any]], rag_status: str
    ) -> str:
        """
        构建对话Prompt

        策略选择：
            1. 有RAG结果 → 融合知识片段
            2. 无结果 + 私有问题 → 提示无证据
            3. 无结果 + 公开问题 → 直接回答
            4. RAG异常 → 降级回答

        @param message: 用户消息
        @param rag_docs: RAG检索结果
        @param rag_status: RAG状态码
        @return: 构建后的Prompt
        """
        docs = [item for item in (rag_docs or []) if isinstance(item, dict)]
        context = "\n\n".join(
            [str(item.get("content") or "") for item in docs if item.get("content")]
        ).strip()

        # 策略1：有RAG结果，融合知识片段
        if context:
            return (
                "你将同时使用知识库证据和你的通用知识回答。\n"
                "要求：优先引用知识片段中的事实；缺失处可补充通用知识；避免编造项目细节。\n"
                f"知识片段：\n{context}\n\n"
                f"用户问题：{message}"
            )

        is_private = _is_project_private_query(message)

        # 策略2：无RAG结果，区分处理
        if rag_status == "no_context":
            if is_private:
                return (
                    "这是项目私有问题，但知识库未检索到直接证据。\n"
                    "请先明确说明未检索到证据，再基于通用经验给出可执行排查建议。\n"
                    f"用户问题：{message}"
                )
            return (
                "这是公开或通用问题。请直接基于通用知识回答，不要提及知识库未命中。\n"
                f"用户问题：{message}"
            )

        # 策略3：RAG异常
        if rag_status and rag_status != "success":
            return (
                "知识库暂不可用。请基于通用知识先给出准确回答，并在最后补一句可稍后重试知识库。\n"
                f"用户问题：{message}"
            )

        # 策略4：直接返回原问题
        return message

    def _build_case_selector_executor(
        self, project_id: str, token: str, all_apis: List[Dict[str, Any]]
    ) -> AgentExecutor:
        """
        构建 LangChain ReAct 执行器

        实现步骤：
            1. 获取LLM实例
            2. 定义ReAct工具函数（列表/详情/关系）
            3. 构建工具集和Prompt模板
            4. 创建AgentExecutor

        @param project_id: 项目ID
        @param token: 平台鉴权token
        @param all_apis: 项目接口池
        @return: AgentExecutor（含工具注册与Prompt约束）
        """
        # 获取LLM实例
        llm = llm_service._get_llm()
        if llm is None:
            raise RuntimeError("llm_not_configured")
        # 获取平台客户端
        platform_client = get_platform_client(token)

        # 定义工具1：获取接口列表
        def get_api_list(_: str) -> str:
            payload = [
                {
                    "id": str(item.get("id") or ""),
                    "name": str(item.get("name") or ""),
                    "path": str(item.get("path") or item.get("url") or ""),
                    "method": str(item.get("method") or ""),
                    "description": str(item.get("description") or ""),
                }
                for item in all_apis
                if isinstance(item, dict) and item.get("id")
            ]
            return json.dumps(payload, ensure_ascii=False)

        # 定义工具2：获取接口详情
        def get_api_detail(api_id: str) -> str:
            detail = platform_client.get_api_detail(str(api_id).strip())
            return json.dumps(detail or {}, ensure_ascii=False)

        # 定义工具3：获取接口依赖关系
        def get_api_relation(api_id: str) -> str:
            # 查找目标接口
            target = None
            for item in all_apis:
                if isinstance(item, dict) and str(item.get("id")) == str(api_id):
                    target = item
                    break
            if target is None:
                return "[]"
            # 提取路径片段用于关联匹配
            path = str(target.get("path") or target.get("url") or "").strip("/")
            segments = [seg for seg in path.split("/") if seg]
            # 查找相关接口
            related: List[Dict[str, Any]] = []
            for item in all_apis:
                if not isinstance(item, dict):
                    continue
                current_id = str(item.get("id") or "")
                current_path = str(item.get("path") or item.get("url") or "")
                if current_id == str(api_id):
                    continue
                # 路径片段匹配
                if any(seg and seg in current_path for seg in segments):
                    related.append(
                        {
                            "id": current_id,
                            "path": current_path,
                            "name": item.get("name"),
                        }
                    )
            return json.dumps(related[:5], ensure_ascii=False)

        # 构建ReAct工具集
        tools = [
            Tool(
                name="get_api_list",
                func=get_api_list,
                description="获取当前项目全部接口列表，输入固定为none",
            ),
            StructuredTool.from_function(
                name="get_api_detail",
                func=lambda api_id: get_api_detail(api_id),
                args_schema=ApiIdInput,
                description="输入接口id，返回该接口详细信息",
            ),
            StructuredTool.from_function(
                name="get_api_relation",
                func=lambda api_id: get_api_relation(api_id),
                args_schema=ApiIdInput,
                description="输入接口id，返回接口依赖关系",
            ),
        ]
        # 构建Prompt模板
        prompt = PromptTemplate.from_template(
            "你是测试用例生成规划代理。\n"
            "你必须先调用get_api_list，再按用户需求筛选流程相关接口。\n"
            "只能基于现有接口选择api_id，禁止创建接口。\n"
            "优先选择与业务流程相关的一组接口（例如登录+注册+鉴权），而非单个无关接口。\n"
            "必须使用工具完成分析后输出最终JSON。\n"
            '最终输出格式必须为：{"api_ids":["1","2"],"reason":"..."}\n'
            "可用工具：\n{tools}\n\n工具名：{tool_names}\n\n"
            "Question: {input}\nThought: {agent_scratchpad}"
        )
        # 创建Agent
        agent = create_react_agent(llm, tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            max_iterations=6,
            handle_parsing_errors=True,
            verbose=False,
        )

    def _select_api_ids(
        self,
        project_id: str,
        token: str,
        user_requirement: str,
        all_apis: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Agent调度入口：根据用户需求从项目接口池中选择候选api_id。
        调度策略：
        1) 优先调用ReAct工具链做语义筛选；
        2) 失败时回退关键词打分；
        3) 流程类需求至少补足多接口链路。
        """
        # 边界检查：空接口池直接返回
        if not all_apis:
            return []
        # 语义分组：建立业务场景与关键词的映射关系
        query = user_requirement.lower()
        semantic_groups = {
            "login": ["登录", "signin", "login", "auth", "token", "oauth", "session"],
            "register": ["注册", "signup", "register", "create user", "user/create"],
            "user": ["用户", "user", "account", "账号", "个人信息"],
            "flow": ["流程", "链路", "闭环", "完整", "前后", "先后", "场景"],
        }
        # 匹配用户需求中的语义分组
        matched_groups = [
            group
            for group, cues in semantic_groups.items()
            if any(cue.lower() in query for cue in cues)
        ]
        # 策略1：优先走 ReAct 工具链，拿到可解释的 api_ids
        try:
            executor = self._build_case_selector_executor(project_id, token, all_apis)
            result = executor.invoke({"input": user_requirement})
            output = result.get("output") if isinstance(result, dict) else ""
            parsed = _try_parse_json_object(str(output or ""))
            api_ids = parsed.get("api_ids") if isinstance(parsed, dict) else []
            ids = [str(item) for item in api_ids if str(item)]
            if ids:
                # 流程类需求需补足多接口链路
                if "flow" in matched_groups and len(ids) < 2:
                    available = [
                        str(item.get("id"))
                        for item in all_apis
                        if isinstance(item, dict) and item.get("id")
                    ]
                    seen = set(ids)
                    for candidate in available:
                        if candidate in seen:
                            continue
                        ids.append(candidate)
                        seen.add(candidate)
                        if len(ids) >= 3:
                            break
                return ids[:5]
        except Exception:
            pass
        # 策略2：回退阶段，使用关键词打分筛选接口
        ranked: List[Dict[str, Any]] = []
        for item in all_apis:
            if not isinstance(item, dict):
                continue
            current_id = str(item.get("id") or "")
            if not current_id:
                continue
            name = str(item.get("name") or "").lower()
            path = str(item.get("path") or item.get("url") or "").lower()
            description = str(item.get("description") or "").lower()
            # 关键词匹配计分
            score = 0
            corpus = f"{name} {path} {description}"
            for token_item in re.split(r"[\s,，。;；]+", query):
                token_item = token_item.strip()
                if token_item and token_item in corpus:
                    score += 1
            # 语义分组加权
            for group in matched_groups:
                cues = semantic_groups.get(group, [])
                if any(cue.lower() in corpus for cue in cues):
                    score += 3
            # 流程组合加权：注册+登录场景
            if "flow" in matched_groups and any(
                tag in matched_groups for tag in ["login", "register", "user"]
            ):
                if any(
                    cue.lower() in corpus
                    for cue in semantic_groups.get("login", [])
                    + semantic_groups.get("register", [])
                ):
                    score += 2
            ranked.append({"id": current_id, "score": score})
        # 排序并返回Top5
        ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
        top = [item["id"] for item in ranked if item.get("score", 0) > 0][:5]
        if top:
            return top
        # 兜底策略：返回前3个接口ID
        fallback = [
            str(item.get("id"))
            for item in all_apis
            if isinstance(item, dict) and item.get("id")
        ]
        return fallback[:3]

    def _build_case_prompt(
        self,
        project_id: str,
        user_requirement: str,
        api_details: List[Dict[str, Any]],
        api_relations: Dict[str, List[str]],
        rag_docs: List[Dict[str, Any]],
        schema_payload: Dict[str, Any],
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        组装用例生成Prompt。
        将接口清单、依赖关系、知识片段与后端Schema压入上下文，约束模型只输出可保存JSON。
        """
        history_text = "\n".join(
            [
                f"{item.get('role')}: {item.get('content')}"
                for item in _normalize_messages(messages)
            ]
        )
        api_list_summary = [
            {
                "id": str(item.get("id")),
                "name": str(item.get("name") or ""),
                "path": str(item.get("path") or item.get("url") or ""),
                "method": str(item.get("method") or ""),
                "moduleId": str(item.get("moduleId") or "0"),
                "moduleName": str(item.get("moduleName") or "默认模块"),
            }
            for item in api_details
        ]
        return (
            "你是接口测试平台的用例生成器。请根据用户需求生成可直接保存的测试用例JSON。\n\n"
            "## 重要约束\n"
            "1. 只能使用下方接口列表中的apiId，禁止创建新接口\n"
            "2. 输出必须是纯JSON对象，不要包含```json标记或任何解释\n"
            "3. 必须符合后端CaseRequest Schema结构\n\n"
            "4. 必须保证 projectId 为当前项目ID，且每个 caseApis.apiId 来自可用接口列表\n\n"
            f"## 项目ID\n{project_id}\n\n"
            f"## 用户需求\n{user_requirement}\n\n"
            f"## 历史对话\n{history_text or '无'}\n\n"
            f"## 可用接口列表\n{json.dumps(api_list_summary, ensure_ascii=False, indent=2)}\n\n"
            f"## 接口依赖关系\n{json.dumps(api_relations, ensure_ascii=False)}\n\n"
            f"## 知识片段\n{json.dumps(rag_docs[:3], ensure_ascii=False)}\n\n"
            f"## 后端Schema参考\n{json.dumps(schema_payload, ensure_ascii=False, indent=2)[:2000]}\n\n"
            "## 小样本（仅示例结构，不可复用示例apiId）\n"
            "{\n"
            '  "name": "登录流程用例",\n'
            '  "projectId": "当前项目ID",\n'
            '  "type": "API",\n'
            '  "moduleId": "模块ID",\n'
            '  "moduleName": "模块名",\n'
            '  "caseApis": [\n'
            '    {"index": 1, "apiId": "真实接口ID", "description": "正向场景", "header": [], "body": {}, "query": [], "rest": [], "assertion": [], "relation": [], "controller": [], "apiMethod": "POST", "apiName": "接口名", "apiPath": "/path"},\n'
            '    {"index": 2, "apiId": "真实接口ID", "description": "异常场景", "header": [], "body": {}, "query": [], "rest": [], "assertion": [], "relation": [], "controller": [], "apiMethod": "GET", "apiName": "接口名", "apiPath": "/path"}\n'
            "  ]\n"
            "}\n\n"
            "## 输出要求\n"
            "1. 顶层字段必须包含：name, projectId, moduleId, moduleName, type='API'\n"
            "2. caseApis数组不能为空，每个元素必须包含：apiId, index, description\n"
            "3. 根据需求选择合适的接口组合，流程类需求需串联多个接口\n"
            "4. 至少生成2个步骤（可包含正向和异常场景）\n"
            "5. 每个步骤补全apiMethod、apiPath、apiName（从接口列表复制）\n\n"
            "## 输出格式\n"
            '你必须输出合法 JSON 对象，以便 response_format={"type":"json_object"} 直接解析。\n'
            "直接输出JSON对象，不要任何解释或Markdown标记。\n"
            "不需要包含后端自动生成字段（如createTime、updateTime、createUser）。\n"
        )

    def _normalize_case(
        self,
        project_id: str,
        case_obj: Dict[str, Any],
        api_details: List[Dict[str, Any]],
        api_relations: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """
        用例标准化校验

        实现步骤：
            1. 校验并填充必填字段
            2. 过滤无效接口ID
            3. 补全步骤元数据
            4. 确保至少2个步骤

        @param project_id: 项目ID
        @param case_obj: LLM生成的原始用例
        @param api_details: 接口详情列表
        @param api_relations: 接口依赖关系
        @return: 标准化后的用例字典
        """
        first_api = api_details[0] if api_details else {}
        valid_api_ids = {
            str(item.get("id"))
            for item in api_details
            if isinstance(item, dict) and item.get("id")
        }
        relation_map = api_relations or {}
        module_id = str(first_api.get("moduleId") or "0")
        module_name = str(first_api.get("moduleName") or "默认模块")
        now_name = f"AI生成用例-{datetime.now().strftime('%m%d%H%M%S')}"
        normalized = dict(case_obj or {})

        # 步骤1：填充必填字段
        normalized["id"] = str(normalized.get("id") or "")
        normalized["num"] = int(normalized.get("num") or 0)
        normalized["name"] = str(normalized.get("name") or now_name)
        normalized["level"] = str(normalized.get("level") or "P1")
        normalized["moduleId"] = str(normalized.get("moduleId") or module_id)
        normalized["moduleName"] = str(normalized.get("moduleName") or module_name)
        normalized["projectId"] = str(project_id)
        normalized["type"] = "API"
        normalized["thirdParty"] = str(normalized.get("thirdParty") or "")
        normalized["description"] = str(
            normalized.get("description") or "AI自动生成用例"
        )
        normalized["environmentIds"] = (
            normalized.get("environmentIds")
            if isinstance(normalized.get("environmentIds"), list)
            else []
        )
        normalized["system"] = str(normalized.get("system") or "web")
        normalized["commonParam"] = (
            normalized.get("commonParam")
            if isinstance(normalized.get("commonParam"), dict)
            else {}
        )
        normalized["status"] = str(normalized.get("status") or "正常")

        # 步骤2：处理用例步骤
        steps = (
            normalized.get("caseApis")
            if isinstance(normalized.get("caseApis"), list)
            else []
        )
        normalized_steps: List[Dict[str, Any]] = []
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            api_id = str(step.get("apiId") or "")
            if not api_id and api_details:
                api_id = str(
                    api_details[min(index, len(api_details) - 1)].get("id") or ""
                )
            if not api_id or api_id not in valid_api_ids:
                continue

            # 获取接口元数据
            api_meta = next(
                (item for item in api_details if str(item.get("id")) == api_id), {}
            )

            # 处理依赖关系
            relation = (
                step.get("relation") if isinstance(step.get("relation"), list) else []
            )
            if not relation:
                upstream = relation_map.get(api_id, [])
                relation = [{"apiId": str(item)} for item in upstream[:2] if str(item)]

            normalized_steps.append(
                {
                    "id": str(step.get("id") or ""),
                    "index": int(
                        step.get("index")
                        if isinstance(step.get("index"), int)
                        else index + 1
                    ),
                    "caseId": str(step.get("caseId") or ""),
                    "apiId": api_id,
                    "description": str(step.get("description") or ""),
                    "header": (
                        step.get("header")
                        if isinstance(step.get("header"), list)
                        else []
                    ),
                    "body": (
                        step.get("body")
                        if isinstance(step.get("body"), dict)
                        else {
                            "type": "json",
                            "form": [],
                            "json": "",
                            "raw": "",
                            "file": [],
                        }
                    ),
                    "query": (
                        step.get("query") if isinstance(step.get("query"), list) else []
                    ),
                    "rest": (
                        step.get("rest") if isinstance(step.get("rest"), list) else []
                    ),
                    "assertion": (
                        step.get("assertion")
                        if isinstance(step.get("assertion"), list)
                        else []
                    ),
                    "relation": relation,
                    "controller": (
                        step.get("controller")
                        if isinstance(step.get("controller"), list)
                        else []
                    ),
                    "apiMethod": str(
                        step.get("apiMethod") or api_meta.get("method") or ""
                    ),
                    "apiName": str(step.get("apiName") or api_meta.get("name") or ""),
                    "apiPath": str(
                        step.get("apiPath")
                        or api_meta.get("path")
                        or api_meta.get("url")
                        or ""
                    ),
                }
            )

        # 步骤3：补足步骤数量（至少2个）
        if len(normalized_steps) < 2 and api_details:
            used_ids = {str(item.get("apiId") or "") for item in normalized_steps}
            for api_meta in api_details:
                api_id = str(api_meta.get("id") or "")
                if not api_id or api_id in used_ids:
                    continue
                idx = len(normalized_steps) + 1
                normalized_steps.append(
                    {
                        "id": "",
                        "index": idx,
                        "caseId": "",
                        "apiId": api_id,
                        "description": "流程补全步骤",
                        "header": [],
                        "body": {
                            "type": "json",
                            "form": [],
                            "json": "",
                            "raw": "",
                            "file": [],
                        },
                        "query": [],
                        "rest": [],
                        "assertion": [],
                        "relation": [
                            {"apiId": str(item)}
                            for item in relation_map.get(api_id, [])[:2]
                        ],
                        "controller": [],
                        "apiMethod": str(api_meta.get("method") or ""),
                        "apiName": str(api_meta.get("name") or ""),
                        "apiPath": str(
                            api_meta.get("path") or api_meta.get("url") or ""
                        ),
                    }
                )
                used_ids.add(api_id)
                if len(normalized_steps) >= 2:
                    break

        # 补充异常场景步骤
        if len(normalized_steps) < 2 and api_details:
            primary = api_details[0]
            idx = len(normalized_steps) + 1
            normalized_steps.append(
                {
                    "id": "",
                    "index": idx,
                    "caseId": "",
                    "apiId": str(primary.get("id") or ""),
                    "description": "异常场景",
                    "header": [],
                    "body": {
                        "type": "json",
                        "form": [],
                        "json": "",
                        "raw": "",
                        "file": [],
                    },
                    "query": [],
                    "rest": [],
                    "assertion": [],
                    "relation": [],
                    "controller": [],
                    "apiMethod": str(primary.get("method") or ""),
                    "apiName": str(primary.get("name") or ""),
                    "apiPath": str(primary.get("path") or primary.get("url") or ""),
                }
            )

        # 重新编号：确保索引连续
        for idx, step in enumerate(normalized_steps):
            step["index"] = idx + 1

        # 填充空列表字段
        normalized["caseApis"] = normalized_steps
        normalized["caseWebs"] = []
        normalized["caseApps"] = []
        return normalized

    def generate_case(
        self,
        project_id: str,
        token: str,
        user_requirement: str,
        selected_apis: Optional[List[str]] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        用例生成主流程。
        @param project_id: 当前项目ID
        @param token: 平台鉴权token
        @param user_requirement: 用户自然语言需求
        @param selected_apis: 前端可选指定接口ID
        @param messages: 历史对话
        @return: {status,case,existing_api_ids,error}

        步骤：拉取接口池 -> 选择候选接口 -> 读取接口详情/关系 -> 融合RAG与Schema -> 生成并校验CaseRequest。
        """
        app_logger.info(
            "case_workflow_start project_id={} requirement={}",
            project_id,
            str(user_requirement)[:120],
        )
        result = self.case_workflow.run(
            CaseWorkflowContext(
                project_id=project_id,
                token=token,
                user_requirement=user_requirement,
                selected_apis=selected_apis,
                messages=messages or [],
            )
        )
        app_logger.info("case_workflow_end status={}", result.get("status"))
        if (
            result.get("status") == "error"
            and result.get("error")
            and not result.get("message")
        ):
            return {"status": "error", "message": str(result.get("error"))}
        return result

    def chat(
        self,
        project_id: str,
        token: str,
        message: str,
        use_rag: bool,
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        非流式聊天入口。

        自动分流：若识别为"用例需求"则走Agent生成流程，否则走RAG增强问答流程。
        """
        # 输入校验
        msg = (message or "").strip()
        if not msg:
            return {"reply": "请先输入问题"}
        # 判断是否为用例生成需求
        if _is_case_request(msg):
            result = self.generate_case(
                project_id, token, msg, selected_apis=[], messages=messages or []
            )
            if result.get("status") == "success":
                return {
                    "reply": "已生成用例预览，请确认后手动保存。",
                    "case": result.get("case"),
                }
            return {"reply": result.get("message") or "用例生成失败，请更换描述"}
        # 走RAG增强问答流程
        docs: List[Dict[str, Any]] = []
        rag_status = ""
        if use_rag:
            rag_result = rag_service.search_with_status(project_id, msg, top_k=5)
            docs = rag_result.get("data", [])
            rag_status = str(rag_result.get("status") or "")
        # 构建Prompt并调用LLM
        prompt = self._build_chat_prompt(msg, docs, rag_status)
        chat_messages = _normalize_messages(messages)
        chat_messages.append({"role": "user", "content": prompt})
        reply = llm_service.chat(chat_messages, system_prompt=CHAT_ROLE_PROMPT)
        return {"reply": reply}

    def stream_chat(
        self,
        project_id: str,
        token: str,
        message: str,
        use_rag: bool,
        messages: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        SSE流式对话生成器。
        
        @param project_id: 项目ID
        @param token: 平台鉴权token
        @param message: 当前轮输入
        @param use_rag: 是否开启知识库检索
        @param messages: 历史消息
        @return: 逐条 yield SSE事件字典

        示例：
        输入：message='请说明登录测试点'
        输出：{"type":"content","delta":"..."} / {"type":"end"}

        事件协议：
        - {"type": "content", "delta": "..."} 增量文本
        - {"type": "case", "case": {...}, "api_ids": [...]} 用例草稿
        """
        # 输入校验
        msg = (message or "").strip()
        if not msg:
            yield {"type": "content", "delta": "请先输入问题"}
            return
        # 判断是否为用例生成需求
        if _is_case_request(msg):
            yield {"type": "content", "delta": "正在生成用例，请稍候..."}
            # 后台线程执行耗时用例生成
            with ThreadPoolExecutor(
                max_workers=1
            ) as executor:
                future = executor.submit(
                    self.generate_case,
                    project_id,
                    token,
                    msg,
                    [],
                    messages or [],
                )
                # 主线程持续输出心跳，避免前端长时间无首包
                while not future.done():
                    time.sleep(0.15)
                    yield {"type": "content", "delta": " "}
                result = future.result()
            # 生成成功，返回用例
            if result.get("status") == "success":
                yield {
                    "type": "content",
                    "delta": "\n已生成用例预览，请在预览区确认并手动保存。",
                }
                yield {
                    "type": "case",
                    "case": result.get("case"),
                    "api_ids": result.get("existing_api_ids", []),
                }
                return
            # 生成失败
            yield {
                "type": "content",
                "delta": "\n"
                + str(result.get("message") or "用例生成失败，请更换描述"),
            }
            return
        # 走RAG增强问答流程
        rag_docs: List[Dict[str, Any]] = []
        rag_status = ""
        if use_rag:
            rag_result = rag_service.search_with_status(project_id, msg, top_k=5)
            rag_docs = rag_result.get("data", [])
            rag_status = str(rag_result.get("status") or "")
        # 构建Prompt
        final_prompt = self._build_chat_prompt(msg, rag_docs, rag_status)
        chat_messages = _normalize_messages(messages)
        chat_messages.append({"role": "user", "content": final_prompt})

        has_output = False
        try:
            yield {"type": "content", "delta": "正在思考，请稍候..."}
            # 后台线程拉取LLM流，主线程负责SSE节奏
            with ThreadPoolExecutor(
                max_workers=1
            ) as executor:
                future = executor.submit(
                    lambda: list(
                        llm_service.chat_with_stream(
                            chat_messages, system_prompt=CHAT_ROLE_PROMPT
                        )
                    )
                )
                # 心跳字符用于强制刷新前端流式状态
                while not future.done():
                    time.sleep(0.12)
                    yield {"type": "content", "delta": " "}
                stream_chunks = future.result()
            # 遍历输出流式内容
            for delta in stream_chunks:
                if delta:
                    has_output = True
                    text = str(delta)
                    step = 20  # 单次切片长度：平衡实时性与渲染开销
                    for i in range(0, len(text), step):
                        yield {"type": "content", "delta": text[i : i + step]}
                        time.sleep(0.02)
        except Exception as e:
            if not has_output:
                fallback = llm_service.chat(
                    chat_messages, system_prompt=CHAT_ROLE_PROMPT
                )
                if fallback:
                    text = str(fallback)
                    step = 12  # fallback切片更细，避免一次性大段刷屏
                    for i in range(0, len(text), step):
                        yield {"type": "content", "delta": text[i : i + step]}
                        time.sleep(0.02)

    def get_api_list_for_selection(
        self, project_id: str, token: str
    ) -> List[Dict[str, Any]]:
        """给前端“选择接口”弹窗提供当前项目接口列表。"""
        return get_platform_client(token).get_api_list(project_id)


agent_service = AgentService()
