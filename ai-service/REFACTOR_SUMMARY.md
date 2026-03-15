# AI服务重构总结

## 重构完成内容

### 1. LangChain 1.x 全面升级

#### 1.1 LCEL (LangChain Expression Language) 改造

- **llm_service.py**: 使用 `llm | StrOutputParser()` LCEL链替代传统链式调用
- **query_rewrite.py**: 使用 LCEL 构建查询改写链 `prompt | llm.bind(response_format={...}) | JsonOutputParser()`
- 支持 `invoke()` / `ainvoke()` / `astream()` 标准化接口

#### 1.2 异步架构优化

- 移除 `ThreadPoolExecutor` 阻塞式代码
- `stream_chat()` 改为纯异步生成器实现
- 新增 `achat()` / `achat_with_stream()` 异步方法

### 2. LangSmith 全链路观测

#### 2.1 @traceable 装饰器重构

- **traceable.py**: 使用 `langsmith.trace` 上下文管理器替代旧版API
- 支持自定义 `run_type`, `name`, `inputs`, `outputs`
- 兼容 LangChain 1.x 的追踪机制

#### 2.2 关键步骤埋点

- 文档索引阶段
- RAG检索阶段 (查询改写、BM25检索、向量检索、RRF融合、重排序)
- 用例生成阶段 (接口拉取、接口筛选、Prompt构建、LLM生成、Pydantic校验)

### 3. 核心Bug修复

#### 3.1 查询改写失效问题

- **问题**: 改写后的查询未实际用于检索
- **修复**: `rag_service.py` 中 `search_with_status()` 方法现在正确使用改写后的查询列表

#### 3.2 "正在思考"提示词问题

- **问题**: AI响应开头包含"正在思考，请稍候..."
- **修复**: `agent_service.py` 中 `stream_chat()` 方法已移除该提示词

#### 3.3 流式输出阻塞问题

- **问题**: 使用 ThreadPoolExecutor 导致流式输出阻塞
- **修复**: 改为纯异步生成器实现

### 4. Pydantic校验失败重试机制

#### 4.1 case_workflow.py 增强

- 新增 `RetryContext` 数据类
- `_generate_and_validate_with_retry()` 方法支持最多2次重试
- 错误上下文累积，每次重试都包含前次的错误信息

### 5. 评估体系重构

#### 5.1 Pytest + LangSmith 评估框架

- **test_rag_eval.py**: RAG评估测试模块

  - 检索指标: Recall, Precision, MRR
  - 生成指标: Faithfulness, Relevance, Completeness
  - LangSmith数据集集成
- **test_agent_eval.py**: Agent评估测试模块

  - 用例生成成功率
  - Schema校验通过率
  - 步骤数量正确率
  - API选择相关性
  - 输出稳定性

#### 5.2 评估数据集构建

- **knowledge_docs.jsonl**: 15篇接口文档，30个片段
- **rag_eval_dataset.jsonl**: 20个RAG评估问答对
- **agent_eval_dataset.jsonl**: 30个用例生成测试场景

#### 5.3 评估环境初始化

- **setup_eval.py**: 一键初始化评估环境
  - LangSmith数据集创建
  - 知识文档索引
  - 环境配置验证

### 6. 单元测试和接口测试

#### 6.1 单元测试

- **test_llm_service.py**: LLM服务单元测试
- **test_rag_service.py**: RAG服务单元测试
- **test_agent_service.py**: Agent服务单元测试

#### 6.2 集成测试

- **test_smoke_requests.py**: 冒烟测试
  - 健康检查接口
  - RAG知识库接口
  - Agent用例生成接口
  - 流式对话接口

### 7. 环境变量配置

#### 7.1 .env 文件支持

```bash
DEEPSEEK_API_KEY=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
LANGSMITH_TRACING=true
PLATFORM_BASE_URL=
```

- 支持从环境变量读取配置
- 添加属性别名 (LANGSMITH_API_KEY, DEEPSEEK_API_KEY等)

### 8. Prompt优化

#### 8.1 assistant_prompts.py

- **CASE_GENERATION_PROMPT**: 结构化Prompt，包含角色定义、约束条件、工作流、Few-shot示例
- **CASE_RETRY_PROMPT**: 重试Prompt，包含错误上下文和修正指导

## 文件变更清单

### 核心服务文件

| 文件                                    | 变更类型 | 说明               |
| --------------------------------------- | -------- | ------------------ |
| app/observability/traceable.py          | 重写     | LangChain 1.x 兼容 |
| app/services/llm_service.py             | 重写     | LCEL链、异步支持   |
| app/services/retrieval/query_rewrite.py | 重写     | LCEL链             |
| app/services/rag_service.py             | 修改     | 查询改写Bug修复    |
| app/services/agent_service.py           | 修改     | 流式输出优化       |
| app/services/case_workflow.py           | 修改     | 重试机制           |
| app/prompts/assistant_prompts.py        | 修改     | Prompt优化         |
| app/config.py                           | 修改     | 环境变量支持       |

### 评估体系文件

| 文件                                | 变更类型 | 说明           |
| ----------------------------------- | -------- | -------------- |
| evals/setup_eval.py                 | 新增     | 评估环境初始化 |
| evals/test_rag_eval.py              | 新增     | RAG评估测试    |
| evals/test_agent_eval.py            | 新增     | Agent评估测试  |
| evals/data/knowledge_docs.jsonl     | 新增     | 知识文档数据   |
| evals/data/rag_eval_dataset.jsonl   | 新增     | RAG评估数据    |
| evals/data/agent_eval_dataset.jsonl | 新增     | Agent评估数据  |

### 测试文件

| 文件                                     | 变更类型 | 说明          |
| ---------------------------------------- | -------- | ------------- |
| tests/unit/test_llm_service.py           | 新增     | LLM单元测试   |
| tests/unit/test_rag_service.py           | 新增     | RAG单元测试   |
| tests/unit/test_agent_service.py         | 新增     | Agent单元测试 |
| tests/integration/test_smoke_requests.py | 修改     | 冒烟测试      |
| run_tests.py                             | 新增     | 测试运行脚本  |

### 配置文件

| 文件       | 变更类型 | 说明         |
| ---------- | -------- | ------------ |
| .env       | 新增     | 环境变量配置 |
| pytest.ini | 修改     | Pytest配置   |

## 使用方法

### 1. 启动AI服务

```bash
conda activate aitest
cd ai-service
python -m app.main
```

### 2. 初始化评估环境

```bash
python -m evals.setup_eval
```

### 3. 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行单元测试
python run_tests.py unit

# 运行集成测试
python run_tests.py integration

# 运行冒烟测试
python run_tests.py smoke

# 运行评估测试
python run_tests.py eval
```

### 4. 查看LangSmith追踪

访问 https://smith.langchain.com 查看追踪记录和评估结果

## 待办事项

- [ ] 启动后端和前端服务进行端到端测试
- [ ] 验证流式输出在前端的显示效果
- [ ] 运行完整的RAG和Agent评估
- [ ] 根据评估结果进一步优化Prompt

## 技术栈

- **LangChain**: 1.x (LCEL, Runnable)
- **LangSmith**: 追踪和评估
- **FastAPI**: Web框架
- **Chroma**: 向量数据库
- **Pytest**: 测试框架
- **DeepSeek**: LLM模型
