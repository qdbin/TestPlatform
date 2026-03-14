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
    return any(item in text for item in case_terms) and any(
        item in text for item in action_terms
    )


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
    return bool(re.search(r"/[a-zA-Z0-9_\-/]+", text))


class AgentService:
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
        api_pool = [
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
        id_set = {item["id"] for item in api_pool}
        try:
            llm = llm_service.get_chat_model()
            if llm is None:
                raise RuntimeError("llm_not_configured")
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
            chain = selector_prompt | llm.with_structured_output(ApiSelectionResult)
            result = chain.invoke(
                {
                    "project_id": project_id,
                    "requirement": user_requirement,
                    "api_pool_json": json.dumps(api_pool, ensure_ascii=False),
                }
            )
            ids = [str(item) for item in result.api_ids if str(item) in id_set]
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
            "你必须输出合法 JSON 对象，以便 response_format={\"type\":\"json_object\"} 直接解析。\n"
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
        normalized["level"] = str(normalized.get("level") or "P0")
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
        normalized["commonParam"] = {
            "functions": (
                normalized["commonParam"].get("functions")
                if isinstance(normalized["commonParam"].get("functions"), list)
                else []
            ),
            "params": (
                normalized["commonParam"].get("params")
                if isinstance(normalized["commonParam"].get("params"), list)
                else []
            ),
            "header": str(normalized["commonParam"].get("header") or ""),
            "proxy": str(normalized["commonParam"].get("proxy") or ""),
        }
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
            relation = self._normalize_relation(
                step.get("relation"), relation_map, api_id
            )
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
                    "header": self._normalize_named_items(step.get("header")),
                    "body": self._normalize_body(step.get("body")),
                    "query": self._normalize_named_items(step.get("query")),
                    "rest": self._normalize_named_items(step.get("rest")),
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
        user_id: str = "",
    ):
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
        return get_platform_client(token).get_api_list(project_id)


agent_service = AgentService()
