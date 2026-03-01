# AI 智能测试助手 - 实施检查清单

## 开发前检查

- [ ] 已阅读项目 README 和源码
- [ ] 已了解现有数据模型（Api、Case、CaseApi 关系）
- [ ] 已确认技术方案 SPEC.md
- [ ] 已确认 TASKS.md 任务列表

---

## 阶段一: 基础设施搭建

### 1.1 FastAPI 服务框架

- [ ] 创建 ai-service 目录结构
- [ ] 安装 Python 依赖包
- [ ] 配置 FastAPI 主入口
- [ ] 配置 CORS 跨域
- [ ] 测试服务启动

### 1.2 Chroma + Embedding

- [ ] 集成 sentence-transformers
- [ ] 测试 bge-small-zh-v1.5 模型加载
- [ ] 配置 Chroma 持久化存储
- [ ] 测试向量存储和检索

### 1.3 SpringBoot 数据库

- [ ] 编写 V1.26\_\_init_ai.sql
- [ ] 创建 AiKnowledge 实体类
- [ ] 创建 AiConversation 实体类
- [ ] 创建 AiConfig 实体类
- [ ] 创建 AiApiIndex 实体类
- [ ] 创建对应 Mapper 接口
- [ ] 创建 Mapper XML 文件

---

## 阶段二: RAG 知识库

### 2.1 知识库 CRUD

- [ ] 后端: GET /autotest/ai/knowledge 列表接口
- [ ] 后端: POST /autotest/ai/knowledge 新增接口
- [ ] 后端: PUT /autotest/ai/knowledge/{id} 更新接口
- [ ] 后端: DELETE /autotest/ai/knowledge/{id} 删除接口
- [ ] 前端: knowledgeManage.vue 组件

### 2.2 文档索引

- [ ] FastAPI: POST /ai/knowledge/index 索引接口
- [ ] 实现文档分块(chinese_text_splitter)
- [ ] 实现 embedding 向量化
- [ ] 实现 Chroma 存储
- [ ] 索引状态回写到数据库

### 2.3 接口同步

- [ ] 后端: POST /autotest/ai/knowledge/sync-api
- [ ] 查询项目所有接口
- [ ] 转换为知识库格式
- [ ] 批量索引

---

## 阶段三: AI 对话

### 3.1 对话 API

- [ ] 后端: POST /autotest/ai/chat SSE 接口
- [ ] 后端: SSE 流式响应处理
- [ ] FastAPI: 对话路由
- [ ] LLM 集成(DeepSeek)
- [ ] RAG 检索集成

### 3.2 前端对话界面

- [ ] 创建 views/aiAssistant/index.vue
- [ ] 路由配置
- [ ] 左侧菜单栏(新建对话、历史列表)
- [ ] 右侧聊天窗口
- [ ] 消息气泡组件
- [ ] SSE 接收处理
- [ ] Markdown 渲染(marked)
- [ ] RAG 开关组件
- [ ] 文件上传组件

### 3.3 会话历史

- [ ] 后端: GET /autotest/ai/chat/history 列表
- [ ] 后端: GET /autotest/ai/chat/{id} 详情
- [ ] 后端: DELETE /autotest/ai/chat/{id} 删除
- [ ] 前端: 加载历史列表

---

## 阶段四: 用例生成 Agent

### 4.1 Agent 工具

- [ ] 平台 API 客户端封装
- [ ] Tool: get_api_list
- [ ] Tool: get_api_detail
- [ ] Tool: save_case
- [ ] Tool: search_knowledge

### 4.2 用例生成

- [ ] 后端: POST /autotest/ai/generate/case
- [ ] FastAPI: Agent 路由
- [ ] Agent 工作流程实现
- [ ] LLM 生成用例 JSON
- [ ] 前端: 用例预览组件

### 4.3 前端预览

- [ ] casePreview.vue 组件
- [ ] 用例 JSON 展示
- [ ] 编辑功能
- [ ] 确认保存按钮
- [ ] 调用 CaseService 落库

---

## 阶段五: 联调测试

### 5.1 接口联调

- [ ] 前后端 API 对接
- [ ] SSE 流式输出测试
- [ ] 文件上传功能测试
- [ ] 会话历史功能测试

### 5.2 AI 功能测试

- [ ] 纯 LLM 对话测试
- [ ] RAG 知识问答测试
- [ ] 接口同步测试
- [ ] 用例生成完整流程测试

### 5.3 性能测试

- [ ] 向量化性能
- [ ] LLM 响应时间
- [ ] SSE 流式延迟

---

## 上线前检查

- [ ] 代码注释完整(30%以上)
- [ ] 无敏感信息泄露
- [ ] 异常处理完善
- [ ] 日志记录完整
- [ ] 配置可外部化
- [ ] 项目隔离正常

---

## 验收标准

| 功能     | 验收条件                             |
| -------- | ------------------------------------ |
| 知识库   | 文档上传成功，索引完成，可检索       |
| 对话     | SSE 流式输出正常，会话保存成功       |
| 用例生成 | 完整流程:选接口 → 生成 → 预览 → 落库 |
| 项目隔离 | 不同项目数据完全隔离                 |
