# 流马测试平台 - 前端应用

## 一、项目概述

### 1.1 项目定位

流马测试平台前端应用，采用 Vue 2 + Element UI 构建，为自动化测试平台提供可视化操作界面。

### 1.2 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 2.7.16 | 渐进式前端框架 |
| Vue Router | 3.6.5 | 路由管理 |
| Vuex | 3.6.2 | 状态管理 |
| Element UI | 2.15.13 | UI组件库 |
| Vite | 4.5.0 | 构建工具 |
| Axios | 1.6.2 | HTTP请求 |
| ECharts | 5.4.3 | 图表可视化 |
| Sass | 1.69.5 | CSS预处理 |

### 1.3 核心特性

- **低代码设计**：可视化配置，降低使用门槛
- **组件化开发**：基于 Element UI 的业务组件封装
- **响应式布局**：适配不同屏幕尺寸
- **实时通信**：WebSocket 实时查看执行进度

---

## 二、项目结构

```
platform-frontend/
├── src/
│   ├── main.js                 # 入口文件
│   ├── App.vue                 # 根组件
│   ├── router/
│   │   └── index.js            # 路由配置
│   ├── vuex/
│   │   └── store.js            # 状态管理
│   ├── utils/
│   │   ├── ajax.js             # HTTP请求封装
│   │   ├── base64.js           # Base64工具
│   │   ├── constant.js         # 常量定义
│   │   ├── jsonpath.js         # JSONPath工具
│   │   └── util.js              # 通用工具
│   └── views/                  # 页面视图
│       ├── caseCenter/         # 用例中心
│       ├── envCenter/          # 环境中心
│       ├── planCenter/         # 计划中心
│       ├── report/             # 测试报告
│       ├── system/             # 系统管理
│       ├── setting/            # 系统设置
│       ├── home/               # 首页看板
│       ├── common/             # 公共组件
│       ├── login.vue           # 登录页
│       └── index.vue           # 首页
├── static/                     # 静态资源
├── index.html                  # HTML模板
├── vite.config.js              # Vite配置
└── package.json                # 依赖配置
```

---

## 三、核心模块说明

### 3.1 用例中心 (caseCenter/)

| 页面 | 功能 |
|------|------|
| caseManage.vue | 用例列表管理 |
| apiCaseEdit.vue | API用例编辑 |
| appCaseEdit.vue | APP用例编辑 |
| webCaseEdit.vue | Web用例编辑 |
| interfaceManage.vue | 接口管理 |
| moduleManage.vue | 模块管理 |

**核心组件**：
- `requestBody.vue` - 请求体配置
- `requestHeader.vue` - 请求头配置
- `requestParamRule.vue` - 参数规则
- `assertion.vue` - 断言配置

### 3.2 环境中心 (envCenter/)

| 页面 | 功能 |
|------|------|
| envManage.vue | 环境管理 |
| engineManage.vue | 引擎管理 |
| deviceManage.vue | 设备管理 |
| deviceControl.vue | 设备控制 |

### 3.3 计划中心 (planCenter/)

| 页面 | 功能 |
|------|------|
| testPlan.vue | 测试计划 |
| testCollection.vue | 测试集合 |
| planEdit.vue | 计划编辑 |

### 3.4 测试报告 (report/)

| 页面 | 功能 |
|------|------|
| testReport.vue | 报告列表 |
| reportDetail.vue | 报告详情 |

### 3.5 系统管理 (system/)

| 页面 | 功能 |
|------|------|
| user.vue | 用户管理 |
| role.vue | 角色管理 |
| project.vue | 项目管理 |

---

## 四、核心功能实现

### 4.1 HTTP 请求封装

```javascript
// utils/ajax.js
import axios from 'axios';
import { Message } from 'element-ui';

const service = axios.create({
    baseURL: process.env.VUE_APP_BASE_API,
    timeout: 30000
});

// 请求拦截器
service.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = 'Bearer ' + token;
        }
        return config;
    },
    error => Promise.reject(error)
);

// 响应拦截器
service.interceptors.response.use(
    response => response.data,
    error => {
        Message.error(error.message);
        return Promise.reject(error);
    }
);

export default service;
```

### 4.2 状态管理 (Vuex)

```javascript
// vuex/store.js
export default new Vuex.Store({
    state: {
        user: {},
        project: {},
        token: '',
        permissions: []
    },
    mutations: {
        SET_USER(state, user) {
            state.user = user;
        },
        SET_TOKEN(state, token) {
            state.token = token;
        }
    },
    actions: {
        login({ commit }, userInfo) {
            // 登录逻辑
        }
    }
});
```

### 4.3 路由守卫

```javascript
// router/index.js
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    if (to.path === '/login') {
        next();
    } else {
        if (token) {
            next();
        } else {
            next('/login');
        }
    }
});
```

---

## 五、组件开发规范

### 5.1 目录组织

```
views/
└── 模块名/
    ├── index.vue              # 列表页
    ├── edit.vue              # 编辑页
    └── common/               # 公共组件
        ├── componentA.vue
        └── componentB.vue
```

### 5.2 组件通信

- **父子通信**：props + emit
- **兄弟通信**：Vuex
- **跨级通信**：Vuex 或 provide/inject

### 5.3 样式规范

- 使用 SCSS 预处理
- 遵循 BEM 命名规范
- 组件样式使用 scoped

---

## 六、常用开发指南

### 6.1 新增页面步骤

1. 在 `views/` 下创建页面目录和组件
2. 在 `router/index.js` 中配置路由
3. 在左侧导航配置中注册菜单

### 6.2 新增组件步骤

1. 在对应模块的 `common/` 目录下创建组件
2. 在页面中 import 并注册使用
3. 如需全局注册，在 `main.js` 中全局注册

### 6.3 API 调用示例

```javascript
// 在组件中调用API
import { getCaseList, saveCase } from '@/api/case';

export default {
    methods: {
        async loadCases() {
            const res = await getCaseList(this.queryParams);
            this.caseList = res.data;
        },
        async handleSave() {
            await saveCase(this.formData);
            this.$message.success('保存成功');
        }
    }
}
```

---

## 七、相关文档

- [前端业务逻辑设计](./assets/frontend相关说明(按需了解即可)/架构说明/业务逻辑设计.md)
- [Vue.js 基础教程](./assets/frontend相关说明(按需了解即可)/技术文档/01-Vue.js基础教程.md)
- [Element UI 组件库](./assets/frontend相关说明(按需了解即可)/技术文档/04-Element%20UI组件库.md)

---

## 八、构建与部署

### 8.1 开发环境

```bash
npm install
npm run dev
```

### 8.2 生产构建

```bash
npm run build
```

### 8.3 环境配置

- `.env.development` - 开发环境
- `.env.production` - 生产环境

---

## 九、联系与支持

- 演示平台：http://demo-ee.liumatest.cn
- 官网地址：http://www.liumatest.cn
- 社区地址：http://community.liumatest.cn
