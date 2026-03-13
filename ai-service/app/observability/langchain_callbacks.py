"""
LangChain回调处理器

核心功能：
    - LLM调用开始/结束/错误回调
    - Agent工具调用开始/结束回调
    - 彩色控制台输出 + 日志记录

使用示例：
    from langchain.chat_models import ChatOpenAI
    llm = ChatOpenAI(callbacks=[langchain_console_callback])
"""

from __future__ import annotations

from colorama import Fore, Style, init
from rich.console import Console
from langchain.callbacks.base import BaseCallbackHandler

from app.observability.logger import app_logger

init(autoreset=True)
console = Console()


class ConsoleLangChainCallbackHandler(BaseCallbackHandler):
    """
    LangChain控制台回调处理器
    
    职责：
        - 监听LLM调用生命周期事件
        - 监听Agent工具调用事件
        - 输出彩色日志到控制台
        - 记录结构化日志到文件
    """

    def on_llm_start(self, serialized, prompts, **kwargs):
        """
        LLM调用开始回调
        
        @param serialized: 序列化后的LLM配置
        @param prompts: 提示词列表
        """
        app_logger.info("llm_start model={} prompt_count={}", serialized.get("name"), len(prompts))
        console.print(Fore.CYAN + f"[LLM START] prompts={len(prompts)}" + Style.RESET_ALL)

    def on_llm_end(self, response, **kwargs):
        """
        LLM调用结束回调
        
        @param response: LLM响应
        """
        generations = getattr(response, "generations", [])
        app_logger.info("llm_end generations={}", len(generations))
        console.print(Fore.GREEN + f"[LLM END] generations={len(generations)}" + Style.RESET_ALL)

    def on_llm_error(self, error, **kwargs):
        """
        LLM调用错误回调
        
        @param error: 异常信息
        """
        app_logger.error("llm_error {}", str(error))
        console.print(Fore.RED + f"[LLM ERROR] {error}" + Style.RESET_ALL)

    def on_tool_start(self, serialized, input_str, **kwargs):
        """
        工具调用开始回调
        
        @param serialized: 序列化后的工具配置
        @param input_str: 工具输入
        """
        app_logger.info("tool_start name={} input={}", serialized.get("name"), input_str[:120])
        console.print(Fore.YELLOW + f"[TOOL START] {serialized.get('name')}" + Style.RESET_ALL)

    def on_tool_end(self, output, **kwargs):
        """
        工具调用结束回调
        
        @param output: 工具输出
        """
        app_logger.info("tool_end output={}", str(output)[:120])
        console.print(Fore.MAGENTA + "[TOOL END]" + Style.RESET_ALL)


langchain_console_callback = ConsoleLangChainCallbackHandler()


if __name__ == "__main__":
    """
    LangChain回调处理器调试代码
    
    调试说明：
        1. 测试回调处理器初始化
        2. 模拟LLM调用事件
    """
    print("=" * 60)
    print("LangChain回调处理器调试")
    print("=" * 60)
    
    # 测试回调处理器
    print("\n1. 回调处理器测试:")
    handler = ConsoleLangChainCallbackHandler()
    print(f"   回调处理器: {handler}")
    
    # 模拟LLM事件
    print("\n2. 模拟LLM事件:")
    handler.on_llm_start({"name": "test-model"}, ["test prompt"])
    handler.on_llm_end(type('Response', (), {'generations': [[]]})())
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
