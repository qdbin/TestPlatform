"""
Agent服务模块

职责：
    1. AI对话与用例生成统一入口
    2. 用例需求识别与自动分流
    3. 对接 LangChain ReAct 工具链
    4. 融合 RAG 知识检索与平台 API

核心类：
    - AgentService: Agent核心服务（对话、用例生成）

主要方法：
    - chat(): 非流式对话入口
    - stream_chat(): SSE流式对话入口
    - generate_case(): 用例生成主流程

实现特点：
    - 用例需求识别：关键词匹配 "用例/测试点/测试场景" + "生成/设计/编写"
    - 接口选择策略：ReAct Agent 优先 + 关键词打分回退
    - 结果校验：Pydantic 模型强校验，失败自动重试
"""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError

try:
    from json_repair import repair_json
except Exception:

    def repair_json(text: str, return_objects: bool = False):
        return re.sub(r",\s*([}\]])", r"\1", text or "")


from app.observability import app_logger
from app.prompts import (
    API_SELECTOR_SYSTEM_PROMPT,
    ASSISTANT_ROLE_PROMPT,
    CHAT_ROLE_PROMPT,
)
from app.schemas import ApiSelectionResult, CaseRequestModel
from app.services.case_workflow import CaseGenerationWorkflow, CaseWorkflowContext
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.tools.platform_tools import get_platform_client


def _try_parse_json_object(text: str) -> Optional[Dict[str, Any]]:
    """
    尝试解析 JSON 对象（含修复）

    实现策略：
        1. 直接解析原始文本
        2. 尝试 json_repair 修复后解析
        3. 正则提取 JSON 对象再解析

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
    标准化对话消息格式

    处理逻辑：
        - 过滤无效消息（非字典、角色不当、内容为空）
        - 保留 user/assistant 角色消息

    @param messages: 原始消息列表
    @return: 标准化后的消息列表
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
    判断是否为用例需求消息

    识别逻辑：
        - 包含用例相关词：用例/测试点/测试场景/测试步骤/test case/case
        - 包含动作词：生成/设计/编写/创建/输出/规划/帮我/给我
        - 同时满足两者才判定为用例需求

    @param message: 用户消息
    @return: 是否为用例需求
    """
    text = (message or "").lower()
    case_terms = ["用例", "测试点", "测试场景", "测试步骤", "test case", "case"]
    action_terms = ["生成", "设计", "编写", "创建", "输出", "规划", "帮我", "给我"]
    return any(item in text for item in case_terms) and any(
        item in text for item in action_terms
    )


def _is_project_private_query(message: str) -> bool:
    """
    判断是否为项目私有问题

    识别逻辑：
        - 包含项目私有关键词列表
        - 或包含 RESTful API 路径格式（/xxx/yyy）

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
    return bool(re.search(r"/[a-zA-Z0-9_\-/]+", text))


class AgentService:
    """
    Agent服务核心类

    职责：
        - 对话与用例生成统一入口
        - 编排 CaseGenerationWorkflow 完成用例生成
        - 提供流式/非流式对话能力

    初始化参数：
        - case_workflow: 用例生成工作流实例
    """

    def __init__(self):
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

    def _normalize_named_items(self, items: Any) -> List[Dict[str, Any]]:
        """
        标准化命名参数项（header/query/rest）

        处理逻辑：
            - 提取 name/value 字段
            - 可选保留 required/type 字段

        @param items: 原始参数列表
        @return: 标准化后的参数列表
        """
        if not isinstance(items, list):
            return []
        result: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            value = str(item.get("value") or "")
            if not name and not value:
                continue
            normalized = {"name": name, "value": value}
            if "required" in item:
                normalized["required"] = bool(item.get("required"))
            if "type" in item and item.get("type") is not None:
                normalized["type"] = str(item.get("type"))
            result.append(normalized)
        return result

    def _normalize_body(self, body: Any) -> Dict[str, Any]:
        """
        标准化请求体

        结构规范：
            - type: body类型（json/form/raw/file）
            - form: form-data参数列表
            - json: JSON字符串
            - raw: 原始文本
            - file: 文件列表

        @param body: 原始body
        @return: 标准化后的body字典
        """
        source = body if isinstance(body, dict) else {}
        body_type = str(source.get("type") or "json")
        form = self._normalize_named_items(source.get("form"))
        file_items = source.get("file") if isinstance(source.get("file"), list) else []
        return {
            "type": body_type,
            "form": form,
            "json": str(source.get("json") or ""),
            "raw": str(source.get("raw") or ""),
            "file": file_items,
        }

    def _normalize_relation(
        self, relation: Any, relation_map: Dict[str, List[str]], api_id: str
    ) -> List[Dict[str, str]]:
        """
        标准化步骤依赖关系

        处理逻辑：
            - 优先使用 relation 中的 apiId
            - 回退到 relation_map 中的上游依赖
            - 最多保留 2 个依赖

        @param relation: 原始依赖关系
        @param relation_map: 依赖关系映射表
        @param api_id: 当前接口ID
        @return: 标准化后的依赖列表
        """
        if isinstance(relation, list):
            result: List[Dict[str, str]] = []
            for item in relation:
                if not isinstance(item, dict):
                    continue
                linked = str(item.get("apiId") or "").strip()
                if linked:
                    result.append({"apiId": linked})
            if result:
                return result[:2]
        upstream = relation_map.get(api_id, [])
        return [{"apiId": str(item)} for item in upstream[:2] if str(item)]

    def _extract_path_tokens(self, api_item: Dict[str, Any]) -> Set[str]:
        """
        从接口路径提取语义词

        处理策略：
            - 按 / _ - { } . 分割
            - 过滤停用词和数字
            - 保留有意义的语义单元

        @param api_item: 接口数据
        @return: 路径词集合
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

        依赖识别策略：
            1. 路径语义相似度匹配
            2. 认证接口优先作为前置依赖
            3. 注册→登录链路优先连接

        @param api_details: 接口详情列表
        @return: {api_id: [依赖api_ids]}
        """
        if not api_details:
            return {}
        relations: Dict[str, List[str]] = {}
        auth_cues = {"login", "signin", "auth", "token", "oauth"}
        register_cues = {"register", "signup", "user", "account"}
        api_tokens = {
            str(item.get("id")): self._extract_path_tokens(item)
            for item in api_details
            if isinstance(item, dict) and item.get("id")
        }
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
                score = len(current_tokens & candidate_tokens)
                if current_method in {"GET", "PUT", "DELETE"} and (
                    candidate_tokens & auth_cues
                ):
                    score += 2
                if (current_tokens & register_cues) and (candidate_tokens & auth_cues):
                    score += 1
                if score > 0:
                    scored.append({"id": candidate_id, "score": score})
            scored.sort(key=lambda x: x.get("score", 0), reverse=True)
            relations[current_id] = [item["id"] for item in scored[:3]]
        return relations

    def _build_chat_prompt(
        self, message: str, rag_docs: List[Dict[str, Any]], rag_status: str
    ) -> str:
        """
        构建对话 Prompt

        策略选择：
            1. 有 RAG 上下文：融合知识片段回答
            2. 无上下文 + 私有问题：提示未命中，提供排查建议
            3. 无上下文 + 公开问题：直接基于通用知识回答
            4. RAG 服务异常：提示稍后重试

        @param message: 用户消息
        @param rag_docs: RAG 检索文档
        @param rag_status: RAG 检索状态
        @return: 构建后的 Prompt
        """
        docs = [item for item in (rag_docs or []) if isinstance(item, dict)]
        context = "\n\n".join(
            [str(item.get("content") or "") for item in docs if item.get("content")]
        ).strip()
        if context:
            return (
                "你将同时使用知识库证据和你的通用知识回答。\n"
                "要求：优先引用知识片段中的事实；缺失处可补充通用知识；避免编造项目细节。\n"
                f"知识片段：\n{context}\n\n"
                f"用户问题：{message}"
            )
        is_private = _is_project_private_query(message)
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
        if rag_status and rag_status != "success":
            return (
                "知识库暂不可用。请基于通用知识先给出准确回答，并在最后补一句可稍后重试知识库。\n"
                f"用户问题：{message}"
            )
        return message

    def _select_api_ids(
        self,
        project_id: str,
        token: str,
        user_requirement: str,
        all_apis: List[Dict[str, Any]],
    ) -> List[str]:
        """
        选择候选接口ID

        实现策略：
            1. ReAct Agent优先选择（调用LLM结构化输出）
            2. 失败时回退关键词打分策略
            3. 流程类需求强制至少3个接口
            4. 无匹配时返回前3个接口作为兜底

        @param project_id: 项目ID
        @param token: 鉴权token
        @param user_requirement: 用户需求描述
        @param all_apis: 可用接口列表
        @return: 选中的接口ID列表（最多5个）
        """
        if not all_apis:
            return []

        # 关键步骤：提取用户需求关键词
        query = user_requirement.lower()

        # 关键步骤：定义语义分组（用于关键词匹配加分）
        semantic_groups = {
            "login": ["登录", "signin", "login", "auth", "token", "oauth", "session"],
            "register": ["注册", "signup", "register", "create user", "user/create"],
            "user": ["用户", "user", "account", "账号", "个人信息"],
            "flow": ["流程", "链路", "闭环", "完整", "前后", "先后", "场景"],
        }

        # 关键步骤：匹配用户需求所属的语义分组
        matched_groups = [
            group
            for group, cues in semantic_groups.items()
            if any(cue.lower() in query for cue in cues)
        ]

        # 关键步骤：构建接口池摘要（用于LLM选择）
        api_pool = [
            {
                "id": str(item.get("id") or ""),  # 接口ID
                "name": str(item.get("name") or ""),  # 接口名称
                "path": str(item.get("path") or item.get("url") or ""),  # 接口路径
                "method": str(item.get("method") or ""),  # HTTP方法
                "description": str(item.get("description") or ""),  # 接口描述
            }
            for item in all_apis
            if isinstance(item, dict) and item.get("id")
        ]
        id_set = {item["id"] for item in api_pool}  # 有效ID集合

        # 关键步骤：尝试LLM结构化选择
        try:
            llm = llm_service.get_chat_model()
            if llm is None:
                raise RuntimeError("llm_not_configured")

            # 关键步骤：构建接口选择Prompt
            selector_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", API_SELECTOR_SYSTEM_PROMPT),
                    (
                        "user",
                        "项目ID: {project_id}\n用户需求: {requirement}\n可用接口列表: {api_pool_json}\n"
                        "请从可用接口里选出最相关接口，流程类需求优先输出2-5个接口。",
                    ),
                ]
            )

            # 关键步骤：调用LLM结构化输出
            chain = selector_prompt | llm.with_structured_output(ApiSelectionResult)
            result = chain.invoke(
                {
                    "project_id": project_id,
                    "requirement": user_requirement,
                    "api_pool_json": json.dumps(api_pool, ensure_ascii=False),
                }
            )
            ids = [str(item) for item in result.api_ids if str(item) in id_set]

            # 关键步骤：流程类需求补全接口
            if ids:
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
                        if len(ids) >= 3:  # 流程类至少3个接口
                            break
                return ids[:5]
        except Exception:
            pass

        # 关键步骤：回退到关键词打分策略
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
            score = 0
            corpus = f"{name} {path} {description}"

            # 关键步骤：关键词匹配得分
            for token_item in re.split(r"[\s,，。;；]+", query):
                token_item = token_item.strip()
                if token_item and token_item in corpus:
                    score += 1

            # 关键步骤：语义分组加分
            for group in matched_groups:
                cues = semantic_groups.get(group, [])
                if any(cue.lower() in corpus for cue in cues):
                    score += 3

            # 关键步骤：流程类需求特殊处理
            if "flow" in matched_groups and any(
                tag in matched_groups for tag in ["login", "register", "user"]
            ):
                if any(
                    cue.lower() in corpus
                    for cue in semantic_groups.get("login", [])
                    + semantic_groups.get("register", [])
                ):
                    score += 2  # 流程类需求优先选择登录/注册接口
            ranked.append({"id": current_id, "score": score})

        # 关键步骤：按分数排序并返回Top-K
        ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
        top = [item["id"] for item in ranked if item.get("score", 0) > 0][:5]
        if top:
            return top

        # 关键步骤：兜底返回前3个接口
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
        构建用例生成 Prompt

        Prompt组成：
            1. 系统指令：角色定义 + 约束规则
            2. 项目ID：确保数据隔离
            3. 用户需求：原始描述
            4. 历史对话：上下文信息
            5. 接口列表：可用接口池
            6. 依赖关系：接口调用链路
            7. 知识片段：RAG检索结果
            8. Schema参考：后端数据结构

        @param project_id: 项目ID
        @param user_requirement: 用户需求
        @param api_details: 接口详情列表
        @param api_relations: 依赖关系图
        @param rag_docs: RAG文档
        @param schema_payload: Case Schema
        @param messages: 历史消息
        @return: 构建后的Prompt
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
            "你必须严格遵循以下约束：\n"
            "1. 只能使用下方接口列表中的apiId，禁止创建新接口\n"
            "2. 输出必须是纯JSON对象，不要包含任何解释\n"
            "3. 必须符合后端CaseRequest和CaseApiRequest结构\n"
            "4. 必须保证 projectId 与当前项目ID完全一致\n"
            "5. 每个步骤都必须包含真实apiId、apiMethod、apiPath、apiName\n"
            "6. 至少2个步骤，建议包含正向与异常场景\n"
            "7. body 必须是对象，至少包含 type/form/json/raw/file 五个字段\n"
            "8. header/query/rest 的每项仅保留 name/value/required/type 相关键\n"
            "9. 不要生成 createTime/updateTime/createUser/updateUser/status 等后端维护字段\n"
            "10. caseApis 的 id/caseId 可留空，apiId 必须为真实ID\n\n"
            f"## 项目ID\n{project_id}\n\n"
            f"## 用户需求\n{user_requirement}\n\n"
            f"## 历史对话\n{history_text or '无'}\n\n"
            f"## 可用接口列表\n{json.dumps(api_list_summary, ensure_ascii=False, indent=2)}\n\n"
            f"## 接口依赖关系\n{json.dumps(api_relations, ensure_ascii=False)}\n\n"
            f"## 知识片段\n{json.dumps(rag_docs[:3], ensure_ascii=False)}\n\n"
            f"## 后端Schema参考\n{json.dumps(schema_payload, ensure_ascii=False, indent=2)[:2000]}\n\n"
            "## 输出示例（仅示例结构，不可复用apiId）\n"
            "{\n"
            '  "name": "登录流程用例",\n'
            '  "projectId": "当前项目ID",\n'
            '  "type": "API",\n'
            '  "moduleId": "模块ID",\n'
            '  "moduleName": "模块名",\n'
            '  "caseApis": [\n'
            '    {"index": 1, "id": "", "caseId": "", "apiId": "真实接口ID", "description": "正向场景", "header": [{"name":"Authorization","value":"${token}"}], "body": {"type":"json","form":[],"json":"{\\"account\\":\\"demo\\",\\"password\\":\\"123456\\"}","raw":"","file":[]}, "query": [], "rest": [], "assertion": [], "relation": [], "controller": [], "apiMethod": "POST", "apiName": "接口名", "apiPath": "/path"},\n'
            '    {"index": 2, "id": "", "caseId": "", "apiId": "真实接口ID", "description": "异常场景", "header": [], "body": {"type":"json","form":[],"json":"{\\"account\\":\\"\\"}","raw":"","file":[]}, "query": [], "rest": [], "assertion": [], "relation": [], "controller": [], "apiMethod": "GET", "apiName": "接口名", "apiPath": "/path"}\n'
            "  ]\n"
            "}\n\n"
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
        标准化用例对象

        处理步骤：
            1. 填充必填字段（projectId/type/status）
            2. 校验并过滤无效步骤
            3. 补充接口元信息
            4. 确保至少2个步骤（流程补全）
            5. 重排步骤序号

        @param project_id: 项目ID
        @param case_obj: LLM生成的用例对象
        @param api_details: 接口详情列表
        @param api_relations: 依赖关系图
        @return: 标准化后的用例字典
        """
        # 关键步骤：提取首个接口信息作为默认值
        first_api = api_details[0] if api_details else {}

        # 关键步骤：构建有效接口ID集合（用于校验）
        valid_api_ids = {
            str(item.get("id"))
            for item in api_details
            if isinstance(item, dict) and item.get("id")
        }
        relation_map = api_relations or {}
        module_id = str(first_api.get("moduleId") or "0")  # 默认模块ID
        module_name = str(first_api.get("moduleName") or "默认模块")  # 默认模块名
        now_name = f"AI生成用例-{datetime.now().strftime('%m%d%H%M%S')}"  # 默认用例名

        # 关键步骤：初始化标准化用例对象
        normalized = dict(case_obj or {})
        normalized["id"] = str(normalized.get("id") or "")  # 用例ID（新增时为空）
        normalized["num"] = int(normalized.get("num") or 0)  # 用例编号
        normalized["name"] = str(normalized.get("name") or now_name)  # 用例名称
        normalized["level"] = str(normalized.get("level") or "P0")  # 优先级
        normalized["moduleId"] = str(normalized.get("moduleId") or module_id)  # 模块ID
        normalized["moduleName"] = str(
            normalized.get("moduleName") or module_name
        )  # 模块名
        normalized["projectId"] = str(project_id)  # 项目ID（数据隔离）
        normalized["type"] = "API"  # 用例类型固定为API
        normalized["thirdParty"] = str(normalized.get("thirdParty") or "")  # 第三方标识
        normalized["description"] = str(
            normalized.get("description") or "AI自动生成用例"
        )
        normalized["environmentIds"] = (
            normalized.get("environmentIds")
            if isinstance(normalized.get("environmentIds"), list)
            else []
        )  # 环境ID列表
        normalized["system"] = str(normalized.get("system") or "web")  # 系统类型
        normalized["commonParam"] = (
            normalized.get("commonParam")
            if isinstance(normalized.get("commonParam"), dict)
            else {}
        )  # 公共参数
        normalized["commonParam"] = {
            "functions": (
                normalized["commonParam"].get("functions")
                if isinstance(normalized["commonParam"].get("functions"), list)
                else []
            ),  # 前置函数
            "params": (
                normalized["commonParam"].get("params")
                if isinstance(normalized["commonParam"].get("params"), list)
                else []
            ),  # 公共参数
            "header": str(normalized["commonParam"].get("header") or ""),  # 公共请求头
            "proxy": str(normalized["commonParam"].get("proxy") or ""),  # 代理配置
        }
        normalized["status"] = str(normalized.get("status") or "正常")  # 用例状态

        # 关键步骤：提取并校验步骤列表
        steps = (
            normalized.get("caseApis")
            if isinstance(normalized.get("caseApis"), list)
            else []
        )
        normalized_steps: List[Dict[str, Any]] = []

        # 关键步骤：遍历并标准化每个步骤
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            api_id = str(step.get("apiId") or "")

            # 关键步骤：尝试从接口列表中获取apiId
            if not api_id and api_details:
                api_id = str(
                    api_details[min(index, len(api_details) - 1)].get("id") or ""
                )

            # 关键步骤：校验apiId是否有效
            if not api_id or api_id not in valid_api_ids:
                continue

            # 关键步骤：获取接口元信息
            api_meta = next(
                (item for item in api_details if str(item.get("id")) == api_id), {}
            )
            relation = self._normalize_relation(
                step.get("relation"), relation_map, api_id
            )

            # 关键步骤：构建标准化步骤对象
            normalized_steps.append(
                {
                    "id": str(step.get("id") or ""),  # 步骤ID（新增时为空）
                    "index": int(
                        step.get("index")
                        if isinstance(step.get("index"), int)
                        else index + 1
                    ),  # 步骤序号
                    "caseId": str(step.get("caseId") or ""),  # 用例ID
                    "apiId": api_id,  # 接口ID
                    "description": str(step.get("description") or ""),  # 步骤描述
                    "header": self._normalize_named_items(step.get("header")),  # 请求头
                    "body": self._normalize_body(step.get("body")),  # 请求体
                    "query": self._normalize_named_items(step.get("query")),  # 查询参数
                    "rest": self._normalize_named_items(step.get("rest")),  # REST参数
                    "assertion": (
                        step.get("assertion")
                        if isinstance(step.get("assertion"), list)
                        else []
                    ),  # 断言列表
                    "relation": relation,  # 依赖关系
                    "controller": (
                        step.get("controller")
                        if isinstance(step.get("controller"), list)
                        else []
                    ),  # 控制器
                    "apiMethod": str(
                        step.get("apiMethod") or api_meta.get("method") or ""
                    ),  # HTTP方法
                    "apiName": str(
                        step.get("apiName") or api_meta.get("name") or ""
                    ),  # 接口名
                    "apiPath": str(
                        step.get("apiPath")
                        or api_meta.get("path")
                        or api_meta.get("url")
                        or ""
                    ),  # 接口路径
                }
            )

        # 关键步骤：确保至少2个步骤（流程补全）
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

        for idx, step in enumerate(normalized_steps):
            step["index"] = idx + 1
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
        user_id: str = "",
    ):
        """
        用例生成主入口

        实现步骤：
            1. 记录日志（开始/结束）
            2. 构建工作流上下文
            3. 调用 CaseGenerationWorkflow 执行
            4. 包装错误信息并返回

        @param project_id: 项目ID
        @param token: 鉴权token
        @param user_requirement: 用户需求描述
        @param selected_apis: 预选接口ID列表
        @param messages: 历史对话消息
        @param user_id: 用户ID
        @return: {status, case, existing_api_ids, message}
        """
        app_logger.info(
            "case_workflow_start project_id={} user_id={} requirement={}",
            project_id,
            user_id,
            str(user_requirement)[:120],
        )
        result = self.case_workflow.run(
            CaseWorkflowContext(
                project_id=project_id,
                token=token,
                user_requirement=user_requirement,
                selected_apis=selected_apis,
                messages=messages or [],
                user_id=user_id or "",
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
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        非流式对话入口

        实现步骤：
            1. 识别用例需求
            2. 是用例需求 → 调用 generate_case
            3. 是问答 → RAG检索 + LLM回答

        @param project_id: 项目ID
        @param token: 鉴权token
        @param message: 用户消息
        @param use_rag: 是否启用RAG
        @param messages: 历史消息
        @param user_id: 用户ID
        @return: {reply, case?}
        """
        msg = (message or "").strip()
        if not msg:
            return {"reply": "请先输入问题"}
        if _is_case_request(msg):
            result = self.generate_case(
                project_id=project_id,
                token=token,
                user_requirement=msg,
                selected_apis=[],
                messages=messages or [],
                user_id=user_id,
            )
            if result.get("status") == "success":
                return {
                    "reply": "已生成用例预览，请确认后手动保存。",
                    "case": result.get("case"),
                }
            return {"reply": result.get("message") or "用例生成失败，请更换描述"}
        docs: List[Dict[str, Any]] = []
        rag_status = ""
        if use_rag:
            rag_result = rag_service.search_with_status(
                project_id, msg, top_k=5, user_id=user_id
            )
            docs = rag_result.get("data", [])
            rag_status = str(rag_result.get("status") or "")
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
        user_id: str = "",
    ):
        """
        SSE流式对话入口

        实现步骤：
            1. 判断是否用例需求
            2. 用例需求：线程池执行 + 事件推送 case 事件
            3. 问答需求：RAG检索 + 流式推送 content 事件
            4. 立即推送首事件避免等待阻塞

        @param project_id: 项目ID
        @param token: 鉴权token
        @param message: 用户消息
        @param use_rag: 是否启用RAG
        @param messages: 历史消息
        @param user_id: 用户ID
        @return: SSE事件生成器
        """
        msg = (message or "").strip()
        if not msg:
            yield {"type": "content", "delta": "请先输入问题"}
            return
        if _is_case_request(msg):
            yield {"type": "content", "delta": "正在生成用例，请稍候..."}
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self.generate_case,
                    project_id,
                    token,
                    msg,
                    [],
                    messages or [],
                    user_id,
                )
                while not future.done():
                    time.sleep(0.15)
                    yield {"type": "content", "delta": " "}
                result = future.result()
            if result.get("status") == "success":
                yield {
                    "type": "content",
                    "delta": "\n已生成用例预览，请在预览区确认并手动保存。",
                }
                yield {
                    "type": "case",
                    "case": result.get("case"),
                    "api_ids": result.get("existing_api_ids", []),
                    "created_api_ids": result.get("existing_api_ids", []),
                }
                return
            yield {
                "type": "content",
                "delta": "\n"
                + str(result.get("message") or "用例生成失败，请更换描述"),
            }
            return
        rag_docs: List[Dict[str, Any]] = []
        rag_status = ""
        if use_rag:
            rag_result = rag_service.search_with_status(
                project_id, msg, top_k=5, user_id=user_id
            )
            rag_docs = rag_result.get("data", [])
            rag_status = str(rag_result.get("status") or "")
        final_prompt = self._build_chat_prompt(msg, rag_docs, rag_status)
        chat_messages = _normalize_messages(messages)
        chat_messages.append({"role": "user", "content": final_prompt})

        has_output = False
        try:
            yield {"type": "content", "delta": "正在思考，请稍候..."}
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    lambda: list(
                        llm_service.chat_with_stream(
                            chat_messages, system_prompt=CHAT_ROLE_PROMPT
                        )
                    )
                )
                while not future.done():
                    time.sleep(0.12)
                    yield {"type": "content", "delta": " "}
                stream_chunks = future.result()
            for delta in stream_chunks:
                if not delta:
                    continue
                has_output = True
                text = str(delta)
                step = 20
                for i in range(0, len(text), step):
                    yield {"type": "content", "delta": text[i : i + step]}
                    time.sleep(0.02)
        except Exception:
            if not has_output:
                fallback = llm_service.chat(
                    chat_messages, system_prompt=CHAT_ROLE_PROMPT
                )
                if fallback:
                    text = str(fallback)
                    step = 12
                    for i in range(0, len(text), step):
                        yield {"type": "content", "delta": text[i : i + step]}
                        time.sleep(0.02)

    def get_api_list_for_selection(
        self, project_id: str, token: str
    ) -> List[Dict[str, Any]]:
        """
        获取接口列表供前端选择

        用于"手动选接口 + Agent生成"协同场景

        @param project_id: 项目ID
        @param token: 鉴权token
        @return: 接口列表
        """
        return get_platform_client(token).get_api_list(project_id)


agent_service = AgentService()
