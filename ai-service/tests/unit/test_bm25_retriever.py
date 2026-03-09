from app.services.retrieval.bm25 import BM25KeywordRetriever


def test_bm25_retriever_should_rank_matching_document_first():
    retriever = BM25KeywordRetriever()
    docs = ["登录接口返回token", "注册接口创建用户", "查询订单列表"]
    metas = [{"doc_name": "a"}, {"doc_name": "b"}, {"doc_name": "c"}]
    result = retriever.search("登录 token", docs, metas, top_k=2)
    assert result
    assert "登录接口" in result[0]["content"]
    assert "bm25_score" in result[0]
