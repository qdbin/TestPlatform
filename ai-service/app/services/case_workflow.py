"""
用例生成Workflow主干 - LangChain 1.x LCEL版本

主干流程：
    1. load_api_pool: 读取项目接口池
    2. select_api_ids: 调用LLM筛选接口（含重试）
    3. load_context: 加载接口详情、依赖、RAG、Schema
    4. generate_and_validate: 生成JSON并标准化校验（含Pydantic校验失败重试）

特性：
    - 完整的LangSmith追踪
    - Pydantic校验失败自动重试
    - 错误上下文传递
    - 异步支持

使用示例：
    workflow = CaseGenerationWorkflow(...)
    result = workflow.run(CaseWorkflowContext(...))
    # result = {"status": "success", "case": {...}, "existing_api_ids": [...]}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set

from pydantic import ValidationError
from langchain_core.runnables import RunnableLambda, RunnableParallel

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.retrieval import query_rewriter
from app.observability import app_logger
from app.observability.traceable import traceable


@dataclass
class CaseWorkflowContext:
    """
    用例生成工作流上下文

    字段说明：
        - project_id: 项目ID（必填，数据隔离）
        - token: 平台鉴权token（调用后端API用）
        - user_requirement: 用户需求描述（必填）
        - selected_apis: 可选指定的接口ID列表
        - messages: 历史对话消息（用于上下文理解）
        - user_id: 用户ID
        - rewritten_requirement: 改写后的需求（内部使用）
        - rewrite_queries: 扩写查询列表（内部使用）

    使用示例：
        context = CaseWorkflowContext(
            project_id="test-project",
            token="xxx",
            user_requirement="设计登录用例",
            selected_apis=[],
            messages=[]
        )
    """
    project_id: str
    token: str
    user_requirement: str
    selected_apis: Optional[List[str]] = None
    messages: Optional[List[Dict[str, Any]]] = None
    user_id: str = ""
    rewritten_requirement: str = ""
    rewrite_queries: Optional[List[str]] = None


@dataclass
class RetryContext:
    """
    重试上下文

    用于记录用例生成过程中的重试状态，
    当Pydantic校验失败时，构建包含错误信息的修正Prompt。

    字段说明：
        - attempt: 当前尝试次数
        - max_attempts: 最大尝试次数
        - last_error: 最后一次错误信息
        - accumulated_context: 累积的错误上下文
    """
    attempt: int = 0
    max_attempts: int = 2
    last_error: str = ""
    accumulated_context: List[str] = field(default_factory=list)


class CaseGenerationWorkflow:
    """
    用例生成工作流 - LangChain 1.x实现

    职责：
        - 编排用例生成的完整流程
        - 协调各模块完成任务
        - 处理异常和重试（特别是Pydantic校验失败重试）
        - 完整的LangSmith追踪

    流程：
        1. 加载接口池
        2. 选择接口ID（LLM + 关键词回退）
        3. 加载上下文（详情、依赖、RAG、Schema）
        4. 生成并校验（含Pydantic校验失败重试）

    依赖注入：
        - get_platform_client: 获取平台API客户端
        - select_api_ids: 接口选择函数
        - build_dependency_relations: 构建依赖关系
        - build_case_prompt: 构建用例生成Prompt
        - normalize_case: 标准化用例对象
        - parse_json_object: JSON解析函数
        - case_model: Pydantic用例模型
        - assistant_role_prompt: 助手角色Prompt
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

    @traceable(name="case_workflow_run", run_type="chain")
    def run(self, context: CaseWorkflowContext) -> Dict[str, Any]:
        """
        用例生成主入口

        执行完整的用例生成流程，包括：
            1. 问题改写 + 加载接口池（并行）
            2. 选择接口ID
            3. 加载上下文
            4. 生成并校验（含重试）

        @param context: 工作流上下文
        @return: {status, case, existing_api_ids, error, message, attempts}

        返回示例：
            {
                "status": "success",
                "case": {"name": "...", "caseApis": [...]},
                "existing_api_ids": ["api-001", "api-002"],
                "attempts": 1
            }
        """
        # 步骤1: 问题改写 + 加载接口池（并行）
        prepared = self._prepare_requirement_and_api_pool(context)
        if "error" in prepared:
            return prepared
        all_apis = prepared["all_apis"]
        all_ids = prepared["all_ids"]
        context.rewritten_requirement = str(prepared.get("rewritten_requirement") or context.user_requirement)
        context.rewrite_queries = prepared.get("rewrite_queries") or [context.rewritten_requirement]

        # 步骤2: 选择接口ID
        selected = self._select_api_ids(context, all_apis, all_ids)
        if not selected:
            api_names = [
                str(item.get("name") or item.get("path") or "")
                for item in all_apis[:10]
                if isinstance(item, dict)
            ]
            hint = f"当前项目可用接口：{', '.join(api_names[:5])}等。请尝试使用更具体的接口名称描述。"
            return {"status": "error", "message": f"未匹配到相关接口。{hint}"}

        # 步骤3: 加载上下文
        loaded = self._load_context(context, selected)
        if "error" in loaded:
            return loaded

        # 步骤4: 生成并校验（含重试机制）
        result = self._generate_and_validate_with_retry(context, loaded)
        return result

    @traceable(name="case_prepare_requirement_and_api_pool", run_type="chain")
    def _prepare_requirement_and_api_pool(self, context: CaseWorkflowContext) -> Dict[str, Any]:
        """
        并行执行问题改写和接口池加载

        使用RunnableParallel实现并行执行，提高效率。
        """
        parallel = RunnableParallel(
            rewrite=RunnableLambda(
                lambda _: query_rewriter.rewrite_and_expand(context.user_requirement)
            ),
            api_pool=RunnableLambda(lambda _: self._load_api_pool(context)),
        )
        result = parallel.invoke({})
        api_pool = result.get("api_pool") if isinstance(result, dict) else None
        if not isinstance(api_pool, dict):
            return {"status": "error", "error": "接口池加载失败"}
        if "error" in api_pool:
            return api_pool

        rewrite_queries = result.get("rewrite") if isinstance(result, dict) else []
        if not isinstance(rewrite_queries, list) or not rewrite_queries:
            rewrite_queries = [context.user_requirement]
        rewritten_requirement = str(rewrite_queries[1] if len(rewrite_queries) > 1 else rewrite_queries[0])
        return {
            "all_apis": api_pool["all_apis"],
            "all_ids": api_pool["all_ids"],
            "rewrite_queries": rewrite_queries,
            "rewritten_requirement": rewritten_requirement,
        }

    @traceable(name="case_load_api_pool", run_type="tool")
    def _load_api_pool(self, context: CaseWorkflowContext) -> Dict[str, Any]:
        """
        加载项目接口池

        通过PlatformClient调用平台后端API获取项目下所有接口。
        """
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

    @traceable(name="case_select_api_ids", run_type="chain")
    def _select_api_ids(
        self,
        context: CaseWorkflowContext,
        all_apis: List[Dict[str, Any]],
        all_ids: Set[str],
    ) -> List[str]:
        """
        选择接口ID

        优先使用用户指定的接口，如果没有则调用LLM选择。
        """
        selected = [
            str(item) for item in (context.selected_apis or []) if str(item) in all_ids
        ]
        requirement = context.rewritten_requirement or context.user_requirement
        if not selected:
            selected = self.select_api_ids(
                context.project_id,
                context.token,
                requirement,
                all_apis,
            )

        # 去重并限制数量
        deduped: List[str] = []
        seen: Set[str] = set()
        for item in selected:
            current = str(item)
            if current in all_ids and current not in seen:
                deduped.append(current)
                seen.add(current)
            if len(deduped) >= 5:
                break

        return deduped

    @traceable(name="case_load_context", run_type="chain")
    def _load_context(
        self, context: CaseWorkflowContext, selected: List[str]
    ) -> Dict[str, Any]:
        """
        加载上下文信息（含RAG）

        加载接口详情、依赖关系、RAG检索结果、Schema等信息。
        """
        platform_client = self.get_platform_client(context.token)
        api_details: List[Dict[str, Any]] = []
        for api_id in selected:
            detail = platform_client.get_api_detail(api_id)
            if detail:
                api_details.append(detail)

        if not api_details:
            return {"error": "接口详情读取失败，请检查接口是否存在或当前账号是否有权限"}

        api_relations = self.build_dependency_relations(api_details)
        rag_query = context.rewritten_requirement or context.user_requirement
        rag_docs = rag_service.search(
            context.project_id,
            rag_query,
            top_k=6,
            user_id=context.user_id,
        )
        schema_payload = platform_client.get_case_schema(context.project_id) or {}

        return {
            "api_details": api_details,
            "api_relations": api_relations,
            "rag_docs": rag_docs,
            "schema_payload": schema_payload,
        }

    @traceable(name="case_generate_validate_with_retry", run_type="chain")
    def _generate_and_validate_with_retry(
        self,
        context: CaseWorkflowContext,
        loaded: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        生成并校验用例（含Pydantic校验失败重试机制）

        重试策略：
            1. 首次生成使用基础Prompt
            2. 如果Pydantic校验失败，记录错误信息
            3. 构建包含错误上下文的修正Prompt
            4. 最多重试2次

        @param context: 工作流上下文
        @param loaded: 加载的上下文信息
        @return: 生成结果
        """
        retry_ctx = RetryContext(max_attempts=2)

        api_details = loaded["api_details"]
        api_relations = loaded["api_relations"]
        rag_docs = loaded["rag_docs"]
        schema_payload = loaded["schema_payload"]

        # 基础Prompt
        base_prompt = self.build_case_prompt(
            context.project_id,
            context.rewritten_requirement or context.user_requirement,
            api_details,
            api_relations,
            rag_docs,
            schema_payload,
            messages=context.messages,
        )

        current_prompt = base_prompt

        while retry_ctx.attempt < retry_ctx.max_attempts:
            retry_ctx.attempt += 1

            try:
                # 调用LLM生成JSON
                raw = llm_service.chat_json(
                    [{"role": "user", "content": current_prompt}],
                    system_prompt=self.assistant_role_prompt,
                )
                parsed = self.parse_json_object(raw or "")
                target = (
                    parsed.get("case")
                    if isinstance(parsed, dict) and isinstance(parsed.get("case"), dict)
                    else parsed
                )
                if not isinstance(target, dict):
                    retry_ctx.last_error = "JSON解析失败：输出不是有效的JSON对象"
                    retry_ctx.accumulated_context.append(
                        f"尝试{retry_ctx.attempt}：输出格式错误"
                    )
                    current_prompt = self._build_retry_prompt(
                        base_prompt, retry_ctx, "输出必须是有效的JSON对象"
                    )
                    continue

                # 标准化用例
                normalized = self.normalize_case(
                    context.project_id, target, api_details, api_relations=api_relations
                )

                # Pydantic校验
                try:
                    model = self.case_model.model_validate(normalized)
                    app_logger.info(
                        "case_generation_success attempt={} case_name={}",
                        retry_ctx.attempt,
                        model.name
                    )
                    return {
                        "status": "success",
                        "case": model.model_dump(),
                        "existing_api_ids": [
                            str(item.get("id")) for item in api_details if item.get("id")
                        ],
                        "attempts": retry_ctx.attempt,
                    }
                except ValidationError as exc:
                    # Pydantic校验失败，记录错误并准备重试
                    error_msg = str(exc)
                    retry_ctx.last_error = error_msg
                    retry_ctx.accumulated_context.append(
                        f"尝试{retry_ctx.attempt}校验失败：{error_msg[:200]}"
                    )
                    app_logger.warning(
                        "case_validation_failed attempt={} error={}",
                        retry_ctx.attempt,
                        error_msg[:200]
                    )
                    current_prompt = self._build_retry_prompt(
                        base_prompt, retry_ctx, error_msg
                    )
                    continue

            except Exception as e:
                retry_ctx.last_error = str(e)
                retry_ctx.accumulated_context.append(f"尝试{retry_ctx.attempt}异常：{str(e)}")
                current_prompt = self._build_retry_prompt(
                    base_prompt, retry_ctx, str(e)
                )
                continue

        # 重试耗尽，返回错误
        app_logger.error(
            "case_generation_failed after {} attempts. Last error: {}",
            retry_ctx.attempt,
            retry_ctx.last_error[:200]
        )

        return {
            "status": "error",
            "message": "用例生成失败，请更换描述或简化需求",
            "error": retry_ctx.last_error,
            "attempts": retry_ctx.attempt,
            "context": retry_ctx.accumulated_context,
        }

    def _build_retry_prompt(
        self,
        base_prompt: str,
        retry_ctx: RetryContext,
        error_msg: str,
    ) -> str:
        """
        构建重试Prompt

        包含：
            - 原始Prompt
            - 历史错误信息
            - 具体修正建议
        """
        retry_instructions = f"""

## 修正要求（第{retry_ctx.attempt}次重试）

之前的生成存在问题，请根据以下错误信息修正：

### 错误信息
{error_msg[:500]}

### 修正建议
1. 仔细检查JSON格式，确保所有引号、括号匹配
2. 确保使用正确的数据类型（字符串、数字、数组、对象）
3. 必填字段必须提供有效值
4. 数组字段必须是有效的JSON数组
5. 不要包含多余的字段或注释

### 历史尝试
{chr(10).join(retry_ctx.accumulated_context)}

请重新生成，确保输出符合要求。
"""
        return base_prompt + retry_instructions


if __name__ == "__main__":
    """用例生成Workflow调试"""
    print("=" * 60)
    print("用例生成Workflow调试 - LangChain 1.x")
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

    # 测试RetryContext
    print("\n2. 重试上下文测试:")
    retry_ctx = RetryContext(max_attempts=3)
    retry_ctx.attempt = 1
    retry_ctx.last_error = "Validation error"
    retry_ctx.accumulated_context.append("尝试1失败")
    print(f"   尝试次数: {retry_ctx.attempt}/{retry_ctx.max_attempts}")
    print(f"   最后错误: {retry_ctx.last_error}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
