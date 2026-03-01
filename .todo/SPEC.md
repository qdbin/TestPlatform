# AI 智能测试助手 - 计划方案说明书

## 一、项目概述

### 1.1 项目背景

流马自动化测试平台是一个成熟的分布式 API/Web/App 自动化测试平台，采用 SpringBoot + Vue 架构。为提升平台智能化水平，增加 AI 辅助测试能力，拟开发 AI 智能测试助手模块。

### 1.2 项目目标

1. **AI 对话助手**：基于 RAG 技术的项目知识库问答系统
2. **智能用例生成**：AI 根据用户需求和项目接口自动生成测试用例
3. **多项目隔离**：知识库和会话按项目隔离，保证数据安全

### 1.3 业务需求确认

| 需求项         | 确认内容                                                                              |
| -------------- | ------------------------------------------------------------------------------------- |
| 对话历史存储   | SpringBoot 数据库（Flyway 管理）                                                      |
| 知识库隔离     | 按项目隔离                                                                            |
| 用例生成流程   | 用户输入需求 → AI 查询项目接口列表 → 用户选择接口 → AI 生成用例 → 前端预览 → 确认落库 |
| 接口数据集成   | 自动将项目接口文档加入知识库                                                          |
| 对话界面       | 独立页面（左侧导航"AI 助手"入口）                                                     |
| 输出方式       | SSE 流式输出                                                                          |
| Agent 数据获取 | FastAPI 直接调用 SpringBoot REST API                                                  |

## 二、技术架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              流马测试平台                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐       │
│  │         Vue前端              │    │       SpringBoot后端         │       │
│  │  (新增AI助手页面)            │    │  (新增AI Controller/Service) │       │
│  └──────────────┬──────────────┘    └──────────────┬──────────────┘       │
│                 │ HTTP API                           │ HTTP API              │
│                 │                                    │                      │
│                 └────────────────────────────────────┼──────────────────────┘
│                                                      │
│                                                      ▼
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        AI服务 (FastAPI独立部署)                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │  │
│  │  │   RAG模块   │  │   Agent     │  │  LangChain  │  │  Chroma  │ │  │
│  │  │  (知识问答)  │  │ (用例生成)  │  │   (LLM调用)  │  │ (向量存储)│ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │  │
│  │                                                                     │  │
│  │  ┌─────────────┐  ┌─────────────┐                                  │  │
│  │  │   bge-small │  │  DeepSeek   │                                  │  │
│  │  │   -zh-v1.5  │  │   /GPT-4    │                                  │  │
│  │  │ (Embedding) │  │   (LLM)     │                                  │  │
│  │  └─────────────┘  └─────────────┘                                  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
TestPlatform/
├── platform-backend/                    # SpringBoot后端 (已有)
│   └── src/main/java/com/autotest/
│       ├── controller/
│       │   └── AiController.java        # 新增AI控制器
│       ├── service/
│       │   └── AiService.java          # 新增AI服务
│       ├── domain/
│       │   ├── AiKnowledge.java        # 新增知识库实体
│       │   └── AiConversation.java     # 新增会话实体
│       ├── mapper/
│       │   ├── AiKnowledgeMapper.java  # 新增
│       │   └── AiConversationMapper.java # 新增
│       ├── dto/
│       │   ├── AiChatRequest.java      # 新增
│       │   └── AiChatResponse.java     # 新增
│       └── resources/
│           └── db/
│               └── V1.26__init_ai.sql  # 新增Flyway脚本
│
├── platform-frontend/                    # Vue前端 (已有)
│   └── src/
│       ├── views/
│       │   └── aiAssistant/           # 新增AI助手页面
│       │       ├── index.vue           # 对话主页
│       │       ├── chatWindow.vue      # 聊天窗口组件
│       │       └── casePreview.vue     # 用例预览组件
│       └── router/
│           └── index.js                # 新增路由配置
│
└── ai-service/                         # 新增AI服务
    ├── app/
    │   ├── main.py                     # FastAPI入口
    │   ├── config.py                   # 配置管理
    │   ├── routers/
    │   │   ├── chat.py                 # 对话路由
    │   │   ├── knowledge.py            # 知识库路由
    │   │   └── agent.py                # Agent路由
    │   ├── services/
    │   │   ├── llm_service.py          # LLM服务
    │   │   ├── rag_service.py          # RAG服务
    │   │   └── agent_service.py        # Agent服务
    │   ├── tools/
    │   │   └── platform_tools.py       # 平台API调用工具
    │   └── utils/
    │       ├── embeddings.py            # Embedding工具
    │       └── chunking.py             # 文档分块工具
    ├── knowledge/                      # 知识库文档存储
    │   └── {project_id}/
    │       └── *.md
    ├── requirements.txt                # Python依赖
    ├── config.yaml                     # 配置文件
    └── README.md                       # 服务说明
```

## 三、数据库设计

### 3.1 新增表结构 (Flyway: V1.26\_\_init_ai.sql)

```sql
-- AI知识库文档表
CREATE TABLE IF NOT EXISTS ai_knowledge (
    id VARCHAR(32) PRIMARY KEY COMMENT '主键ID',
    project_id VARCHAR(32) NOT NULL COMMENT '所属项目ID',
    name VARCHAR(255) NOT NULL COMMENT '文档名称',
    content TEXT COMMENT '文档内容(Markdown)',
    doc_type VARCHAR(32) DEFAULT 'manual' COMMENT 'manual:使用手册 guide:引导文档 api_doc:接口文档 custom:自定义',
    source_type VARCHAR(32) DEFAULT 'manual' COMMENT 'manual:手动上传 auto:自动生成',
    status VARCHAR(16) DEFAULT 'active' COMMENT 'active:有效 deleted:已删除',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '更新时间戳',
    create_user VARCHAR(32) COMMENT '创建人',
    update_user VARCHAR(32) COMMENT '更新人',
    INDEX idx_project (project_id),
    INDEX idx_type (doc_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI知识库文档表';

-- AI会话历史表
CREATE TABLE IF NOT EXISTS ai_conversation (
    id VARCHAR(32) PRIMARY KEY COMMENT '主键ID',
    project_id VARCHAR(32) NOT NULL COMMENT '项目ID',
    user_id VARCHAR(32) NOT NULL COMMENT '用户ID',
    session_type VARCHAR(32) DEFAULT 'chat' COMMENT 'chat:知识问答 case_generate:用例生成',
    title VARCHAR(255) COMMENT '会话标题',
    messages JSON NOT NULL COMMENT '对话消息JSON: [{role: user/assistant, content: 内容, time: 时间戳}]',
    context JSON COMMENT '上下文数据: {selected_apis: [], current_case: {}}',
    use_rag TINYINT(1) DEFAULT 1 COMMENT '是否启用RAG',
    status VARCHAR(16) DEFAULT 'active' COMMENT 'active:有效 closed:已关闭',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '更新时间戳',
    INDEX idx_project_user (project_id, user_id),
    INDEX idx_session_type (session_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI会话历史表';

-- AI配置表
CREATE TABLE IF NOT EXISTS ai_config (
    id VARCHAR(32) PRIMARY KEY COMMENT '主键ID',
    config_key VARCHAR(64) NOT NULL COMMENT '配置键: provider/model/api_key/base_url',
    config_value VARCHAR(500) COMMENT '配置值',
    is_global TINYINT(1) DEFAULT 0 COMMENT '是否全局配置(1:全局 0:项目级)',
    project_id VARCHAR(32) COMMENT '项目ID(全局配置时为空)',
    status VARCHAR(16) DEFAULT 'active' COMMENT 'active:有效 deleted:已删除',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '更新时间戳',
    UNIQUE KEY uk_key_project (config_key, project_id),
    INDEX idx_global (is_global)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI配置表';

-- AI接口索引表(记录哪些接口已加入知识库)
CREATE TABLE IF NOT EXISTS ai_api_index (
    id VARCHAR(32) PRIMARY KEY COMMENT '主键ID',
    project_id VARCHAR(32) NOT NULL COMMENT '项目ID',
    api_id VARCHAR(32) NOT NULL COMMENT '接口ID',
    api_name VARCHAR(255) COMMENT '接口名称',
    api_path VARCHAR(500) COMMENT '接口路径',
    api_method VARCHAR(16) COMMENT '请求方法',
    api_info TEXT COMMENT '接口详细信息(JSON)',
    indexed_status VARCHAR(16) DEFAULT 'pending' COMMENT 'pending:待索引 ready:已索引 error:索引失败',
    error_msg VARCHAR(500) COMMENT '错误信息',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '索引时间戳',
    INDEX idx_project (project_id),
    INDEX idx_api (api_id),
    INDEX idx_status (indexed_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI接口索引表';
```

## 四、SpringBoot 后端设计

### 4.1 Controller 层

**AiController.java** - AI 控制器

| 接口                              | 方法   | 说明                 |
| --------------------------------- | ------ | -------------------- |
| `/autotest/ai/chat`               | POST   | AI 对话(SSE 流式)    |
| `/autotest/ai/chat/history`       | GET    | 获取会话历史列表     |
| `/autotest/ai/chat/{id}`          | GET    | 获取会话详情         |
| `/autotest/ai/chat/{id}`          | DELETE | 删除会话             |
| `/autotest/ai/knowledge`          | GET    | 获取知识库列表       |
| `/autotest/ai/knowledge`          | POST   | 新增知识库文档       |
| `/autotest/ai/knowledge/{id}`     | PUT    | 更新知识库文档       |
| `/autotest/ai/knowledge/{id}`     | DELETE | 删除知识库文档       |
| `/autotest/ai/knowledge/index`    | POST   | 触发知识库索引       |
| `/autotest/ai/knowledge/sync-api` | POST   | 同步项目接口到知识库 |
| `/autotest/ai/generate/case`      | POST   | 生成测试用例(草稿)   |
| `/autotest/ai/generate/case/save` | POST   | 确认并保存用例       |
| `/autotest/ai/config`             | GET    | 获取 AI 配置         |
| `/autotest/ai/config`             | POST   | 保存 AI 配置         |

### 4.2 Service 层

**AiService.java** - AI 服务

```java
@Service
@Transactional(rollbackFor = Exception.class)
public class AiService {

    // 对话服务
    public String chat(AiChatRequest request);
    public List<AiConversation> getConversationList(String projectId, String userId);
    public AiConversation getConversationDetail(String conversationId);
    public void deleteConversation(String conversationId);

    // 知识库服务
    public List<AiKnowledge> getKnowledgeList(String projectId);
    public String saveKnowledge(AiKnowledge knowledge);
    public void updateKnowledge(AiKnowledge knowledge);
    public void deleteKnowledge(String knowledgeId);
    public void indexKnowledge(String knowledgeId);
    public void syncProjectApis(String projectId);

    // 用例生成服务
    public Map<String, Object> generateCaseDraft(AiGenerateCaseRequest request);
    public void saveGeneratedCase(String caseData);

    // 配置服务
    public AiConfig getConfig(String projectId);
    public void saveConfig(AiConfig config);
}
```

### 4.3 调用 AI 服务

```java
@Service
public class AiClientService {

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    @Value("${ai.service.api-key}")
    private String aiApiKey;

    // 对话(SSE流式)
    public Flux<String> chatStream(AiChatRequest request);

    // 用例生成
    public Map<String, Object> generateCase(AiGenerateCaseRequest request);

    // 知识库操作
    public void indexDocument(String knowledgeId, String content);
    public List<String> searchKnowledge(String query, String projectId);
}
```

## 五、FastAPI AI 服务设计

### 5.1 核心路由

**routers/chat.py** - 对话路由

```python
@router.post("/chat")
async def chat(request: ChatRequest):
    """AI对话接口(SSE流式返回)"""
    # 1. 获取项目上下文(接口列表、函数列表等)
    # 2. 判断是否启用RAG
    # 3. 构建Prompt
    # 4. 调用LLM生成回答
    # 5. 流式返回
    pass

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE流式对话"""
    pass

@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """获取会话历史"""
    pass
```

**routers/knowledge.py** - 知识库路由

```python
@router.post("/index")
async def index_document(request: IndexRequest):
    """文档索引"""
    # 1. 文档分块
    # 2. Embedding向量化
    # 3. 存储到Chroma
    pass

@router.delete("/index/{knowledge_id}")
async def delete_index(knowledge_id: str):
    """删除索引"""
    pass

@router.post("/search")
async def search_knowledge(request: SearchRequest):
    """知识检索"""
    # 1. 查询向量
    # 2. 返回相关片段
    pass

@router.post("/sync/api")
async def sync_project_apis(project_id: str, apis: List[ApiInfo]):
    """同步项目接口到知识库"""
    # 将接口信息转换为文档并索引
    pass
```

**routers/agent.py** - Agent 路由

```python
@router.post("/generate/case")
async def generate_case(request: GenerateCaseRequest):
    """AI用例生成"""
    # 1. 调用平台工具获取接口列表
    # 2. 让用户选择接口
    # 3. 生成用例JSON
    # 4. 返回预览
    pass

@router.post("/generate/case/refine")
async def refine_case(request: RefineCaseRequest):
    """用例优化"""
    pass
```

### 5.2 LangChain Agent 设计

**tools/platform_tools.py** - 平台 API 调用工具

```python
from langchain.agents import Tool

def get_platform_client():
    """获取平台API客户端"""
    pass

# 工具1: 获取项目接口列表
get_api_list_tool = Tool(
    name="get_api_list",
    func=lambda project_id: get_platform_client().get_apis(project_id),
    description="获取项目接口列表，返回接口ID、名称、路径、请求方法"
)

# 工具2: 获取接口详情
get_api_detail_tool = Tool(
    name="get_api_detail",
    func=lambda api_id: get_platform_client().get_api_detail(api_id),
    description="获取指定接口的详细信息"
)

# 工具3: 获取项目环境
get_environment_tool = Tool(
    name="get_environment",
    func=lambda project_id: get_platform_client().get_envs(project_id),
    description="获取项目的环境配置"
)

# 工具4: 知识库检索
search_knowledge_tool = Tool(
    name="search_knowledge",
    func=lambda query: search_rag_knowledge(query),
    description="搜索项目知识库"
)

# 工具5: 保存用例
save_case_tool = Tool(
    name="save_case",
    func=lambda case_data: get_platform_client().save_case(case_data),
    description="保存测试用例到平台"
)
```

### 5.3 RAG 服务设计

**services/rag_service.py** - RAG 服务

```python
class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name='BAAI/bge-small-zh-v1.5',
            model_kwargs={'device': 'cpu'}
        )
        self.client = chromadb.PersistentClient(path="./chroma_data")

    def create_collection(self, project_id: str):
        """创建项目知识库集合"""
        return self.client.get_or_create_collection(
            name=f"project_{project_id}",
            metadata={"project_id": project_id}
        )

    def add_document(self, project_id: str, knowledge_id: str, content: str):
        """添加文档到知识库"""
        # 1. 文档分块
        chunks = self.chunk_text(content)
        # 2. 向量化
        embeddings = self.embeddings.embed_documents(chunks)
        # 3. 存储
        collection = self.create_collection(project_id)
        collection.add(
            embeddings=embeddings,
            documents=chunks,
            ids=[f"{knowledge_id}_{i}" for i in range(len(chunks))],
            metadatas=[{"knowledge_id": knowledge_id, "chunk_index": i} for i in range(len(chunks))]
        )

    def search(self, project_id: str, query: str, top_k: int = 5):
        """检索知识库"""
        collection = self.client.get_or_create_collection(name=f"project_{project_id}")
        query_embedding = self.embeddings.embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results

    def delete_document(self, knowledge_id: str):
        """删除知识库文档"""
        pass
```

### 5.4 配置管理

**config.yaml** - AI 服务配置

```yaml
# LLM配置
llm:
  provider: "deepseek" # deepseek/openai/anthropic/qwen
  model: "deepseek-chat"
  api_key: "${DEEPSEEK_API_KEY}"
  base_url: "https://api.deepseek.com/v1"
  temperature: 0.7
  max_tokens: 2000

# Embedding配置
embedding:
  model: "BAAI/bge-small-zh-v1.5"
  device: "cpu" # cpu/cuda
  batch_size: 32

# Chroma配置
vector_store:
  persist_directory: "./chroma_data"
  collection_name_prefix: "project_"

# 平台API配置
platform:
  base_url: "http://localhost:8080"
  timeout: 30

# 服务配置
server:
  host: "0.0.0.0"
  port: 8001
  cors_origins:
    - "http://localhost:5173"
    - "http://localhost:8080"
```

## 六、前端设计

### 6.1 路由配置

```javascript
// router/index.js 新增
{
    path: '/aiAssistant',
    name: 'AI助手',
    component: () => import('@/views/aiAssistant/index'),
    meta: { title: 'AI助手', requiresAuth: true }
}
```

### 6.2 页面结构

**views/aiAssistant/index.vue** - AI 助手主页

```
┌─────────────────────────────────────────────────────────────┐
│  左侧菜单栏 (250px)         │  右侧主区域                     │
│  ┌─────────────────────┐   │  ┌─────────────────────────┐  │
│  │ [+ 新建对话]         │   │  │     搜索框              │  │
│  │ ─────────────────── │   │  └─────────────────────────┘  │
│  │ 对话历史列表         │   │  ┌─────────────────────────┐  │
│  │ ├─ 用户登录测试      │   │  │                         │  │
│  │ ├─ 接口文档查询      │   │  │    聊天消息区域          │  │
│  │ └─ 用例生成          │   │  │    (消息气泡+时间)       │  │
│  │                     │   │  │                         │  │
│  │ ─────────────────── │   │  │                         │  │
│  │ [x] 知识库管理       │   │  │                         │  │
│  │ [⚙] 设置            │   │  └─────────────────────────┘  │
│  └─────────────────────┘   │  ┌─────────────────────────┐  │
│                            │  │ [🤖] [📎] [📤] [  输入框 ] │  │
│                            │  │ RAG开关   上传   发送    │  │
│                            │  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 核心组件

| 组件                | 说明                                                  |
| ------------------- | ----------------------------------------------------- |
| chatWindow.vue      | 聊天窗口组件，支持 SSE 流式输出、Markdown 渲染        |
| casePreview.vue     | 用例预览组件，展示 AI 生成的用例 JSON，支持编辑和确认 |
| knowledgeManage.vue | 知识库管理组件，文档上传、索引状态查看                |
| settings.vue        | AI 配置组件，模型选择、API Key 配置                   |

### 6.4 SSE 流式输出实现

```javascript
// 使用EventSource或fetch+ReadableStream实现SSE
async function sendMessage(message, useRag) {
  const response = await fetch("/autotest/ai/chat/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      token: getToken(),
    },
    body: JSON.stringify({
      message,
      use_rag: useRag,
      project_id: currentProjectId,
    }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value);
    // 逐字追加到聊天窗口
    appendMessage("assistant", text);
  }
}
```

## 七、用例生成流程设计

### 7.1 完整流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI用例生成流程                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  用户输入需求                                                            │
│  "帮我测试用户登录接口"                                                   │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Step1: Agent调用平台API获取项目接口列表                            │   │
│  │   → Tool: get_api_list(project_id)                              │   │
│  │   返回: [{id: "1", name: "用户登录", path: "/api/login", ...}]   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  前端展示接口列表，用户选择接口                                           │
│  ☑ 用户登录 /api/login (POST)                                          │
│  ☐ 用户注册 /api/register (POST)                                       │
│  ☐ 获取用户信息 /api/user/info (GET)                                   │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Step2: Agent获取选中接口详情 + 知识库检索                         │   │
│  │   → Tool: get_api_detail(api_id)                                │   │
│  │   → Tool: search_knowledge("接口格式示例")                       │   │
│  │   返回: 接口参数、请求格式、已有测试用例等                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Step3: LLM生成用例JSON                                           │   │
│  │   Prompt包含:                                                     │   │
│  │   - 接口信息 (path, method, params)                               │   │
│  │   - 知识库上下文 (接口格式规范)                                    │   │
│  │   - 用例模板 (CaseApi结构)                                        │   │
│  │   - 生成要求 (正向+异常场景)                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         │                                                               │
│         ▼                                                               │
│  前端预览生成用例                                                        │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │ caseName: "用户登录-正常场景"                                   │      │
│  │ caseApis: [                                                     │      │
│  │   {                                                             │      │
│  │     apiId: "1",                                                 │      │
│  │     method: "POST",                                              │      │
│  │     path: "/api/login",                                          │      │
│  │     header: {...},                                               │      │
│  │     body: {"username": "{{username}}", "password": "{{pwd}}"}, │      │
│  │     assertion: [                                                │      │
│  │       {"from": "resBody", "method": "jsonpath",                │      │
│  │        "expression": "$.code", "assertion": "equals",          │      │
│  │        "expect": "200"},                                         │      │
│  │       {"from": "resBody", "method": "jsonpath",                │      │
│  │        "expression": "$.data.token", "assertion": "notEmpty"}  │      │
│  │     ]                                                            │      │
│  │   }                                                             │      │
│  │ ]                                                                │      │
│  └──────────────────────────────────────────────────────────────┘      │
│         │                                                               │
│         ▼                                                               │
│  用户确认 → 调用CaseService.saveCase()落库                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 用例数据结构

生成的用例 JSON 结构（与现有 CaseService 兼容）:

```json
{
  "name": "用户登录-正常场景",
  "type": "API",
  "level": "P1",
  "moduleId": "xxx",
  "projectId": "xxx",
  "description": "测试用户正常登录场景",
  "caseApis": [
    {
      "apiId": "接口ID",
      "description": "步骤描述",
      "header": "{\"Content-Type\": \"application/json\"}",
      "body": "{\"username\": \"{{username}}\", \"password\": \"{{password}}\"}",
      "query": "",
      "assertion": "[{\"from\":\"resBody\",\"method\":\"jsonpath\",\"expression\":\"$.code\",\"assertion\":\"equals\",\"expect\":\"200\"}]",
      "relation": "[]"
    }
  ]
}
```

## 八、实施计划

### 8.1 开发阶段划分

| 阶段     | 任务                      | 预估工时  |
| -------- | ------------------------- | --------- |
| 阶段一   | 基础设施搭建              | 2 天      |
|          | - FastAPI 服务框架搭建    | 0.5 天    |
|          | - Chroma + Embedding 集成 | 0.5 天    |
|          | - Flyway 数据库脚本       | 0.5 天    |
|          | - SpringBoot 基础代码     | 0.5 天    |
| 阶段二   | RAG 知识库功能            | 3 天      |
|          | - 知识库 CRUD API         | 1 天      |
|          | - 文档索引流程            | 1 天      |
|          | - 接口自动同步            | 1 天      |
| 阶段三   | AI 对话功能               | 3 天      |
|          | - 对话 API (SSE)          | 1 天      |
|          | - 前端对话界面            | 1.5 天    |
|          | - 会话历史管理            | 0.5 天    |
| 阶段四   | 用例生成 Agent            | 4 天      |
|          | - Agent 工具开发          | 1 天      |
|          | - 用例生成逻辑            | 1.5 天    |
|          | - 前端预览组件            | 1.5 天    |
| 阶段五   | 联调测试                  | 2 天      |
|          | - 前后端联调              | 1 天      |
|          | - AI 服务联调             | 1 天      |
| **合计** |                           | **14 天** |

### 8.2 依赖项

**Python 依赖 (ai-service/requirements.txt)**

```
fastapi==0.109.0
uvicorn==0.27.0
langchain==0.1.4
langchain-community==0.0.16
chromadb==0.4.22
sentence-transformers==2.3.1
pydantic==2.5.3
python-multipart==0.0.6
sse-starlette==1.8.2
httpx==0.26.0
pyyaml==6.0.1
```

**前端新增依赖**

```
marked==11.1.1      # Markdown渲染
highlight.js==11.9.0 # 代码高亮
```

## 九、配置说明

### 9.1 SpringBoot 配置

```properties
# application.properties 新增
ai.service.url=http://localhost:8001
ai.service.api-key=your-api-key
```

### 9.2 环境变量

```bash
# .env (ai-service)
DEEPSEEK_API_KEY=sk-xxxxxxxx
PLATFORM_BASE_URL=http://localhost:8080
```

## 十、接口规范

### 10.1 AI 对话接口

**请求**

```json
POST /autotest/ai/chat
{
    "project_id": "项目ID",
    "message": "用户消息",
    "use_rag": true,
    "conversation_id": "会话ID(新建时为空)"
}
```

**响应 (SSE)**

```
data: {"type": "start"}
data: {"type": "content", "delta": "你好"}
data: {"type": "content", "delta": "，我是"}
data: {"type": "content", "delta": "AI助手"}
data: {"type": "end"}
```

### 10.2 用例生成接口

**请求**

```json
POST /autotest/ai/generate/case
{
    "project_id": "项目ID",
    "user_requirement": "测试用户登录接口",
    "selected_apis": ["api_id_1", "api_id_2"]
}
```

**响应**

```json
{
  "case_name": "用户登录测试",
  "case_description": "测试用户登录接口",
  "case_type": "API",
  "case_level": "P1",
  "case_module_id": "模块ID",
  "case_apis": [
    {
      "api_id": "接口ID",
      "api_name": "用户登录",
      "api_method": "POST",
      "api_path": "/api/login",
      "step_description": "用户登录",
      "header": "{\"Content-Type\": \"application/json\"}",
      "body": "{\"username\": \"{{username}}\", \"password\": \"{{password}}\"}",
      "assertion": "[...]"
    }
  ]
}
```

## 十一、注意事项

1. **接口数据同步**: 每次项目接口变动时需触发同步到知识库
2. **RAG 开关**: 用户可选择是否启用 RAG，关闭时为纯 LLM 对话
3. **流式输出**: 必须支持 SSE 流式，提升用户体验
4. **错误处理**: AI 服务调用失败时需有降级处理
5. **项目隔离**: 所有数据操作必须带 project_id 过滤
6. **安全**: API Key 等敏感信息存数据库，加密存储

## 十二、相关文档

- [后端 README](../platform-backend/README.md)
- [前端 README](../platform-frontend/README.md)
- [引擎 README](../TestEngin/README.md)
