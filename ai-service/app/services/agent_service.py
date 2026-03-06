from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from pydantic import BaseModel, ValidationError, ConfigDict

try:
    from json_repair import repair_json
except Exception:

    def repair_json(text: str, return_objects: bool = False):
        return re.sub(r",\s*([}\]])", r"\1", text or "")


from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.tools.platform_tools import get_platform_client

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
7. 禁止补充数据库不存在的接口、字段或路径

## 错误处理
- 无相关接口时：明确告知"当前项目未找到相关接口"
- 知识库无结果：说明"未检索到相关文档"，再给通用建议
- 格式错误：自动重试一次，失败则返回明确错误"""


class CaseApiStepModel(BaseModel):
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


def _try_parse_json_object(text: str) -> Optional[Dict[str, Any]]:
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
    text = (message or "").lower()
    case_terms = ["用例", "测试点", "测试场景", "测试步骤", "test case", "case"]
    action_terms = ["生成", "设计", "编写", "创建", "输出", "规划", "帮我", "给我"]
    has_case = any(item in text for item in case_terms)
    has_action = any(item in text for item in action_terms)
    return has_case and has_action


def _is_project_private_query(message: str) -> bool:
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
    def _extract_path_tokens(self, api_item: Dict[str, Any]) -> Set[str]:
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
                overlap = len(current_tokens & candidate_tokens)
                score = overlap
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

    def _build_case_selector_executor(
        self, project_id: str, token: str, all_apis: List[Dict[str, Any]]
    ) -> AgentExecutor:
        llm = llm_service._get_llm()
        if llm is None:
            raise RuntimeError("llm_not_configured")
        platform_client = get_platform_client(token)

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

        def get_api_detail(api_id: str) -> str:
            detail = platform_client.get_api_detail(str(api_id).strip())
            return json.dumps(detail or {}, ensure_ascii=False)

        def get_api_relation(api_id: str) -> str:
            target = None
            for item in all_apis:
                if isinstance(item, dict) and str(item.get("id")) == str(api_id):
                    target = item
                    break
            if target is None:
                return "[]"
            path = str(target.get("path") or target.get("url") or "").strip("/")
            segments = [seg for seg in path.split("/") if seg]
            related: List[Dict[str, Any]] = []
            for item in all_apis:
                if not isinstance(item, dict):
                    continue
                current_id = str(item.get("id") or "")
                current_path = str(item.get("path") or item.get("url") or "")
                if current_id == str(api_id):
                    continue
                if any(seg and seg in current_path for seg in segments):
                    related.append(
                        {
                            "id": current_id,
                            "path": current_path,
                            "name": item.get("name"),
                        }
                    )
            return json.dumps(related[:5], ensure_ascii=False)

        def generate_testcase(api_ids_csv: str) -> str:
            ids = [
                item.strip()
                for item in str(api_ids_csv or "").split(",")
                if item.strip()
            ]
            return json.dumps({"api_ids": ids[:5]}, ensure_ascii=False)

        tools = [
            Tool(
                name="get_api_list",
                func=get_api_list,
                description="获取当前项目全部接口列表，输入固定为none",
            ),
            Tool(
                name="get_api_detail",
                func=get_api_detail,
                description="输入接口id，返回该接口详细信息",
            ),
            Tool(
                name="get_api_relation",
                func=get_api_relation,
                description="输入接口id，返回接口依赖关系",
            ),
            Tool(
                name="generate_testcase",
                func=generate_testcase,
                description="输入逗号分隔api_id，输出api_ids数组",
            ),
        ]
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
        if not all_apis:
            return []
        query = user_requirement.lower()
        semantic_groups = {
            "login": ["登录", "signin", "login", "auth", "token", "oauth", "session"],
            "register": ["注册", "signup", "register", "create user", "user/create"],
            "user": ["用户", "user", "account", "账号", "个人信息"],
            "flow": ["流程", "链路", "闭环", "完整", "前后", "先后", "场景"],
        }
        matched_groups = [
            group
            for group, cues in semantic_groups.items()
            if any(cue.lower() in query for cue in cues)
        ]
        try:
            executor = self._build_case_selector_executor(project_id, token, all_apis)
            result = executor.invoke({"input": user_requirement})
            output = result.get("output") if isinstance(result, dict) else ""
            parsed = _try_parse_json_object(str(output or ""))
            api_ids = parsed.get("api_ids") if isinstance(parsed, dict) else []
            ids = [str(item) for item in api_ids if str(item)]
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
                        if len(ids) >= 3:
                            break
                return ids[:5]
        except Exception:
            pass
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
            for token_item in re.split(r"[\s,，。;；]+", query):
                token_item = token_item.strip()
                if token_item and token_item in corpus:
                    score += 1
            for group in matched_groups:
                cues = semantic_groups.get(group, [])
                if any(cue.lower() in corpus for cue in cues):
                    score += 3
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
        ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
        top = [item["id"] for item in ranked if item.get("score", 0) > 0][:5]
        if top:
            return top
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
            f"## 项目ID\n{project_id}\n\n"
            f"## 用户需求\n{user_requirement}\n\n"
            f"## 历史对话\n{history_text or '无'}\n\n"
            f"## 可用接口列表\n{json.dumps(api_list_summary, ensure_ascii=False, indent=2)}\n\n"
            f"## 接口依赖关系\n{json.dumps(api_relations, ensure_ascii=False)}\n\n"
            f"## 知识片段\n{json.dumps(rag_docs[:3], ensure_ascii=False)}\n\n"
            f"## 后端Schema参考\n{json.dumps(schema_payload, ensure_ascii=False, indent=2)[:2000]}\n\n"
            "## 输出要求\n"
            "1. 顶层字段必须包含：name, projectId, moduleId, moduleName, type='API'\n"
            "2. caseApis数组不能为空，每个元素必须包含：apiId, index, description\n"
            "3. 根据需求选择合适的接口组合，流程类需求需串联多个接口\n"
            "4. 至少生成2个步骤（可包含正向和异常场景）\n"
            "5. 每个步骤补全apiMethod、apiPath、apiName（从接口列表复制）\n\n"
            "## 输出格式\n"
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
            api_meta = next(
                (item for item in api_details if str(item.get("id")) == api_id), {}
            )
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
    ):
        platform_client = get_platform_client(token)
        all_apis = platform_client.get_api_list(project_id) or []
        if not all_apis:
            reason = ""
            if hasattr(platform_client, "get_last_error"):
                reason = str(platform_client.get_last_error() or "")
            if reason:
                return {"status": "error", "message": f"读取接口列表失败：{reason}"}
            return {
                "status": "error",
                "message": "当前项目暂无可用接口，请先在【接口管理】中创建接口后再生成用例",
            }
        all_ids = {
            str(item.get("id"))
            for item in all_apis
            if isinstance(item, dict) and item.get("id")
        }
        if not all_ids:
            return {
                "status": "error",
                "message": "接口列表解析异常，请检查接口数据格式",
            }
        selected = [str(item) for item in (selected_apis or []) if str(item) in all_ids]
        if not selected:
            selected = self._select_api_ids(
                project_id, token, user_requirement, all_apis
            )
        selected = [item for item in selected if item in all_ids][:5]
        if not selected:
            api_names = [
                str(item.get("name") or item.get("path") or "")
                for item in all_apis[:10]
                if isinstance(item, dict)
            ]
            hint = f"当前项目可用接口：{', '.join(api_names[:5])}等。请尝试使用更具体的接口名称描述。"
            return {"status": "error", "message": f"未匹配到相关接口。{hint}"}
        api_details: List[Dict[str, Any]] = []
        for api_id in selected:
            detail = platform_client.get_api_detail(api_id)
            if detail:
                api_details.append(detail)
        if not api_details:
            return {
                "status": "error",
                "message": "接口详情读取失败，请检查接口是否存在或当前账号是否有权限",
            }
        api_relations = self._build_dependency_relations(api_details)
        rag_docs = rag_service.search(project_id, user_requirement, top_k=6)
        schema_payload = platform_client.get_case_schema(project_id) or {}
        prompt = self._build_case_prompt(
            project_id,
            user_requirement,
            api_details,
            api_relations,
            rag_docs,
            schema_payload,
            messages=messages,
        )
        last_error = ""
        for attempt in range(2):
            raw = llm_service.chat(
                [{"role": "user", "content": prompt}],
                system_prompt=ASSISTANT_ROLE_PROMPT,
            )
            parsed = _try_parse_json_object(raw or "")
            target = (
                parsed.get("case")
                if isinstance(parsed, dict) and isinstance(parsed.get("case"), dict)
                else parsed
            )
            if not isinstance(target, dict):
                last_error = "json_parse_failed"
                prompt = (
                    prompt
                    + "\n\n注意：上次输出不是有效JSON，请直接输出JSON对象，不要任何解释。"
                )
                continue
            normalized = self._normalize_case(
                project_id, target, api_details, api_relations=api_relations
            )
            try:
                model = CaseRequestModel.model_validate(normalized)
                return {
                    "status": "success",
                    "case": model.model_dump(),
                    "existing_api_ids": [
                        str(item.get("id")) for item in api_details if item.get("id")
                    ],
                }
            except ValidationError as e:
                last_error = str(e)
                prompt = (
                    prompt
                    + f"\n\n注意：上次输出校验失败：{str(e)[:200]}。请修正后重新输出。"
                )
                continue
        return {
            "status": "error",
            "message": "用例生成失败，请更换描述或简化需求",
            "error": last_error,
        }

    def chat(
        self,
        project_id: str,
        token: str,
        message: str,
        use_rag: bool,
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        msg = (message or "").strip()
        if not msg:
            return {"reply": "请先输入问题"}
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
        docs: List[Dict[str, Any]] = []
        rag_status = ""
        if use_rag:
            rag_result = rag_service.search_with_status(project_id, msg, top_k=5)
            docs = rag_result.get("data", [])
            rag_status = str(rag_result.get("status") or "")
        prompt = self._build_chat_prompt(msg, docs, rag_status)
        chat_messages = _normalize_messages(messages)
        chat_messages.append({"role": "user", "content": prompt})
        reply = llm_service.chat(chat_messages, system_prompt=ASSISTANT_ROLE_PROMPT)
        return {"reply": reply}

    def stream_chat(
        self,
        project_id: str,
        token: str,
        message: str,
        use_rag: bool,
        messages: Optional[List[Dict[str, Any]]] = None,
    ):
        msg = (message or "").strip()
        if not msg:
            yield {"type": "content", "delta": "请先输入问题"}
            return
        if _is_case_request(msg):
            result = self.generate_case(
                project_id, token, msg, selected_apis=[], messages=messages or []
            )
            if result.get("status") == "success":
                reply = "已生成用例预览，请在预览区确认并手动保存。"
                for char in reply:
                    yield {"type": "content", "delta": char}
                yield {
                    "type": "case",
                    "case": result.get("case"),
                    "api_ids": result.get("existing_api_ids", []),
                }
                return
            for char in str(result.get("message") or "用例生成失败，请更换描述"):
                yield {"type": "content", "delta": char}
            return
        rag_docs: List[Dict[str, Any]] = []
        rag_status = ""
        if use_rag:
            rag_result = rag_service.search_with_status(project_id, msg, top_k=5)
            rag_docs = rag_result.get("data", [])
            rag_status = str(rag_result.get("status") or "")
        final_prompt = self._build_chat_prompt(msg, rag_docs, rag_status)
        chat_messages = _normalize_messages(messages)
        chat_messages.append({"role": "user", "content": final_prompt})

        has_output = False
        try:
            for delta in llm_service.chat_with_stream(
                chat_messages, system_prompt=ASSISTANT_ROLE_PROMPT
            ):
                if delta:
                    has_output = True
                    yield {"type": "content", "delta": delta}
        except Exception as e:
            print(f"流式输出异常: {e}")
            if not has_output:
                fallback = llm_service.chat(
                    chat_messages, system_prompt=ASSISTANT_ROLE_PROMPT
                )
                if fallback:
                    text = str(fallback)
                    step = 12
                    for i in range(0, len(text), step):
                        yield {"type": "content", "delta": text[i : i + step]}

    def get_api_list_for_selection(
        self, project_id: str, token: str
    ) -> List[Dict[str, Any]]:
        return get_platform_client(token).get_api_list(project_id)


agent_service = AgentService()
