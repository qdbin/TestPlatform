"""
LLM服务模块 - LangChain 1.x LCEL版本

职责：
    1. 封装 LangChain ChatOpenAI 的多provider调用
    2. 支持普通对话/JSON对话/流式对话三种模式
    3. 支持 deepseek/qwen/openai 等多模型切换
    4. 集成 LangSmith 全链路追踪
    5. 使用LCEL (LangChain Expression Language) 构建可组合链路

核心类：
    - LLMService: LLM统一服务类

主要方法：
    - chat(): 普通同步对话 (invoke)
    - achat(): 异步普通对话 (ainvoke)
    - chat_json(): JSON模式对话
    - chat_with_stream(): 流式对话 (astream)
    - chat_structured(): 结构化输出

LCEL链构建示例：
    chain = prompt | llm | output_parser
    result = chain.invoke(inputs)
"""

from typing import Optional, Dict, Any, List, AsyncIterator, Iterator, Type, TypeVar, Union
import os

os.environ.pop("OPENAI_PROXY", None)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnableSerializable
from langsmith import trace

from app.config import config
from app.observability import app_logger

StructuredModelT = TypeVar("StructuredModelT", bound=Any)


class LLMService:
    """
    LLM服务类 - LangChain 1.x LCEL实现

    职责：
        - 统一封装 LangChain ChatOpenAI 的调用
        - 支持多provider切换（deepseek/qwen/openai）
        - 提供普通/JSON/流式/结构化四种对话模式
        - 全链路LangSmith追踪

    设计模式：
        - 延迟初始化：LLM实例在首次使用时创建
        - 单例模式：全局共享一个LLMService实例
    """

    def __init__(self):
        self._llm: Optional[ChatOpenAI] = None
        self._streaming_llm: Optional[ChatOpenAI] = None
        self._provider = config.llm_provider.lower()
        self._json_llm: Optional[ChatOpenAI] = None

    def _create_llm(self, streaming: bool = False) -> ChatOpenAI:
        """
        创建底层 LangChain ChatOpenAI 客户端

        @param streaming: 是否启用流式模式
        @return: ChatOpenAI实例

        支持的Provider：
            - deepseek: DeepSeek API
            - openai: OpenAI API
            - qwen: 阿里云通义千问
        """
        common_params = {
            "model": config.llm_model,
            "temperature": config.llm_temperature,
            "max_tokens": config.llm_max_tokens,
            "streaming": streaming,
        }

        if self._provider in ("deepseek", "openai"):
            return ChatOpenAI(
                **common_params,
                api_key=config.llm_api_key,
                base_url=config.llm_base_url,
            )
        elif self._provider == "qwen":
            return ChatOpenAI(
                **common_params,
                api_key=config.llm_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
        else:
            raise ValueError(f"Unknown LLM provider: {self._provider}")

    def _get_llm(self) -> Optional[ChatOpenAI]:
        """延迟获取LLM实例（非流式）"""
        if self._llm is None:
            try:
                self._llm = self._create_llm(streaming=False)
            except Exception as e:
                app_logger.error("LLM初始化失败: {}", str(e))
                return None
        return self._llm

    def _get_streaming_llm(self) -> Optional[ChatOpenAI]:
        """延迟获取流式LLM实例"""
        if self._streaming_llm is None:
            try:
                self._streaming_llm = self._create_llm(streaming=True)
            except Exception as e:
                app_logger.error("流式LLM初始化失败: {}", str(e))
                return None
        return self._streaming_llm

    def _get_json_llm(self) -> Optional[ChatOpenAI]:
        """获取JSON模式LLM（绑定response_format）"""
        if self._json_llm is None:
            base_llm = self._get_llm()
            if base_llm:
                self._json_llm = base_llm.bind(response_format={"type": "json_object"})
        return self._json_llm

    def get_chat_model(self) -> Optional[ChatOpenAI]:
        """获取原始ChatModel（用于LCEL链构建）"""
        return self._get_llm()

    def _build_messages(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> List[BaseMessage]:
        """
        转换消息格式为标准LangChain消息

        @param messages: 原始消息列表 [{"role": "user", "content": "..."}, ...]
        @param system_prompt: 系统提示词（可选）
        @return: LangChain消息列表

        角色映射：
            - user -> HumanMessage
            - assistant -> AIMessage
            - system -> SystemMessage
        """
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
        return langchain_messages

    def chat(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> str:
        """
        普通同步对话 - 使用LCEL链

        LCEL链结构：
            messages -> LLM -> StrOutputParser -> result

        @param messages: 对话消息列表
        @param system_prompt: 系统提示词
        @return: AI回复文本
        """
        llm = self._get_llm()
        if llm is None:
            return "AI服务未配置，请检查API Key"

        langchain_messages = self._build_messages(messages, system_prompt)

        # 使用LCEL链: 消息 -> LLM -> 字符串输出
        chain = llm | StrOutputParser()

        with trace(name="llm_chat", run_type="llm", inputs={"messages": messages}):
            try:
                return chain.invoke(langchain_messages)
            except Exception as e:
                app_logger.error("LLM对话失败: {}", str(e))
                return f"AI服务调用失败: {str(e)}"

    async def achat(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> str:
        """
        异步普通对话 - 使用LCEL链

        @param messages: 对话消息列表
        @param system_prompt: 系统提示词
        @return: AI回复文本
        """
        llm = self._get_llm()
        if llm is None:
            return "AI服务未配置，请检查API Key"

        langchain_messages = self._build_messages(messages, system_prompt)
        chain = llm | StrOutputParser()

        with trace(name="llm_achat", run_type="llm", inputs={"messages": messages}):
            try:
                return await chain.ainvoke(langchain_messages)
            except Exception as e:
                app_logger.error("异步LLM对话失败: {}", str(e))
                return f"AI服务调用失败: {str(e)}"

    def chat_json(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> str:
        """
        JSON模式对话 - 强制返回JSON格式

        实现原理：
            - 使用 response_format={"type": "json_object"} 强制JSON输出
            - 适用于结构化数据生成（如用例生成）

        @param messages: 对话消息列表
        @param system_prompt: 系统提示词
        @return: JSON字符串
        """
        llm = self._get_json_llm()
        if llm is None:
            return "{}"

        langchain_messages = self._build_messages(messages, system_prompt)

        with trace(name="llm_chat_json", run_type="llm", inputs={"messages": messages}):
            try:
                response = llm.invoke(langchain_messages)
                return response.content if response and response.content else "{}"
            except Exception as e:
                app_logger.error("JSON模式对话失败: {}", str(e))
                # 降级为普通对话
                return self.chat(messages, system_prompt)

    async def achat_json(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> str:
        """异步JSON模式对话"""
        llm = self._get_json_llm()
        if llm is None:
            return "{}"

        langchain_messages = self._build_messages(messages, system_prompt)

        with trace(name="llm_achat_json", run_type="llm", inputs={"messages": messages}):
            try:
                response = await llm.ainvoke(langchain_messages)
                return response.content if response and response.content else "{}"
            except Exception as e:
                app_logger.error("异步JSON模式对话失败: {}", str(e))
                return await self.achat(messages, system_prompt)

    def chat_with_stream(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> Iterator[str]:
        """
        流式对话生成 - 使用LCEL的stream

        @param messages: 对话消息列表
        @param system_prompt: 系统提示词
        @return: 文本片段生成器

        使用示例：
            for chunk in llm_service.chat_with_stream(messages):
                print(chunk, end="", flush=True)
        """
        llm = self._get_streaming_llm()
        if llm is None:
            yield "[错误: AI服务未配置]"
            return

        langchain_messages = self._build_messages(messages, system_prompt)
        chain = llm | StrOutputParser()

        with trace(name="llm_stream", run_type="llm", inputs={"messages": messages}):
            try:
                for chunk in chain.stream(langchain_messages):
                    if chunk:
                        yield chunk
            except Exception as e:
                app_logger.error("流式生成错误: {}", str(e))
                yield f"[错误: {str(e)}]"

    async def achat_with_stream(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        异步流式对话生成 - 真正的异步流式

        @param messages: 对话消息列表
        @param system_prompt: 系统提示词
        @return: 文本片段异步生成器
        """
        llm = self._get_streaming_llm()
        if llm is None:
            yield "[错误: AI服务未配置]"
            return

        langchain_messages = self._build_messages(messages, system_prompt)
        chain = llm | StrOutputParser()

        with trace(name="llm_astream", run_type="llm", inputs={"messages": messages}):
            try:
                async for chunk in chain.astream(langchain_messages):
                    if chunk:
                        yield chunk
            except Exception as e:
                app_logger.error("异步流式生成错误: {}", str(e))
                yield f"[错误: {str(e)}]"

    def chat_structured(
        self,
        messages: List[Dict[str, str]],
        output_model: Type[StructuredModelT],
        system_prompt: Optional[str] = None,
    ) -> Optional[StructuredModelT]:
        """
        结构化输出 - 使用with_structured_output

        实现原理：
            - 使用 llm.with_structured_output(Model) 绑定输出结构
            - LLM自动返回符合Pydantic模型的结构化数据

        @param messages: 对话消息列表
        @param output_model: Pydantic模型类
        @param system_prompt: 系统提示词
        @return: 结构化输出对象

        使用示例：
            class MyOutput(BaseModel):
                name: str
                age: int

            result = llm_service.chat_structured(messages, MyOutput)
        """
        llm = self._get_llm()
        if llm is None:
            return None

        langchain_messages = self._build_messages(messages, system_prompt)

        with trace(name="llm_structured", run_type="llm", inputs={"messages": messages}):
            try:
                structured_llm = llm.with_structured_output(output_model)
                return structured_llm.invoke(langchain_messages)
            except Exception as exc:
                app_logger.warning("structured_output_failed error={}", str(exc))
                return None

    async def achat_structured(
        self,
        messages: List[Dict[str, str]],
        output_model: Type[StructuredModelT],
        system_prompt: Optional[str] = None,
    ) -> Optional[StructuredModelT]:
        """异步结构化输出"""
        llm = self._get_llm()
        if llm is None:
            return None

        langchain_messages = self._build_messages(messages, system_prompt)

        with trace(name="llm_astructured", run_type="llm", inputs={"messages": messages}):
            try:
                structured_llm = llm.with_structured_output(output_model)
                return await structured_llm.ainvoke(langchain_messages)
            except Exception as exc:
                app_logger.warning("async_structured_output_failed error={}", str(exc))
                return None

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """简单prompt生成"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, system_prompt)

    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """异步简单prompt生成"""
        messages = [{"role": "user", "content": prompt}]
        return await self.achat(messages, system_prompt)


# 全局LLM服务实例
llm_service = LLMService()


if __name__ == "__main__":
    """LLM服务调试"""
    import asyncio

    print("=" * 60)
    print("LLM服务调试 - LangChain 1.x LCEL")
    print("=" * 60)

    # 1. 普通对话测试
    print("\n1. 普通对话测试:")
    messages = [{"role": "user", "content": "你好，请用一句话介绍自己"}]
    response = llm_service.chat(messages)
    print(f"   响应: {response[:100]}...")

    # 2. JSON模式测试
    print("\n2. JSON模式测试:")
    json_messages = [
        {"role": "user", "content": '请用JSON格式返回 {"name": "张三", "age": 25}'}
    ]
    json_response = llm_service.chat_json(json_messages)
    print(f"   响应: {json_response[:100]}...")

    # 3. 流式输出测试
    print("\n3. 流式输出测试:")
    stream_messages = [{"role": "user", "content": "用一句话介绍接口测试"}]
    print("   流式响应: ", end="")
    for chunk in llm_service.chat_with_stream(stream_messages):
        print(chunk, end="", flush=True)
    print("\n")

    # 4. 异步测试
    async def test_async():
        print("\n4. 异步对话测试:")
        response = await llm_service.achat([{"role": "user", "content": "你好"}])
        print(f"   异步响应: {response[:50]}...")

    asyncio.run(test_async())

    print("=" * 60)
    print("调试完成")
    print("=" * 60)
