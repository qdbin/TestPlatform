import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import app.services.agent_service as agent_service_module
from app.services.agent_service import AgentService, _is_case_request

TEST_PROJECT_ID = "unit-test-agent-project"
TEST_TOKEN = "unit-test-token"


def _collect_async_events(stream):
    async def _run():
        result = []
        async for event in stream:
            result.append(event)
        return result
    return asyncio.run(_run())


def test_agent_service_has_required_methods():
    service = AgentService()
    assert hasattr(service, "generate_case")
    assert hasattr(service, "chat")
    assert hasattr(service, "stream_chat")


def test_is_case_request_positive():
    assert _is_case_request("请帮我生成一个登录测试用例") is True
    assert _is_case_request("设计支付流程测试场景并输出case") is True


def test_is_case_request_negative():
    assert _is_case_request("你好") is False
    assert _is_case_request("登录接口需要什么参数") is False


def test_chat_plain_mode(monkeypatch):
    service = AgentService()
    monkeypatch.setattr(agent_service_module.llm_service, "chat", lambda messages, system_prompt=None: "plain-reply")
    result = service.chat(
        project_id=TEST_PROJECT_ID,
        token=TEST_TOKEN,
        message="你好",
        use_rag=False,
        messages=[],
    )
    assert result.get("reply") == "plain-reply"


def test_chat_case_mode(monkeypatch):
    service = AgentService()
    monkeypatch.setattr(
        service,
        "generate_case",
        lambda project_id, token, user_requirement, selected_apis=None, messages=None, user_id="": {
            "status": "success",
            "case": {"projectId": project_id, "type": "API", "caseApis": [{"apiId": "a1"}, {"apiId": "a2"}]},
        },
    )
    result = service.chat(
        project_id=TEST_PROJECT_ID,
        token=TEST_TOKEN,
        message="帮我生成登录测试用例",
        use_rag=True,
        messages=[],
    )
    assert "case" in result
    assert result["case"]["projectId"] == TEST_PROJECT_ID


def test_stream_chat_plain_mode(monkeypatch):
    service = AgentService()

    async def fake_stream(messages, system_prompt=None):
        yield "A"
        yield "B"

    monkeypatch.setattr(agent_service_module.llm_service, "achat_with_stream", fake_stream)
    events = _collect_async_events(
        service.stream_chat(
            project_id=TEST_PROJECT_ID,
            token=TEST_TOKEN,
            message="普通问答",
            use_rag=False,
            messages=[],
        )
    )
    assert events[0]["type"] == "content"
    assert events[-1]["type"] == "end"


def test_stream_chat_case_mode(monkeypatch):
    service = AgentService()
    monkeypatch.setattr(
        service,
        "generate_case",
        lambda project_id, token, user_requirement, selected_apis=None, messages=None, user_id="": {
            "status": "success",
            "case": {"projectId": project_id, "type": "API", "caseApis": [{"apiId": "x1"}, {"apiId": "x2"}]},
            "existing_api_ids": ["x1", "x2"],
        },
    )
    events = _collect_async_events(
        service.stream_chat(
            project_id=TEST_PROJECT_ID,
            token=TEST_TOKEN,
            message="请生成用例",
            use_rag=True,
            messages=[],
        )
    )
    event_types = [evt.get("type") for evt in events]
    assert "case" in event_types
    assert event_types[-1] == "end"
