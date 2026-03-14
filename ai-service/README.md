# AI 智能测试助手服务

FastAPI + LangChain + Chroma 向量库实现的 AI 服务，为测试平台提供智能对话、知识库管理、用例生成能力。

## 1 项目概述

### 1.1 定位

AI 服务是自动化测试平台的重构新增模块，作为独立服务通过 HTTP 与 SpringBoot 后端交互，提供：

- **AI 对话**：基于大模型的智能问答
- **知识库管理**：文档向量检索（RAG）
- **用例生成**：ReAct Agent 自动生成测试用例

### 1.2 架构特点

- 前后端分离：独立 FastAPI 服务，通过 REST API 与后端通信
- 单库隔离：Chroma 使用单集合，元数据实现项目数据隔离
- 流式输出：SSE 协议实现实时流式响应
- 降级机制：Embedding 不可用时自动降级为关键词匹配

---

## 2 技术架构

### 2.1 技术栈

| 层级 | 技术选型 |
|------|----------|
| Web 框架 | FastAPI |
| LLM 集成 | LangChain |
| 向量数据库 | Chroma |
| Embedding | Ollama / OpenAI |
| 大模型 | DeepSeek / Qwen / OpenAI |

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
│   │   └── retrieval/       # 检索增强
│   │       ├── bm25.py      # BM25 关键词检索
│   │       └── reranker.py  # BGE 精排
│   ├── tools/               # 工具模块
│   │   └── platform_tools.py
│   ├── utils/               # 工具类
│   │   └── chunking.py      # 文本分块
│   └── schemas/             # Pydantic 模型
├── evals/                   # 评估模块
└── tests/                   # 测试模块
```

---

## 3 功能模块

### 3.1 路由层

| 文件 | 路径 | 核心接口 |
|------|------|----------|
| chat.py | /ai | `/chat/stream` SSE 流式对话 |
| knowledge.py | /ai/rag | `/add` `/delete` `/query` `/stats` |
| agent.py | /ai/agent | `/generate-case` `/api-list` |

### 3.2 服务层

**AgentService**：对话分流和用例生成
- `chat()` / `stream_chat()`：对话入口
- `generate_case()`：用例生成
- `_is_case_request()`：用例需求识别
- `_select_api_ids()`：接口选择

**LLMService**：大模型交互
- `chat()` / `chat_with_stream()`：对话
- `generate()`：prompt 生成

**RAGService**：知识检索
- `add_document()` / `delete_document()`：索引操作
- `search()` / `search_with_status()`：检索

### 3.3 工具层

**PlatformClient**：平台 API 客户端
- `get_api_list()` / `get_api_detail()`：接口查询
- `get_case_schema()`：Schema 获取

---

## 4 核心流程

### 4.1 AI 对话流程

```
用户 → 后端 → FastAPI → AgentService
                          ├─ 用例需求 → generate_case()
                          └─ 问答需求 → RAG检索 → LLM → 流式响应
```

### 4.2 知识库索引流程

```
后端 → FastAPI → RAGService
                ├─ 文本分块
                ├─ Embedding 向量化
                └─ Chroma 持久化
```

### 4.3 用例生成流程

```
需求输入 → 获取接口池
        → 选择接口（ReAct/关键词）
        → 获取依赖关系
        → RAG 增强
        → LLM 生成
        → Pydantic 校验
        → 返回前端预览
```

---

## 5 配置说明

### 5.1 config.yaml

```yaml
llm:
  provider: deepseek
  model: deepseek-chat
  api_key: sk-xxx

embedding:
  provider: openai
  model: text-embedding-3-small

vector_store:
  persist_directory: ./chroma_data

platform:
  base_url: http://localhost:8080

server:
  host: 0.0.0.0
  port: 8001
```

### 5.2 环境变量

| 变量 | 说明 |
|------|------|
| DEEPSEEK_API_KEY | LLM API Key |
| PLATFORM_BASE_URL | 平台地址 |

---

## 6 启动服务

```bash
cd ai-service
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --reload --port 8001

# 健康检查
curl http://localhost:8001/health
```

---

## 7 接口规范

### 7.1 SSE 事件格式

```json
{"type": "content", "delta": "..."}
{"type": "case", "case": {...}}
{"type": "error", "message": "..."}
{"type": "end"}
```

### 7.2 项目隔离规则

- 向量库：通过 `project_id` 元数据过滤
- 对话历史：前端维护，每次请求携带
- 接口查询：必须携带 project_id
