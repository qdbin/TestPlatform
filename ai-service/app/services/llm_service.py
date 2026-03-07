"""
LLM服务模块
负责与大语言模型交互，支持多种provider切换
"""

from typing import Optional, Dict, Any, List, Iterator
import os

os.environ.pop("OPENAI_PROXY", None)
try:
    from langchain_openai import ChatOpenAI
except Exception:
    from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage
from app.config import config


class LLMService:
    """LLM服务类"""

    def __init__(self):
        self._llm = None
        self._provider = config.llm_provider.lower()

    def _create_llm(self, streaming: bool):
        if self._provider == "deepseek" or self._provider == "openai":
            return ChatOpenAI(
                model=config.llm_model,
                openai_api_key=config.llm_api_key,
                base_url=config.llm_base_url,
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens,
                streaming=streaming,
            )
        if self._provider == "qwen":
            return ChatOpenAI(
                model=config.llm_model,
                openai_api_key=config.llm_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens,
                streaming=streaming,
            )
        raise ValueError(f"Unknown LLM provider: {self._provider}")

    def _get_llm(self):
        """延迟获取LLM"""
        if self._llm is None:
            try:
                self._llm = self._create_llm(False)
            except Exception as e:
                print(f"LLM初始化失败: {e}")
                return None
        return self._llm

    def chat(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> str:
        """对话生成"""
        llm = self._get_llm()
        if llm is None:
            return "AI服务未配置，请检查API Key"

        langchain_messages = []

        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif role == "system":
                langchain_messages.append(SystemMessage(content=content))

        response = llm.invoke(langchain_messages)
        return response.content

    def chat_with_stream(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> Iterator[str]:
        """流式对话生成 - 返回字符串迭代器"""
        try:
            llm = self._create_llm(True)
        except Exception as e:
            print(f"创建流式LLM失败: {e}")
            return iter([])

        langchain_messages: List[BaseMessage] = []

        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif role == "system":
                langchain_messages.append(SystemMessage(content=content))

        def stream_generator():
            try:
                for chunk in llm.stream(langchain_messages):
                    if hasattr(chunk, "content") and chunk.content:
                        yield chunk.content
            except Exception as e:
                print(f"流式生成错误: {e}")
                yield f"[错误: {str(e)}]"

        return stream_generator()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """简单prompt生成"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, system_prompt)


llm_service = LLMService()
