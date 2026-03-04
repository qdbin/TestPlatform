# Vue Router路由管理

## 什么是Vue Router？

Vue Router是Vue.js官方的路由管理器（Router：路由器）。它和Vue.js的核心深度集成，让构建单页面应用（SPA：Single Page Application）变得易如反掌。

**英文全称**：Vue Router = Vue + Router（路由）
**中文理解**：页面导航管理员，负责管理"在哪个地址显示哪个页面"

**生活类比**：就像酒店的楼层导航系统，你告诉它想去哪个房间（URL地址），它就告诉你该怎么走（显示哪个组件）。

## 核心概念

### 1. 路由（Route）

**英文原意**：路线、路径
**技术含义**：URL路径与组件的映射关系

```javascript
// 定义路由映射
const routes = [
  { path: '/home', component: Home },
  { path: '/about', component: About }
]
```

### 2. 路由器（Router）

**英文原意**：路由器
**技术含义**：管理所有路由的对象

```javascript
// 创建路由器实例
const router = new VueRouter({
  routes // （缩写）相当于 routes: routes
})
```

### 3. 路由视图（Router View）

**英文原意**：路由视图
**技术含义**：显示匹配组件的占位符

```html
<!-- 路由出口 -->
<!-- 路由匹配到的组件将渲染在这里 -->
<router-view></router-view>
```

## 基本使用

### 1. 安装和配置

```javascript
// 1. 引入Vue和VueRouter
import Vue from 'vue'
import VueRouter from 'vue-router'

// 2. 使用VueRouter插件
Vue.use(VueRouter)

// 3. 定义路由组件
const Home = { template: '<div>首页</div>' }
const About = { template: '<div>关于</div>' }

// 4. 定义路由映射
const routes = [
  { path: '/home', component: Home },
  { path: '/about', component: About }
]

// 5. 创建router实例
const router = new VueRouter({
  routes // 简写，相当于 routes: routes
})

// 6. 创建和挂载根实例
new Vue({
  router,  // 注入路由器
  template: `
    <div id="app">
      <h1>Hello App!</h1>
      <p>
        <!-- 使用 router-link 组件来导航 -->
        <router-link to="/home">Go to Home</router-link>
        <router-link to="/about">Go to About</router-link>
      </p>
      <!-- 路由出口 -->
      <router-view></router-view>
    </div>
  `
}).$mount('#app')
```

### 2. 路由导航

#### 声明式导航（使用router-link）

```html
<!-- 普通链接 -->
<router-link to="/home">首页</router-link>

<!-- 带参数的链接 -->
<router-link to="/user/123">用户123</router-link>

<!-- 命名路由 -->
<router-link :to="{ name: 'user', params: { userId: 123 }}">用户123</router-link>

<!-- 带查询参数的链接 -->
<router-link :to="{ path: 'register', query: { plan: 'private' }}">注册</router-link>
```

#### 编程式导航（使用代码导航）

```javascript
// 字符串路径
this.$router.push('/home')

// 对象形式
this.$router.push({ path: '/home' })

// 命名路由
this.$router.push({ name: 'user', params: { userId: '123' }})

// 带查询参数
this.$router.push({ path: 'register', query: { plan: 'private' }})
```

## 在LiuMa项目中的路由配置

### 1. 路由结构分析

**文件路径**：`/src/router/index.js`

```javascript
// 导入组件（使用懒加载）
const login = () => import('@/views/login')
const index = () => import('@/views/index')
const Homepage = () => import('@/views/home/dashboard')

// 公共组件中心
const FileManage = () => import('@/views/baseCenter/fileManage')
const CommonParam = () => import('@/views/baseCenter/commonParam')
const FuncManage = () => import('@/views/baseCenter/funcManage')

// 环境中心
const EnvManage = () => import('@/views/envCenter/envManage')
const EngineManage = () => import('@/views/envCenter/engineManage')
const DeviceManage = () => import('@/views/envCenter/deviceManage')
```

### 2. 路由权限控制

```javascript
{
  path: '/common/fileManage',
  name: '文件管理',
  component: FileManage,
  meta: {
    requirePerm: "NORMAL_MENU",    // 需要的权限
    requireAuth: true            // 是否需要登录
  }
}
```

### 3. 动态路由参数

```javascript
{
  path: '/common/funcManage/edit/:functionId',  // :functionId 是动态参数
  name: '函数编辑',
  component: FuncEdit,
  meta: {
    requirePerm: "NORMAL_MENU",
    requireAuth: true
  }
}
```

**使用方式**：
```javascript
// 在组件中获取参数
this.$route.params.functionId
```

### 4. 嵌套路由（子路由）

```javascript
{
  path: '/index',
  name: '首页',
  component: index,
  children: [
    {
      path: '/home/dashboard',
      name: '主页',
      component: Homepage,
      meta: {
        requireAuth: true
      }
    },
    // 其他子路由...
  ]
}
```

## 路由守卫（Navigation Guards）

**英文原意**：导航守卫
**中文理解**：路由的"安检员