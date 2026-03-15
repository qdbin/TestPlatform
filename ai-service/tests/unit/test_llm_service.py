import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.llm_service import LLMService


def test_llm_service_has_required_methods():
    service = LLMService()
    assert hasattr(service, "chat")
    assert hasattr(service, "achat")
    assert hasattr(service, "chat_json")
    assert hasattr(service, "achat_with_stream")


def test_build_messages():
    service = LLMService()
    messages = service._build_messages(
        [{"role": "user", "content": "u"}, {"role": "assistant", "content": "a"}],
        system_prompt="s",
    )
    assert len(messages) == 3


def test_chat_fallback_when_llm_unavailable(monkeypatch):
    service = LLMService()
    monkeypatch.setattr(service, "_get_llm", lambda: None)
    text = service.chat([{"role": "user", "content": "hi"}])
    assert "AI服务未配置" in text


def test_chat_json_fallback_when_llm_unavailable(monkeypatch):
    service = LLMService()
    monkeypatch.setattr(service, "_get_json_llm", lambda: None)
    text = service.chat_json([{"role": "user", "content": "hi"}])
    assert text == "{}"


def test_chat_stream_fallback_when_llm_unavailable(monkeypatch):
    service = LLMService()
    monkeypatch.setattr(service, "_get_streaming_llm", lambda: None)
    chunks = list(service.chat_with_stream([{"role": "user", "content": "hi"}]))
    assert chunks
    assert "错误" in chunks[0]


def test_achat_fallback_when_llm_unavailable(monkeypatch):
    service = LLMService()
    monkeypatch.setattr(service, "_get_llm", lambda: None)
    text = asyncio.run(service.achat([{"role": "user", "content": "hi"}]))
    assert "AI服务未配置" in text


def test_achat_stream_fallback_when_llm_unavailable(monkeypatch):
    service = LLMService()
    monkeypatch.setattr(service, "_get_streaming_llm", lambda: None)

    async def collect():
        result = []
        async for item in service.achat_with_stream([{"role": "user", "content": "hi"}]):
            result.append(item)
        return result

    chunks = asyncio.run(collect())
    assert chunks
    assert "错误" in chunks[0]
