# AI 智能测试助手服务

FastAPI + LangChain 1.x + Chroma 向量库实现的 AI 服务，为测试平台提供智能对话、知识库管理、用例生成能力。

## 1 项目概述

### 1.1 定位

AI 服务是自动化测试平台的重构新增模块，作为独立服务通过 HTTP 与 SpringBoot 后端交互，提供：

- **AI 对话**：基于大模型的智能问答
- **知识库管理**：文档向量检索（RAG）
- **用例生成**：ReAct Agent 自动生成测试用例

### 1.2 架构特点

- **前后端分离**：独立 FastAPI 服务，通过 REST API 与后端通信
- **单库隔离**：Chroma 使用单集合，元数据实现项目数据隔离
- **流式输出**：SSE 协议实现实时流式响应
- **降级机制**：Embedding 不可用时自动降级为关键词匹配
- **全链路追踪**：集成 LangSmith 实现调用链追踪

## 2 技术架构

### 2.1 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| Web 框架 | FastAPI | 高性能异步 Web 框架 |
| LLM 集成 | LangChain 1.x | LLM 应用开发框架 |
| 向量数据库 | Chroma | 轻量级向量数据库 |
| Embedding | Ollama / OpenAI | 文本向量化 |
| 大模型 | DeepSeek / Qwen / OpenAI | LLM 推理 |
| 日志 | Loguru | 结构化日志 |
| 观测 | LangSmith | LLM 应用观测平台 |

### 2.2 目录结构

```
ai-service/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── routers/             # 路由层
│   │   ├── chat.py          # AI 对话路由
│   │   ├── knowledge.py     # RAG 知识库路由
│   │   └── agent.py         # 用例生成路由
│   ├── services/            # 业务逻辑层
│   │   ├── agent_service.py # Agent 核心服务
│   │   ├── llm_service.py   # LLM 服务
│   │   ├── rag_service.py   # RAG 服务
│   │   ├── case_workflow.py # 用例生成工作流
│   │   └── retrieval/       # 检索增强
│   │       ├── bm25.py      # BM25 关键词检索
│   │       ├── query_rewrite.py  # 查询改写
│   │       └── reranker.py  # BGE 精排
│   ├── tools/               # 工具模块
│   │   └── platform_tools.py # 平台 API 客户端
│   ├── utils/               # 工具类
│   │   ├── chunking.py      # 文本分块
│   │   └── markdown_parent_child_chunking.py  # Markdown 分块
│   ├── prompts/             # Prompt 模板
│   │   └── assistant_prompts.py
│   ├── schemas/             # Pydantic 模型
│   │   └── ai_models.py
│   └── observability/       # 可观测性
│       ├── logger.py        # 日志
│       ├── langsmith.py     # LangSmith 配置
│       └── traceable.py     # 追踪装饰器
├── evals/                   # 评估模块
├── tests/                   # 测试模块
├── config.yaml              # 配置文件
└── requirements.txt         # 依赖
```

## 3 功能模块

### 3.1 路由层

| 文件 | 路径 | 核心接口 |
|------|------|----------|
| chat.py | /ai | `/chat/stream` SSE 流式对话 |
| knowledge.py | /ai/rag | `/add` `/delete` `/query` `/stats` |
| agent.py | /ai/agent | `/generate-case` `/api-list` |

### 3.2 服务层

**AgentService**：对话分流和用例生成
- `stream_chat()`：流式对话入口
- `generate_case()`：用例生成
- `_is_case_request()`：用例需求识别
- `_select_api_ids()`：接口选择（LLM + 关键词回退）

**LLMService**：大模型交互
- `chat()` / `achat()`：普通对话
- `chat_json()` / `achat_json()`：JSON 模式对话
- `chat_with_stream()` / `achat_with_stream()`：流式对话
- `chat_structured()` / `achat_structured()`：结构化输出

**RAGService**：知识检索
- `add_document()`：添加文档到向量库
- `delete_document()`：删除文档
- `search()` / `search_with_status()`：混合检索

**CaseGenerationWorkflow**：用例生成工作流
- `run()`：执行完整用例生成流程
- `_prepare_requirement_and_api_pool()`：需求改写 + 接口池加载
- `_select_api_ids()`：接口选择
- `_load_context()`：加载上下文
- `_generate_and_validate_with_retry()`：生成并校验（含 Pydantic 校验失败重试）

### 3.3 检索增强层

**BM25KeywordRetriever**：BM25 关键词检索
- 基于概率模型的关键词检索算法
- 支持中文分词和停用词过滤

**QueryRewriter**：查询改写
- 同义词扩展
- 查询扩写
- 复杂查询分解

**BGEReranker**：BGE 重排序
- 使用 BGE 模型计算查询-文档相关性
- 支持批量处理和降级策略

### 3.4 工具层

**PlatformClient**：平台 API 客户端
- `get_api_list()`：获取接口列表
- `get_api_detail()`：获取接口详情
- `get_case_schema()`：获取用例 Schema

## 4 核心流程

### 4.1 AI 对话流程

```
用户 → 后端 → FastAPI → AgentService
                          ├─ 用例需求 → generate_case()
                          └─ 问答需求 → RAG检索 → LLM → 流式响应
```

**SSE 事件类型**：
- `{"type": "content", "delta": "..."}` - 文本内容片段
- `{"type": "case", "case": {...}}` - 生成的用例
- `{"type": "error", "message": "..."}` - 错误信息
- `{"type": "end"}` - 流结束标记

### 4.2 知识库索引流程

```
后端 → FastAPI → RAGService
                ├─ Markdown 父子分块
                ├─ Embedding 向量化
                └─ Chroma 持久化
```

**数据隔离**：
- 项目级：通过 `project_id` 元数据过滤
- 文档级：通过 `doc_id` 元数据标识

### 4.3 用例生成流程

```
需求输入 → 改写用户需求
        → 加载项目接口池
        → 选择候选接口（ReAct/关键词）
        → 获取接口详情与依赖关系
        → RAG 增强
        → LLM 生成
        → Pydantic 校验（含重试）
        → 返回前端预览
```

### 4.4 RAG 混合检索流程

```
查询输入 → 查询改写与扩写
        → 并行向量检索 + 关键词检索
        → 结果融合（RRF）
        → BGE 重排序
        → 返回 Top-K 结果
```

## 5 配置说明

### 5.1 config.yaml

```yaml
llm:
  provider: deepseek          # LLM 提供商: deepseek/qwen/openai
  model: deepseek-chat        # 模型名称
  api_key: sk-xxx             # API Key
  base_url: https://api.deepseek.com/v1  # 网关地址
  temperature: 0.7            # 温度参数
  max_tokens: 2000            # 最大 token 数

embedding:
  provider: openai            # Embedding 提供商: openai/ollama
  model: text-embedding-3-small  # 模型名称
  openai_api_key: ""          # OpenAI API Key
  openai_base_url: https://api.openai.com/v1
  ollama_url: http://localhost:11434
  ollama_model: nomic-embed-text

vector_store:
  persist_directory: ./chroma_data  # 向量库持久化目录
  collection_name: knowledge_docs   # 集合名

platform:
  base_url: http://localhost:8080   # 平台后端地址
  timeout: 30                       # 请求超时（秒）

server:
  host: 0.0.0.0
  port: 8001
  cors_origins:                   # CORS 允许的源
    - http://localhost:5173
    - http://localhost:8080

langsmith:
  api_key: ""                   # LangSmith API Key
  project: test-platform-ai     # 项目名称
  tracing: false                # 是否启用追踪
```

### 5.2 环境变量

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key（覆盖配置） |
| `OPENAI_API_KEY` | OpenAI API Key（覆盖配置） |
| `PLATFORM_BASE_URL` | 平台后端地址（覆盖配置） |
| `LANGSMITH_API_KEY` | LangSmith API Key（覆盖配置） |
| `LANGSMITH_PROJECT` | LangSmith 项目名称（覆盖配置） |
| `LANGSMITH_TRACING` | 是否启用追踪（覆盖配置） |

## 6 启动服务

```bash
cd ai-service

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --reload --port 8001

# 健康检查
curl http://localhost:8001/health
```

## 7 接口规范

### 7.1 SSE 事件格式

```json
{"type": "content", "delta": "..."}
{"type": "case", "case": {...}, "api_ids": [...]}
{"type": "error", "message": "..."}
{"type": "end"}
```

### 7.2 项目隔离规则

- **向量库**：通过 `project_id` 元数据过滤
- **对话历史**：前端维护，每次请求携带
- **接口查询**：必须携带 `project_id`

## 8 调试与测试

每个核心模块都包含 `if __name__ == "__main__"` 调试代码，可直接运行测试：

```bash
# 测试配置模块
python app/config.py

# 测试 LLM 服务
python app/services/llm_service.py

# 测试 RAG 服务
python app/services/rag_service.py

# 测试 Agent 服务
python app/services/agent_service.py

# 测试 BM25 检索
python app/services/retrieval/bm25.py

# 测试查询改写
python app/services/retrieval/query_rewrite.py

# 测试 Prompt 模板
python app/prompts/assistant_prompts.py
```

## 9 相关文档

- [业务逻辑设计](./assets/ai服务相关说明/框架设计/业务逻辑设计.md)
- [功能模块](./assets/ai服务相关说明/框架设计/功能模块.md)
- [数据设计](./assets/ai服务相关说明/框架设计/数据设计.md)
- [PRD 文档](./assets/ai服务相关说明/PRD.md)
