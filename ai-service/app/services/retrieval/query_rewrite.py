"""
查询改写与查询扩写模块

核心功能：
    - 改写：优化用户查询表达
    - 扩写：扩展相关查询词
    - 融合：返回多条查询供混合检索

使用示例：
    rewriter = QueryRewriter()
    queries = rewriter.rewrite_and_expand("如何登录")
    # ["如何登录", "用户登录步骤", "接口认证方法"]
"""

from __future__ import annotations

import json
from typing import List

from app.services.llm_service import llm_service


class QueryRewriter:
    """
    查询改写器

    职责：
        - 调用LLM对用户查询进行改写
        - 生成扩写查询以提升召回率
        - 失败时返回原始查询
    """

    def rewrite_and_expand(self, query: str) -> List[str]:
        """
        查询改写与扩写主入口

        实现步骤：
            1. 构建改写Prompt
            2. 调用LLM JSON模式生成改写/扩写结果
            3. 解析JSON，合并去重
            4. 失败时返回原始查询

        @param query: 用户原始查询
        @return: [原始查询, 改写, 扩写1, 扩写2]

        示例：
            输入："如何登录"
            输出：["如何登录", "用户登录接口", "登录验证方法", "身份认证流程"]
        """
        # 构建改写Prompt
        prompt = (
            "你是检索查询改写器。"
            "请针对输入问题给出 1 条改写和 2 条扩写，输出 JSON："
            '{"rewrites": ["..."], "expansions": ["...", "..."]}'
            f"\n输入问题：{query}"
        )
        try:
            # 调用LLM进行改写
            raw = llm_service.chat_json([{"role": "user", "content": prompt}])
            payload = json.loads(raw)
            # 提取改写和扩写结果
            rewrites = payload.get("rewrites") if isinstance(payload, dict) else []
            expansions = payload.get("expansions") if isinstance(payload, dict) else []
            # 合并去重
            result = [str(query).strip()]
            for item in rewrites or []:
                text = str(item).strip()
                if text and text not in result:
                    result.append(text)
            for item in expansions or []:
                text = str(item).strip()
                if text and text not in result:
                    result.append(text)
            # 限制返回数量
            return result[:4]
        except Exception:
            # 失败时返回原始查询
            return [str(query).strip()]


query_rewriter = QueryRewriter()


if __name__ == "__main__":
    """
    查询改写器调试代码

    调试说明：
        1. 测试查询改写
    """
    print("=" * 60)
    print("查询改写器调试")
    print("=" * 60)

    # 测试改写
    print("\n1. 查询改写测试:")
    test_queries = ["如何登录", "用户注册接口", "接口测试"]
    for q in test_queries:
        result = query_rewriter.rewrite_and_expand(q)
        print(f"   原始: {q}")
        print(f"   结果: {result}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
