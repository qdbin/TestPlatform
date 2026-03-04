# AI 相关模块 MVP 任务清单（待办）

## 需求分析

### 需求澄清与对齐（必须输出到实现约束）
- [ ] 明确“切页面不断”的默认策略与可选“离开确认中断”策略开关位置
- [ ] 明确“接口生成”的触发条件与输出形态（仅生成建议/直接生成可保存接口草稿）
- [ ] 明确“用例生成”输出必须对齐的后端字段集合（CaseRequest + CaseApiRequest）
- [ ] 明确知识库索引状态在 DB/UI 的最终呈现字段（indexed/degraded/errorMessage/vectorCount）

### 依赖关系梳理
- [ ] 梳理前端复用组件清单：接口新增组件、用例新增组件（API）
- [ ] 梳理后端可复用接口清单：api/list、api/save、case/save、knowledge CRUD/index
- [ ] 梳理 AI 服务对后端调用的鉴权方式与超时/重试策略

## 设计实现

### P0：知识库弹窗化（UI 与交互）
- [ ] 左侧“知识库”Tab 仅保留入口按钮，移除目录树与所有文档操作控件
- [ ] 新增“知识库管理”弹窗：目录树展示、节点操作、新建目录/文档入口
- [ ] 文档查看/编辑弹窗在“知识库管理”弹窗内联动（避免多处状态不一致）
- [ ] 删除目录前端提示与后端拦截一致（目录存在子节点时禁止删除）

### P0：RAG 向量检索恢复（Embedding 修复）
- [ ] 将默认 Embedding 改为 OpenAI 兼容 Embeddings API（DeepSeek base_url）
- [ ] 增加 RAG 状态诊断接口：embedding 可用性、最近错误、向量库统计
- [ ] 索引接口返回结构化结果（indexed/degraded/error/vectorCount），前端展示明确状态
- [ ] 检索接口返回引用片段与元信息（文档id/名称/片段），用于答案引用与调试

### P0：对话真流式（端到端）
- [ ] FastAPI 改造 chat_stream：从 LLM 流式输出逐 token 直接 SSE yield
- [ ] SpringBoot 转发层：客户端断开时中断下游读流任务并回收资源
- [ ] 前端 SSE 读取：实时拼接、即时渲染、允许停止；避免“读完才显示”
- [ ] Mermaid/Markdown 渲染与流式拼接兼容（避免频繁全量重渲染卡顿）

### P0：路由切换不断（后台不中断）
- [ ] 移除“离开页面即 abort”的默认行为（或引入 keep-alive 承载 AI 页面）
- [ ] 若开启“离开确认中断”：在 AI 页面实现 beforeRouteLeave 弹框并按用户选择 abort
- [ ] 补充回归：切换到其他页面后返回，流式输出仍可继续追加或至少不会破坏会话状态

### P0：relativeURL.replace 异常修复
- [ ] 定位触发链路（AI 模块 buildApiUrl/fetch/ajax wrapper）
- [ ] 统一保证 URL 输入为 string，并对非法值做显式错误（不吞异常）
- [ ] 增加最小回归验证：对话发送、知识库 CRUD、索引、用例生成均不再触发该报错

### P0：用例生成（接口ID驱动 + 可编辑预览 + 真保存）
- [ ] FastAPI：生成前查询并校验 selectedApis 均为本项目有效 apiId
- [ ] FastAPI：对“不存在接口”返回 missingApis，触发前端进入“接口生成”弹窗流程
- [ ] FastAPI：提示词严格约束输出为 CaseRequest（含 caseApis[].apiId）
- [ ] 前端：用例预览改为复用 apiCaseEdit 组件并支持编辑（不使用 JSON `<pre>`）
- [ ] 前端：保存动作调用既有 /autotest/case/save，并以真实返回决定提示
- [ ] 后端：移除/改造占位 /autotest/ai/generate/case/save，避免误导
- [ ] 后端：保存时增加 apiId 存在性与 projectId 一致性校验（仅限 AI 路径或通用校验）

### P1：接口生成（不存在接口先生成再保存）
- [ ] FastAPI：实现“接口草稿生成”能力（method/path/name/headers/body/query/rest/描述/模块）
- [ ] 前端：复用接口管理新增接口组件渲染草稿，用户编辑后保存到后端 api 表
- [ ] 前端：保存成功后自动回填新 apiId 到“用例生成”已选接口集合

### 测试与验收（必须落地）
- [ ] FastAPI：补齐 tests/ 单测（RAG/对话流式/用例生成结构校验/接口生成）
- [ ] SpringBoot：补齐 src/test/java AI 相关测试（知识库删除保护/代理透传/最小保存冒烟）
- [ ] 端到端：使用真实账号 LMadmin 完成 RAG、对话流式、用例生成与落库验收
