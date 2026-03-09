"""
查询改写与查询扩写模块。
"""

from __future__ import annotations

import json
from typing import List

from app.services.llm_service import llm_service


class QueryRewriter:
    def rewrite_and_expand(self, query: str) -> List[str]:
        prompt = (
            "你是检索查询改写器。"
            "请针对输入问题给出 1 条改写和 2 条扩写，输出 JSON："
            '{"rewrites": ["..."], "expansions": ["...", "..."]}'
            f"\n输入问题：{query}"
        )
        try:
            raw = llm_service.chat_json([{"role": "user", "content": prompt}])
            payload = json.loads(raw)
            rewrites = payload.get("rewrites") if isinstance(payload, dict) else []
            expansions = payload.get("expansions") if isinstance(payload, dict) else []
            result = [str(query).strip()]
            for item in rewrites or []:
                text = str(item).strip()
                if text and text not in result:
                    result.append(text)
            for item in expansions or []:
                text = str(item).strip()
                if text and text not in result:
                    result.append(text)
            return result[:4]
        except Exception:
            return [str(query).strip()]


query_rewriter = QueryRewriter()
