"""
Prompt模板模块

职责：
    1. 定义AI助手的角色Prompt
    2. 构建用例生成的Prompt
    3. 构建接口选择的Prompt

导出内容：
    - ASSISTANT_ROLE_PROMPT: 助手角色Prompt
    - CASE_GENERATION_PROMPT: 用例生成Prompt模板
    - build_case_prompt: 构建用例生成Prompt函数
    - build_api_selection_prompt: 构建接口选择Prompt函数
"""

from app.prompts.assistant_prompts import (
    ASSISTANT_ROLE_PROMPT,
    CASE_GENERATION_PROMPT_TEMPLATE as CASE_GENERATION_PROMPT,
    build_case_prompt,
    build_api_selection_prompt,
    build_rag_qa_prompt,
)

__all__ = [
    "ASSISTANT_ROLE_PROMPT",
    "CASE_GENERATION_PROMPT",
    "build_case_prompt",
    "build_api_selection_prompt",
    "build_rag_qa_prompt",
]
