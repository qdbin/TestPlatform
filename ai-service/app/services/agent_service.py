from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from pydantic import BaseModel, ValidationError

try:
    from json_repair import repair_json
except Exception:
    def repair_json(text: str, return_objects: bool = False):
        return re.sub(r",\s*([}\]])", r"\1", text or "")

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.tools.platform_tools import get_platform_client

ASSISTANT_ROLE_PROMPT = """你是接口测试平台的AI服务助手。
你可以回答接口测试问题，也可以基于当前项目已有接口生成结构化测试用例。
禁止虚构平台能力，禁止建议自动创建接口。"""


class CaseApiStepModel(BaseModel):
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


def _normalize_messages(messages: Optional[List[Dict[str, Any]]]) -> List[Dict[str, str]]:
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
    return result[-30:]


def _is_case_request(message: str) -> bool:
    text = (message or "").lower()
    keywords = ["用例", "测试点", "case", "生成用例", "测试场景"]
    return any(item in text for item in keywords)


class AgentService:
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
                    related.append({"id": current_id, "path": current_path, "name": item.get("name")})
            return json.dumps(related[:5], ensure_ascii=False)

        def generate_testcase(api_ids_csv: str) -> str:
            ids = [item.strip() for item in str(api_ids_csv or "").split(",") if item.strip()]
            return json.dumps({"api_ids": ids[:5]}, ensure_ascii=False)

        tools = [
            Tool(name="get_api_list", func=get_api_list, description="获取当前项目全部接口列表，输入固定为none"),
            Tool(name="get_api_detail", func=get_api_detail, description="输入接口id，返回该接口详细信息"),
            Tool(name="get_api_relation", func=get_api_relation, description="输入接口id，返回接口依赖关系"),
            Tool(name="generate_testcase", func=generate_testcase, description="输入逗号分隔api_id，输出api_ids数组"),
        ]
        prompt = PromptTemplate.from_template(
            "你是测试用例生成规划代理。\n"
            "只能基于现有接口选择api_id，禁止创建接口。\n"
            "必须使用工具完成分析后输出最终JSON。\n"
            "最终输出格式必须为：{\"api_ids\":[\"1\",\"2\"],\"reason\":\"...\"}\n"
            "可用工具：\n{tools}\n\n工具名：{tool_names}\n\n"
            "Question: {input}\nThought: {agent_scratchpad}"
        )
        agent = create_react_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, max_iterations=6, handle_parsing_errors=True, verbose=False)

    def _select_api_ids(self, project_id: str, token: str, user_requirement: str, all_apis: List[Dict[str, Any]]) -> List[str]:
        if not all_apis:
            return []
        try:
            executor = self._build_case_selector_executor(project_id, token, all_apis)
            result = executor.invoke({"input": user_requirement})
            output = result.get("output") if isinstance(result, dict) else ""
            parsed = _try_parse_json_object(str(output or ""))
            api_ids = parsed.get("api_ids") if isinstance(parsed, dict) else []
            ids = [str(item) for item in api_ids if str(item)]
            if ids:
                return ids[:5]
        except Exception:
            pass
        query = user_requirement.lower()
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
            for token_item in re.split(r"[\s,，。;；]+", query):
                token_item = token_item.strip()
                if token_item and token_item in f"{name} {path} {description}":
                    score += 1
            ranked.append({"id": current_id, "score": score})
        ranked.sort(key=lambda x: x.get("score", 0), reverse=True)
        top = [item["id"] for item in ranked if item.get("score", 0) > 0][:5]
        if top:
            return top
        fallback = [str(item.get("id")) for item in all_apis if isinstance(item, dict) and item.get("id")]
        return fallback[:3]

    def _build_case_prompt(
        self,
        project_id: str,
        user_requirement: str,
        api_details: List[Dict[str, Any]],
        rag_docs: List[Dict[str, Any]],
        schema_payload: Dict[str, Any],
    ) -> str:
        return (
            "你是接口测试平台用例生成器。\n"
            "你只能使用给定接口详情中的apiId，不允许新增接口。\n"
            "输出必须是一个JSON对象，且必须可被后端CaseRequest接收。\n\n"
            f"projectId={project_id}\n"
            f"用户需求={user_requirement}\n"
            f"接口详情={json.dumps(api_details, ensure_ascii=False)}\n"
            f"知识片段={json.dumps(rag_docs, ensure_ascii=False)}\n"
            f"后端Schema={json.dumps(schema_payload, ensure_ascii=False)}\n\n"
            "要求：\n"
            "1) 顶层字段包含CaseRequest核心字段，type必须是API。\n"
            "2) caseApis不能为空，且每个步骤必须包含apiId。\n"
            "3) 至少生成2个步骤（正向+异常）。\n"
            "4) 不要输出解释，不要Markdown，只输出JSON。\n"
        )

    def _normalize_case(self, project_id: str, case_obj: Dict[str, Any], api_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        first_api = api_details[0] if api_details else {}
        valid_api_ids = {str(item.get("id")) for item in api_details if isinstance(item, dict) and item.get("id")}
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
        normalized["description"] = str(normalized.get("description") or "AI自动生成用例")
        normalized["environmentIds"] = normalized.get("environmentIds") if isinstance(normalized.get("environmentIds"), list) else []
        normalized["system"] = str(normalized.get("system") or "web")
        normalized["commonParam"] = normalized.get("commonParam") if isinstance(normalized.get("commonParam"), dict) else {}
        normalized["status"] = str(normalized.get("status") or "正常")
        steps = normalized.get("caseApis") if isinstance(normalized.get("caseApis"), list) else []
        normalized_steps: List[Dict[str, Any]] = []
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            api_id = str(step.get("apiId") or "")
            if not api_id and api_details:
                api_id = str(api_details[min(index, len(api_details) - 1)].get("id") or "")
            if not api_id or api_id not in valid_api_ids:
                continue
            api_meta = next((item for item in api_details if str(item.get("id")) == api_id), {})
            normalized_steps.append(
                {
                    "id": str(step.get("id") or ""),
                    "index": int(step.get("index") if isinstance(step.get("index"), int) else index + 1),
                    "caseId": str(step.get("caseId") or ""),
                    "apiId": api_id,
                    "description": str(step.get("description") or ""),
                    "header": step.get("header") if isinstance(step.get("header"), list) else [],
                    "body": step.get("body") if isinstance(step.get("body"), dict) else {"type": "json", "form": [], "json": "", "raw": "", "file": []},
                    "query": step.get("query") if isinstance(step.get("query"), list) else [],
                    "rest": step.get("rest") if isinstance(step.get("rest"), list) else [],
                    "assertion": step.get("assertion") if isinstance(step.get("assertion"), list) else [],
                    "relation": step.get("relation") if isinstance(step.get("relation"), list) else [],
                    "controller": step.get("controller") if isinstance(step.get("controller"), list) else [],
                    "apiMethod": str(step.get("apiMethod") or api_meta.get("method") or ""),
                    "apiName": str(step.get("apiName") or api_meta.get("name") or ""),
                    "apiPath": str(step.get("apiPath") or api_meta.get("path") or api_meta.get("url") or ""),
                }
            )
        if len(normalized_steps) < 2 and api_details:
            primary = str(api_details[0].get("id") or "")
            if primary and primary in valid_api_ids:
                while len(normalized_steps) < 2:
                    idx = len(normalized_steps) + 1
                    normalized_steps.append(
                        {
                            "id": "",
                            "index": idx,
                            "caseId": "",
                            "apiId": primary,
                            "description": "正向场景" if idx == 1 else "异常场景",
                            "header": [],
                            "body": {"type": "json", "form": [], "json": "", "raw": "", "file": []},
                            "query": [],
                            "rest": [],
                            "assertion": [],
                            "relation": [],
                            "controller": [],
                            "apiMethod": str(api_details[0].get("method") or ""),
                            "apiName": str(api_details[0].get("name") or ""),
                            "apiPath": str(api_details[0].get("path") or api_details[0].get("url") or ""),
                        }
                    )
        normalized["caseApis"] = normalized_steps
        normalized["caseWebs"] = []
        normalized["caseApps"] = []
        return normalized

    def generate_case(self, project_id: str, token: str, user_requirement: str, selected_apis: Optional[List[str]] = None):
        platform_client = get_platform_client(token)
        all_apis = platform_client.get_api_list(project_id) or []
        if not all_apis:
            return {"status": "error", "message": "请先创建接口"}
        all_ids = {str(item.get("id")) for item in all_apis if isinstance(item, dict) and item.get("id")}
        selected = [str(item) for item in (selected_apis or []) if str(item) in all_ids]
        if not selected:
            selected = self._select_api_ids(project_id, token, user_requirement, all_apis)
        selected = [item for item in selected if item in all_ids][:5]
        if not selected:
            return {"status": "error", "message": "请先创建接口"}
        api_details: List[Dict[str, Any]] = []
        for api_id in selected:
            detail = platform_client.get_api_detail(api_id)
            if detail:
                api_details.append(detail)
        if not api_details:
            return {"status": "error", "message": "请先创建接口"}
        rag_docs = rag_service.search(project_id, user_requirement, top_k=6)
        schema_payload = platform_client.get_case_schema(project_id) or {}
        prompt = self._build_case_prompt(project_id, user_requirement, api_details, rag_docs, schema_payload)
        last_error = ""
        for _ in range(2):
            raw = llm_service.chat([{"role": "user", "content": prompt}], system_prompt=ASSISTANT_ROLE_PROMPT)
            parsed = _try_parse_json_object(raw or "")
            target = parsed.get("case") if isinstance(parsed, dict) and isinstance(parsed.get("case"), dict) else parsed
            if not isinstance(target, dict):
                last_error = "json_parse_failed"
                continue
            normalized = self._normalize_case(project_id, target, api_details)
            try:
                model = CaseRequestModel.model_validate(normalized)
                return {
                    "status": "success",
                    "case": model.model_dump(),
                    "existing_api_ids": [str(item.get("id")) for item in api_details if item.get("id")],
                }
            except ValidationError as e:
                last_error = str(e)
                continue
        return {"status": "error", "message": "用例生成失败，请更换描述", "error": last_error}

    def chat(self, project_id: str, token: str, message: str, use_rag: bool) -> Dict[str, Any]:
        msg = (message or "").strip()
        if not msg:
            return {"reply": "请先输入问题"}
        if _is_case_request(msg):
            result = self.generate_case(project_id, token, msg, selected_apis=[])
            if result.get("status") == "success":
                return {"reply": "已生成用例草稿，请确认后保存。", "case": result.get("case")}
            return {"reply": result.get("message") or "用例生成失败，请更换描述"}
        docs = rag_service.search(project_id, msg, top_k=5) if use_rag else []
        if use_rag and not docs:
            return {"reply": "未找到相关文档"}
        context = "\n\n".join([str(item.get("content") or "") for item in docs if item]) if docs else ""
        prompt = msg if not context else f"请基于以下资料回答：\n{context}\n\n用户问题：{msg}"
        reply = llm_service.chat([{"role": "user", "content": prompt}], system_prompt=ASSISTANT_ROLE_PROMPT)
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
            return
        if _is_case_request(msg):
            result = self.generate_case(project_id, token, msg, selected_apis=[])
            if result.get("status") == "success":
                reply = "已生成用例草稿，请在预览区确认并手动保存。"
                for char in reply:
                    yield {"type": "content", "delta": char}
                yield {"type": "case", "case": result.get("case"), "api_ids": result.get("existing_api_ids", [])}
                return
            for char in str(result.get("message") or "用例生成失败，请更换描述"):
                yield {"type": "content", "delta": char}
            return
        rag_docs = rag_service.search(project_id, msg, top_k=5) if use_rag else []
        if use_rag and not rag_docs:
            for char in "未找到相关文档":
                yield {"type": "content", "delta": char}
            return
        context = "\n\n".join([str(item.get("content") or "") for item in rag_docs if item]) if rag_docs else ""
        final_prompt = msg if not context else f"请基于以下资料回答：\n{context}\n\n用户问题：{msg}"
        chat_messages = _normalize_messages(messages)
        chat_messages.append({"role": "user", "content": final_prompt})
        chunks = llm_service.chat_with_stream(chat_messages, system_prompt=ASSISTANT_ROLE_PROMPT)
        has_output = False
        for chunk in chunks:
            delta = ""
            if hasattr(chunk, "content") and isinstance(getattr(chunk, "content"), str):
                delta = getattr(chunk, "content")
            elif isinstance(chunk, str):
                delta = chunk
            if delta:
                has_output = True
                yield {"type": "content", "delta": delta}
        if not has_output:
            fallback = llm_service.chat(chat_messages, system_prompt=ASSISTANT_ROLE_PROMPT)
            if fallback:
                yield {"type": "content", "delta": fallback}

    def get_api_list_for_selection(self, project_id: str, token: str) -> List[Dict[str, Any]]:
        return get_platform_client(token).get_api_list(project_id)


agent_service = AgentService()
