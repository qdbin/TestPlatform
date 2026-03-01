# AI 智能测试助手 - 待办事项

## 项目信息

- **项目名称**: AI 智能测试助手
- **技术栈**: SpringBoot + Vue + FastAPI + LangChain + Chroma
- **预计工时**: 14 天

---

## 阶段一: 基础设施搭建 (2 天)

### 1.1 FastAPI 服务框架搭建

- [ ] 创建 ai-service 目录结构
- [ ] 配置 FastAPI 主入口和路由
- [ ] 配置日志和异常处理
- [ ] 编写 requirements.txt 依赖

### 1.2 Chroma + Embedding 集成

- [ ] 集成 bge-small-zh-v1.5 embedding 模型
- [ ] 配置 Chroma 向量数据库
- [ ] 实现文档分块工具

### 1.3 SpringBoot 基础代码

- [ ] 创建 Flyway 数据库脚本 V1.26\_\_init_ai.sql
- [ ] 创建 AiKnowledge/AiConversation 实体类
- [ ] 创建对应 Mapper 接口和 XML

---

## 阶段二: RAG 知识库功能 (3 天)

### 2.1 知识库 CRUD API

- [ ] 后端 AiController 知识库接口
- [ ] 后端 AiService 知识库逻辑
- [ ] 前端知识库管理页面

### 2.2 文档索引流程

- [ ] FastAPI 文档索引接口
- [ ] 文档分块+向量化+存储流程
- [ ] 索引状态跟踪和更新

### 2.3 接口自动同步

- [ ] 项目接口同步到知识库功能
- [ ] 接口信息转换为文档格式
- [ ] 增量索引支持

---

## 阶段三: AI 对话功能 (3 天)

### 3.1 对话 API (SSE)

- [ ] 后端 AI 对话 Controller
- [ ] 后端 SSE 流式响应处理
- [ ] FastAPI 对话路由和 LLM 集成

### 3.2 前端对话界面

- [ ] 创建 aiAssistant 目录和页面
- [ ] 左侧历史会话列表
- [ ] 右侧聊天窗口(消息气泡)
- [ ] Markdown 渲染支持
- [ ] SSE 流式输出实现
- [ ] RAG 开关、上传附件功能

### 3.3 会话历史管理

- [ ] 会话列表查询
- [ ] 会话详情查看
- [ ] 会话删除功能

---

## 阶段四: 用例生成 Agent (4 天)

### 4.1 Agent 工具开发

- [ ] 平台 API 调用客户端封装
- [ ] LangChain Tools 定义
- [ ] 工具: get_api_list
- [ ] 工具: get_api_detail
- [ ] 工具: save_case
- [ ] 工具: search_knowledge

### 4.2 用例生成逻辑

- [ ] Agent 路由和流程设计
- [ ] 接口选择和详情获取
- [ ] LLM 生成用例 JSON
- [ ] 前端预览组件开发
- [ ] 用例确认和落库

### 4.3 前端预览组件

- [ ] casePreview.vue 组件
- [ ] 用例 JSON 展示和编辑
- [ ] 确认保存功能

---

## 阶段五: 联调测试 (2 天)

### 5.1 前后端联调

- [ ] SpringBoot 与 FastAPI 联调
- [ ] 前端与后端 API 联调
- [ ] SSE 流式输出测试

### 5.2 AI 服务联调

- [ ] LLM API 调用测试
- [ ] RAG 检索测试
- [ ] Agent 工具调用测试
- [ ] 端到端流程测试

---

## 关键里程碑

| 里程碑       | 完成标准                             |
| ------------ | ------------------------------------ |
| M1: 基础框架 | FastAPI 服务可启动，Chroma 可用      |
| M2: 知识库   | 文档上传 → 索引 → 检索全流程通       |
| M3: 对话     | SSE 流式对话正常，会话保存正常       |
| M4: 用例生成 | 完整流程:选接口 → 生成 → 预览 → 落库 |
| M5: 交付     | 前后端联调通过，可演示               |

---

## 技术栈清单

### 后端 (SpringBoot)

- [x] SpringBoot 2.6.0
- [x] MyBatis
- [x] Flyway

### 前端 (Vue)

- [x] Vue 2.7.16
- [x] Element UI 2.15.13
- [ ] marked (Markdown 渲染)
- [ ] highlight.js (代码高亮)

### AI 服务 (FastAPI)

- [ ] FastAPI 0.109.0
- [ ] LangChain 0.1.4
- [ ] Chroma 0.4.22
- [ ] bge-small-zh-v1.5
- [ ] DeepSeek API

---

## 配置文件清单

| 文件                 | 位置                                                    | 说明         |
| -------------------- | ------------------------------------------------------- | ------------ |
| V1.26\_\_init_ai.sql | platform-backend/src/main/resources/db/                 | 数据库脚本   |
| AiController.java    | platform-backend/src/main/java/com/autotest/controller/ | 后端控制器   |
| AiService.java       | platform-backend/src/main/java/com/autotest/service/    | 后端服务     |
| main.py              | ai-service/app/                                         | FastAPI 入口 |
| config.yaml          | ai-service/                                             | AI 服务配置  |
| requirements.txt     | ai-service/                                             | Python 依赖  |

---

## 注意事项

1. **项目隔离**: 所有接口必须带 project_id 过滤
2. **RAG 开关**: 用户可选择是否启用 RAG
3. **流式输出**: 对话必须支持 SSE 流式
4. **错误处理**: AI 服务调用失败需有降级处理
5. **API 安全**: API Key 等敏感信息加密存储
