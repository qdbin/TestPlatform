"""
查询改写模块

职责：
    1. 使用LLM对查询进行语义改写和扩写
    2. 生成多个查询变体以提高检索召回率

实现：
    - 仅使用LLM进行查询改写
    - 支持对话历史作为上下文
    - 返回3个查询变体（原始+2个改写）

使用示例：
    from app.services.retrieval.query_rewrite import query_rewriter

    queries = query_rewriter.rewrite_and_expand("登录接口参数")
    # 返回: ["登录接口参数", "如何调用登录API", "登录接口请求参数说明"]
"""

from typing import List, Dict, Any, Optional
import json
import re

from app.observability import app_logger
from app.observability.traceable import traceable
from app.prompts.assistant_prompts import (
    QUERY_REWRITE_SYSTEM_PROMPT,
    build_query_rewrite_prompt,
)
from app.services.llm_service import llm_service


class QueryRewriter:
    """
    查询改写器（LLM驱动）

    特性：
        - 仅使用LLM进行语义改写
        - 支持对话历史上下文
        - 保证至少返回原始查询
    """

    def _clean_query_text(self, value: str) -> str:
        cleaned = str(value or "").strip()
        cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        cleaned = re.sub(r"[“”\"'`]+", "", cleaned).strip()
        return cleaned

    def _normalize_rewrites(
        self, query: str, rewrites: List[str], max_variants: int
    ) -> List[str]:
        seen = {self._clean_query_text(query)}
        result = [query]

        for item in rewrites:
            value = self._clean_query_text(item)
            if not value or value in seen:
                continue
            if len(value) > 80:
                value = value[:80].strip()
            seen.add(value)
            result.append(value)
            if len(result) >= max_variants:
                break

        return result[:max_variants]

    def _rewrite_with_llm(
        self,
        query: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        max_variants: int = 3,
    ) -> List[str]:
        prompt = build_query_rewrite_prompt(query=query, messages=messages)
        raw_text = llm_service.chat_json(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=QUERY_REWRITE_SYSTEM_PROMPT,
        )

        try:
            payload = json.loads(raw_text)
            if isinstance(payload, dict) and isinstance(payload.get("rewrites"), list):
                return self._normalize_rewrites(
                    query, [str(x) for x in payload["rewrites"]], max_variants
                )
        except Exception:
            app_logger.warning("LLM查询改写解析失败: {}", raw_text)

        return [query]

    @traceable(name="rag_query_rewrite", run_type="chain")
    def rewrite_and_expand(
        self,
        query: str,
        max_variants: int = 3,
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        使用LLM改写并扩展查询

        @param query: 原始查询
        @param max_variants: 最大变体数量（默认3）
        @param messages: 对话历史（用于上下文）
        @return: 查询变体列表
        """
        if not query:
            return []

        return self._rewrite_with_llm(
            query=self._clean_query_text(query),
            messages=messages,
            max_variants=max_variants,
        )


query_rewriter = QueryRewriter()


if __name__ == "__main__":
    print("=" * 60)
    print("查询改写器调试（LLM驱动）")
    print("=" * 60)

    rewriter = QueryRewriter()

    test_queries = [
        "登录接口参数",
        "用户注册API",
        "查询订单接口",
    ]

    for q in test_queries:
        variants = rewriter.rewrite_and_expand(q)
        print(f"\n原始: {q}")
        print(f"改写: {variants}")

    print("\n" + "=" * 60)
