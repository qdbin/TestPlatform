"""
配置管理模块
负责加载和管理AI服务的配置信息，支持YAML配置与环境变量覆盖

配置优先级：
    1. 环境变量（最高优先级）
    2. config.yaml 文件
    3. 默认值（最低优先级）

配置项分类：
    - LLM配置：提供商、模型、API Key、温度参数等
    - Embedding配置：模型、设备、批处理大小
    - Chroma向量库配置：持久化目录、集合名
    - 平台配置：后端地址、超时时间
    - 服务配置：监听地址、端口、CORS
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class Config:
    """
    配置管理单例（Singleton）

    职责：读取 config.yaml，并支持环境变量覆盖敏感配置。

    一、配置文件加载：项目根目录下的 config.yaml
    二、环境变量覆盖：DEEPSEEK_API_KEY / OPENAI_API_KEY / PLATFORM_BASE_URL
    三、配置访问：通过 get() 方法或属性访问器获取配置值

    示例：
        config = Config()
        api_key = config.llm_api_key  # 获取LLM API Key
        port = config.get("server.port", 8001)  # 带默认值的获取
    """

    _instance: Optional["Config"] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """
        加载配置文件

        步骤：
            1. 查找项目根目录的 config.yaml
            2. 解析 YAML 内容到内部字典
            3. 加载环境变量覆盖
        """
        project_root = Path(__file__).parent.parent
        load_dotenv(project_root / ".env", override=False)
        config_path = project_root / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        self._load_env_overrides()

    def _load_env_overrides(self) -> None:
        """
        环境变量覆盖配置

        覆盖规则：
            1. DEEPSEEK_API_KEY -> llm.api_key
            2. OPENAI_API_KEY -> llm.api_key
            3. PLATFORM_BASE_URL -> platform.base_url
        """
        # DeepSeek API Key 覆盖
        if os.getenv("DEEPSEEK_API_KEY"):
            if "llm" not in self._config:
                self._config["llm"] = {}
            self._config["llm"]["api_key"] = os.getenv("DEEPSEEK_API_KEY")

        # OpenAI API Key 覆盖
        if os.getenv("OPENAI_API_KEY"):
            if "llm" not in self._config:
                self._config["llm"] = {}
            self._config["llm"]["api_key"] = os.getenv("OPENAI_API_KEY")

        # 平台地址覆盖
        if os.getenv("PLATFORM_BASE_URL"):
            if "platform" not in self._config:
                self._config["platform"] = {}
            self._config["platform"]["base_url"] = os.getenv("PLATFORM_BASE_URL")

        # LangSmith配置覆盖
        if os.getenv("LANGSMITH_API_KEY"):
            if "langsmith" not in self._config:
                self._config["langsmith"] = {}
            self._config["langsmith"]["api_key"] = os.getenv("LANGSMITH_API_KEY")
        if os.getenv("LANGCHAIN_API_KEY"):
            if "langsmith" not in self._config:
                self._config["langsmith"] = {}
            self._config["langsmith"]["api_key"] = os.getenv("LANGCHAIN_API_KEY")
        if os.getenv("LANGSMITH_PROJECT"):
            if "langsmith" not in self._config:
                self._config["langsmith"] = {}
            self._config["langsmith"]["project"] = os.getenv("LANGSMITH_PROJECT")
        if os.getenv("LANGSMITH_TRACING"):
            if "langsmith" not in self._config:
                self._config["langsmith"] = {}
            self._config["langsmith"]["tracing"] = os.getenv("LANGSMITH_TRACING")

        # Embedding配置覆盖
        if os.getenv("EMBEDDING_PROVIDER"):
            if "embedding" not in self._config:
                self._config["embedding"] = {}
            self._config["embedding"]["provider"] = os.getenv("EMBEDDING_PROVIDER")

        if os.getenv("EMBEDDING_OPENAI_API_KEY"):
            if "embedding" not in self._config:
                self._config["embedding"] = {}
            self._config["embedding"]["openai_api_key"] = os.getenv(
                "EMBEDDING_OPENAI_API_KEY"
            )

        if os.getenv("EMBEDDING_OPENAI_BASE_URL"):
            if "embedding" not in self._config:
                self._config["embedding"] = {}
            self._config["embedding"]["openai_base_url"] = os.getenv(
                "EMBEDDING_OPENAI_BASE_URL"
            )

        if os.getenv("EMBEDDING_OLLAMA_URL"):
            if "embedding" not in self._config:
                self._config["embedding"] = {}
            self._config["embedding"]["ollama_url"] = os.getenv("EMBEDDING_OLLAMA_URL")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取`config.ymal`的配置值，支持点号分隔的嵌套键

        @param key: 配置键，支持 "llm.provider" 格式
        @param default: 默认值
        @return: 配置值

        示例：
            config.get("llm.provider")  # 返回 "deepseek"
            config.get("llm.nonexistent", "default")  # 返回 "default"
        """
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

    # ==================== LLM 配置属性 ====================
    @property
    def llm_provider(self) -> str:
        """LLM 提供商：deepseek / qwen / openai"""
        return self.get("llm.provider", "deepseek")

    @property
    def llm_model(self) -> str:
        """LLM 模型名称"""
        return self.get("llm.model", "deepseek-v3.2")

    @property
    def llm_api_key(self) -> str:
        """LLM API Key"""
        return self.get("llm.api_key", "")

    @property
    def llm_base_url(self) -> str:
        """LLM 网关地址（兼容 OpenAI 协议）"""
        return self.get("llm.base_url", "https://api.deepseek.com/v1")

    @property
    def llm_temperature(self) -> float:
        """LLM 温度参数：控制生成随机性（0-2）"""
        return self.get("llm.temperature", 0.7)

    @property
    def llm_max_tokens(self) -> int:
        """LLM 最大 token 数"""
        return self.get("llm.max_tokens", 2000)

    # ==================== Embedding 配置属性 ====================
    @property
    def embedding_provider(self) -> str:
        """Embedding 提供商：ollama / openai"""
        return self.get("embedding.provider", "ollama")

    @property
    def embedding_openai_api_key(self) -> str:
        """OpenAI Embedding API Key"""
        return self.get("embedding.openai_api_key", "")

    @property
    def embedding_openai_base_url(self) -> str:
        """OpenAI Embedding 网关地址"""
        return self.get("embedding.openai_base_url", "https://api.openai.com/v1")

    @property
    def embedding_openai_model(self) -> str:
        """OpenAI Embedding 模型名称"""
        return self.get("embedding.openai_model", "text-embedding-3-small")

    @property
    def embedding_ollama_url(self) -> str:
        """Ollama Embedding 服务地址"""
        return self.get("embedding.ollama_url", "http://localhost:11434")

    @property
    def embedding_ollama_model(self) -> str:
        """Ollama Embedding 模型名称"""
        return self.get("embedding.ollama_model", "nomic-embed-text")

    @property
    def embedding_model(self) -> str:
        """Embedding 模型名称（用于重排序等其他用途）"""
        return self.get("embedding.model", "BAAI/bge-small-zh-v1.5")

    @property
    def embedding_device(self) -> str:
        """Embedding 设备：cpu / cuda"""
        return self.get("embedding.device", "cpu")

    @property
    def embedding_batch_size(self) -> int:
        """Embedding 批处理大小"""
        return self.get("embedding.batch_size", 32)

    # ==================== Chroma 向量库配置属性 ====================
    @property
    def chroma_persist_dir(self) -> str:
        """向量库持久化目录"""
        return self.get("vector_store.persist_directory", "./chroma_data")

    @property
    def chroma_prefix(self) -> str:
        """向量库集合名前缀"""
        return self.get("vector_store.collection_name_prefix", "project_")

    @property
    def chroma_collection_name(self) -> str:
        """向量库集合名"""
        return self.get("vector_store.collection_name", "knowledge_docs")

    # ==================== 平台配置属性 ====================
    @property
    def platform_base_url(self) -> str:
        """测试平台后端地址"""
        return self.get("platform.base_url", "http://localhost:8080")

    @property
    def platform_timeout(self) -> int:
        """平台 API 请求超时（秒）"""
        return self.get("platform.timeout", 30)

    # ==================== 服务配置属性 ====================
    @property
    def server_host(self) -> str:
        """服务监听地址"""
        return self.get("server.host", "0.0.0.0")

    @property
    def server_port(self) -> int:
        """服务监听端口"""
        return self.get("server.port", 8001)

    @property
    def cors_origins(self) -> list:
        """CORS 允许的源地址"""
        return self.get(
            "server.cors_origins", ["http://localhost:5173", "http://localhost:8080"]
        )

    @property
    def langsmith_api_key(self) -> str:
        """LangSmith API Key"""
        return self.get("langsmith.api_key", "")

    # 别名，用于兼容其他模块
    LANGSMITH_API_KEY = property(lambda self: self.langsmith_api_key)

    @property
    def langsmith_project(self) -> str:
        """LangSmith 项目名称"""
        return self.get("langsmith.project", "test-platform-ai")

    # 别名
    LANGSMITH_PROJECT = property(lambda self: self.langsmith_project)

    @property
    def langsmith_tracing(self) -> bool:
        """是否启用 LangSmith 追踪"""
        value = self.get("langsmith.tracing", False)
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "on"}

    # DeepSeek API Key 别名
    @property
    def DEEPSEEK_API_KEY(self) -> str:
        """DeepSeek API Key（别名）"""
        return self.llm_api_key


# 全局配置实例
config = Config()


if __name__ == "__main__":
    """
    配置模块调试代码
    用于验证配置加载和环境变量覆盖是否生效
    """
    print("=" * 50)
    print("配置模块调试")
    print("=" * 50)

    # 基础配置访问测试
    print(f"\n1. LLM 配置:")
    print(f"   - Provider: {config.llm_provider}")
    print(f"   - Model: {config.llm_model}")
    print(
        f"   - API Key: {config.llm_api_key[:10]}..."
        if config.llm_api_key
        else "   - API Key: (未设置)"
    )
    print(f"   - Base URL: {config.llm_base_url}")

    print(f"\n2. Embedding 配置:")
    print(f"   - Provider: {config.embedding_provider}")
    print(
        f"   - OpenAI API Key: {'已设置' if config.embedding_openai_api_key else '未设置'}"
    )
    print(f"   - OpenAI Base URL: {config.embedding_openai_base_url}")
    print(f"   - OpenAI Model: {config.embedding_openai_model}")
    print(f"   - Ollama URL: {config.embedding_ollama_url}")
    print(f"   - Ollama Model: {config.embedding_ollama_model}")
    print(f"   - Model (重排序): {config.embedding_model}")
    print(f"   - Device: {config.embedding_device}")

    print(f"\n3. Chroma 向量库配置:")
    print(f"   - Persist Dir: {config.chroma_persist_dir}")
    print(f"   - Collection Name: {config.chroma_collection_name}")

    print(f"\n4. 平台配置:")
    print(f"   - Base URL: {config.platform_base_url}")
    print(f"   - Timeout: {config.platform_timeout}s")

    print(f"\n5. 服务配置:")
    print(f"   - Host: {config.server_host}")
    print(f"   - Port: {config.server_port}")
    print(f"   - CORS Origins: {config.cors_origins}")

    # get() 方法测试
    print(f"\n6. get() 方法测试:")
    print(f"   - config.get('llm.provider'): {config.get('llm.provider')}")
    print(
        f"   - config.get('llm.nonexistent', 'default'): {config.get('llm.nonexistent', 'default')}"
    )
    print(f"   - config.get('platform.base_url'): {config.get('platform.base_url')}")

    print("\n" + "=" * 50)
    print("调试完成")
    print("=" * 50)
