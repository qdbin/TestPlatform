"""Agent服务模块"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
try:
    from json_repair import repair_json
except Exception:
    def repair_json(text: str, return_objects: bool = False):
        fixed = re.sub(r",\s*([}\]])", r"\1", text or "")
        return fixed

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.tools.platform_tools import get_platform_client

ASSISTANT_ROLE_PROMPT = """
你是接口测试平台的AI服务助手。
你的身份说明：当用户询问“你是谁/你能做什么”时，明确回答“我是接口测试平台的AI服务助手”，并简要列出你能提供的能力与用户可执行的下一步操作。
你的能力边界：
1) 解答接口测试、自动化测试、测试平台使用问题
2) 基于知识库内容进行问答与总结
3) 生成结构化测试用例草稿
4) 对报错、结果、流程给出排查建议
输出要求：优先简洁、结构清晰；不要编造不存在的平台能力。
""".strip()


def _try_parse_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    try:
        repaired_text = repair_json(text, return_objects=False)
        parsed = json.loads(repaired_text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        repaired_text = repair_json(match.group(0), return_objects=False)
        parsed = json.loads(repaired_text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None
    return None


def _case_prompt(
    user_requirement: str,
    project_id: str,
    api_details: List[Dict[str, Any]],
    knowledge: List[Dict[str, Any]],
) -> str:
    api_block = json.dumps(api_details, ensure_ascii=False)
    kb_block = json.dumps(knowledge, ensure_ascii=False)
    return (
        "你是一个专业的API测试用例生成助手。\n"
        "请根据用户需求、接口详情、以及知识库片段，生成一份符合流马测试平台 CaseRequest 结构的用例JSON。\n"
        "输出必须是一个JSON对象，不要输出任何额外解释或Markdown代码块。\n\n"
        f"用户需求：{user_requirement}\n\n"
        f"项目ID：{project_id}\n\n"
        f"接口详情(JSON)：{api_block}\n\n"
        f"知识库片段(JSON)：{kb_block}\n\n"
        "要求：\n"
        "- 仅输出一个可直接用于后端 CaseRequest 的 JSON 对象\n"
        "- 必填字段必须包含：id/num/name/level/moduleId/moduleName/projectId/type/description/caseApis\n"
        "- id 固定输出空字符串，type 固定输出 API，projectId 必须等于项目ID\n"
        "- caseApis 中每个步骤必须包含：id/index/caseId/apiId/description/header/body/query/rest/assertion/relation/controller\n"
        "- 断言尽量基于 resBody jsonpath 对 code/message/data 做校验，controller 中体现前后置动作\n"
        "- 至少输出2个步骤：1个正向场景 + 1个异常场景\n"
        "- 输出必须是可被 json-repair 修复为合法 JSON 的对象结构\n"
    )


def _interface_prompt(user_requirement: str, project_id: str) -> str:
    return (
        "你是一个API设计助手，请根据用户测试需求生成候选接口定义。\n"
        "输出必须是JSON对象，不要输出解释文字。\n"
        "格式：{\"interfaces\":[{\"name\":\"\",\"path\":\"\",\"method\":\"GET|POST|PUT|DELETE\",\"description\":\"\"}]}\n"
        f"项目ID：{project_id}\n"
        f"用户需求：{user_requirement}\n"
        "要求：\n"
        "- path必须以/开头\n"
        "- method只能是GET/POST/PUT/DELETE之一\n"
        "- 至少输出1个接口，最多输出5个\n"
    )


def _normalize_case_api_step(
    step: Dict[str, Any],
    fallback_api_id: str,
    valid_api_ids: set,
    api_meta_map: Dict[str, Dict[str, Any]],
    index: int,
) -> Optional[Dict[str, Any]]:
    if not isinstance(step, dict):
        return None
    api_id = str(step.get("apiId") or fallback_api_id or "")
    if not api_id or (valid_api_ids and api_id not in valid_api_ids):
        return None
    api_meta = api_meta_map.get(api_id, {})
    return {
        "id": str(step.get("id") or ""),
        "index": int(step.get("index") if isinstance(step.get("index"), int) else index),
        "caseId": str(step.get("caseId") or ""),
        "apiId": api_id,
        "description": str(step.get("description") or ""),
        "header": step.get("header") if isinstance(step.get("header"), list) else [],
        "body": step.get("body") if isinstance(step.get("body"), dict) else {},
        "query": step.get("query") if isinstance(step.get("query"), list) else [],
        "rest": step.get("rest") if isinstance(step.get("rest"), list) else [],
        "assertion": step.get("assertion") if isinstance(step.get("assertion"), list) else [],
        "relation": step.get("relation") if isinstance(step.get("relation"), list) else [],
        "controller": step.get("controller") if isinstance(step.get("controller"), list) else [],
        "apiMethod": str(step.get("apiMethod") or api_meta.get("method") or ""),
        "apiName": str(step.get("apiName") or api_meta.get("name") or ""),
        "apiPath": str(step.get("apiPath") or api_meta.get("path") or ""),
    }


def _normalize_case_request(
    case_obj: Dict[str, Any], project_id: str, api_details: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    if not isinstance(case_obj, dict):
        return None
    first_api_id = ""
    first_module_id = ""
    first_module_name = ""
    if api_details and isinstance(api_details[0], dict):
        first_api_id = str(api_details[0].get("id") or "")
        first_module_id = str(api_details[0].get("moduleId") or "")
        first_module_name = str(api_details[0].get("moduleName") or "")
    normalized: Dict[str, Any] = dict(case_obj)
    normalized["id"] = str(normalized.get("id") or "")
    normalized["num"] = int(normalized.get("num") if isinstance(normalized.get("num"), int) else 0)
    normalized["name"] = str(normalized.get("name") or f"AI生成用例-{datetime.now().strftime('%m%d%H%M%S')}")
    normalized["level"] = str(normalized.get("level") or "P1")
    normalized["moduleId"] = str(normalized.get("moduleId") or first_module_id or "default")
    normalized["moduleName"] = str(normalized.get("moduleName") or first_module_name or "AI生成模块")
    normalized["projectId"] = str(project_id)
    normalized["type"] = "API"
    normalized["thirdParty"] = str(normalized.get("thirdParty") or "")
    normalized["description"] = str(normalized.get("description") or "AI自动生成API测试用例")
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
    raw_steps = normalized.get("caseApis")
    if not isinstance(raw_steps, list):
        raw_steps = []
    valid_api_ids = {
        str(item.get("id"))
        for item in api_details
        if isinstance(item, dict) and item.get("id")
    }
    api_meta_map = {
        str(item.get("id")): item
        for item in api_details
        if isinstance(item, dict) and item.get("id")
    }
    normalized_steps: List[Dict[str, Any]] = []
    for idx, step in enumerate(raw_steps):
        normalized_step = _normalize_case_api_step(
            step, first_api_id, valid_api_ids, api_meta_map, idx
        )
        if normalized_step is not None:
            normalized_steps.append(normalized_step)
    if not normalized_steps and first_api_id:
        normalized_steps = [
            _normalize_case_api_step(
                {
                    "index": 0,
                    "apiId": first_api_id,
                    "description": "正向场景",
                    "assertion": [],
                },
                first_api_id,
                valid_api_ids,
                api_meta_map,
                0,
            ),
            _normalize_case_api_step(
                {
                    "index": 1,
                    "apiId": first_api_id,
                    "description": "异常场景",
                    "assertion": [],
                },
                first_api_id,
                valid_api_ids,
                api_meta_map,
                1,
            ),
        ]
        normalized_steps = [s for s in normalized_steps if s is not None]
    if not normalized_steps:
        return None
    normalized["caseApis"] = normalized_steps
    normalized["caseWebs"] = []
    normalized["caseApps"] = []
    return normalized


class AgentService:
    def _generate_interface_candidates(
        self, project_id: str, user_requirement: str
    ) -> List[Dict[str, Any]]:
        prompt = _interface_prompt(user_requirement, project_id)
        content = llm_service.chat([{"role": "user", "content": prompt}])
        parsed = _try_parse_json_object(content or "")
        interfaces = parsed.get("interfaces") if isinstance(parsed, dict) else []
        if not isinstance(interfaces, list):
            return []
        normalized = []
        for item in interfaces[:5]:
            if not isinstance(item, dict):
                continue
            method = str(item.get("method") or "GET").upper()
            if method not in {"GET", "POST", "PUT", "DELETE"}:
                method = "GET"
            path = str(item.get("path") or "").strip()
            if not path:
                continue
            if not path.startswith("/"):
                path = f"/{path}"
            normalized.append(
                {
                    "name": str(item.get("name") or "AI候选接口"),
                    "path": path,
                    "method": method,
                    "description": str(item.get("description") or ""),
                }
            )
        return normalized

    def _auto_select_api_ids(
        self, project_id: str, token: str, query: str, limit: int = 3
    ) -> List[str]:
        platform_client = get_platform_client(token)
        apis = platform_client.get_api_list(project_id) or []
        candidates: List[Dict[str, Any]] = []
        
        # 简单分词（按空格或常见标点）
        keywords = [k for k in re.split(r"[\s,，.。;；]+", query) if k]
        
        for api in apis:
            if not isinstance(api, dict):
                continue
            name = str(api.get("name") or "")
            url = str(api.get("url") or api.get("path") or "")
            desc = str(api.get("description") or "")
            method = str(api.get("method") or "")
            
            score = 0
            # 基础匹配
            full_text = f"{name} {url} {desc} {method}".lower()
            for kw in keywords:
                if not kw: continue
                kw_lower = kw.lower()
                if kw_lower in full_text:
                    score += 1
                if kw_lower in name.lower(): # 名字匹配权重更高
                    score += 2
            
            # 如果查询包含特定方法
            if "get" in query.lower() and method.lower() == "get": score += 1
            if "post" in query.lower() and method.lower() == "post": score += 1
            
            if score > 0:
                candidates.append({"id": api.get("id"), "score": score})
                
        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        return [str(c.get("id")) for c in candidates if c.get("id")][:limit]

    def _fallback_chat(
        self, project_id: str, token: str, message: str, use_rag: bool
    ) -> Dict[str, Any]:
        message = (message or "").strip()
        if any(k in message for k in ["用例", "case", "测试点", "测试用例", "生成"]):
            result = self.generate_case(project_id, token, message, selected_apis=[])
            if isinstance(result, dict) and result.get("case") is not None:
                return {
                    "reply": "已根据你的描述生成用例草稿。",
                    "case": result.get("case"),
                }
            return {"reply": "用例生成失败，请检查接口与权限配置。"}

        knowledge: List[Dict[str, Any]] = []
        if use_rag:
            knowledge = rag_service.search(project_id, message, top_k=5)
        context = "\n\n".join([str(d.get("content") or "") for d in knowledge if d])
        prompt = message
        if context:
            prompt = (
                f"参考资料：\n{context}\n\n用户问题：{message}\n\n请结合参考资料回答。"
            )
        reply = llm_service.chat(
            [{"role": "user", "content": prompt}], system_prompt=ASSISTANT_ROLE_PROMPT
        )
        return {"reply": reply}

    def _build_tools(self, project_id: str, token: str, use_rag: bool) -> List[Tool]:
        platform_client = get_platform_client(token)

        def answer_with_rag(query: str) -> str:
            query = (query or "").strip()
            knowledge: List[Dict[str, Any]] = []
            if use_rag and query:
                knowledge = rag_service.search(project_id, query, top_k=5)

            context = "\n\n".join([str(d.get("content") or "") for d in knowledge if d])
            prompt = query
            if context:
                prompt = f"参考资料：\n{context}\n\n用户问题：{query}\n\n请结合参考资料回答。"

            reply = llm_service.chat(
                [{"role": "user", "content": prompt}], system_prompt=ASSISTANT_ROLE_PROMPT
            )
            return json.dumps({"reply": reply, "case": None}, ensure_ascii=False)

        def generate_case(query: str) -> str:
            query = (query or "").strip()
            apis = platform_client.get_api_list(project_id) or []

            candidates: List[Dict[str, Any]] = []
            for api in apis:
                if not isinstance(api, dict):
                    continue
                name = str(api.get("name") or "")
                url = str(api.get("url") or api.get("path") or "")
                method = str(api.get("method") or "")
                score = 0
                for kw in ["登录", "鉴权", "认证", "token", "login", "auth"]:
                    if kw.lower() in name.lower() or kw.lower() in url.lower():
                        score += 2
                candidates.append(
                    {
                        "score": score,
                        "id": api.get("id"),
                        "name": name,
                        "url": url,
                        "method": method,
                    }
                )
            candidates.sort(key=lambda x: x.get("score", 0), reverse=True)

            picked_ids = [c.get("id") for c in candidates[:3] if c.get("id")]
            if not picked_ids and candidates:
                picked_ids = [candidates[0].get("id")]

            api_details: List[Dict[str, Any]] = []
            for api_id in picked_ids[:3]:
                api = platform_client.get_api_detail(str(api_id))
                if api:
                    api_details.append(api)

            knowledge: List[Dict[str, Any]] = []
            if use_rag and query:
                knowledge = rag_service.search(project_id, query, top_k=5)

            prompt = _case_prompt(query, project_id, api_details, knowledge)
            content = llm_service.chat([{"role": "user", "content": prompt}])
            parsed = _try_parse_json_object(content)
            case_obj = _normalize_case_request(parsed or {}, project_id, api_details)
            if case_obj is None:
                case_obj = {
                    "error": "case_json_parse_failed",
                    "raw": content,
                }
            reply = "已根据你的描述生成用例草稿（可在平台内再调整断言/参数提取）。"
            return json.dumps({"reply": reply, "case": case_obj}, ensure_ascii=False)

        return [
            Tool(
                name="answer_with_rag",
                func=answer_with_rag,
                description="用于普通问答：结合知识库检索后回答。输出JSON字符串。",
            ),
            Tool(
                name="generate_case",
                func=generate_case,
                description="用于生成测试用例：会自动选取相关接口并生成Case JSON。输出JSON字符串。",
            ),
        ]

    def _build_executor(
        self, project_id: str, token: str, use_rag: bool
    ) -> AgentExecutor:
        tools = self._build_tools(project_id, token, use_rag)
        llm = llm_service._get_llm()
        if llm is None:
            raise RuntimeError("llm_not_configured")

        prompt = PromptTemplate.from_template(
            "你是一个专业的自动化测试助手。\n"
            "你需要根据用户输入决定：\n"
            "- 普通问题：调用 answer_with_rag。\n"
            "- 生成用例/测试方案/测试点：调用 generate_case。\n\n"
            "规则：你必须先且至少调用一次工具（answer_with_rag 或 generate_case），不允许直接输出最终答案。\n\n"
            "你有如下工具可用：\n{tools}\n\n"
            "工具名称：{tool_names}\n\n"
            "使用如下格式：\n"
            "Question: 用户问题\n"
            "Thought: 你的思考\n"
            "Action: 工具名称（必须是可用工具之一）\n"
            "Action Input: 工具输入\n"
            "Observation: 工具返回\n"
            "...（可重复多次）\n"
            "Thought: 我已得到答案\n"
            "Final Answer: 最终答案（必须是JSON对象）\n\n"
            '最终输出JSON格式示例：{{"reply":"给用户的回复","case":null}}\n\n'
            "Begin!\n\n"
            "Question: {input}\n"
            "Thought: {agent_scratchpad}"
        )

        agent = create_react_agent(llm, tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            max_iterations=4,
            handle_parsing_errors=True,
        )

    def chat(
        self, project_id: str, token: str, message: str, use_rag: bool
    ) -> Dict[str, Any]:

        msg = (message or "").strip()
        if not msg:
            return {"reply": "请先输入问题。"}

        try:
            executor = self._build_executor(project_id, token, use_rag)
            result = executor.invoke({"input": msg})
            output = result.get("output") if isinstance(result, dict) else None
            if (
                isinstance(output, str)
                and "Agent stopped due to iteration limit" in output
            ):
                return self._fallback_chat(project_id, token, message, use_rag)
            parsed = _try_parse_json_object(output or "")
            if parsed and isinstance(parsed.get("reply"), str):
                return parsed
            if isinstance(output, str) and output.strip():
                return {"reply": output.strip()}
            return {"reply": "AI响应为空，请稍后重试。"}
        except Exception as e:
            if str(e) == "llm_not_configured":
                if use_rag:
                    docs = rag_service.search(project_id, message.strip(), top_k=5)
                    if docs:
                        lines = ["当前未配置可用的模型API Key，先返回知识库检索结果："]
                        for i, d in enumerate(docs, 1):
                            lines.append(f"{i}. {str(d.get('content') or '')[:300]}")
                        return {"reply": "\n".join(lines)}
                return {"reply": "AI服务未配置，请先在设置中配置可用的模型API Key。"}
            return {"reply": f"AI服务调用失败：{str(e)}"}

    def stream_chat(
        self, project_id: str, token: str, message: str, use_rag: bool
    ):
        msg = (message or "").strip()
        if not msg:
            return
        if any(k in msg for k in ["用例", "case", "测试点", "测试用例", "生成"]):
            result = self.generate_case(project_id, token, msg, selected_apis=[])
            reply = "已根据你的描述生成用例草稿。"
            case_obj = None
            interfaces = None
            if isinstance(result, dict):
                if result.get("status") == "success":
                    case_obj = result.get("case")
                if result.get("status") == "needs_api_create":
                    interfaces = result.get("interfaces")
                if isinstance(result.get("message"), str) and result.get("message"):
                    reply = result.get("message")
            for ch in reply:
                yield {"type": "content", "delta": ch}
            if case_obj is not None:
                yield {"type": "case", "case": case_obj}
            if interfaces:
                yield {"type": "interfaces", "interfaces": interfaces}
            return
        knowledge: List[Dict[str, Any]] = []
        if use_rag:
            knowledge = rag_service.search(project_id, msg, top_k=5)
        context = "\n\n".join([str(d.get("content") or "") for d in knowledge if d])
        prompt = msg
        if context:
            prompt = f"参考资料：\n{context}\n\n用户问题：{msg}\n\n请结合参考资料回答。"
        chunks = llm_service.chat_with_stream(
            [{"role": "user", "content": prompt}], system_prompt=ASSISTANT_ROLE_PROMPT
        )
        has_content = False
        for chunk in chunks:
            delta = ""
            if hasattr(chunk, "content"):
                content = getattr(chunk, "content")
                if isinstance(content, str):
                    delta = content
                elif isinstance(content, list):
                    parts: List[str] = []
                    for item in content:
                        if isinstance(item, str):
                            parts.append(item)
                        elif isinstance(item, dict) and isinstance(item.get("text"), str):
                            parts.append(item.get("text"))
                    delta = "".join(parts)
            elif isinstance(chunk, str):
                delta = chunk
            if delta:
                has_content = True
                if len(delta) > 24:
                    step = 8
                    for i in range(0, len(delta), step):
                        yield {"type": "content", "delta": delta[i : i + step]}
                else:
                    yield {"type": "content", "delta": delta}
        if not has_content:
            fallback = llm_service.chat(
                [{"role": "user", "content": prompt}], system_prompt=ASSISTANT_ROLE_PROMPT
            )
            if fallback:
                yield {"type": "content", "delta": fallback}

    def get_api_list_for_selection(
        self, project_id: str, token: str
    ) -> List[Dict[str, Any]]:
        platform_client = get_platform_client(token)
        return platform_client.get_api_list(project_id)

    def generate_case(
        self,
        project_id: str,
        token: str,
        user_requirement: str,
        selected_apis: Optional[List[str]] = None,
    ):
        selected_apis = [str(api_id) for api_id in (selected_apis or []) if api_id]
        platform_client = get_platform_client(token)
        api_details: List[Dict[str, Any]] = []
        all_apis = platform_client.get_api_list(project_id) or []
        existing_api_ids = {
            str(item.get("id"))
            for item in all_apis
            if isinstance(item, dict) and item.get("id")
        }
        missing_selected_api_ids = [
            api_id for api_id in selected_apis if api_id not in existing_api_ids
        ]
        selected_apis = [api_id for api_id in selected_apis if api_id in existing_api_ids]

        if not selected_apis:
            selected_apis = self._auto_select_api_ids(
                project_id, token, user_requirement, limit=3
            )

        for api_id in selected_apis[:5]:
            api = platform_client.get_api_detail(api_id)
            if api:
                api_details.append(api)
        if not api_details:
            return {
                "status": "needs_api_create",
                "message": "当前项目未匹配到可用接口，请先保存接口后再生成用例",
                "missing_api_ids": missing_selected_api_ids,
                "interfaces": self._generate_interface_candidates(
                    project_id, user_requirement
                ),
            }
        knowledge: List[Dict[str, Any]] = rag_service.search(
            project_id, user_requirement, top_k=5
        )
        prompt = _case_prompt(user_requirement, project_id, api_details, knowledge)
        content = llm_service.chat([{"role": "user", "content": prompt}])
        parsed = _try_parse_json_object(content)
        normalized = _normalize_case_request(parsed or {}, project_id, api_details)
        if normalized:
            return {
                "status": "success",
                "case": normalized,
                "existing_api_ids": [str(item.get("id")) for item in api_details if item.get("id")],
                "missing_api_ids": missing_selected_api_ids,
            }
        return {
            "status": "error",
            "message": "无法解析用例JSON",
            "raw_response": content,
        }


agent_service = AgentService()
