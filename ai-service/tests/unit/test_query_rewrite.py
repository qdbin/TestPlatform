import json

from app.services.retrieval.query_rewrite import QueryRewriter


def test_query_rewrite_should_use_llm_and_limit_to_three(monkeypatch):
    rewriter = QueryRewriter()

    def mock_chat_json(messages, system_prompt):
        return json.dumps(
            {
                "rewrites": [
                    "登录接口参数要求",
                    "login API 请求参数",
                    "认证接口入参有哪些",
                    "这个应该被截断",
                ]
            },
            ensure_ascii=False,
        )

    monkeypatch.setattr(
        "app.services.retrieval.query_rewrite.llm_service.chat_json", mock_chat_json
    )
    variants = rewriter.rewrite_and_expand(
        "登录接口要什么参数？？？",
        max_variants=3,
        messages=[
            {"role": "user", "content": "我在看接口文档"},
            {"role": "assistant", "content": "你是想看登录接口吗"},
        ],
    )
    assert 1 <= len(variants) <= 3
    assert all(len(item) <= 80 for item in variants)
    assert len(set(variants)) == len(variants)


def test_query_rewrite_should_fallback_when_llm_invalid(monkeypatch):
    rewriter = QueryRewriter()

    def mock_chat_json(messages, system_prompt):
        return "not-json"

    monkeypatch.setattr(
        "app.services.retrieval.query_rewrite.llm_service.chat_json", mock_chat_json
    )
    variants = rewriter.rewrite_and_expand("注册接口返回什么", max_variants=3)
    assert variants
    assert len(variants) <= 3
