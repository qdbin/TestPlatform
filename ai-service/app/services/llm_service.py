"""
LLM服务模块
负责与大语言模型交互，支持多种provider切换
"""
from typing import Optional, Dict, Any, List
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.config import config


class LLMService:
    """LLM服务类"""
    
    def __init__(self):
        self._llm = None
        self._init_llm()
    
    def _init_llm(self) -> None:
        """初始化LLM客户端"""
        provider = config.llm_provider.lower()
        
        if provider == "deepseek" or provider == "openai":
            self._llm = ChatOpenAI(
                model=config.llm_model,
                api_key=config.llm_api_key,
                base_url=config.llm_base_url,
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens,
                streaming=False
            )
        elif provider == "anthropic":
            # TODO: 支持Claude
            raise NotImplementedError("Anthropic (Claude) not yet supported")
        elif provider == "qwen":
            self._llm = ChatOpenAI(
                model=config.llm_model,
                api_key=config.llm_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=config.llm_temperature,
                max_tokens=config.llm_max_tokens,
                streaming=False
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        """
        对话生成
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词
            
        Returns:
            AI回复内容
        """
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
        
        response = self._llm.invoke(langchain_messages)
        return response.content
    
    def chat_with_stream(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None):
        """
        流式对话生成
        
        Args:
            messages: 消息列表
            system_prompt: 系统提示词
            
        Returns:
            生成器，逐字返回
        """
        # 切换到流式模式
        self._llm.streaming = True
        
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
        
        # 切换回非流式模式
        self._llm.streaming = False
        
        return self._llm.stream(langchain_messages)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        简单prompt生成
        
        Args:
            prompt: 用户prompt
            system_prompt: 系统提示词
            
        Returns:
            生成内容
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, system_prompt)


# 全局LLM服务实例
llm_service = LLMService()
