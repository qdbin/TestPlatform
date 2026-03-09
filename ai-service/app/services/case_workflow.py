"""
用例生成Workflow主干。

主干节点：
1) load_api_pool：读取项目接口池。
2) select_api_ids：调用 ReAct 子节点筛选接口。
3) load_context：加载接口详情、依赖、RAG、Schema。
4) generate_and_validate：生成JSON并标准化校验。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable, Set

from pydantic import ValidationError

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service


@dataclass
class CaseWorkflowContext:
    project_id: str
    token: str
    user_requirement: str
    selected_apis: Optional[List[str]]
    messages: Optional[List[Dict[str, Any]]]


class CaseGenerationWorkflow:
    def __init__(
        self,
        get_platform_client: Callable[[str], Any],
        select_api_ids: Callable[[str, str, str, List[Dict[str, Any]]], List[str]],
        build_dependency_relations: Callable[[List[Dict[str, Any]]], Dict[str, List[str]]],
        build_case_prompt: Callable[..., str],
        normalize_case: Callable[..., Dict[str, Any]],
        parse_json_object: Callable[[str], Optional[Dict[str, Any]]],
        case_model: Any,
        assistant_role_prompt: str,
    ):
        self.get_platform_client = get_platform_client
        self.select_api_ids = select_api_ids
        self.build_dependency_relations = build_dependency_relations
        self.build_case_prompt = build_case_prompt
        self.normalize_case = normalize_case
        self.parse_json_object = parse_json_object
        self.case_model = case_model
        self.assistant_role_prompt = assistant_role_prompt

    def run(self, context: CaseWorkflowContext) -> Dict[str, Any]:
        api_pool = self._load_api_pool(context)
        if "error" in api_pool:
            return api_pool
        all_apis = api_pool["all_apis"]
        all_ids = api_pool["all_ids"]

        selected = self._select_api_ids(context, all_apis, all_ids)
        if not selected:
            api_names = [
                str(item.get("name") or item.get("path") or "")
                for item in all_apis[:10]
                if isinstance(item, dict)
            ]
            hint = f"当前项目可用接口：{', '.join(api_names[:5])}等。请尝试使用更具体的接口名称描述。"
            return {"status": "error", "message": f"未匹配到相关接口。{hint}"}

        loaded = self._load_context(context, selected)
        if "error" in loaded:
            return loaded

        return self._generate_and_validate(context, **loaded)

    def _load_api_pool(self, context: CaseWorkflowContext) -> Dict[str, Any]:
        platform_client = self.get_platform_client(context.token)
        all_apis = platform_client.get_api_list(context.project_id) or []
        if not all_apis:
            reason = ""
            if hasattr(platform_client, "get_last_error"):
                reason = str(platform_client.get_last_error() or "")
            if reason:
                return {"status": "error", "error": reason}
            return {
                "status": "error",
                "error": "当前项目暂无可用接口，请先在【接口管理】中创建接口后再生成用例",
            }
        all_ids = {
            str(item.get("id"))
            for item in all_apis
            if isinstance(item, dict) and item.get("id")
        }
        if not all_ids:
            return {"status": "error", "error": "接口列表解析异常，请检查接口数据格式"}
        return {"all_apis": all_apis, "all_ids": all_ids}

    def _select_api_ids(
        self,
        context: CaseWorkflowContext,
        all_apis: List[Dict[str, Any]],
        all_ids: Set[str],
    ) -> List[str]:
        selected = [
            str(item)
            for item in (context.selected_apis or [])
            if str(item) in all_ids
        ]
        if not selected:
            selected = self.select_api_ids(
                context.project_id,
                context.token,
                context.user_requirement,
                all_apis,
            )
        return [item for item in selected if item in all_ids][:5]

    def _load_context(
        self, context: CaseWorkflowContext, selected: List[str]
    ) -> Dict[str, Any]:
        platform_client = self.get_platform_client(context.token)
        api_details: List[Dict[str, Any]] = []
        for api_id in selected:
            detail = platform_client.get_api_detail(api_id)
            if detail:
                api_details.append(detail)
        if not api_details:
            return {"error": "接口详情读取失败，请检查接口是否存在或当前账号是否有权限"}

        api_relations = self.build_dependency_relations(api_details)
        rag_docs = rag_service.search(context.project_id, context.user_requirement, top_k=6)
        schema_payload = platform_client.get_case_schema(context.project_id) or {}
        return {
            "api_details": api_details,
            "api_relations": api_relations,
            "rag_docs": rag_docs,
            "schema_payload": schema_payload,
        }

    def _generate_and_validate(
        self,
        context: CaseWorkflowContext,
        api_details: List[Dict[str, Any]],
        api_relations: Dict[str, List[str]],
        rag_docs: List[Dict[str, Any]],
        schema_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        prompt = self.build_case_prompt(
            context.project_id,
            context.user_requirement,
            api_details,
            api_relations,
            rag_docs,
            schema_payload,
            messages=context.messages,
        )
        last_error = ""
        for _ in range(2):
            raw = llm_service.chat_json(
                [{"role": "user", "content": prompt}],
                system_prompt=self.assistant_role_prompt,
            )
            parsed = self.parse_json_object(raw or "")
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
            normalized = self.normalize_case(
                context.project_id, target, api_details, api_relations=api_relations
            )
            try:
                model = self.case_model.model_validate(normalized)
                return {
                    "status": "success",
                    "case": model.model_dump(),
                    "existing_api_ids": [
                        str(item.get("id")) for item in api_details if item.get("id")
                    ],
                }
            except ValidationError as exc:
                last_error = str(exc)
                prompt = (
                    prompt
                    + f"\n\n注意：上次输出校验失败：{str(exc)[:200]}。请修正后重新输出。"
                )
                continue
        return {
            "status": "error",
            "message": "用例生成失败，请更换描述或简化需求",
            "error": last_error,
        }
