import os

from app.config import config


def setup_langsmith() -> None:
    if not config.langsmith_tracing:
        return
    if config.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = config.langsmith_api_key
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = config.langsmith_project
