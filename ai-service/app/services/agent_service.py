"""Agent服务模块"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.tools.platform_tools import get_platform_client


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

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None
    return None


def _case_prompt(
    user_requirement: str,
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
        f"接口详情(JSON)：{api_block}\n\n"
        f"知识库片段(JSON)：{kb_block}\n\n"
        "要求：\n"
        "- 用例类型固定为 API\n"
        "- 至少包含1个正向场景和1个异常场景（可作为同一用例的多个步骤或多个用例）\n"
        "- 断言尽量基于 resBody jsonpath 对 code/message/data 做校验\n"
        "- 字段命名使用后端 CaseRequest 常用风格：name/type/level/moduleId/projectId/description/caseApis\n"
    )


class AgentService:
    def _auto_select_api_ids(
        self, project_id: str, token: str, query: str, limit: int = 3
    ) -> List[str]:
        platform_client = get_platform_client(token)
        apis = platform_client.get_api_list(project_id) or []
        candidates: List[Dict[str, Any]] = []
        for api in apis:
            if not isinstance(api, dict):
                continue
            name = str(api.get("name") or "")
            url = str(api.get("url") or api.get("path") or "")
            score = 0
            for kw in ["登录", "鉴权", "认证", "token", "login", "auth"]:
                if kw.lower() in name.lower() or kw.lower() in url.lower():
                    score += 2
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
        reply = llm_service.chat([{"role": "user", "content": prompt}])
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

            reply = llm_service.chat([{"role": "user", "content": prompt}])
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

            prompt = _case_prompt(query, api_details, knowledge)
            content = llm_service.chat([{"role": "user", "content": prompt}])
            case_obj = _try_parse_json_object(content) or {
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

        if any(k in msg for k in ["用例", "case", "测试点", "测试用例", "生成"]):
            result = self.generate_case(project_id, token, msg, selected_apis=[])
            if isinstance(result, dict) and result.get("case") is not None:
                return {
                    "reply": "已根据你的描述生成用例草稿。",
                    "case": result.get("case"),
                }
            return {"reply": "用例生成失败，请检查接口与权限配置。"}

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
        selected_apis = selected_apis or []
        platform_client = get_platform_client(token)
        api_details: List[Dict[str, Any]] = []

        if not selected_apis:
            selected_apis = self._auto_select_api_ids(
                project_id, token, user_requirement, limit=3
            )

        for api_id in selected_apis[:5]:
            api = platform_client.get_api_detail(api_id)
            if api:
                api_details.append(api)
        knowledge: List[Dict[str, Any]] = rag_service.search(
            project_id, user_requirement, top_k=5
        )
        prompt = _case_prompt(user_requirement, api_details, knowledge)
        content = llm_service.chat([{"role": "user", "content": prompt}])
        parsed = _try_parse_json_object(content)
        if parsed:
            return {"status": "success", "case": parsed}
        return {
            "status": "error",
            "message": "无法解析用例JSON",
            "raw_response": content,
        }


agent_service = AgentService()
