"""
Prompt模板模块

职责：
    1. 定义AI助手的角色Prompt
    2. 构建用例生成的Prompt
    3. 构建接口选择的Prompt
    4. 提供Prompt构建工具函数

Prompt设计原则：
    1. 角色明确：定义AI助手的身份和能力
    2. 上下文丰富：提供足够的背景信息
    3. 格式规范：明确输出格式要求
    4. 示例引导：提供示例帮助理解
"""

from typing import List, Dict, Any, Optional


# ==================== 角色Prompt ====================

ASSISTANT_ROLE_PROMPT = """你是一个专业的自动化测试助手，具备以下能力：

1. **测试知识**：熟悉API测试、Web测试、App测试的各种方法和最佳实践
2. **接口分析**：能够分析接口文档，理解接口功能、参数和返回值
3. **用例设计**：能够根据需求设计全面的测试用例，包括正向、反向、边界场景
4. **断言设计**：能够为测试步骤设计合理的断言
5. **依赖分析**：能够识别接口之间的依赖关系

你的回答应该：
- 专业、准确、简洁
- 提供实用的测试建议
- 使用中文回答
- 必要时提供代码示例

当用户要求生成测试用例时，你需要：
1. 分析用户需求，理解测试目标
2. 选择合适的接口
3. 设计测试步骤
4. 配置请求参数
5. 设计断言规则
6. 返回符合规范的用例JSON
"""


QUERY_REWRITE_SYSTEM_PROMPT = """你是企业级RAG检索系统的查询改写专家。

【角色】
- 你擅长中文技术问答检索重写，理解接口测试、平台后端、PRD、系统设计文档。

【目标】
- 生成最多3条高质量检索查询，覆盖：
  1) 基于历史会话的上下文补全改写
  2) 关键词扩写（同义词/专业词）
  3) 缩写词与噪声清洗（去口头语、错别字、冗余词）
  4) 伪答案导向改写（将用户问题转成可检索的“关键信息表达”）

【约束】
- 严格保留用户核心意图，不新增无关需求，不改变问句方向。
- 每条查询必须简洁，推荐不超过40字，最长不超过80字。
- 去重，避免表达雷同。
- 数量必须在1~3条之间。
- 仅输出JSON，不要解释。

【输出JSON格式】
{
  "rewrites": [
    "查询1",
    "查询2",
    "查询3"
  ]
}
"""


def build_query_rewrite_prompt(
    query: str,
    messages: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    构建查询改写Prompt

    @param query: 当前用户问题
    @param messages: 历史会话（最近若干条）
    @return: 用户提示词文本
    """
    history_lines: List[str] = []
    if messages:
        for item in messages[-6:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or "").strip()
            content = str(item.get("content") or "").strip()
            if not role or not content:
                continue
            history_lines.append(f"{role}: {content[:300]}")
    history_text = "\n".join(history_lines) if history_lines else "无历史会话"
    return (
        "请根据以下信息生成检索查询改写。\n\n"
        f"【当前问题】\n{query}\n\n"
        f"【历史会话】\n{history_text}\n\n"
        "请返回JSON。"
    )


# ==================== 用例生成Prompt ====================

CASE_GENERATION_PROMPT_TEMPLATE = """请根据以下信息生成一个完整的API测试用例：

## 项目信息
- 项目ID: {project_id}

## 用户需求
{user_requirement}

## 可用接口
{api_details}

## 接口依赖关系
{api_relations}

## 相关知识库内容
{rag_context}

## 用例Schema说明
{schema_info}

## 生成要求

1. **用例名称**：简洁明了，体现测试目标
2. **用例等级**：P0(核心)/P1(重要)/P2(一般)/P3(次要)
3. **测试步骤**：
   - 按依赖顺序排列接口
   - 每个步骤包含：apiId、description、header、body、query、rest、assertion
   - 参数值使用合理的测试数据
4. **断言设计**：
   - 状态码断言
   - 响应字段断言
   - 支持JSONPath表达式
5. **依赖配置**：
   - 使用relation字段配置前置接口
   - 支持参数传递

## 输出格式

请输出符合以下格式的JSON：

```json
{{
  "name": "用例名称",
  "level": "P1",
  "moduleId": "",
  "moduleName": "",
  "description": "用例描述",
  "caseApis": [
    {{
      "apiId": "接口ID",
      "description": "步骤描述",
      "header": [],
      "body": {{"type": "json", "json": "{{}}"}},
      "query": [],
      "rest": [],
      "assertion": [
        {{"type": "status", "expect": 200}}
      ],
      "relation": []
    }}
  ]
}}
```

注意：
- 只输出JSON，不要包含其他说明文字
- 确保JSON格式正确，可以被解析
- 使用实际的接口ID和参数
"""


def build_case_prompt(
    project_id: str,
    user_requirement: str,
    api_details: List[Dict[str, Any]],
    api_relations: Dict[str, List[str]],
    rag_docs: List[Dict[str, Any]],
    schema_payload: Optional[Dict[str, Any]] = None,
    messages: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    构建用例生成Prompt

    @param project_id: 项目ID
    @param user_requirement: 用户需求
    @param api_details: 接口详情列表
    @param api_relations: 接口依赖关系
    @param rag_docs: RAG检索结果
    @param schema_payload: 用例Schema
    @param messages: 历史消息
    @return: 完整的Prompt字符串
    """
    # 格式化接口详情
    api_details_str = _format_api_details(api_details)

    # 格式化依赖关系
    api_relations_str = _format_api_relations(api_relations)

    # 格式化RAG上下文
    rag_context_str = _format_rag_context(rag_docs)

    # 格式化Schema信息
    schema_info_str = _format_schema_info(schema_payload)

    # 构建历史上下文
    history_context = ""
    if messages and len(messages) > 0:
        history = []
        for msg in messages[-5:]:  # 只取最近5条
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role and content:
                history.append(f"{role}: {content}")
        if history:
            history_context = "\n\n## 历史对话\n" + "\n".join(history)

    prompt = CASE_GENERATION_PROMPT_TEMPLATE.format(
        project_id=project_id,
        user_requirement=user_requirement,
        api_details=api_details_str,
        api_relations=api_relations_str,
        rag_context=rag_context_str,
        schema_info=schema_info_str,
    )

    if history_context:
        prompt += history_context

    return prompt


def _format_api_details(api_details: List[Dict[str, Any]]) -> str:
    """格式化接口详情"""
    if not api_details:
        return "无可用接口"

    lines = []
    for i, api in enumerate(api_details, 1):
        api_id = api.get("id", "")
        name = api.get("name", "")
        path = api.get("path", "")
        method = api.get("method", "")
        description = api.get("description", "")

        line = f"{i}. ID: {api_id}, 名称: {name}, 路径: {method} {path}"
        if description:
            line += f", 描述: {description}"
        lines.append(line)

    return "\n".join(lines)


def _format_api_relations(api_relations: Dict[str, List[str]]) -> str:
    """格式化接口依赖关系"""
    if not api_relations:
        return "无依赖关系"

    lines = []
    for api_id, deps in api_relations.items():
        deps_str = ", ".join(deps)
        lines.append(f"- {api_id} 依赖于: {deps_str}")

    return "\n".join(lines)


def _format_rag_context(rag_docs: List[Dict[str, Any]]) -> str:
    """格式化RAG上下文"""
    if not rag_docs:
        return "无相关知识库内容"

    lines = []
    for i, doc in enumerate(rag_docs[:3], 1):  # 只取前3条
        content = doc.get("content", "")
        if content:
            # 截断过长的内容
            if len(content) > 500:
                content = content[:500] + "..."
            lines.append(f"{i}. {content}")

    return "\n\n".join(lines) if lines else "无相关知识库内容"


def _format_schema_info(schema_payload: Optional[Dict[str, Any]]) -> str:
    """格式化Schema信息"""
    if not schema_payload:
        return "使用标准用例Schema"

    # 简化Schema信息
    info = []
    if isinstance(schema_payload, dict):
        if "fields" in schema_payload:
            info.append(f"包含字段: {len(schema_payload['fields'])}个")
        if "required" in schema_payload:
            info.append(f"必填字段: {', '.join(schema_payload['required'])}")

    return "; ".join(info) if info else "使用标准用例Schema"


# ==================== 接口选择Prompt ====================

API_SELECTION_PROMPT_TEMPLATE = """请从以下接口中选择与用户需求最相关的接口。

## 用户需求
{user_requirement}

## 可用接口列表
{api_list}

## 选择要求

1. 根据用户需求，选择最相关的接口
2. 最多选择5个接口
3. 优先选择核心功能接口
4. 考虑接口之间的依赖关系

## 输出格式

请输出JSON格式：

```json
{{
  "api_ids": ["接口ID1", "接口ID2", ...],
  "reason": "选择原因说明"
}}
```

注意：
- 只输出JSON，不要包含其他说明
- 确保接口ID来自可用接口列表
- 如果没有相关接口，返回空数组
"""


def build_api_selection_prompt(
    user_requirement: str, all_apis: List[Dict[str, Any]]
) -> str:
    """
    构建接口选择Prompt

    @param user_requirement: 用户需求
    @param all_apis: 所有可用接口
    @return: Prompt字符串
    """
    # 格式化接口列表
    api_lines = []
    for i, api in enumerate(all_apis, 1):
        api_id = api.get("id", "")
        name = api.get("name", "")
        path = api.get("path", "")
        method = api.get("method", "")
        desc = api.get("description", "")

        line = f"{i}. ID: {api_id}, 名称: {name}, 路径: {method} {path}"
        if desc:
            line += f", 描述: {desc}"
        api_lines.append(line)

    api_list_str = "\n".join(api_lines) if api_lines else "无可用接口"

    return API_SELECTION_PROMPT_TEMPLATE.format(
        user_requirement=user_requirement,
        api_list=api_list_str,
    )


# ==================== 问答Prompt ====================

RAG_QA_PROMPT_TEMPLATE = """基于以下知识库内容，回答用户问题。

## 知识库内容
{context}

## 用户问题
{question}

请根据知识库内容回答问题。如果知识库中没有相关信息，请说明。
"""


def build_rag_qa_prompt(question: str, context: str) -> str:
    """
    构建RAG问答Prompt

    @param question: 用户问题
    @param context: 检索到的上下文
    @return: Prompt字符串
    """
    return RAG_QA_PROMPT_TEMPLATE.format(
        context=context,
        question=question,
    )


if __name__ == "__main__":
    """Prompt模板调试"""
    print("=" * 60)
    print("Prompt模板调试")
    print("=" * 60)

    # 测试用例生成Prompt
    print("\n1. 用例生成Prompt示例:")
    test_apis = [
        {"id": "api-1", "name": "登录接口", "path": "/api/login", "method": "POST"},
        {"id": "api-2", "name": "注册接口", "path": "/api/register", "method": "POST"},
    ]
    prompt = build_case_prompt(
        project_id="test-project",
        user_requirement="设计登录测试用例",
        api_details=test_apis,
        api_relations={"api-1": ["api-2"]},
        rag_docs=[{"content": "登录接口需要用户名和密码"}],
    )
    print(f"   Prompt长度: {len(prompt)} 字符")
    print(f"   前200字符: {prompt[:200]}...")

    # 测试接口选择Prompt
    print("\n2. 接口选择Prompt示例:")
    selection_prompt = build_api_selection_prompt("登录功能", test_apis)
    print(f"   Prompt长度: {len(selection_prompt)} 字符")
    print(f"   前200字符: {selection_prompt[:200]}...")

    # 测试RAG问答Prompt
    print("\n3. RAG问答Prompt示例:")
    qa_prompt = build_rag_qa_prompt(
        "登录需要什么参数？",
        "登录接口需要用户名和密码参数。"
    )
    print(f"   Prompt长度: {len(qa_prompt)} 字符")
    print(f"   内容:\n{qa_prompt}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
