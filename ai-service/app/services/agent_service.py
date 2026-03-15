"""
Agent服务模块 - LangChain 1.x LCEL版本

职责：
    1. 对话分流：识别用例需求 vs 问答需求
    2. 用例生成：ReAct Agent选择接口 + 固定工作流生成用例
    3. 流式对话：SSE事件流编排
    4. 集成 LangSmith 全链路追踪

核心类：
    - AgentService: Agent主服务
    - ApiSelectionResult: 接口选择结果模型

主要方法：
    - stream_chat(): 流式对话入口
    - generate_case(): 用例生成入口
    - _is_case_request(): 用例需求识别
    - _select_api_ids(): 接口选择（LLM + 关键词回退）

用例生成流程：
    1. 改写用户需求
    2. 加载项目接口池
    3. 选择候选接口（ReAct/关键词）
    4. 获取接口详情与依赖关系
    5. RAG增强
    6. LLM生成
    7. Pydantic校验（含重试）
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, AsyncIterator, Iterator

from langchain_core.runnables import RunnableLambda, RunnableParallel

from app.config import config
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.retrieval import query_rewriter
from app.services.case_workflow import CaseGenerationWorkflow, CaseWorkflowContext
from app.schemas import CaseRequestModel, ApiSelectionResult
from app.prompts import (
    ASSISTANT_ROLE_PROMPT,
    CASE_GENERATION_PROMPT,
    build_case_prompt,
    build_api_selection_prompt,
)
from app.tools.platform_tools import PlatformClient
from app.observability import app_logger
from app.observability.traceable import traceable


class AgentService:
    """
    Agent主服务 - LangChain 1.x LCEL实现

    职责：
        - 对话分流（用例生成 vs 问答）
        - 用例生成Agent（ReAct选择 + 工作流生成）
        - 流式对话编排
        - 全链路LangSmith追踪

    核心流程：
        1. stream_chat: 流式对话入口
           - 识别用例需求
           - 分流到用例生成或问答
        2. generate_case: 用例生成
           - 选择接口
           - 执行工作流
        3. _select_api_ids: 接口选择
           - LLM选择 + 关键词回退
    """

    def __init__(self):
        self._workflow = None

    def _get_platform_client(self, token: str) -> PlatformClient:
        """获取平台API客户端"""
        return PlatformClient(token=token)

    @traceable(name="agent_stream_chat", run_type="chain")
    async def stream_chat(
        self,
        project_id: str,
        token: str,
        message: str,
        use_rag: bool,
        messages: Optional[List[Dict[str, Any]]] = None,
        user_id: str = "",
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        流式对话主入口

        实现步骤：
            1. 识别是否为用例生成需求
            2. 如果是用例需求，执行用例生成流程
            3. 如果是问答需求，执行RAG检索并流式回答

        SSE事件类型：
            - content: 文本内容片段
            - case: 生成的用例
            - error: 错误信息
            - end: 流结束标记

        @param project_id: 项目ID（隔离）
        @param token: 平台鉴权token
        @param message: 用户消息
        @param use_rag: 是否启用RAG
        @param messages: 历史消息
        @param user_id: 用户ID
        @yield: SSE事件字典
        """
        messages = messages or []
        is_case_request = self._is_case_request(message)

        # 用例生成需求
        if is_case_request:
            result = self.generate_case(
                project_id=project_id,
                token=token,
                user_requirement=message,
                selected_apis=[],
                messages=messages,
                user_id=user_id,
            )

            # 发送思考过程
            yield {"type": "content", "delta": "正在分析需求并生成测试用例...\n\n"}

            if result.get("status") == "success":
                yield {"type": "case", "case": result.get("case")}
                api_ids = result.get("existing_api_ids", [])
                yield {
                    "type": "content",
                    "delta": f"\n已为您生成测试用例，涉及 {len(api_ids)} 个接口。",
                }
            else:
                error_msg = result.get("message") or result.get("error") or "未知错误"
                yield {"type": "error", "message": error_msg}

            yield {"type": "end"}
            return

        # 问答需求 - 执行RAG检索
        rag_context = ""
        if use_rag:
            rag_results = rag_service.search(
                project_id, message, top_k=5, user_id=user_id
            )
            if rag_results:
                rag_context = "\n\n".join(
                    [
                        str(item.get("content") or "")
                        for item in rag_results[:3]
                        if item
                    ]
                )

        # 构建Prompt
        system_prompt = ASSISTANT_ROLE_PROMPT
        if rag_context:
            system_prompt += (
                f"\n\n以下是相关知识库内容供参考：\n{rag_context}\n\n请基于以上知识回答用户问题。"
            )

        # 构建消息列表
        chat_messages = [{"role": "user", "content": message}]
        if messages:
            chat_messages = messages + chat_messages

        # 流式生成
        for chunk in llm_service.chat_with_stream(chat_messages, system_prompt):
            yield {"type": "content", "delta": chunk}

        yield {"type": "end"}

    def _is_case_request(self, message: str) -> bool:
        """
        识别是否为用例生成需求

        规则：
            - 包含"用例"、"测试用例"、"测试场景"等关键词
            - 包含"生成"、"创建"、"设计"等动作词

        @param message: 用户消息
        @return: 是否为用例需求
        """
        case_keywords = ["用例", "测试用例", "测试场景", "测试方案", "测试流程"]
        action_keywords = ["生成", "创建", "设计", "编写", "写", "做"]

        message_lower = message.lower()
        has_case_keyword = any(kw in message_lower for kw in case_keywords)
        has_action_keyword = any(kw in message_lower for kw in action_keywords)

        return has_case_keyword and has_action_keyword

    @traceable(name="agent_generate_case", run_type="chain")
    def generate_case(
        self,
        project_id: str,
        token: str,
        user_requirement: str,
        selected_apis: Optional[List[str]] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        用例生成主入口

        执行完整的用例生成流程：
            1. 改写用户需求
            2. 加载项目接口池
            3. 选择候选接口
            4. 获取接口详情与依赖关系
            5. RAG增强
            6. LLM生成
            7. Pydantic校验

        @param project_id: 项目ID（必填）
        @param token: 平台鉴权token
        @param user_requirement: 用户需求描述
        @param selected_apis: 预选接口ID列表（可选）
        @param messages: 历史消息（可选）
        @param user_id: 用户ID
        @return: {status, case, existing_api_ids, error, message}
        """
        workflow = self._get_workflow()
        context = CaseWorkflowContext(
            project_id=project_id,
            token=token,
            user_requirement=user_requirement,
            selected_apis=selected_apis or [],
            messages=messages or [],
            user_id=user_id,
        )
        return workflow.run(context)

    def _get_workflow(self) -> CaseGenerationWorkflow:
        """获取用例生成工作流实例（延迟初始化）"""
        if self._workflow is None:
            self._workflow = CaseGenerationWorkflow(
                get_platform_client=self._get_platform_client,
                select_api_ids=self._select_api_ids,
                build_dependency_relations=self._build_dependency_relations,
                build_case_prompt=build_case_prompt,
                normalize_case=self._normalize_case,
                parse_json_object=self._parse_json_object,
                case_model=CaseRequestModel,
                assistant_role_prompt=ASSISTANT_ROLE_PROMPT,
            )
        return self._workflow

    @traceable(name="agent_select_api_ids", run_type="chain")
    def _select_api_ids(
        self,
        project_id: str,
        token: str,
        user_requirement: str,
        all_apis: List[Dict[str, Any]],
    ) -> List[str]:
        """
        选择接口ID（LLM + 关键词回退）

        实现步骤：
            1. 尝试使用LLM选择接口
            2. 如果LLM失败，使用关键词匹配回退

        @param project_id: 项目ID
        @param token: 平台鉴权token
        @param user_requirement: 用户需求
        @param all_apis: 所有可用接口列表
        @return: 选中的接口ID列表
        """
        # 步骤1：LLM选择
        try:
            selected = self._llm_select_apis(user_requirement, all_apis)
            if selected:
                return selected
        except Exception as e:
            app_logger.warning("LLM选择接口失败: {}", str(e))

        # 步骤2：关键词匹配回退
        return self._keyword_select_apis(user_requirement, all_apis)

    def _llm_select_apis(
        self, user_requirement: str, all_apis: List[Dict[str, Any]]
    ) -> List[str]:
        """
        使用LLM选择接口

        通过结构化输出获取接口选择结果。
        """
        prompt = build_api_selection_prompt(user_requirement, all_apis)

        result = llm_service.chat_structured(
            [{"role": "user", "content": prompt}],
            output_model=ApiSelectionResult,
            system_prompt=ASSISTANT_ROLE_PROMPT,
        )

        if result and result.api_ids:
            return result.api_ids
        return []

    def _keyword_select_apis(
        self, user_requirement: str, all_apis: List[Dict[str, Any]]
    ) -> List[str]:
        """
        关键词匹配选择接口（回退策略）

        当LLM选择失败时，使用简单的关键词匹配。
        """
        keywords = set(user_requirement.lower().split())
        scored_apis = []

        for api in all_apis:
            if not isinstance(api, dict):
                continue
            api_id = str(api.get("id") or "")
            name = str(api.get("name") or "").lower()
            path = str(api.get("path") or "").lower()
            desc = str(api.get("description") or "").lower()

            score = 0
            for kw in keywords:
                if kw in name:
                    score += 3
                if kw in path:
                    score += 2
                if kw in desc:
                    score += 1

            if score > 0:
                scored_apis.append((api_id, score))

        # 按分数排序并返回前5个
        scored_apis.sort(key=lambda x: x[1], reverse=True)
        return [api_id for api_id, _ in scored_apis[:5]]

    def _build_dependency_relations(
        self, api_details: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        构建接口依赖关系

        分析接口之间的依赖关系，用于用例生成时确定执行顺序。

        @param api_details: 接口详情列表
        @return: {api_id: [dependent_api_id, ...]}

        依赖识别规则：
            - 登录接口通常是其他接口的前置依赖
            - 注册接口通常是登录的前置依赖
            - 根据接口名称和路径推断依赖关系
        """
        relations: Dict[str, List[str]] = {}
        api_map = {str(api.get("id")): api for api in api_details if api.get("id")}

        for api_id, api in api_map.items():
            name = str(api.get("name") or "").lower()
            path = str(api.get("path") or "").lower()

            deps = []
            # 识别登录接口的依赖（通常是注册）
            if "login" in name or "登录" in name:
                for other_id, other_api in api_map.items():
                    if other_id == api_id:
                        continue
                    other_name = str(other_api.get("name") or "").lower()
                    if "register" in other_name or "注册" in other_name:
                        deps.append(other_id)

            # 识别业务接口的依赖（通常是登录）
            if deps or ("login" not in name and "注册" not in name):
                for other_id, other_api in api_map.items():
                    if other_id == api_id:
                        continue
                    other_name = str(other_api.get("name") or "").lower()
                    if "login" in other_name or "登录" in other_name:
                        if other_id not in deps:
                            deps.append(other_id)

            if deps:
                relations[api_id] = deps

        return relations

    def _normalize_case(
        self,
        project_id: str,
        case_data: Dict[str, Any],
        api_details: List[Dict[str, Any]],
        api_relations: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """
        标准化用例对象

        将LLM生成的用例数据转换为符合平台后端规范的格式。

        @param project_id: 项目ID
        @param case_data: LLM生成的用例数据
        @param api_details: 接口详情列表
        @param api_relations: 接口依赖关系
        @return: 标准化的用例对象
        """
        api_relations = api_relations or {}
        api_map = {str(api.get("id")): api for api in api_details if api.get("id")}

        # 基础字段
        normalized = {
            "id": "",
            "num": 0,
            "name": str(case_data.get("name") or "自动生成用例"),
            "level": str(case_data.get("level") or "P1"),
            "moduleId": str(case_data.get("moduleId") or ""),
            "moduleName": str(case_data.get("moduleName") or ""),
            "projectId": project_id,
            "type": "API",
            "thirdParty": "",
            "description": str(case_data.get("description") or ""),
            "environmentIds": [],
            "system": "web",
            "commonParam": {},
            "status": "Normal",
            "caseApis": [],
            "caseWebs": [],
            "caseApps": [],
        }

        # 处理caseApis
        case_apis = case_data.get("caseApis") or []
        if not isinstance(case_apis, list):
            case_apis = []

        for idx, step in enumerate(case_apis, 1):
            if not isinstance(step, dict):
                continue

            api_id = str(step.get("apiId") or "")
            api_info = api_map.get(api_id, {})

            normalized_step = {
                "id": "",
                "index": idx,
                "caseId": "",
                "apiId": api_id,
                "description": str(step.get("description") or ""),
                "header": step.get("header") or [],
                "body": step.get("body") or {},
                "query": step.get("query") or [],
                "rest": step.get("rest") or [],
                "assertion": step.get("assertion") or [],
                "relation": [],
                "controller": [],
                "apiMethod": str(api_info.get("method") or step.get("apiMethod") or ""),
                "apiName": str(api_info.get("name") or step.get("apiName") or ""),
                "apiPath": str(api_info.get("path") or step.get("apiPath") or ""),
            }

            # 添加依赖关系
            if api_id in api_relations:
                for dep_id in api_relations[api_id]:
                    normalized_step["relation"].append({
                        "apiId": dep_id,
                        "type": "pre",
                    })

            normalized["caseApis"].append(normalized_step)

        return normalized

    def _parse_json_object(self, text: str) -> Optional[Dict[str, Any]]:
        """
        解析JSON对象

        从文本中提取JSON对象，支持代码块格式。

        @param text: 包含JSON的文本
        @return: 解析后的字典或None
        """
        if not text:
            return None

        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试从代码块中提取
        import re

        # 匹配 ```json ... ``` 或 ``` ... ```
        patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        return None

    def get_api_list_for_selection(
        self, project_id: str, token: str
    ) -> List[Dict[str, Any]]:
        """
        获取接口列表供用户选择

        @param project_id: 项目ID
        @param token: 平台鉴权token
        @return: 接口列表
        """
        platform_client = self._get_platform_client(token)
        return platform_client.get_api_list(project_id) or []


# 全局Agent服务实例
agent_service = AgentService()


if __name__ == "__main__":
    """Agent服务调试"""
    import asyncio

    print("=" * 60)
    print("Agent服务调试 - LangChain 1.x")
    print("=" * 60)

    # 测试用例需求识别
    print("\n1. 用例需求识别测试:")
    test_messages = [
        "帮我生成一个登录用例",
        "设计一个注册测试场景",
        "什么是接口测试？",
        "帮我写一个测试用例",
    ]
    for msg in test_messages:
        is_case = agent_service._is_case_request(msg)
        print(f"   '{msg}' -> {'用例需求' if is_case else '问答需求'}")

    # 测试关键词选择
    print("\n2. 关键词选择接口测试:")
    test_apis = [
        {"id": "api-1", "name": "用户登录", "path": "/api/login", "description": "用户登录接口"},
        {"id": "api-2", "name": "用户注册", "path": "/api/register", "description": "用户注册接口"},
        {"id": "api-3", "name": "获取用户信息", "path": "/api/user/info", "description": "获取用户信息"},
    ]
    selected = agent_service._keyword_select_apis("登录功能测试", test_apis)
    print(f"   需求: '登录功能测试'")
    print(f"   选中: {selected}")

    # 测试依赖关系构建
    print("\n3. 依赖关系构建测试:")
    relations = agent_service._build_dependency_relations(test_apis)
    print(f"   依赖关系: {relations}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
