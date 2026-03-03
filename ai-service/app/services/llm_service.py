"""
LLM服务模块
负责与大语言模型交互，支持多种provider切换
"""

from typing import Optional, Dict, Any, List
import os
os.environ.pop("OPENAI_PROXY", None)
try:
    from langchain_openai import ChatOpenAI
except Exception:
    from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.config import config


class LLMService:
    """LLM服务类"""

    def __init__(self):
        self._llm = None
        self._provider = config.llm_provider.lower()

    def _get_llm(self):
        """延迟获取LLM"""
        if self._llm is None:
            try:
                if self._provider == "deepseek" or self._provider == "openai":
                    self._llm = ChatOpenAI(
                        model=config.llm_model,
                        openai_api_key=config.llm_api_key,
                        base_url=config.llm_base_url,
                        temperature=config.llm_temperature,
                        max_tokens=config.llm_max_tokens,
                        streaming=False,
                    )
                elif self._provider == "qwen":
                    self._llm = ChatOpenAI(
                        model=config.llm_model,
                        openai_api_key=config.llm_api_key,
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                        temperature=config.llm_temperature,
                        max_tokens=config.llm_max_tokens,
                        streaming=False,
                    )
                else:
                    raise ValueError(f"Unknown LLM provider: {self._provider}")
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
    ):
        """流式对话生成"""
        llm = self._get_llm()
        if llm is None:
            return iter([])

        llm.streaming = True

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

        return llm.stream(langchain_messages)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """简单prompt生成"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, system_prompt)


llm_service = LLMService()
