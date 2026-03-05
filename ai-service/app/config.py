"""
配置管理模块
负责加载和管理AI服务的配置信息
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """配置管理类"""

    _instance: Optional["Config"] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """加载配置文件"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        self._load_env_overrides()

    def _load_env_overrides(self) -> None:
        """环境变量覆盖"""
        # LLM配置环境变量
        if os.getenv("DEEPSEEK_API_KEY"):
            if "llm" not in self._config:
                self._config["llm"] = {}
            self._config["llm"]["api_key"] = os.getenv("DEEPSEEK_API_KEY")

        if os.getenv("OPENAI_API_KEY"):
            if "llm" not in self._config:
                self._config["llm"] = {}
            self._config["llm"]["api_key"] = os.getenv("OPENAI_API_KEY")

        if os.getenv("PLATFORM_BASE_URL"):
            if "platform" not in self._config:
                self._config["platform"] = {}
            self._config["platform"]["base_url"] = os.getenv("PLATFORM_BASE_URL")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的键"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @property
    def llm_provider(self) -> str:
        return self.get("llm.provider", "deepseek")

    @property
    def llm_model(self) -> str:
        return self.get("llm.model", "deepseek-v3.2")

    @property
    def llm_api_key(self) -> str:
        return self.get("llm.api_key", "")

    @property
    def llm_base_url(self) -> str:
        return self.get("llm.base_url", "https://api.deepseek.com/v1")

    @property
    def llm_temperature(self) -> float:
        return self.get("llm.temperature", 0.7)

    @property
    def llm_max_tokens(self) -> int:
        return self.get("llm.max_tokens", 2000)

    @property
    def embedding_model(self) -> str:
        return self.get("embedding.model", "BAAI/bge-small-zh-v1.5")

    @property
    def embedding_device(self) -> str:
        return self.get("embedding.device", "cpu")

    @property
    def embedding_batch_size(self) -> int:
        return self.get("embedding.batch_size", 32)

    @property
    def chroma_persist_dir(self) -> str:
        return self.get("vector_store.persist_directory", "./chroma_data")

    @property
    def chroma_prefix(self) -> str:
        return self.get("vector_store.collection_name_prefix", "project_")

    @property
    def platform_base_url(self) -> str:
        return self.get("platform.base_url", "http://localhost:8080")

    @property
    def platform_timeout(self) -> int:
        return self.get("platform.timeout", 30)

    @property
    def server_host(self) -> str:
        return self.get("server.host", "0.0.0.0")

    @property
    def server_port(self) -> int:
        return self.get("server.port", 8001)

    @property
    def cors_origins(self) -> list:
        return self.get(
            "server.cors_origins", ["http://localhost:5173", "http://localhost:8080"]
        )


config = Config()
