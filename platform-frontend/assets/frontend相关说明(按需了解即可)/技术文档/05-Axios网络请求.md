# Axios网络请求

## 什么是Axios？

Axios是一个基于Promise的HTTP客户端（HTTP Client），用于浏览器和node.js。它可以发送异步HTTP请求到REST端点，并处理响应数据。

**英文全称**：Axios（源自希腊语"axios"，意为"值得"）
**中文理解**：网络请求"快递员"，专门负责前后端之间的数据传递

**生活类比**：就像快递公司的快递员，你告诉他要送什么（请求数据）、送到哪里（URL地址），他就会帮你把包裹（请求）送到目的地，然后把回执（响应）带回来给你。

## 为什么选择Axios？

### 1. HTTP客户端对比

| 工具 | 特点 | 优点 | 缺点 |
|------|------|------|------|
| **Axios** | 基于Promise | 支持Promise、拦截器、自动转换JSON | 需要额外安装 |
| Fetch API | 原生API | 无需安装、标准API | 不支持IE、需要手动处理错误 |
| jQuery.ajax | jQuery内置 | 兼容性好、功能丰富 | 依赖jQuery、体积大 |
| XMLHttpRequest | 原生API | 兼容性好 | API复杂、需要手动封装 |

### 2. Axios的核心优势

- **Promise支持**：基于Promise，支持async/await语法
- **请求/响应拦截器**：可以在请求发送前和响应返回后进行处理
- **自动转换JSON**：自动将请求和响应数据转换为JSON格式
- **错误处理**：统一的错误处理机制
- **取消请求**：支持取消正在进行的请求
- **防止CSRF**：内置CSRF保护
- **支持Node.js**：可以在Node.js环境中使用

## 快速开始

### 1. 安装Axios

```bash
# 使用npm安装
npm install axios

# 使用yarn安装
yarn add axios
```

### 2. 基础使用

```javascript
// 引入axios
import axios from 'axios'

// GET请求
axios.get('/api/user')
  .then(response => {
    console.log(response.data)
  })
  .catch(error => {
    console.error(error)
  })

// POST请求
axios.post('/api/user', {
    name: '张三',
    age: 25
  })
  .then(response => {
    console.log(response.data)
  })
  .catch(error => {
    console.error(error)
  })

// 使用async/await（推荐）
async function getUser() {
  try {
    const response = await axios.get('/api/user')
    console.log(response.data)
  } catch (error) {
    console.error(error)
  }
}
```

### 3. 基础配置

```javascript
// 设置基础URL
axios.defaults.baseURL = 'http://localhost:8080'

// 设置请求超时时间
axios.defaults.timeout = 5000

// 设置请求头
axios.defaults.headers.common['Authorization'] = 'Bearer token'
axios.defaults.headers.post['Content-Type'] = 'application/json'
```

## 在LiuMa项目中的应用

### 1. 网络请求封装（/src/utils/ajax.js）

```javascript
import axios from 'axios'
import { Message } from 'element-ui'
import store from '@/vuex/store'
import router from '@/router'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.BASE_API, // api的base_url
  timeout: 15000, // 请求超时时间
  withCredentials: true // 允许携带cookie
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    if (store.getters.token) {
      // 让每个请求携带token
      config.headers['Authorization'] = 'Bearer ' + store.getters.token
    }
    return config
  },
  error => {
    // 对请求错误做些什么
    console.log('request error:', error)
    Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    const res = response.data
    
    // 如果返回的状态码不是200，则提示错误
    if (res.code !== 200) {
      Message({
        message: res.message || 'Error',
        type: 'error',
        duration: 5 * 1000
      })
      
      // 401: 未登录或token过期
      if (res.code === 401) {
        // 清除token
        store.dispatch('FedLogOut').then(() => {
          // 跳转登录页
          router.push('/login')
        })
      }
      
      return Promise.reject(new Error(res.message || 'Error'))
    } else {
      return res
    }
  },
  error => {
    // 对响应错误做点什么
    console.log('response error:', error)
    
    Message({
      message: error.message,
      type: 'error',
      duration: 5 * 1000
    })
    
    return Promise.reject(error)
  }
)

export default service
```

### 2. API接口封装（/src/api/login.js）

```javascript
import request from '@/utils/ajax'

// 登录接口
export function login(username, password) {
  return request({
    url: '/user/login',
    method: 'post',
    data: {
      username,
      password
    }
  })
}

// 获取用户信息接口
export function getInfo() {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

// 退出登录接口
export function logout() {
  return request({
    url: '/user/logout',
    method: 'post'
  })
}
```

### 3. 在组件中使用

```javascript
// 在登录组件中使用
import { login } from '@/api/login'

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
    async handleLogin() {
      this.loading = true
      try {
        const response = await login(this.loginForm.username, this.loginForm.password)
        
        // 保存token到vuex
        this.$store.dispatch('Login', response.data.token)
        
        // 跳转到首页
        this.$router.push('/')
        
        this.$message.success('登录成功！')
      } catch (error) {
        console.error('登录失败:', error)
        this.$message.error('登录失败，请检查用户名和密码')
      } finally {
        this.loading = false
      }
    }
  }
}
```

## 核心概念详解

### 1. 请求配置（Request Config）

```javascript
{
  // 请求URL
  url: '/user',
  
  // 请求方法
  method: 'get', // 默认值
  
  // 基础URL，将自动加在url前面
  baseURL: 'https://api.example.com',
  
  // 允许在向服务器发送前，修改请求数据
  transformRequest: [function (data, headers) {
    // 对 data 进行任意转换处理
    return data;
  }],
  
  // 在传递给 then/catch 前，允许修改响应数据
  transformResponse: [function (data) {
    // 对 data 进行任意转换处理
    return data;
  }],
  
  // 自定义请求头
  headers: {'X-Requested-With': 'XMLHttpRequest'},
  
  // 请求参数
  params: {
    ID: 12345
  },
  
  // 请求体数据
  data: {
    firstName: 'Fred'
  },
  
  // 超时时间
  timeout: 1000,
  
  // 跨域请求时是否需要使用凭证
  withCredentials: false,
  
  // 响应数据格式
  responseType: 'json', // 默认值
  
  // 上传进度事件
  onUploadProgress: function (progressEvent) {
    // 处理原生进度事件
  },
  
  // 下载进度事件
  onDownloadProgress: function (progressEvent) {
    // 处理原生进度事件
  },
  
  // 自定义错误处理
  validateStatus: function (status) {
    return status >= 200 && status < 300; // 默认值
  }
}
```

### 2. 响应结构（Response Schema）

```javascript
{
  // 响应数据
  data: {},
  
  // 响应状态码
  status: 200,
  
  // 响应状态文本
  statusText: 'OK',
  
  // 响应头
  headers: {},
  
  // 请求配置
  config: {},
  
  // 请求对象
  request: {}
}
```

### 3. 拦截器（Interceptors）

**英文原意**：拦截器、截听器
**技术含义**：在请求或响应被处理前拦截它们

```javascript
// 添加请求拦截器
axios.interceptors.request.use(function (config) {
  // 在发送请求之前做些什么
  config.headers.Authorization = 'Bearer token'
  return config;
}, function (error) {
  // 对请求错误做些什么
  return Promise.reject(error);
});

// 添加响应拦截器
axios.interceptors.response.use(function (response) {
  // 对响应数据做点什么
  if (response.data.code === 401) {
    // 处理未授权情况
    router.push('/login')
  }
  return response;
}, function (error) {
  // 对响应错误做点什么
  if (error.response.status === 404) {
    // 处理404错误
    console.log('请求的资源不存在')
  }
  return Promise.reject(error);
});

// 移除拦截器
const myInterceptor = axios.interceptors.request.use(function () {/*...*/});
axios.interceptors.request.eject(myInterceptor);
```

## 高级用法

### 1. 取消请求（Cancellation）

```javascript
// 使用CancelToken
const CancelToken = axios.CancelToken;
const source = CancelToken.source();

axios.get('/user/12345', {
  cancelToken: source.token
}).catch(function (thrown) {
  if (axios.isCancel(thrown)) {
    console.log('Request canceled', thrown.message);
  } else {
    // 处理错误
  }
});

// 取消请求（message参数是可选的）
source.cancel('Operation canceled by the user.');

// 在Vue组件中使用
export default {
  data() {
    return {
      cancelTokenSource: null
    }
  },
  methods: {
    async fetchData() {
      // 取消之前的请求
      if (this.cancelTokenSource) {
        this.cancelTokenSource.cancel('取消之前的请求')
      }
      
      // 创建新的取消令牌
      this.cancelTokenSource = axios.CancelToken.source()
      
      try {
        const response = await axios.get('/api/data', {
          cancelToken: this.cancelTokenSource.token
        })
        this.data = response.data
      } catch (error) {
        if (axios.isCancel(error)) {
          console.log('请求被取消:', error.message)
        } else {
          console.error('请求失败:', error)
        }
      }
    }
  },
  beforeDestroy() {
    // 组件销毁时取消请求
    if (this.cancelTokenSource) {
      this.cancelTokenSource.cancel('组件销毁')
    }
  }
}
```

### 2. 并发请求（Concurrency）

```javascript
// 使用axios.all和axios.spread
function getUserAccount() {
  return axios.get('/user/12345');
}

function getUserPermissions() {
  return axios.get('/user/12345/permissions');
}

axios.all([getUserAccount(), getUserPermissions()])
  .then(axios.spread(function (acct, perms) {
    // 两个请求现在都执行完成
    console.log('用户账户:', acct.data)
    console.log('用户权限:', perms.data)
  }));

// 使用async/await（推荐）
async function getUserData() {
  try {
    const [accountResponse, permissionsResponse] = await axios.all([
      axios.get('/user/12345'),
      axios.get('/user/12345/permissions')
    ])
    
    return {
      account: accountResponse.data,
      permissions: permissionsResponse.data
    }
  } catch (error) {
    console.error('获取用户数据失败:', error)
    throw error
  }
}

// 或者使用Promise.all
async function getUserData2() {
  try {
    const [accountResponse, permissionsResponse] = await Promise.all([
      axios.get('/user/12345'),
      axios.get('/user/12345/permissions')
    ])
    
    return {
      account: accountResponse.data,
      permissions: permissionsResponse.data
    }
  } catch (error) {
    console.error('获取用户数据失败:', error)
    throw error
  }
}
```

### 3. 文件上传（File Upload）

```javascript
// 基础文件上传
async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
        console.log(`上传进度: ${percentCompleted}%`)
      }
    })
    
    return response.data
  } catch (error) {
    console.error('文件上传失败:', error)
    throw error
  }
}

// 多文件上传
async function uploadMultipleFiles(files) {
  const formData = new FormData()
  
  files.forEach(file => {
    formData.append('files', file)
  })
  
  try {
    const response = await axios.post('/api/upload-multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    return response.data
  } catch (error) {
    console.error('文件上传失败:', error)
    throw error
  }
}

// 在Vue组件中使用
export default {
  data() {
    return {
      uploadProgress: 0,
      uploading: false
    }
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      this.uploading = true
      this.uploadProgress = 0
      
      try {
        const response = await this.uploadFile(file)
        this.$message.success('文件上传成功！')
        console.log('上传结果:', response)
      } catch (error) {
        this.$message.error('文件上传失败！')
      } finally {
        this.uploading = false
      }
    },
    
    async uploadFile(file) {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await this.$axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          this.uploadProgress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
        }
      })
      
      return response.data
    }
  }
}
```

### 4. 文件下载（File Download）

```javascript
// 文件下载
async function downloadFile(url, filename) {
  try {
    const response = await axios.get(url, {
      responseType: 'blob', // 重要：指定响应类型为blob
      onDownloadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
        console.log(`下载进度: ${percentCompleted}%`)
      }
    })
    
    // 创建下载链接
    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
    
    return response.data
  } catch (error) {
    console.error('文件下载失败:', error)
    throw error
  }
}

// 在Vue组件中使用
export default {
  methods: {
    async handleDownload(fileId, filename) {
      try {
        await this.downloadFile(`/api/download/${fileId}`, filename)
        this.$message.success('文件下载成功！')
      } catch (error) {
        this.$message.error('文件下载失败！')
      }
    },
    
    async downloadFile(url, filename) {
      const response = await this.$axios.get(url, {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    }
  }
}
```

## 错误处理最佳实践

### 1. 统一的错误处理

```javascript
// 创建错误处理类
class RequestError extends Error {
  constructor(message, code, response) {
    super(message)
    this.name = 'RequestError'
    this.code = code
    this.response = response
  }
}

// 在响应拦截器中统一处理
axios.interceptors.response.use(
  response => {
    // 业务逻辑成功
    if (response.data.code === 200) {
      return response.data
    }
    
    // 业务逻辑失败
    throw new RequestError(
      response.data.message || '请求失败',
      response.data.code,
      response
    )
  },
  error => {
    // HTTP错误
    if (error.response) {
      // 服务器响应了请求，但状态码不在2xx范围内
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          throw new RequestError('请求参数错误', 400, error.response)
        case 401:
          throw new RequestError('未授权，请重新登录', 401, error.response)
        case 403:
          throw new RequestError('没有权限访问', 403, error.response)
        case 404:
          throw new RequestError('请求的资源不存在', 404, error.response)
        case 500:
          throw new RequestError('服务器内部错误', 500, error.response)
        default:
          throw new RequestError(`请求失败: ${status}`, status, error.response)
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      throw new RequestError('网络连接失败，请检查网络', 'NETWORK_ERROR', null)
    } else {
      // 发送请求时发生了错误
      throw new RequestError('请求发送失败', 'REQUEST_ERROR', null)
    }
  }
)

// 在组件中使用
try {
  const data = await axios.get('/api/data')
  console.log('请求成功:', data)
} catch (error) {
  if (error instanceof RequestError) {
    console.error('请求错误:', error.message, '错误码:', error.code)
    
    // 根据错误码进行不同的处理
    switch (error.code) {
      case 401:
        // 跳转到登录页
        router.push('/login')
        break
      case 403:
        // 显示权限不足提示
        Message.error('您没有权限执行此操作')
        break
      case 'NETWORK_ERROR':
        // 显示网络错误提示
        Message.error('网络连接失败，请检查网络设置')
        break
      default:
        // 显示通用错误提示
        Message.error(error.message || '请求失败')
    }
  } else {
    console.error('未知错误:', error)
    Message.error('发生未知错误')
  }
}
```

### 2. 重试机制

```javascript
// 请求重试函数
async function requestWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await axios(url, options)
      return response
    } catch (error) {
      // 如果是最后一次尝试，则抛出错误
      if (i === maxRetries - 1) {
        throw error
      }
      
      // 如果不是网络错误，不重试
      if (!error.code === 'NETWORK_ERROR') {
        throw error
      }
      
      // 等待一段时间后重试（指数退避）
      const delay = Math.pow(2, i) * 1000
      console.log(`请求失败，${delay}ms后重试...`)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
}

// 在拦截器中实现重试
axios.interceptors.response.use(
  response => response,
  async error => {
    const config = error.config
    
    // 如果配置中没有retry属性，不重试
    if (!config || !config.retry) {
      return Promise.reject(error)
    }
    
    // 如果已经重试了指定次数，不再重试
    config.retryCount = config.retryCount || 0
    if (config.retryCount >= config.retry) {
      return Promise.reject(error)
    }
    
    // 增加重试次数
    config.retryCount += 1
    
    // 等待一段时间后重试
    const delay = Math.pow(2, config.retryCount) * 1000
    console.log(`请求失败，${delay}ms后重试...`)
    
    await new Promise(resolve => setTimeout(resolve, delay))
    
    // 重新发送请求
    return axios(config)
  }
)

// 使用重试机制
const response = await axios.get('/api/data', {
  retry: 3, // 最多重试3次
  retryDelay: 1000 // 重试间隔1秒
})
```

## 性能优化

### 1. 请求缓存

```javascript
// 简单的请求缓存
const requestCache = new Map()

async function cachedRequest(url, options = {}) {
  // 生成缓存key
  const cacheKey = `${url}_${JSON.stringify(options)}`
  
  // 检查缓存
  if (requestCache.has(cacheKey)) {
    console.log('使用缓存数据:', cacheKey)
    return requestCache.get(cacheKey)
  }
  
  // 发送请求
  const response = await axios(url, options)
  
  // 缓存响应（设置5分钟过期时间）
  requestCache.set(cacheKey, response)
  setTimeout(() => {
    requestCache.delete(cacheKey)
  }, 5 * 60 * 1000)
  
  return response
}

// 在Vue中使用
export default {
  methods: {
    async getUserData(userId) {
      try {
        const response = await cachedRequest(`/api/user/${userId}`)
        return response.data
      } catch (error) {
        console.error('获取用户数据失败:', error)
        throw error
      }
    }
  }
}
```

### 2. 请求去重

```javascript
// 请求去重
const pendingRequests = new Map()

async function deduplicatedRequest(url, options = {}) {
  // 生成请求key
  const requestKey = `${url}_${JSON.stringify(options)}`
  
  // 检查是否有正在进行的相同请求
  if (pendingRequests.has(requestKey)) {
    console.log('请求已存在，等待结果:', requestKey)
    return pendingRequests.get(requestKey)
  }
  
  // 创建新的请求
  const requestPromise = axios(url, options)
  
  // 存储请求promise
  pendingRequests.set(requestKey, requestPromise)
  
  try {
    const response = await requestPromise
    return response
  } finally {
    // 请求完成后删除
    pendingRequests.delete(requestKey)
  }
}
```

### 3. 请求队列

```javascript
// 请求队列管理器
class RequestQueue {
  constructor(maxConcurrent = 5) {
    this.maxConcurrent = maxConcurrent
    this.queue = []
    this.running = 0
  }
  
  async add(requestFn) {
    return new Promise((resolve, reject) => {
      this.queue.push({
        requestFn,
        resolve,
        reject
      })
      
      this.process()
    })
  }
  
  async process() {
    if (this.running >= this.maxConcurrent || this.queue.length === 0) {
      return
    }
    
    this.running++
    const { requestFn, resolve, reject } = this.queue.shift()
    
    try {
      const result = await requestFn()
      resolve(result)
    } catch (error) {
      reject(error)
    } finally {
      this.running--
      this.process()
    }
  }
}

// 使用请求队列
const requestQueue = new RequestQueue(3) // 最多3个并发请求

// 添加请求到队列
const response = await requestQueue.add(() => 
  axios.get('/api/data')
)
```

## 常见问题解答

### Q1：如何处理跨域问题？

**A**：
1. **开发环境**：配置代理服务器
```javascript
// vue.config.js
module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      }
    }
  }
}
```

2. **生产环境**：后端设置CORS头
```javascript
// 后端设置
response.setHeader('Access-Control-Allow-Origin', '*')
response.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
response.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')
```

### Q2：如何设置全局的请求头？

**A**：
```javascript
// 方法一：设置默认请求头
axios.defaults.headers.common['Authorization'] = 'Bearer token'
axios.defaults.headers.post['Content-Type'] = 'application/json'

// 方法二：在拦截器中设置
axios.interceptors.request.use(config => {
  config.headers['Authorization'] = 'Bearer token'
  config.headers['X-Custom-Header'] = 'custom-value'
  return config
})
```

### Q3：如何处理网络超时？

**A**：
```javascript
// 设置超时时间
const service = axios.create({
  timeout: 5000, // 5秒超时
  timeoutErrorMessage: '网络连接超时，请检查网络'
})

// 在错误处理中捕获超时
service.interceptors.response.use(
  response => response,
  error => {
    if (error.code === 'ECONNABORTED') {
      // 超时处理
      Message.error('请求超时，请稍后重试')
    }
    return Promise.reject(error)
  }
)
```

### Q4：如何上传大文件？

**A**：
```javascript
// 分片上传大文件
async function uploadLargeFile(file, chunkSize = 5 * 1024 * 1024) {
  const chunks = Math.ceil(file.size / chunkSize)
  const uploadedChunks = []
  
  for (let i = 0; i < chunks; i++) {
    const start = i * chunkSize
    const end = Math.min(start + chunkSize, file.size)
    const chunk = file.slice(start, end)
    
    const formData = new FormData()
    formData.append('file', chunk)
    formData.append('chunk', i)
    formData.append('chunks', chunks)
    formData.append('filename', file.name)
    
    try {
      const response = await axios.post('/api/upload-chunk', formData)
      uploadedChunks.push(i)
      console.log(`分片 ${i + 1}/${chunks} 上传完成`)
    } catch (error) {
      console.error(`分片 ${i + 1} 上传失败:`, error)
      throw error
    }
  }
  
  // 合并分片
  await axios.post('/api/merge-chunks', {
    filename: file.name,
    chunks: chunks
  })
  
  console.log('文件上传完成')
}
```

### Q5：如何实现请求防抖？

**A**：
```javascript
// 请求防抖
function debounceRequest(requestFn, delay = 300) {
  let timeoutId = null
  let pendingPromise = null
  
  return function (...args) {
    // 清除之前的定时器
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    
    // 返回新的Promise
    return new Promise((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await requestFn(...args)
          resolve(result)
        } catch (error) {
          reject(error)
        }
      }, delay)
    })
  }
}

// 使用防抖
const debouncedSearch = debounceRequest(async (keyword) => {
  const response = await axios.get('/api/search', {
    params: { keyword }
  })
  return response.data
}, 500)

// 在输入框中使用
export default {
  methods: {
    async handleSearch(keyword) {
      try {
        const results = await debouncedSearch(keyword)
        this.searchResults = results
      } catch (error) {
        console.error('搜索失败:', error)
      }
    }
  }
}
```

## 实战：完整的请求封装

```javascript
// /src/utils/request.js
import axios from 'axios'
import { Message, MessageBox } from 'element-ui'
import store from '@/store'
import { getToken } from '@/utils/auth'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // api的base_url
  timeout: 5000 // 请求超时时间
})

// request拦截器
service.interceptors.request.use(
  config => {
    // 是否需要设置token
    const isToken = (config.headers || {}).isToken === false
    if (getToken() && !isToken) {
      config.headers['Authorization'] = 'Bearer ' + getToken() // 让每个请求携带自定义token 请根据实际情况自行修改
    }
    // get请求映射params参数
    if (config.method === 'get' && config.params) {
      let url = config.url + '?';
      for (const propName of Object.keys(config.params)) {
        const value = config.params[propName];
        var part = encodeURIComponent(propName) + "=";
        if (value !== null && typeof(value) !== "undefined") {
          if (typeof value === 'object') {
            for (const key of Object.keys(value)) {
              let params = propName + '[' + key + ']';
              var subPart = encodeURIComponent(params) + "=";
              url += subPart + encodeURIComponent(value[key]) + "&";
            }
          } else {
            url += part + encodeURIComponent(value) + "&";
          }
        }
      }
      url = url.slice(0, -1);
      config.params = {};
      config.url = url;
    }
    return config
  },
  error => {
    console.log(error)
    Promise.reject(error)
  }
)

// response拦截器
service.interceptors.response.use(
  response => {
    const code = response.data.code || 200;
    const msg = response.data.msg || '操作成功'
    if (code === 401) {
      MessageBox.confirm(
        '登录状态已过期，您可以继续留在该页面，或者重新登录',
        '系统提示',
        {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        store.dispatch('LogOut').then(() => {
          location.reload() // 为了重新实例化vue-router对象 避免bug
        })
      })
      return Promise.reject('error')
    } else if (code !== 200) {
      Message({
        message: msg,
        type: 'error'
      })
      return Promise.reject('error')
    } else {
      return response.data
    }
  },
  error => {
    console.log('err' + error)
    let { message } = error;
    if (message == "Network Error") {
      message = "后端接口连接异常";
    } else if (message.includes("timeout")) {
      message = "系统接口请求超时";
    } else if (message.includes("Request failed with status code")) {
      message = "系统接口" + message.substr(message.length - 3) + "异常";
    }
    Message({
      message: message,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service
```

## 下一步学习

掌握了Axios后，建议继续学习：
1. **GraphQL** - 现代API查询语言
2. **WebSocket** - 实时通信
3. **Service Worker** - 离线缓存和请求拦截
4. **HTTP/2** - 现代HTTP协议

## 面试常见问题

1. **Axios和Fetch有什么区别？**
2. **如何处理Axios的请求超时？**
3. **Axios的拦截器是如何实现的？**
4. **如何取消Axios的请求？**
5. **Axios如何处理文件上传？**
6. **如何实现Axios的请求重试机制？**
7. **Axios如何处理跨域问题？**

通过本教程的学习，你应该对Axios有了全面的了解。LiuMa项目中的网络请求封装是一个很好的实战案例，建议你仔细研究其错误处理、拦截器和请求封装的设计思路。