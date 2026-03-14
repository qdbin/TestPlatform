"""
LLM服务模块

职责：
    1. 封装 LangChain ChatOpenAI 的多provider调用
    2. 支持普通对话/JSON对话/流式对话三种模式
    3. 支持 deepseek/qwen/openai 等多模型切换

核心类：
    - LLMService: LLM统一服务类

主要方法：
    - chat(): 普通同步对话
    - chat_json(): JSON模式对话
    - chat_with_stream(): 流式对话
"""

from typing import Optional, Dict, Any, List, Iterator, Type, TypeVar
import os

os.environ.pop("OPENAI_PROXY", None)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from pydantic import BaseModel
from app.config import config
from app.observability import app_logger, langchain_console_callback

StructuredModelT = TypeVar("StructuredModelT", bound=BaseModel)


class LLMService:
    """
    LLM服务类

    职责：
        - 统一封装 LangChain ChatOpenAI 的调用
        - 支持多provider切换（deepseek/qwen/openai）
        - 提供普通/JSON/流式三种对话模式
    """

    def __init__(self):
        self._llm = None
        self._provider = config.llm_provider.lower()

    def _create_llm(self, streaming: bool):
        """
        创建底层 LangChain ChatOpenAI 客户端

        实现步骤：
            1. 根据 provider 选择对应配置
            2. 设置 base_url、model、temperature 等参数
            3. 返回 ChatOpenAI 实例

        @param streaming: 是否启用流式输出
        @return: ChatOpenAI 实例
        """
        # DeepSeek/OpenAI 兼容模式
        if self._provider == "deepseek" or self._provider == "openai":
            return ChatOpenAI(
                model=config.llm_model,
                openai_api_key=config.llm_api_key,
                base_url=config.llm_base_url,
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens,
                streaming=streaming,
                callbacks=[langchain_console_callback],
            )
        # 阿里云 Qwen 模式
        if self._provider == "qwen":
            return ChatOpenAI(
                model=config.llm_model,
                openai_api_key=config.llm_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens,
                streaming=streaming,
                callbacks=[langchain_console_callback],
            )
        raise ValueError(f"Unknown LLM provider: {self._provider}")

    def _get_llm(self):
        """
        延迟获取LLM实例

        使用单例模式缓存LLM实例，避免重复创建
        """
        # 检查缓存是否有效
        if self._llm is None:
            try:
                # 创建LLM实例并缓存
                self._llm = self._create_llm(False)
            except Exception as e:
                app_logger.error("LLM初始化失败: {}", str(e))
                return None
        return self._llm

    def get_chat_model(self):
        return self._get_llm()

    def _build_langchain_messages(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str]
    ) -> List[BaseMessage]:
        """
        转换消息格式

        将前端消息格式转换为 LangChain 所需格式：
            - user -> HumanMessage
            - assistant -> AIMessage
            - system -> SystemMessage

        @param messages: 前端消息列表
        @param system_prompt: 系统提示词
        @return: LangChain 消息列表
        """
        # 初始化消息列表
        langchain_messages: List[BaseMessage] = []
        # 添加系统提示词
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        # 遍历转换每条消息
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # 根据角色类型转换
            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif role == "system":
                langchain_messages.append(SystemMessage(content=content))
        return langchain_messages

    def chat(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> str:
        """
        普通同步对话

        @param messages: 历史消息列表
        @param system_prompt: 系统提示词
        @return: 完整回答文本
        """
        # 获取LLM实例
        llm = self._get_llm()
        # 检查LLM是否可用
        if llm is None:
            return "AI服务未配置，请检查API Key"
        # 转换消息格式
        langchain_messages = self._build_langchain_messages(messages, system_prompt)
        # 调用LLM获取回复
        response = llm.invoke(langchain_messages)
        return response.content

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        JSON模式对话

        实现策略：
            1. 优先使用 response_format={"type":"json_object"} 约束模型输出JSON
            2. 模型不支持时回退到普通 invoke

        @param messages: 历史消息列表
        @param system_prompt: 系统提示词
        @return: JSON格式回答文本
        """
        # 获取LLM实例
        llm = self._get_llm()
        if llm is None:
            return "{}"
        # 转换消息格式
        langchain_messages = self._build_langchain_messages(messages, system_prompt)
        # 尝试使用JSON模式
        try:
            response = llm.bind(response_format={"type": "json_object"}).invoke(
                langchain_messages
            )
            return response.content if response and response.content else "{}"
        except Exception:
            # 回退到普通模式
            response = llm.invoke(langchain_messages)
            return response.content if response and response.content else "{}"

    def chat_with_stream(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> Iterator[str]:
        """
        流式对话生成

        与 chat() 的区别：
            - 通过 llm.stream() 按增量块返回
            - 供 SSE 链路直通转发

        @param messages: 历史消息列表
        @param system_prompt: 系统提示词
        @return: 增量文本生成器
        """
        # 创建支持流式的LLM实例
        try:
            llm = self._create_llm(True)
        except Exception as e:
            app_logger.error("创建流式LLM失败: {}", str(e))
            return iter([])
        # 转换消息格式
        langchain_messages = self._build_langchain_messages(messages, system_prompt)

        def stream_generator():
            # 遍历流式响应块
            try:
                for chunk in llm.stream(langchain_messages):
                    if hasattr(chunk, "content") and chunk.content:
                        yield chunk.content
            except Exception as e:
                app_logger.error("流式生成错误: {}", str(e))
                yield f"[错误: {str(e)}]"

        return stream_generator()

    def chat_structured(
        self,
        messages: List[Dict[str, str]],
        output_model: Type[StructuredModelT],
        system_prompt: Optional[str] = None,
    ) -> Optional[StructuredModelT]:
        llm = self._get_llm()
        if llm is None:
            return None
        langchain_messages = self._build_langchain_messages(messages, system_prompt)
        try:
            structured_llm = llm.with_structured_output(output_model)
            return structured_llm.invoke(langchain_messages)
        except Exception as exc:
            app_logger.warning("structured_output_failed error={}", str(exc))
            return None

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        简单 prompt 生成

        内部调用 chat() 方法，适用于一次性生成场景

        @param prompt: 用户 prompt
        @param system_prompt: 系统提示词
        @return: 生成文本
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, system_prompt)


llm_service = LLMService()


if __name__ == "__main__":
    """
    LLM服务调试代码

    调试说明：
        1. 测试普通对话
        2. 测试JSON模式
        3. 测试流式输出

    注意：需要正确配置 LLM API Key
    """
    print("=" * 60)
    print("LLM服务调试")
    print("=" * 60)

    # 测试1：普通对话
    print("\n1. 普通对话测试:")
    messages = [{"role": "user", "content": "你好，请介绍一下你自己"}]
    response = llm_service.chat(messages)
    print(f"   响应: {response[:100]}...")

    # 测试2：JSON模式
    print("\n2. JSON模式测试:")
    json_messages = [
        {"role": "user", "content": "请用JSON格式返回 {'name': '张三', 'age': 25}"}
    ]
    json_response = llm_service.chat_json(json_messages)
    print(f"   响应: {json_response[:100]}...")

    # 测试3：流式输出
    print("\n3. 流式输出测试:")
    stream_messages = [{"role": "user", "content": "用一句话介绍接口测试"}]
    print("   流式响应: ", end="")
    for chunk in llm_service.chat_with_stream(stream_messages):
        print(chunk, end="", flush=True)
    print("\n")

    print("=" * 60)
    print("调试完成")
    print("=" * 60)
