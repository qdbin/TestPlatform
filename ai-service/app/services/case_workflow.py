"""
用例生成Workflow主干

主干流程：
    1. load_api_pool: 读取项目接口池
    2. select_api_ids: 调用ReAct子节点筛选接口
    3. load_context: 加载接口详情、依赖、RAG、Schema
    4. generate_and_validate: 生成JSON并标准化校验

使用示例：
    workflow = CaseGenerationWorkflow(...)
    result = workflow.run(CaseWorkflowContext(...))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable, Set

from pydantic import ValidationError

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service


@dataclass
class CaseWorkflowContext:
    """
    用例生成工作流上下文

    字段说明：
        - project_id: 项目ID
        - token: 平台鉴权token
        - user_requirement: 用户需求描述
        - selected_apis: 可选指定的接口ID列表
        - messages: 历史对话消息
    """

    project_id: str
    token: str
    user_requirement: str
    selected_apis: Optional[List[str]]
    messages: Optional[List[Dict[str, Any]]]


class CaseGenerationWorkflow:
    """
    用例生成工作流

    职责：
        - 编排用例生成的完整流程
        - 协调各模块完成任务
        - 处理异常和重试
    """

    def __init__(
        self,
        get_platform_client: Callable[[str], Any],
        select_api_ids: Callable[[str, str, str, List[Dict[str, Any]]], List[str]],
        build_dependency_relations: Callable[
            [List[Dict[str, Any]]], Dict[str, List[str]]
        ],
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
        """
        用例生成主入口

        实现步骤：
            1. 加载接口池
            2. 选择接口ID
            3. 加载上下文（详情、依赖、RAG、Schema）
            4. 生成并校验用例

        @param context: 工作流上下文
        @return: {status, case, existing_api_ids, error}
        """
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
        """
        加载项目接口池

        @return: {all_apis, all_ids} 或 {status: "error", error: "..."}
        """
        # 调用平台客户端获取接口列表
        platform_client = self.get_platform_client(context.token)
        all_apis = platform_client.get_api_list(context.project_id) or []
        # 检查接口列表是否为空
        if not all_apis:
            # 获取详细错误信息
            reason = ""
            if hasattr(platform_client, "get_last_error"):
                reason = str(platform_client.get_last_error() or "")
            if reason:
                return {"status": "error", "error": reason}
            return {
                "status": "error",
                "error": "当前项目暂无可用接口，请先在【接口管理】中创建接口后再生成用例",
            }
        # 提取所有接口ID
        all_ids = {
            str(item.get("id"))
            for item in all_apis
            if isinstance(item, dict) and item.get("id")
        }
        # 检查ID提取结果
        if not all_ids:
            return {"status": "error", "error": "接口列表解析异常，请检查接口数据格式"}
        return {"all_apis": all_apis, "all_ids": all_ids}

    def _select_api_ids(
        self,
        context: CaseWorkflowContext,
        all_apis: List[Dict[str, Any]],
        all_ids: Set[str],
    ) -> List[str]:
        """选择接口ID"""
        # 优先使用用户指定的接口ID
        selected = [
            str(item) for item in (context.selected_apis or []) if str(item) in all_ids
        ]
        # 未指定时调用Agent自动选择
        if not selected:
            selected = self.select_api_ids(
                context.project_id,
                context.token,
                context.user_requirement,
                all_apis,
            )
        # 去重并限制返回数量
        return [item for item in selected if item in all_ids][:5]

    def _load_context(
        self, context: CaseWorkflowContext, selected: List[str]
    ) -> Dict[str, Any]:
        """
        加载上下文信息

        包括：接口详情、接口依赖关系、知识库文档、Case Schema
        """
        # 获取平台客户端
        platform_client = self.get_platform_client(context.token)
        # 逐个获取接口详情
        api_details: List[Dict[str, Any]] = []
        for api_id in selected:
            detail = platform_client.get_api_detail(api_id)
            if detail:
                api_details.append(detail)
        # 检查接口详情是否获取成功
        if not api_details:
            return {"error": "接口详情读取失败，请检查接口是否存在或当前账号是否有权限"}

        # 构建接口依赖关系
        api_relations = self.build_dependency_relations(api_details)
        # 检索知识库文档
        rag_docs = rag_service.search(
            context.project_id, context.user_requirement, top_k=6
        )
        # 获取Case Schema
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
        """
        生成并校验用例

        实现步骤：
            1. 构建Prompt
            2. 调用LLM生成JSON
            3. 解析JSON对象
            4. 标准化处理
            5. Pydantic校验
            6. 失败重试一次
        """
        # 步骤1：构建用例生成Prompt
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
        # 最多重试2次
        for _ in range(2):
            # 步骤2：调用LLM生成JSON
            raw = llm_service.chat_json(
                [{"role": "user", "content": prompt}],
                system_prompt=self.assistant_role_prompt,
            )
            # 步骤3：解析JSON对象
            parsed = self.parse_json_object(raw or "")
            target = (
                parsed.get("case")
                if isinstance(parsed, dict) and isinstance(parsed.get("case"), dict)
                else parsed
            )
            # JSON解析失败时提示重试
            if not isinstance(target, dict):
                last_error = "json_parse_failed"
                prompt = (
                    prompt
                    + "\n\n注意：上次输出不是有效JSON，请直接输出JSON对象，不要任何解释。"
                )
                continue
            # 步骤4：标准化处理
            normalized = self.normalize_case(
                context.project_id, target, api_details, api_relations=api_relations
            )
            # 步骤5：Pydantic校验
            try:
                model = self.case_model.model_validate(normalized)
                # 校验成功，返回成功结果
                return {
                    "status": "success",
                    "case": model.model_dump(),
                    "existing_api_ids": [
                        str(item.get("id")) for item in api_details if item.get("id")
                    ],
                }
            except ValidationError as exc:
                # 校验失败，记录错误信息并重试
                last_error = str(exc)
                prompt = (
                    prompt
                    + f"\n\n注意：上次输出校验失败：{str(exc)[:200]}。请修正后重新输出。"
                )
                continue
        # 重试耗尽，返回错误结果
        return {
            "status": "error",
            "message": "用例生成失败，请更换描述或简化需求",
            "error": last_error,
        }


if __name__ == "__main__":
    """
    用例生成Workflow调试代码

    调试说明：
        1. 测试工作流上下文创建
        2. 模拟工作流执行
    """
    print("=" * 60)
    print("用例生成Workflow调试")
    print("=" * 60)

    # 测试上下文创建
    print("\n1. 上下文创建测试:")
    context = CaseWorkflowContext(
        project_id="test-project",
        token="test-token",
        user_requirement="设计登录用例",
        selected_apis=[],
        messages=[],
    )
    print(f"   项目ID: {context.project_id}")
    print(f"   用户需求: {context.user_requirement}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
