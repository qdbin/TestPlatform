# 后端说明文档索引

本文档对后端模块 assets 目录下的说明文档进行索引和简要说明。

## 目录结构

```
platform-backend/
└── assets/
    └── backend相关说明(按需了解即可)/
        ├── PRD.md                      # 产品需求文档
        ├── 业务逻辑设计.md               # 核心业务流程设计
        ├── 数据设计.md                  # 数据库设计文档
        ├── 系统功能结构图.md             # 系统功能架构
        ├── 接口说明.md                  # API接口文档
        └── api/
            ├── AllInOne.md              # 整合接口文档
            ├── openapi.json             # OpenAPI规范
            ├── postman.json             # Postman导入文件
            └── swagger.json             # Swagger文档
```

## 文档说明

### 核心文档

| 文档 | 说明 | 优先级 |
|------|------|--------|
| 业务逻辑设计.md | 用户登录认证、测试用例管理、测试计划执行、引擎调度等核心流程 | ⭐⭐⭐ |
| 数据设计.md | 数据库表结构设计、ER关系、数据流转过程 | ⭐⭐⭐ |
| 系统功能结构图.md | 系统模块划分、功能职责 | ⭐⭐ |
| PRD.md | 产品需求定义 | ⭐ |

### 接口文档

| 文档 | 说明 |
|------|------|
| 接口说明.md | 详细接口文档 |
| swagger.json | Swagger/OpenAPI规范 |
| postman.json | Postman导入集合 |
| openapi.json | OpenAPI 3.0规范 |

## 快速定位

- **了解业务流程** → `业务逻辑设计.md`
- **查看数据结构** → `数据设计.md`
- **查阅API接口** → `api/swagger.json` 或 `接口说明.md`
- **理解功能模块** → `系统功能结构图.md`
