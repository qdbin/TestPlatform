import base64
import os
import uuid
from typing import Any, Dict, Iterable, List

import pytest
import requests


AI_BASE_URL = os.getenv("AI_BASE_URL", "http://localhost:8001")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8080")
EVAL_ACCOUNT = os.getenv("EVAL_ACCOUNT", "LMadmin")
EVAL_PASSWORD = os.getenv("EVAL_PASSWORD", "Liuma@123456")


def _ai_ready() -> bool:
    try:
        resp = requests.get(f"{AI_BASE_URL}/health", timeout=3)
        return resp.ok
    except Exception:
        return False


def _backend_ready() -> bool:
    try:
        encoded = base64.b64encode(EVAL_PASSWORD.encode("utf-8")).decode("utf-8")
        resp = requests.post(
            f"{BACKEND_BASE_URL}/autotest/login",
            json={"account": EVAL_ACCOUNT, "password": encoded},
            timeout=5,
        )
        return resp.ok
    except Exception:
        return False


def _unwrap_backend_data(payload: Dict[str, Any]) -> Any:
    if not isinstance(payload, dict):
        return None
    if "data" in payload:
        return payload.get("data")
    return payload


def _extract_list(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        if isinstance(data.get("list"), list):
            return [x for x in data.get("list", []) if isinstance(x, dict)]
        if isinstance(data.get("data"), list):
            return [x for x in data.get("data", []) if isinstance(x, dict)]
    return []


def _iter_sse_events(resp: requests.Response) -> Iterable[Dict[str, Any]]:
    for raw in resp.iter_lines(decode_unicode=True):
        if not raw:
            continue
        if not str(raw).startswith("data:"):
            continue
        chunk = str(raw)[5:].strip()
        if not chunk:
            continue
        try:
            event = requests.models.complexjson.loads(chunk)
        except Exception:
            continue
        if isinstance(event, dict):
            yield event


@pytest.fixture(scope="session")
def runtime_context() -> Dict[str, str]:
    if not _ai_ready() or not _backend_ready():
        pytest.skip("AI服务或后端未启动，跳过全链路接口测试")
    encoded = base64.b64encode(EVAL_PASSWORD.encode("utf-8")).decode("utf-8")
    login_resp = requests.post(
        f"{BACKEND_BASE_URL}/autotest/login",
        json={"account": EVAL_ACCOUNT, "password": encoded},
        timeout=15,
    )
    assert login_resp.status_code == 200
    token = str(login_resp.headers.get("token") or "").strip()
    assert token
    projects_resp = requests.post(
        f"{BACKEND_BASE_URL}/autotest/project/list/1/2000",
        json={},
        headers={"token": token},
        timeout=15,
    )
    assert projects_resp.status_code == 200
    projects = _extract_list(_unwrap_backend_data(projects_resp.json()))
    selected_project_id = ""
    for item in projects:
        pid = str(item.get("id") or "")
        if not pid:
            continue
        api_resp = requests.post(
            f"{BACKEND_BASE_URL}/autotest/api/list/1/2000",
            json={"projectId": pid},
            headers={"token": token},
            timeout=15,
        )
        if api_resp.status_code != 200:
            continue
        api_list = _extract_list(_unwrap_backend_data(api_resp.json()))
        if api_list:
            selected_project_id = pid
            break
    assert selected_project_id
    return {"token": token, "project_id": selected_project_id}


def test_ai_service_rag_endpoints(runtime_context: Dict[str, str]):
    project_id = runtime_context["project_id"]
    doc_id = f"it-doc-{uuid.uuid4().hex[:12]}"
    add_payload = {
        "project_id": project_id,
        "user_id": "it-user",
        "doc_id": doc_id,
        "doc_type": "manual",
        "doc_name": "登录流程说明",
        "content": "# 登录\n\n## 请求\n- account\n- password",
    }
    add_resp = requests.post(f"{AI_BASE_URL}/ai/rag/add", json=add_payload, timeout=30)
    assert add_resp.status_code == 200
    add_data = add_resp.json()
    assert add_data.get("status") == "success"
    query_resp = requests.post(
        f"{AI_BASE_URL}/ai/rag/query",
        json={
            "project_id": project_id,
            "user_id": "it-user",
            "question": "登录需要什么参数",
            "top_k": 3,
            "messages": [],
        },
        timeout=30,
    )
    assert query_resp.status_code == 200
    query_data = query_resp.json()
    assert query_data.get("status") == "success"
    assert "rag_status" in query_data
    stats_resp = requests.get(f"{AI_BASE_URL}/ai/rag/stats/{project_id}", timeout=20)
    assert stats_resp.status_code == 200
    assert stats_resp.json().get("status") == "success"
    del_resp = requests.post(
        f"{AI_BASE_URL}/ai/rag/delete",
        json={"project_id": project_id, "doc_id": doc_id},
        timeout=30,
    )
    assert del_resp.status_code == 200
    assert del_resp.json().get("status") == "success"


def test_ai_service_agent_endpoints(runtime_context: Dict[str, str]):
    token = runtime_context["token"]
    project_id = runtime_context["project_id"]
    api_resp = requests.get(
        f"{AI_BASE_URL}/ai/agent/api-list/{project_id}",
        headers={"token": token},
        timeout=30,
    )
    assert api_resp.status_code == 200
    api_data = api_resp.json()
    assert api_data.get("status") == "success"
    assert isinstance(api_data.get("data"), list)
    assert len(api_data.get("data")) > 0
    case_resp = requests.post(
        f"{AI_BASE_URL}/ai/agent/generate-case",
        headers={"token": token},
        json={
            "project_id": project_id,
            "user_id": "it-user",
            "user_requirement": "生成注册后登录流程用例，包含正向和异常场景",
            "selected_apis": [],
            "messages": [],
        },
        timeout=180,
    )
    assert case_resp.status_code == 200
    case_data = case_resp.json()
    assert case_data.get("status") == "success"
    generated_case = case_data.get("case") or {}
    assert generated_case.get("projectId") == project_id
    assert generated_case.get("type") == "API"
    steps = generated_case.get("caseApis") or []
    assert isinstance(steps, list)
    assert len(steps) >= 2
    for step in steps:
        assert str(step.get("apiId") or "").strip()


def test_backend_ai_endpoints(runtime_context: Dict[str, str]):
    token = runtime_context["token"]
    project_id = runtime_context["project_id"]
    headers = {"token": token}
    list_resp = requests.get(
        f"{BACKEND_BASE_URL}/autotest/ai/knowledge",
        params={"projectId": project_id},
        headers=headers,
        timeout=30,
    )
    assert list_resp.status_code == 200
    assert isinstance(_unwrap_backend_data(list_resp.json()), list)
    doc_name = f"it-kb-{uuid.uuid4().hex[:8]}"
    save_resp = requests.post(
        f"{BACKEND_BASE_URL}/autotest/ai/knowledge",
        headers=headers,
        json={
            "projectId": project_id,
            "parentId": "0",
            "name": doc_name,
            "content": "自动化测试登录用例说明",
            "docType": "manual",
            "sourceType": "manual",
        },
        timeout=30,
    )
    assert save_resp.status_code == 200
    doc_id = str(_unwrap_backend_data(save_resp.json()) or "")
    assert doc_id
    detail_resp = requests.get(
        f"{BACKEND_BASE_URL}/autotest/ai/knowledge/{doc_id}",
        params={"projectId": project_id},
        headers=headers,
        timeout=30,
    )
    assert detail_resp.status_code == 200
    detail_data = _unwrap_backend_data(detail_resp.json()) or {}
    assert str(detail_data.get("id") or "") == doc_id
    index_resp = requests.post(
        f"{BACKEND_BASE_URL}/autotest/ai/knowledge/index/{doc_id}",
        params={"projectId": project_id},
        headers=headers,
        timeout=60,
    )
    assert index_resp.status_code == 200
    schema_resp = requests.get(
        f"{BACKEND_BASE_URL}/autotest/ai/schema/case",
        params={"projectId": project_id},
        headers=headers,
        timeout=30,
    )
    assert schema_resp.status_code == 200
    schema_data = _unwrap_backend_data(schema_resp.json()) or {}
    assert isinstance(schema_data, dict)
    api_list_resp = requests.get(
        f"{BACKEND_BASE_URL}/autotest/ai/agent/api-list/{project_id}",
        headers=headers,
        timeout=30,
    )
    assert api_list_resp.status_code == 200
    case_resp = requests.post(
        f"{BACKEND_BASE_URL}/autotest/ai/generate-case",
        headers=headers,
        json={
            "projectId": project_id,
            "userRequirement": "生成登录接口正向和异常用例",
            "selectedApis": [],
            "messages": [],
        },
        timeout=180,
    )
    assert case_resp.status_code == 200
    case_data = _unwrap_backend_data(case_resp.json()) or {}
    assert case_data.get("status") == "success"
    stream_resp = requests.post(
        f"{BACKEND_BASE_URL}/autotest/ai/chat/stream",
        headers=headers,
        json={
            "projectId": project_id,
            "message": "请生成登录流程测试用例",
            "useRag": True,
            "messages": [],
        },
        stream=True,
        timeout=120,
    )
    assert stream_resp.status_code == 200
    got_case_or_content = False
    got_end = False
    for event in _iter_sse_events(stream_resp):
        event_type = str(event.get("type") or "")
        if event_type in {"content", "case"}:
            got_case_or_content = True
        if event_type == "error":
            pytest.fail(str(event.get("message") or "SSE返回错误事件"))
        if event_type == "end":
            got_end = True
            break
    assert got_case_or_content
    assert got_end
    delete_resp = requests.delete(
        f"{BACKEND_BASE_URL}/autotest/ai/knowledge/{doc_id}",
        params={"projectId": project_id},
        headers=headers,
        timeout=30,
    )
    assert delete_resp.status_code == 200
