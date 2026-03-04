# jQuery基础教程

## 什么是jQuery？

jQuery是一个快速、小巧、功能丰富的JavaScript库。它使HTML文档遍历和操作、事件处理、动画和Ajax等操作变得更加简单。

**英文原意**：JavaScript Query（JavaScript查询）
**中文理解**：JavaScript的"瑞士军刀"，让复杂的JavaScript操作变得简单

**生活类比**：就像用遥控器控制电视一样，jQuery让你用简单的指令控制复杂的网页操作，而不需要了解电视内部的复杂电路。

### jQuery的核心优势

| 优势 | 说明 | 对比原生JavaScript |
|------|------|-------------------|
| **简洁的语法** | `$('selector').action()` | `document.querySelector('selector').action()` |
| **跨浏览器兼容** | 自动处理浏览器差异 | 需要手动处理兼容性问题 |
| **链式调用** | `$('#box').addClass('active').show()` | 需要多次获取元素 |
| **丰富的选择器** | CSS选择器 + jQuery扩展 | 有限的选择器 |
| **强大的DOM操作** | 一行代码完成复杂操作 | 多行代码实现 |
| **完善的Ajax支持** | 简单的API | 复杂的XMLHttpRequest |

## 为什么选择jQuery？

### 1. 技术选型对比

| 技术 | 发布时间 | 特点 | 适用场景 |
|------|----------|------|----------|
| **jQuery** | 2006年 | 成熟稳定、插件丰富 | 传统项目、快速开发 |
| **原生JS** | 1995年 | 性能好、无需依赖 | 现代浏览器、性能要求高 |
| **Vue/React** | 2013/2014年 | 组件化、响应式 | 大型单页应用 |
| **Alpine.js** | 2019年 | 轻量级、Vue语法 | 简单交互、小型项目 |

### 2. jQuery在LiuMa项目中的作用

在LiuMa项目中，jQuery主要用于：
- **DOM操作**：处理Element UI组件的底层DOM
- **Ajax请求**：处理一些简单的异步请求
- **事件处理**：处理用户交互事件
- **工具函数**：简化一些常见的JavaScript操作

**注意**：现代Vue项目主要使用Vue的数据绑定和组件系统，jQuery作为补充工具使用。

## 核心概念详解

### 1. 选择器（Selector）

**英文原意**：选择器
**技术含义**：用于查找和选择HTML元素

```javascript
// 基本选择器
$('#id')                    // ID选择器，等价于 document.getElementById('id')
$('.class')                 // 类选择器，等价于 document.getElementsByClassName('class')
$('tag')                   // 标签选择器，等价于 document.getElementsByTagName('tag')

// 组合选择器
$('.class1.class2')        // 同时包含两个类
$('.class1, .class2')      // 选择多个元素
$('.parent > .child')      // 直接子元素
$('.ancestor .descendant') // 后代元素

// 属性选择器
$('[href]')                // 有href属性的元素
$('[href="value"]')        // href属性等于value的元素
$('[href^="https"]')       // href属性以https开头
$('[href$=".pdf"]')        // href属性以.pdf结尾
$('[href*="google"]')      // href属性包含google

// 表单选择器
$(':input')                // 所有表单元素
$(':text')                  // 所有type="text"的input
$(':checkbox')              // 所有复选框
$(':radio')                 // 所有单选框
$(':selected')              // 被选中的option
$(':checked')               // 被选中的checkbox或radio

// 过滤选择器
$(':first')                 // 第一个元素
$(':last')                  // 最后一个元素
$(':even')                  // 偶数索引元素（从0开始）
$(':odd')                   // 奇数索引元素
$(':eq(index)')             // 指定索引的元素
$(':gt(index)')             // 大于指定索引的元素
$(':lt(index)')              // 小于指定索引的元素

// 内容过滤选择器
$(':contains("text")')     // 包含指定文本的元素
$(':empty')                  // 空元素
$(':parent')                // 有子元素的元素
$(':has(selector)')          // 包含指定选择器的元素
```

### 2. DOM操作

**英文原意**：Document Object Model（文档对象模型）
**技术含义**：操作HTML元素的内容、属性和样式

#### 内容操作
```javascript
// 获取内容
$('#element').text()                    // 获取文本内容
$('#element').html()                    // 获取HTML内容
$('#element').val()                     // 获取表单值

// 设置内容
$('#element').text('新文本')              // 设置文本内容
$('#element').html('<b>新HTML</b>')        // 设置HTML内容
$('#element').val('新值')                 // 设置表单值

// 追加内容
$('#element').append('<p>追加内容</p>')      // 内部末尾追加
$('#element').prepend('<p>前置内容</p>')     // 内部开头追加
$('#element').after('<p>后面插入</p>')       // 外部后面插入
$('#element').before('<p>前面插入</p>')      // 外部前面插入
```

#### 属性操作
```javascript
// 获取属性
$('#element').attr('href')                // 获取href属性值
$('#element').prop('checked')             // 获取checked属性（布尔值）

// 设置属性
$('#element').attr('href', 'http://example.com')  // 设置href属性
$('#element').prop('checked', true)                 // 设置checked属性
$('#element').removeAttr('disabled')               // 移除属性

// CSS类操作
$('#element').addClass('active')           // 添加类
$('#element').removeClass('active')        // 移除类
$('#element').toggleClass('active')        // 切换类
$('#element').hasClass('active')           // 检查是否有类
```

#### 样式操作
```javascript
// 设置单个样式
$('#element').css('color', 'red')          // 设置颜色
$('#element').css('font-size', '16px')     // 设置字体大小

// 设置多个样式
$('#element').css({
  'color': 'red',
  'font-size': '16px',
  'background-color': '#f0f0f0'
});

// 获取样式
$('#element').css('color')               // 获取颜色值
$('#element').css('font-size')             // 获取字体大小
```

### 3. 事件处理

**英文原意**：事件
**技术含义**：响应用户的操作（点击、键盘、鼠标等）

```javascript
// 基本事件绑定
$('#button').click(function() {
  alert('按钮被点击了！');
});

// 事件委托（推荐）
$(document).on('click', '#button', function() {
  alert('按钮被点击了！');
});

// 多个事件绑定
$('#element').on({
  mouseenter: function() {
    $(this).css('background-color', '#f0f0f0');
  },
  mouseleave: function() {
    $(this).css('background-color', '');
  },
  click: function() {
    alert('元素被点击了！');
  }
});

// 常见事件类型
$('#element').click(handler)              // 点击事件
$('#element').dblclick(handler)           // 双击事件
$('#element').mouseenter(handler)         // 鼠标进入
$('#element').mouseleave(handler)         // 鼠标离开
$('#element').mouseover(handler)          // 鼠标悬停
$('#element').mouseout(handler)           // 鼠标移出
$('#element').keydown(handler)            // 键盘按下
$('#element').keyup(handler)              // 键盘释放
$('#element').focus(handler)              // 获得焦点
$('#element').blur(handler)               // 失去焦点
$('#element').change(handler)             // 内容改变
$('#element').submit(handler)             // 表单提交

// 事件对象
$('#element').click(function(event) {
  event.preventDefault();                   // 阻止默认行为
  event.stopPropagation();                 // 阻止事件冒泡
  console.log(event.target);                // 触发事件的元素
  console.log(event.pageX, event.pageY);    // 鼠标位置
});

// 移除事件
$('#element').off('click');                // 移除点击事件
$('#element').off();                       // 移除所有事件
```

### 4. 动画效果

**英文原意**：动画
**技术含义**：让元素产生平滑的视觉效果变化

```javascript
// 基本显示/隐藏
$('#element').show()                       // 显示元素
$('#element').hide()                       // 隐藏元素
$('#element').toggle()                     // 切换显示/隐藏

// 淡入淡出
$('#element').fadeIn(1000)                 // 淡入（1秒）
$('#element').fadeOut(1000)                // 淡出（1秒）
$('#element').fadeToggle(1000)               // 切换淡入淡出
$('#element').fadeTo(1000, 0.5)            // 淡到指定透明度

// 滑动效果
$('#element').slideDown(1000)              // 向下滑动显示
$('#element').slideUp(1000)                // 向上滑动隐藏
$('#element').slideToggle(1000)            // 切换滑动效果

// 自定义动画
$('#element').animate({
  left: '250px',
  opacity: '0.5',
  height: '150px',
  width: '150px'
}, 1000);                                  // 1秒内完成动画

// 动画队列
$('#element')
  .animate({left: '100px'}, 500)
  .animate({top: '100px'}, 500)
  .animate({opacity: '0.5'}, 500);

// 停止动画
$('#element').stop()                         // 停止当前动画
$('#element').stop(true)                     // 停止所有动画
$('#element').stop(true, true)               // 停止所有动画并跳到结束
```

### 5. Ajax请求

**英文原意**：Asynchronous JavaScript and XML（异步JavaScript和XML）
**技术含义**：在不刷新页面的情况下与服务器交换数据

```javascript
// 基本GET请求
$.ajax({
  url: '/api/data',
  method: 'GET',
  success: function(data) {
    console.log('成功获取数据:', data);
  },
  error: function(xhr, status, error) {
    console.log('请求失败:', error);
  }
});

// 简化的GET请求
$.get('/api/data', function(data) {
  console.log('成功获取数据:', data);
});

// POST请求
$.ajax({
  url: '/api/submit',
  method: 'POST',
  data: {
    name: '张三',
    age: 25
  },
  success: function(response) {
    console.log('提交成功:', response);
  },
  error: function(xhr, status, error) {
    console.log('提交失败:', error);
  }
});

// 简化的POST请求
$.post('/api/submit', {
  name: '张三',
  age: 25
}, function(response) {
  console.log('提交成功:', response);
});

// 处理JSON数据
$.ajax({
  url: '/api/users',
  method: 'GET',
  dataType: 'json',                        // 指定返回数据类型
  success: function(users) {
    users.forEach(function(user) {
      console.log(user.name);
    });
  }
});

// 发送JSON数据
$.ajax({
  url: '/api/users',
  method: 'POST',
  contentType: 'application/json',         // 指定发送数据类型
  data: JSON.stringify({
    name: '李四',
    email: 'lisi@example.com'
  }),
  success: function(response) {
    console.log('用户创建成功:', response);
  }
});

// 文件上传
var formData = new FormData();
formData.append('file', $('#fileInput')[0].files[0]);

$.ajax({
  url: '/api/upload',
  method: 'POST',
  data: formData,
  processData: false,                      // 不处理数据
  contentType: false,                      // 不设置内容类型
  success: function(response) {
    console.log('文件上传成功:', response);
  }
});
```

### 6. 工具函数

**英文原意**：工具函数
**技术含义**：jQuery提供的实用工具方法

```javascript
// 遍历数组或对象
$.each([1, 2, 3], function(index, value) {
  console.log('索引:', index, '值:', value);
});

$.each({a: 1, b: 2, c: 3}, function(key, value) {
  console.log('键:', key, '值:', value);
});

// 类型判断
$.isArray([1, 2, 3])                      // true
$.isFunction(function(){})                 // true
$.isEmptyObject({})                        // true
$.isPlainObject({a: 1})                    // true

// 扩展对象
var obj1 = {a: 1, b: 2};
var obj2 = {b: 3, c: 4};
var merged = $.extend(obj1, obj2);        // {a: 1, b: 3, c: 4}

// 深拷贝
var original = {a: {b: 1}};
var copy = $.extend(true, {}, original);  // 深拷贝

// 序列化表单
var formData = $('#myForm').serialize();   // name=value&name2=value2
var formArray = $('#myForm').serializeArray(); // [{name: 'name', value: 'value'}]

// 解析JSON
var json = '{"name": "张三", "age": 25}';
var obj = $.parseJSON(json);               // {name: "张三", age: 25}

// 去除字符串两端空格
var str = '  hello world  ';
var trimmed = $.trim(str);                 // 'hello world'
```

## 在LiuMa项目中的应用

### 1. 项目中的jQuery使用场景

```javascript
// src/utils/ajax.js - 网络请求封装
import $ from 'jquery'

// 基于jQuery的Ajax封装
const ajax = {
  // GET请求
  get: function(url, data, success, error) {
    return $.ajax({
      url: url,
      type: 'GET',
      data: data,
      dataType: 'json',
      success: success,
      error: error || this.defaultError
    });
  },
  
  // POST请求
  post: function(url, data, success, error) {
    return $.ajax({
      url: url,
      type: 'POST',
      data: JSON.stringify(data),
      contentType: 'application/json;charset=UTF-8',
      dataType: 'json',
      success: success,
      error: error || this.defaultError
    });
  },
  
  // 默认错误处理
  defaultError: function(xhr, status, error) {
    if (xhr.status === 401) {
      // 未授权，跳转到登录页
      window.location.href = '/login';
    } else if (xhr.status === 500) {
      console.error('服务器错误:', error);
    } else {
      console.error('请求失败:', error);
    }
  }
};

// 将ajax方法挂载到Vue原型上
Vue.prototype.$get = ajax.get;
Vue.prototype.$post = ajax.post;
```

### 2. 与Vue的配合使用

```javascript
// Vue组件中使用jQuery
export default {
  mounted() {
    // 使用jQuery操作DOM（不推荐，但在某些情况下需要）
    this.$nextTick(() => {
      // 初始化第三方插件（如日期选择器）
      $('#datePicker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true
      });
      
      // 滚动到指定位置
      $('.content-wrapper').animate({
        scrollTop: 0
      }, 500);
    });
  },
  
  methods: {
    // 使用jQuery的Ajax
    loadData() {
      this.$get('/api/test-cases', { page: 1, size: 10 })
        .then(data => {
          this.tableData = data.content;
        })
        .catch(error => {
          console.error('加载数据失败:', error);
        });
    },
    
    // 提交表单
    submitForm() {
      const formData = {
        name: this.form.name,
        description: this.form.description
      };
      
      this.$post('/api/test-cases', formData)
        .then(response => {
          this.$message.success('创建成功');
          this.$router.push('/case-center');
        })
        .catch(error => {
          this.$message.error('创建失败: ' + error.message);
        });
    }
  }
}
```

### 3. 工具函数使用

```javascript
// 在Vue组件中使用jQuery工具函数
export default {
  data() {
    return {
      selectedIds: [],
      tableData: []
    };
  },
  
  methods: {
    // 批量处理数据
    processData() {
      // 使用$.each遍历数组
      $.each(this.tableData, (index, item) => {
        if (item.selected) {
          this.selectedIds.push(item.id);
        }
      });
      
      // 使用$.grep过滤数组
      const filteredData = $.grep(this.tableData, (item) => {
        return item.status === 'active';
      });
      
      console.log('选中的ID:', this.selectedIds);
      console.log('活跃的数据:', filteredData);
    },
    
    // 合并配置项
    getConfig() {
      const defaultConfig = {
        pageSize: 10,
        pageNum: 1,
        sortBy: 'id',
        sortOrder: 'desc'
      };
      
      const userConfig = {
        pageSize: 20,
        sortBy: 'name'
      };
      
      // 使用$.extend合并对象
      return $.extend({}, defaultConfig, userConfig);
      // 结果: {pageSize: 20, pageNum: 1, sortBy: 'name', sortOrder: 'desc'}
    },
    
    // 表单序列化
    serializeForm() {
      // 将表单数据转换为查询字符串
      const formData = $('#searchForm').serialize();
      console.log('表单数据:', formData);
      // 输出: name=test&status=active&date=2024-01-01
      
      // 将表单数据转换为对象数组
      const formArray = $('#searchForm').serializeArray();
      console.log('表单数组:', formArray);
      // 输出: [{name: 'name', value: 'test'}, {name: 'status', value: 'active'}]
    }
  }
}
```

## 实战：完整的jQuery示例

### 1. 创建一个动态表格

```html
<!DOCTYPE html>
<html>
<head>
  <title>jQuery动态表格示例</title>
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <style>
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
    th { background-color: #f5f5f5; }
    .highlight { background-color: #ffffcc; }
    .btn { padding: 5px 10px; margin: 2px; cursor: pointer; }
    .btn-primary { background: #007bff; color: white; border: none; }
    .btn-danger { background: #dc3545; color: white; border: none; }
  </style>
</head>
<body>
  <h2>测试用例管理</h2>
  
  <!-- 搜索表单 -->
  <form id="searchForm">
    <input type="text" name="keyword" placeholder="搜索关键词">
    <select name="status">
      <option value="">全部状态</option>
      <option value="active">活跃</option>
      <option value="inactive">非活跃</option>
    </select>
    <button type="submit" class="btn btn-primary">搜索</button>
    <button type="button" id="addBtn" class="btn btn-primary">添加</button>
  </form>
  
  <!-- 数据表格 -->
  <table id="dataTable">
    <thead>
      <tr>
        <th><input type="checkbox" id="selectAll"></th>
        <th>ID</th>
        <th>用例名称</th>
        <th>状态</th>
        <th>创建时间</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody id="tableBody">
      <!-- 数据将通过jQuery动态加载 -->
    </tbody>
  </table>
  
  <!-- 分页 -->
  <div id="pagination"></div>
  
  <!-- 添加/编辑模态框 -->
  <div id="modal" style="display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 1px solid #ddd; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    <h3 id="modalTitle">添加测试用例</h3>
    <form id="modalForm">
      <input type="hidden" id="caseId">
      <div>
        <label>用例名称:</label>
        <input type="text" id="caseName" required>
      </div>
      <div>
        <label>状态:</label>
        <select id="caseStatus">
          <option value="active">活跃</option>
          <option value="inactive">非活跃</option>
        </select>
      </div>
      <div>
        <button type="submit" class="btn btn-primary">保存</button>
        <button type="button" id="cancelBtn" class="btn">取消</button>
      </div>
    </form>
  </div>

  <script>
    $(document).ready(function() {
      // 模拟数据
      let testCases = [
        { id: 1, name: '登录功能测试', status: 'active', createTime: '2024-01-15 10:30:00' },
        { id: 2, name: '注册功能测试', status: 'active', createTime: '2024-01-16 14:20:00' },
        { id: 3, name: '搜索功能测试', status: 'inactive', createTime: '2024-01-17 09:15:00' }
      ];
      
      let currentPage = 1;
      let pageSize = 5;
      
      // 渲染表格
      function renderTable(data) {
        const tbody = $('#tableBody');
        tbody.empty();
        
        if (data.length === 0) {
          tbody.append('<tr><td colspan="6" style="text-align: center;">暂无数据</td></tr>');
          return;
        }
        
        $.each(data, function(index, item) {
          const row = $('<tr>').addClass(index % 2 === 0 ? 'even' : 'odd');
          row.html(`
            <td><input type="checkbox" class="row-checkbox" value="${item.id}"></td>
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td><span class="status-${item.status}">${item.status}</span></td>
            <td>${item.createTime}</td>
            <td>
              <button class="btn btn-primary edit-btn" data-id="${item.id}">编辑</button>
              <button class="btn btn-danger delete-btn" data-id="${item.id}">删除</button>
            </td>
          `);
          tbody.append(row);
        });
      }
      
      // 渲染分页
      function renderPagination(totalItems, currentPage, pageSize) {
        const totalPages = Math.ceil(totalItems / pageSize);
        const pagination = $('#pagination');
        pagination.empty();
        
        for (let i = 1; i <= totalPages; i++) {
          const pageBtn = $('<button>')
            .text(i)
            .addClass('btn')
            .addClass(i === currentPage ? 'btn-primary' : '')
            .prop('disabled', i === currentPage)
            .click(function() {
              currentPage = i;
              loadData();
            });
          pagination.append(pageBtn);
        }
      }
      
      // 加载数据
      function loadData() {
        // 模拟分页
        const start = (currentPage - 1) * pageSize;
        const end = start + pageSize;
        const pageData = testCases.slice(start, end);
        
        renderTable(pageData);
        renderPagination(testCases.length, currentPage, pageSize);
      }
      
      // 搜索功能
      $('#searchForm').submit(function(event) {
        event.preventDefault();
        
        const formData = $(this).serializeArray();
        const keyword = formData.find(item => item.name === 'keyword').value;
        const status = formData.find(item => item.name === 'status').value;
        
        // 过滤数据
        const filteredData = $.grep(testCases, function(item) {
          const matchKeyword = !keyword || item.name.toLowerCase().includes(keyword.toLowerCase());
          const matchStatus = !status || item.status === status;
          return matchKeyword && matchStatus;
        });
        
        renderTable(filteredData);
        renderPagination(filteredData.length, 1, pageSize);
      });
      
      // 全选/取消全选
      $('#selectAll').change(function() {
        $('.row-checkbox').prop('checked', $(this).prop('checked'));
      });
      
      // 行点击高亮
      $(document).on('click', 'tr', function(event) {
        // 如果点击的是复选框或按钮，不触发高亮
        if ($(event.target).is('input, button')) {
          return;
        }
        $(this).toggleClass('highlight').siblings().removeClass('highlight');
      });
      
      // 添加按钮
      $('#addBtn').click(function() {
        $('#modalTitle').text('添加测试用例');
        $('#caseId').val('');
        $('#caseName').val('');
        $('#caseStatus').val('active');
        $('#modal').fadeIn();
      });
      
      // 编辑按钮
      $(document).on('click', '.edit-btn', function(event) {
        event.stopPropagation();
        const id = $(this).data('id');
        const item = testCases.find(tc => tc.id === id);
        
        if (item) {
          $('#modalTitle').text('编辑测试用例');
          $('#caseId').val(item.id);
          $('#caseName').val(item.name);
          $('#caseStatus').val(item.status);
          $('#modal').fadeIn();
        }
      });
      
      // 删除按钮
      $(document).on('click', '.delete-btn', function(event) {
        event.stopPropagation();
        const id = $(this).data('id');
        
        if (confirm('确定要删除这个测试用例吗？')) {
          testCases = $.grep(testCases, function(item) {
            return item.id !== id;
          });
          loadData();
          alert('删除成功！');
        }
      });
      
      // 模态框表单提交
      $('#modalForm').submit(function(event) {
        event.preventDefault();
        
        const id = $('#caseId').val();
        const name = $('#caseName').val();
        const status = $('#caseStatus').val();
        
        if (!name.trim()) {
          alert('请输入用例名称！');
          return;
        }
        
        if (id) {
          // 编辑
          const item = testCases.find(tc => tc.id === parseInt(id));
          if (item) {
            item.name = name;
            item.status = status;
          }
        } else {
          // 添加
          const newId = testCases.length > 0 ? Math.max(...testCases.map(tc => tc.id)) + 1 : 1;
          testCases.push({
            id: newId,
            name: name,
            status: status,
            createTime: new Date().toLocaleString()
          });
        }
        
        $('#modal').fadeOut();
        loadData();
        alert(id ? '编辑成功！' : '添加成功！');
      });
      
      // 取消按钮
      $('#cancelBtn').click(function() {
        $('#modal').fadeOut();
      });
      
      // 点击模态框外部关闭
      $(document).click(function(event) {
        if ($(event.target).is('#modal')) {
          $('#modal').fadeOut();
        }
      });
      
      // 初始化加载数据
      loadData();
    });
  </script>
</body>
</html>
```

### 2. 与Vue结合使用

```javascript
// Vue组件中使用jQuery
<template>
  <div class="test-case-manager">
    <el-table
      :data="tableData"
      style="width: 100%"
      @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="用例名称"></el-table-column>
      <el-table-column prop="status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="batch-actions" v-if="selectedRows.length > 0">
      <el-button type="danger" @click="handleBatchDelete">批量删除</el-button>
      <span>已选择 {{ selectedRows.length }} 项</span>
    </div>
  </div>
</template>

<script>
import $ from 'jquery'

export default {
  name: 'TestCaseManager',
  data() {
    return {
      tableData: [],
      selectedRows: [],
      loading: false
    }
  },
  
  mounted() {
    this.loadData();
    
    // 使用jQuery处理一些DOM操作
    this.$nextTick(() => {
      // 添加键盘快捷键支持
      $(document).on('keydown', (event) => {
        // Ctrl + A 全选
        if (event.ctrlKey && event.key === 'a') {
          event.preventDefault();
          this.$refs.table.toggleAllSelection();
        }
        
        // Delete 删除选中项
        if (event.key === 'Delete' && this.selectedRows.length > 0) {
          this.handleBatchDelete();
        }
      });
    });
  },
  
  beforeDestroy() {
    // 清理事件监听
    $(document).off('keydown');
  },
  
  methods: {
    // 加载数据（使用jQuery的Ajax）
    loadData() {
      this.loading = true;
      
      $.ajax({
        url: '/api/test-cases',
        method: 'GET',
        data: {
          page: 1,
          size: 100
        },
        dataType: 'json',
        success: (data) => {
          this.tableData = data.content;
          this.loading = false;
        },
        error: (xhr, status, error) => {
          this.$message.error('加载数据失败: ' + error);
          this.loading = false;
        }
      });
    },
    
    // 使用jQuery工具函数处理数据
    handleSelectionChange(val) {
      this.selectedRows = val;
      
      // 使用jQuery的each方法处理选中项
      const ids = [];
      $.each(val, (index, row) => {
        ids.push(row.id);
      });
      
      console.log('选中的ID:', ids);
    },
    
    // 批量删除
    handleBatchDelete() {
      if (this.selectedRows.length === 0) {
        return;
      }
      
      this.$confirm(`确定要删除选中的 ${this.selectedRows.length} 个测试用例吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 使用jQuery的map和grep处理数据
        const ids = $.map(this.selectedRows, (row) => row.id);
        
        $.ajax({
          url: '/api/test-cases/batch-delete',
          method: 'POST',
          data: JSON.stringify({ ids }),
          contentType: 'application/json',
          success: (response) => {
            this.$message.success('批量删除成功');
            
            // 使用jQuery的grep过滤掉已删除的数据
            this.tableData = $.grep(this.tableData, (row) => {
              return !ids.includes(row.id);
            });
            
            this.selectedRows = [];
          },
          error: (xhr, status, error) => {
            this.$message.error('删除失败: ' + error);
          }
        });
      });
    },
    
    // 编辑
    handleEdit(row) {
      // 深拷贝数据，避免直接修改
      const editData = $.extend(true, {}, row);
      
      // 打开编辑对话框
      this.$prompt('请输入新的用例名称', '编辑测试用例', {
        inputValue: editData.name,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }).then(({ value }) => {
        editData.name = value;
        
        $.ajax({
          url: `/api/test-cases/${editData.id}`,
          method: 'PUT',
          data: JSON.stringify(editData),
          contentType: 'application/json',
          success: (response) => {
            this.$message.success('编辑成功');
            
            // 更新本地数据
            const index = this.tableData.findIndex(item => item.id === editData.id);
            if (index !== -1) {
              this.tableData.splice(index, 1, editData);
            }
          },
          error: (xhr, status, error) => {
            this.$message.error('编辑失败: ' + error);
          }
        });
      });
    },
    
    // 删除
    handleDelete(row) {
      this.$confirm(`确定要删除测试用例 "${row.name}" 吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        $.ajax({
          url: `/api/test-cases/${row.id}`,
          method: 'DELETE',
          success: (response) => {
            this.$message.success('删除成功');
            
            // 从本地数据中移除
            const index = this.tableData.findIndex(item => item.id === row.id);
            if (index !== -1) {
              this.tableData.splice(index, 1);
            }
          },
          error: (xhr, status, error) => {
            this.$message.error('删除失败: ' + error);
          }
        });
      });
    },
    
    // 获取状态样式
    getStatusType(status) {
      const statusMap = {
        'active': 'success',
        'inactive': 'info',
        'pending': 'warning',
        'failed': 'danger'
      };
      return statusMap[status] || 'info';
    }
  }
}
</script>

<style scoped>
.batch-actions {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.status-active {
  color: #67c23a;
}

.status-inactive {
  color: #909399;
}
</style>
```

## 最佳实践

### 1. jQuery与Vue的配合原则

```javascript
// ✅ 推荐：在Vue的生命周期钩子中使用jQuery
export default {
  mounted() {
    // 初始化第三方jQuery插件
    this.$nextTick(() => {
      $('#datepicker').datepicker();
    });
  },
  
  beforeDestroy() {
    // 清理jQuery事件和插件
    $('#datepicker').datepicker('destroy');
  }
}

// ❌ 避免：直接操作Vue管理的DOM
export default {
  methods: {
    updateElement() {
      // 不要这样做！Vue会管理这个DOM
      $('#vue-managed-element').text('新内容');
    }
  }
}

// ✅ 推荐：使用Vue的数据绑定
export default {
  data() {
    return {
      elementText: '旧内容'
    };
  },
  
  methods: {
    updateElement() {
      this.elementText = '新内容'; // Vue会自动更新DOM
    }
  }
}
```

### 2. Ajax请求的封装

```javascript
// utils/request.js - 统一的请求封装
import $ from 'jquery'
import { Message } from 'element-ui'

class Request {
  constructor() {
    this.baseURL = process.env.VUE_APP_BASE_API || '';
    this.timeout = 10000;
    
    // 设置全局Ajax默认值
    $.ajaxSetup({
      timeout: this.timeout,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      dataType: 'json',
      contentType: 'application/json;charset=UTF-8'
    });
  }
  
  // GET请求
  get(url, params = {}) {
    return new Promise((resolve, reject) => {
      $.ajax({
        url: this.baseURL + url,
        type: 'GET',
        data: params,
        success: (data) => {
          if (data.code === 200) {
            resolve(data.data);
          } else {
            Message.error(data.message || '请求失败');
            reject(data);
          }
        },
        error: (xhr, status, error) => {
          this.handleError(xhr, reject);
        }
      });
    });
  }
  
  // POST请求
  post(url, data = {}) {
    return new Promise((resolve, reject) => {
      $.ajax({
        url: this.baseURL + url,
        type: 'POST',
        data: JSON.stringify(data),
        success: (data) => {
          if (data.code === 200) {
            resolve(data.data);
          } else {
            Message.error(data.message || '请求失败');
            reject(data);
          }
        },
        error: (xhr, status, error) => {
          this.handleError(xhr, reject);
        }
      });
    });
  }
  
  // 错误处理
  handleError(xhr, reject) {
    let message = '网络错误';
    
    if (xhr.status === 401) {
      message = '未授权，请重新登录';
      // 跳转到登录页
      window.location.href = '/login';
    } else if (xhr.status === 403) {
      message = '没有权限';
    } else if (xhr.status === 404) {
      message = '请求的资源不存在';
    } else if (xhr.status >= 500) {
      message = '服务器错误';
    }
    
    Message.error(message);
    reject({
      status: xhr.status,
      message: message
    });
  }
}

export default new Request();
```

### 3. 工具函数的封装

```javascript
// utils/tools.js - jQuery工具函数封装
import $ from 'jquery'

const tools = {
  // 深拷贝对象
  deepClone(obj) {
    return $.extend(true, {}, obj);
  },
  
  // 数组去重
  uniqueArray(array, key) {
    if (key) {
      const seen = {};
      return $.grep(array, function(item) {
        const k = item[key];
        return seen.hasOwnProperty(k) ? false : (seen[k] = true);
      });
    } else {
      return $.grep(array, function(item, index) {
        return index === $.inArray(item, array);
      });
    }
  },
  
  // 格式化文件大小
  formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },
  
  // 防抖函数
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  
  // 节流函数
  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  },
  
  // 获取URL参数
  getUrlParams() {
    const params = {};
    const search = window.location.search.substring(1);
    const pairs = search.split('&');
    
    $.each(pairs, function(index, pair) {
      const [key, value] = pair.split('=');
      if (key) {
        params[decodeURIComponent(key)] = decodeURIComponent(value || '');
      }
    });
    
    return params;
  },
  
  // 设置URL参数
  setUrlParams(params) {
    const url = new URL(window.location);
    $.each(params, function(key, value) {
      if (value === null || value === undefined || value === '') {
        url.searchParams.delete(key);
      } else {
        url.searchParams.set(key, value);
      }
    });
    
    window.history.replaceState({}, '', url);
  }
};

export default tools;
```

## 常见问题解答

### Q1：jQuery和Vue一起使用会有冲突吗？

**A**：
- **不会直接冲突**，但需要遵循一些原则：
  - Vue负责数据管理和DOM更新
  - jQuery负责Vue不管理的DOM操作和工具函数
  - 避免jQuery直接操作Vue管理的DOM元素
  - 在Vue的生命周期钩子中安全使用jQuery

### Q2：什么时候应该使用jQuery，什么时候用原生JS？

**A**：
- **使用jQuery的场景**：
  - 需要处理复杂的DOM选择器
  - 需要跨浏览器兼容的旧项目
  - 使用依赖jQuery的第三方插件
  - 快速原型开发

- **使用原生JS的场景**：
  - 现代浏览器环境
  - 性能要求高的操作
  - 简单的DOM操作
  - 学习现代JavaScript特性

### Q3：jQuery过时了吗？

**A**：
- **没有完全过时**：
  - 仍然有很多网站在使用
  - 很多老项目需要维护
  - 一些第三方插件依赖jQuery
  - 在某些场景下仍然很有用

- **趋势**：
  - 新项目更多使用Vue、React等现代框架
  - 原生JavaScript功能越来越强大
  - 现代浏览器兼容性越来越好

### Q4：如何优化jQuery性能？

**A**：
1. **缓存jQuery对象**：
```javascript
// ❌ 不好的做法
$('.my-element').addClass('active');
$('.my-element').removeClass('inactive');
$('.my-element').attr('data-status', 'active');

// ✅ 推荐做法
const $element = $('.my-element');
$element.addClass('active');
$element.removeClass('inactive');
$element.attr('data-status', 'active');
```

2. **使用事件委托**：
```javascript
// ❌ 不好的做法
$('.button').click(function() {
  // 每次添加新按钮都需要重新绑定
});

// ✅ 推荐做法
$(document).on('click', '.button', function() {
  // 动态添加的按钮也会自动绑定事件
});
```

3. **批量操作DOM**：
```javascript
// ❌ 不好的做法
$.each(data, function(index, item) {
  $('#list').append('<li>' + item.name + '</li>');
});

// ✅ 推荐做法
let html = '';
$.each(data, function(index, item) {
  html += '<li>' + item.name + '</li>';
});
$('#list').append(html);
```

### Q5：jQuery选择器性能如何优化？

**A**：
1. **使用ID选择器**：`$('#id')` - 最快的选择器
2. **使用类选择器**：`$('.class')` - 次优选择
3. **避免复杂选择器**：`$('div.class span[attr=value]')` - 性能较差
4. **限定搜索范围**：`$('#container').find('.item')` - 比`$('.item')`性能好
5. **缓存选择结果**：避免重复查询相同的元素

## 下一步学习

掌握了jQuery基础后，建议继续学习：
1. **原生JavaScript进阶** - 现代JavaScript特性（ES6+）
2. **Vue.js深入** - 组件化开发、状态管理
3. **CSS3动画** - 现代CSS动画技术
4. **Fetch API** - 现代的网络请求API
5. **Web APIs** - 浏览器提供的原生API

## 面试常见问题

1. **jQuery和原生JavaScript有什么区别？**
2. **jQuery的选择器原理是什么？**
3. **jQuery中的事件委托是什么？如何实现？**
4. **jQuery的链式调用是如何实现的？**
5. **jQuery的Ajax和原生Fetch有什么区别？**
6. **jQuery中的ready和window.onload有什么区别？**
7. **如何优化jQuery的性能？**
8. **jQuery的extend方法有什么作用？**
9. **jQuery中的事件冒泡和默认行为如何阻止？**
10. **jQuery在现代项目中还有必要使用吗？**

通过本教程的学习，你应该对jQuery有了全面的了解。记住，jQuery是一个工具，在合适的场景下使用它会大大提高开发效率。在现代Vue项目中，jQuery主要作为补充工具使用，负责一些Vue不擅长的DOM操作和工具函数。