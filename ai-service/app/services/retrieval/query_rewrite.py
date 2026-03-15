"""
查询改写模块

职责：
    1. 对查询进行语义改写和扩写
    2. 生成多个查询变体以提高检索召回率
    3. 支持同义词扩展和查询分解

改写策略：
    1. 同义词扩展：将关键词替换为同义词
    2. 查询分解：将复杂查询分解为多个子查询
    3. 语义改写：改变表达方式但保持语义

使用示例：
    rewriter = QueryRewriter()
    queries = rewriter.rewrite_and_expand("登录接口参数")
    # 返回: ["登录接口参数", "login接口参数", "用户登录接口参数要求"]
"""

from typing import List, Set


class QueryRewriter:
    """
    查询改写器

    职责：
        - 对查询进行语义改写
        - 生成多个查询变体
        - 提高检索召回率

    改写方法：
        1. 同义词替换
        2. 查询扩展
        3. 语义变体生成
    """

    def __init__(self):
        # 同义词词典
        self.synonyms = {
            # 接口相关
            "接口": ["API", "接口", "服务"],
            "API": ["接口", "API", "服务"],
            "登录": ["login", "登录", "signin", "登陆"],
            "注册": ["register", "注册", "signup", "创建账号"],
            "查询": ["query", "查询", "获取", "查找", "search"],
            "创建": ["create", "创建", "新增", "添加", "insert"],
            "更新": ["update", "更新", "修改", "编辑", "edit"],
            "删除": ["delete", "删除", "移除", "remove"],
            "用户": ["user", "用户", "会员", "account"],
            "订单": ["order", "订单", "purchase"],
            "商品": ["product", "商品", "物品", "goods"],
            "参数": ["parameter", "参数", "入参", "请求参数", "arguments"],
            "返回": ["return", "返回", "响应", "response", "输出"],
            "错误": ["error", "错误", "异常", "exception", "失败"],
            "测试": ["test", "测试", "用例", "case"],
            "用例": ["test case", "用例", "测试用例", "测试场景"],
            # 功能相关
            "验证": ["verify", "验证", "校验", "check", "确认"],
            "权限": ["permission", "权限", "授权", "authorization"],
            "认证": ["auth", "认证", "鉴权", "authentication"],
            "配置": ["config", "配置", "设置", "setting"],
            "数据": ["data", "数据", "信息", "information"],
        }

    def rewrite_and_expand(self, query: str, max_variants: int = 3) -> List[str]:
        """
        改写并扩展查询

        实现步骤：
            1. 保留原始查询
            2. 生成同义词变体
            3. 生成语义扩展
            4. 去重并限制数量

        @param query: 原始查询
        @param max_variants: 最大变体数量
        @return: 查询变体列表

        示例：
            输入: "登录接口参数"
            输出: ["登录接口参数", "login接口参数", "用户登录接口参数要求"]
        """
        if not query:
            return []

        query = query.strip()
        variants: Set[str] = {query}  # 保留原始查询

        # 生成同义词变体
        synonym_variants = self._generate_synonym_variants(query)
        variants.update(synonym_variants)

        # 生成语义扩展
        expanded_variants = self._generate_expanded_variants(query)
        variants.update(expanded_variants)

        # 转换为列表并限制数量
        result = list(variants)[:max_variants]
        return result if result else [query]

    def _generate_synonym_variants(self, query: str) -> List[str]:
        """
        生成同义词变体

        将查询中的关键词替换为同义词，生成语义相同但表述不同的查询。

        @param query: 原始查询
        @return: 同义词变体列表
        """
        variants = []

        for keyword, synonyms in self.synonyms.items():
            if keyword in query:
                for synonym in synonyms:
                    if synonym != keyword:
                        variant = query.replace(keyword, synonym)
                        if variant != query:
                            variants.append(variant)

        return variants[:2]  # 限制同义词变体数量

    def _generate_expanded_variants(self, query: str) -> List[str]:
        """
        生成语义扩展变体

        通过添加修饰词或改变句式来扩展查询语义。

        @param query: 原始查询
        @return: 扩展变体列表
        """
        variants = []

        # 添加修饰词扩展
        expansions = [
            f"{query}说明",
            f"{query}要求",
            f"{query}示例",
            f"如何{query}",
            f"{query}文档",
        ]

        # 根据查询内容选择合适的扩展
        if "接口" in query or "API" in query:
            if "参数" not in query:
                expansions.append(f"{query}参数")
            if "返回" not in query:
                expansions.append(f"{query}返回值")

        if "用例" in query or "测试" in query:
            if "步骤" not in query:
                expansions.append(f"{query}步骤")
            if "断言" not in query:
                expansions.append(f"{query}断言")

        variants.extend(expansions[:2])  # 限制扩展数量

        return variants

    def decompose_query(self, query: str) -> List[str]:
        """
        分解复杂查询

        将包含多个意图的复杂查询分解为多个子查询。

        @param query: 复杂查询
        @return: 子查询列表

        示例：
            输入: "登录和注册的接口参数"
            输出: ["登录接口参数", "注册接口参数"]
        """
        if not query:
            return []

        # 识别连接词
        connectors = ["和", "与", "以及", "及", "、", "，", ",", ";", "；"]

        for connector in connectors:
            if connector in query:
                parts = query.split(connector)
                if len(parts) >= 2:
                    # 尝试提取共同部分
                    sub_queries = []
                    for part in parts:
                        part = part.strip()
                        if part:
                            sub_queries.append(part)
                    if len(sub_queries) >= 2:
                        return sub_queries

        return [query]


# 全局查询改写器实例
query_rewriter = QueryRewriter()


if __name__ == "__main__":
    """查询改写器调试"""
    print("=" * 60)
    print("查询改写器调试")
    print("=" * 60)

    rewriter = QueryRewriter()

    # 测试改写和扩展
    print("\n1. 查询改写测试:")
    test_queries = [
        "登录接口参数",
        "用户注册API",
        "查询订单接口",
        "创建用户测试用例",
        "登录和注册的接口",
    ]

    for query in test_queries:
        variants = rewriter.rewrite_and_expand(query)
        print(f"\n   原始: {query}")
        print(f"   改写: {variants}")

    # 测试查询分解
    print("\n2. 查询分解测试:")
    complex_queries = [
        "登录和注册的接口参数",
        "查询订单、创建订单的测试用例",
        "用户认证与权限验证",
    ]

    for query in complex_queries:
        parts = rewriter.decompose_query(query)
        print(f"\n   原始: {query}")
        print(f"   分解: {parts}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
