import os

import pytest
import requests


AI_BASE_URL = os.getenv("AI_BASE_URL", "http://localhost:8001")


def _service_ready() -> bool:
    try:
        resp = requests.get(f"{AI_BASE_URL}/health", timeout=3)
        return resp.ok
    except Exception:
        return False


@pytest.mark.skipif(not _service_ready(), reason="AI服务未启动，跳过冒烟测试")
def test_health_smoke():
    resp = requests.get(f"{AI_BASE_URL}/health", timeout=10)
    assert resp.status_code == 200
    assert resp.json().get("status") == "healthy"


@pytest.mark.skipif(not _service_ready(), reason="AI服务未启动，跳过冒烟测试")
def test_rag_query_smoke():
    payload = {"project_id": "1", "question": "登录接口", "top_k": 1, "messages": []}
    resp = requests.post(f"{AI_BASE_URL}/ai/rag/query", json=payload, timeout=20)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "success"
    assert "rag_status" in data
