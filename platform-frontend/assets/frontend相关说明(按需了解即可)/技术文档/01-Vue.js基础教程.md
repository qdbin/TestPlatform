# Vue.js基础教程

## 什么是Vue.js？

Vue.js（读音 /vjuː/，类似于 **view**）是一套用于构建用户界面的**渐进式框架**（Progressive Framework）。

**大白话解释**：Vue就像是一套乐高积木，你可以只用其中几块，也可以用整套来搭建复杂的应用。它不像某些框架那样"全有或全无"，而是可以根据需要逐步采用。

## 核心概念

### 1. 声明式渲染（Declarative Rendering）

**英文原意**：声明式渲染
**中文理解**：你只需要告诉Vue"想要什么"，不用管"怎么做"

**传统方式**（命令式）：
```javascript
// 命令式：一步步告诉浏览器怎么做
var div = document.getElementById('app')
div.innerHTML = 'Hello World'
```

**Vue方式**（声明式）：
```html
<!-- 声明式：只告诉Vue想要什么结果 -->
<div id="app">
  {{ message }}
</div>
```

```javascript
// Vue实例
var app = new Vue({
  el: '#app',
  data: {
    message: 'Hello World!'
  }
})
```

### 2. 组件系统（Component System）

**英文原意**：组件系统
**中文理解**：把复杂的页面拆分成可复用的小块

**生活类比**：就像搭积木，每个积木块（组件）都是独立的，可以重复使用，组合起来就能搭建复杂的建筑。

```javascript
// 定义一个组件
Vue.component('todo-item', {
  props: ['todo'],
  template: '<li>{{ todo.text }}</li>'
})

// 使用组件
new Vue({
  el: '#app',
  data: {
    groceryList: [
      { id: 0, text: '蔬菜' },
      { id: 1, text: '奶酪' },
      { id: 2, text: '随便其它什么人吃的东西' }
    ]
  }
})
```

### 3. 响应式数据（Reactive Data）

**英文原意**：响应式数据
**中文理解**：数据变了，界面自动更新

**生活类比**：就像温度计，温度（数据）变化了，水银柱（界面）会自动上升或下降，你不用手动去调整。

```javascript
var vm = new Vue({
  el: '#example',
  data: {
    message: 'Hello'
  }
})

// 改变数据
vm.message = 'Goodbye'
// 界面会自动更新，无需手动操作DOM
```

## Vue实例详解

### 创建一个Vue实例

```javascript
var vm = new Vue({
  // 选项
  el: '#app',        // 挂载点（要控制的DOM元素）
  data: {            // 数据对象
    message: 'Hello Vue!'
  },
  methods: {         // 方法定义
    reverseMessage: function () {
      this.message = this.message.split('').reverse().join('')
    }
  }
})
```

**参数说明**：
- **el**（element）：告诉Vue要控制页面上的哪个元素
- **data**：存储页面需要显示的数据
- **methods**：定义页面中需要用到的方法

### 数据绑定

#### 1. 插值表达式（Interpolation）
```html
<!-- 双大括号语法 -->
<span>{{ message }}</span>
```

#### 2. 指令（Directives）

**英文原意**：指令
**中文理解**：Vue提供的特殊属性，以`v-`开头

```html
<!-- v-bind: 绑定属性 -->
<img v-bind:src="imageSrc">

<!-- v-if: 条件渲染 -->
<p v-if="seen">现在你看到我了</p>

<!-- v-for: 列表渲染 -->
<li v-for="item in items">{{ item.text }}</li>

<!-- v-on: 事件监听 -->
<button v-on:click="reverseMessage">反转消息</button>
```

## 在LiuMa项目中的实际应用

### 1. 登录组件实例

**文件路径**：`/src/views/login.vue`

```javascript
export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loading: false
    }
  },
  methods: {
    handleLogin() {
      this.loading = true
      // 登录逻辑...
    }
  }
}
```

### 2. 数据展示组件

**文件路径**：`/src/views/home/dashboard.vue`

```javascript
data() {
  return {
    // 统计数据
    statistics: {
      apiCaseCount: 0,
      webCaseCount: 0,
      appCaseCount: 0
    },
    // 图表数据
    chartData: {
      dateList: [],
      apiData: [],
      webData: [],
      appData: []
    }
  }
},
mounted() {
  // 组件挂载后获取数据
  this.loadStatistics()
  this.loadChartData()
}
```

## 生命周期钩子（Lifecycle Hooks）

**英文原意**：生命周期钩子
**中文理解**：Vue实例从创建到销毁过程中的各个阶段

**生活类比**：就像人的生命周期（出生、成长、工作、退休），Vue实例也有它的生命周期。

```javascript
new Vue({
  data: {
    a: 1
  },
  created: function () {
    // `this` 指向 vm 实例
    console.log('a is: ' + this.a)
  },
  mounted: function() {
    console.log('组件已挂载到DOM')
  },
  updated: function() {
    console.log('数据已更新')
  },
  destroyed: function() {
    console.log('组件已销毁')
  }
})
```

**常用生命周期**：
- **created**：实例创建完成后调用，此时数据已初始化
- **mounted**：el被新创建的vm.$el替换，并挂载到实例上之后调用
- **updated**：数据更新导致的虚拟DOM重新渲染和打补丁后调用
- **destroyed**：Vue实例销毁后调用

## 计算属性（Computed Properties）

**英文原意**：计算属性
**中文理解**：基于已有数据计算出新数据，并且会自动缓存

```javascript
var vm = new Vue({
  el: '#example',
  data: {
    firstName: 'Foo',
    lastName: 'Bar'
  },
  computed: {
    // 计算属性的 getter
    fullName: function () {
      // `this` 指向 vm 实例
      return this.firstName + ' ' + this.lastName
    }
  }
})
```

**与普通方法的区别**：
- 计算属性会缓存结果，只有依赖的数据变化时才会重新计算
- 方法每次调用都会重新执行

## 侦听器（Watchers）

**英文原意**：侦听器
**中文理解**：监听数据变化，执行相应操作

```javascript
var vm = new Vue({
  data: {
    question: '',
    answer: 'I cannot give you an answer until you ask a question!'
  },
  watch: {
    // 如果 `question` 发生改变，这个函数就会运行
    question: function (newQuestion, oldQuestion) {
      this.answer = 'Waiting for you to stop typing...'
      this.debouncedGetAnswer()
    }
  }
})
```

## 常见问题解答

### Q1：Vue和jQuery有什么区别？

**A**：
- **jQuery**：主要解决DOM操作和浏览器兼容性问题，需要你手动操作DOM
- **Vue**：关注数据层，数据变化自动更新DOM，几乎不需要手动操作DOM

**类比**：jQuery像是手动档汽车，需要你手动换挡；Vue像是自动档汽车，自动帮你处理换挡。

### Q2：什么时候该用methods，什么时候用computed？

**A**：
- **methods**：执行操作、事件处理、需要传参的函数
- **computed**：根据已有数据计算新数据，需要缓存的场景

### Q3：Vue的响应式系统是如何工作的？

**A**：Vue使用**数据劫持**结合**发布者-订阅者模式**：
1. 通过Object.defineProperty()劫持各个属性的setter和getter
2. 在数据变动时发布消息给订阅者，触发相应的监听回调
3. 这个过程是自动的，开发者无需手动操作

## 最佳实践

### 1. 组件命名规范
```javascript
// 推荐：使用多单词命名
Vue.component('todo-item', {
  // ...
})

// 避免：使用单单词
Vue.component('todo', {
  // ...
})
```

### 2. 数据初始化
```javascript
data() {
  return {
    // 初始化所有需要响应式的数据
    message: '',
    list: [],
    obj: {}
  }
}
```

### 3. 避免直接操作DOM
```javascript
// 不推荐
document.getElementById('app').innerHTML = 'Hello'

// 推荐
this.message = 'Hello'  // 让Vue自动更新DOM
```

## 入门Demo：待办事项列表

```html
<!DOCTYPE html>
<html>
<head>
  <title>Vue Todo List Demo</title>
  <script src="https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"></script>
</head>
<body>
  <div id="todo-app">
    <h2>待办事项列表</h2>
    <input v-model="newTodo" @keyup.enter="addTodo" placeholder="添加新任务">
    <button @click="addTodo">添加</button>
    
    <ul>
      <li v-for="todo in todos" :key="todo.id">
        <span>{{ todo.text }}</span>
        <button @click="removeTodo(todo.id)">删除</button>
      </li>
    </ul>
    
    <p>总计：{{ totalTodos }} 项</p>
  </div>

  <script>
    new Vue({
      el: '#todo-app',
      data: {
        newTodo: '',
        todos: [
          { id: 1, text: '学习Vue.js基础' },
          { id: 2, text: '实践组件开发' }
        ],
        nextId: 3
      },
      computed: {
        totalTodos() {
          return this.todos.length
        }
      },
      methods: {
        addTodo() {
          if (this.newTodo.trim()) {
            this.todos.push({
              id: this.nextId++,
              text: this.newTodo.trim()
            })
            this.newTodo = ''
          }
        },
        removeTodo(id) {
          this.todos = this.todos.filter(todo => todo.id !== id)
        }
      }
    })
  </script>
</body>
</html>
```

## 学习建议

1. **先理解概念**：不要急于写代码，先理解Vue的核心概念
2. **多动手实践**：通过小项目巩固知识点
3. **阅读官方文档**：Vue官方文档非常详细，是最好的学习资料
4. **查看源码实现**：通过LiuMa项目的实际代码加深理解

## 下一步学习

掌握了Vue.js基础后，建议继续学习：
1. **Vue Router路由管理** - 实现单页面应用
2. **Vuex状态管理** - 管理复杂应用状态
3. **组件化开发** - 构建可复用的组件库

## 常见面试题

1. **Vue的双向数据绑定原理是什么？**
2. **computed和watch的区别？**
3. **Vue的生命周期有哪些？**
4. **Vue组件间的通信方式？**
5. **v-if和v-show的区别？**

通过本教程的学习，你应该对Vue.js有了基础的理解。接下来建议通过实际项目来加深理解，LiuMa项目中的各个组件都是很好的学习案例。