"""
LangChain回调处理器。
"""

from __future__ import annotations

from colorama import Fore, Style, init
from rich.console import Console
from langchain.callbacks.base import BaseCallbackHandler

from app.observability.logger import app_logger

init(autoreset=True)
console = Console()


class ConsoleLangChainCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        app_logger.info("llm_start model={} prompt_count={}", serialized.get("name"), len(prompts))
        console.print(Fore.CYAN + f"[LLM START] prompts={len(prompts)}" + Style.RESET_ALL)

    def on_llm_end(self, response, **kwargs):
        generations = getattr(response, "generations", [])
        app_logger.info("llm_end generations={}", len(generations))
        console.print(Fore.GREEN + f"[LLM END] generations={len(generations)}" + Style.RESET_ALL)

    def on_llm_error(self, error, **kwargs):
        app_logger.error("llm_error {}", str(error))
        console.print(Fore.RED + f"[LLM ERROR] {error}" + Style.RESET_ALL)

    def on_tool_start(self, serialized, input_str, **kwargs):
        app_logger.info("tool_start name={} input={}", serialized.get("name"), input_str[:120])
        console.print(Fore.YELLOW + f"[TOOL START] {serialized.get('name')}" + Style.RESET_ALL)

    def on_tool_end(self, output, **kwargs):
        app_logger.info("tool_end output={}", str(output)[:120])
        console.print(Fore.MAGENTA + "[TOOL END]" + Style.RESET_ALL)


langchain_console_callback = ConsoleLangChainCallbackHandler()
