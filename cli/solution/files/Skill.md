# TestPlatform CLI Skill Guide

## 安装说明

1. 确保已安装 Python 3.8+。
2. 进入 `testplatform_cli` 目录。
3. 安装依赖：

```bash
pip install -e .
```

## 使用说明

`testplatform` 是一个基于 Typer 的自动化测试平台 CLI 工具，提供全链路接口与用例管理功能。

## 命令示例

### 登录

```bash
# 使用账号密码登录平台
testplatform login -a <account> -p <password> --url <base_url>

# 示例
testplatform login -a demo -p 123456 --url http://localhost:8080
testplatform login -a LMadmin -p Liuma@123456
```

### 用户管理

```bash
# 查询用户列表
testplatform user list

# 添加新用户
testplatform user add -n "张三" -e zhangsan@example.com

# 查看当前用户信息
testplatform user info
```

### 项目管理

```bash
# 创建新项目
testplatform project create -n "电商项目" -d "电商平台测试项目"

# 查询项目列表
testplatform project list

# 设置当前项目
testplatform project use <project_id>

# 查询项目成员
testplatform project members -p <project_id>
```

### 环境管理

```bash
# 创建新环境
testplatform env create -n "测试环境" -u "http://test.example.com"

# 查询环境列表
testplatform env list

# 设置当前环境
testplatform env select <env_id>
```

### 模块管理

```bash
# 创建模块
testplatform module create -n "订单模块" -p <project_id>

# 查询模块列表
testplatform module list

# 查看模块树
testplatform module tree
```

### 接口管理

```bash
# 创建接口
testplatform api create -n "获取商品列表" -m GET --path /api/products -p <project_id>
testplatform api create -n "添加购物车" -m POST --path /api/cart/add -p <project_id>

# 查询接口列表
testplatform api list -p <project_id>

# 查看接口详情
testplatform api get <api_id>
```

### 用例管理

```bash
# 创建用例
testplatform case create -n "添加商品到购物车" -t API -a <api_id1> -a <api_id2>

# 查询用例列表
testplatform case list -p <project_id>

# 导出用例
testplatform case export <case_id> -t API -o mycase.yaml
```

## 购物车场景

### 场景说明

`case shopping-cart` 命令用于演示【多个商品添加到购物车】的端到端场景，包含以下步骤：

1. **获取商品列表** - 调用商品查询接口
2. **添加商品A到购物车** - 添加第一个商品
3. **添加商品B到购物车** - 添加第二个商品
4. **验证购物车商品数量** - 验证购物车中商品总数

### 使用示例

```bash
# 创建购物车场景用例
testplatform case shopping-cart -p <project_id> -m <module_id>

# 示例
testplatform case shopping-cart -p proj123456 -m mod789012
```

### 场景用例详情

执行上述命令后，系统会自动创建一个名为"多个商品添加到购物车"的API类型用例，包含：

- **用例名称**: 多个商品添加到购物车
- **用例类型**: API
- **优先级**: P1
- **用例描述**: 端到端场景：多个商品添加到购物车，验证购物车功能正常
- **包含步骤**:
  - 步骤1: 获取商品列表（验证返回200状态码）
  - 步骤2: 添加商品A到购物车（productId: A001, quantity: 1）
  - 步骤3: 添加商品B到购物车（productId: B002, quantity: 2）
  - 步骤4: 验证购物车商品数量（验证totalCount等于3）

### 前置条件

执行购物车场景前，需要确保：

1. 已登录平台: `testplatform login -a <account> -p <password>`
2. 已创建或选择项目: `testplatform project use <project_id>`
3. 已创建模块（可选）: `testplatform module create -n "购物车模块"`

## 域名服务

```bash
# 创建域名
testplatform domain create -n "生产环境" -d "api.example.com"

# 查询域名列表
testplatform domain list

# 删除域名
testplatform domain delete <domain_id>
```

## 自定义参数

```bash
# 创建公共参数
testplatform param create -n "token" -v "Bearer xxx" -t header

# 查询参数列表
testplatform param list

# 删除参数
testplatform param delete <param_id>
```

## 其他命令

```bash
# 查看当前状态
testplatform status

# 登出
testplatform logout

# 显示帮助
testplatform --help
testplatform <command> --help
```

## 依赖说明

项目依赖包含：
- `typer` - CLI框架
- `rich` - 终端美化
- `httpx` - HTTP客户端
- `pyyaml` - YAML处理
- `appdirs` - 配置目录管理

## 完整流程示例

```bash
# 1. 登录
testplatform login -a demo -p 123456

# 2. 创建项目
testplatform project create -n "购物车测试项目"

# 3. 设置当前项目（假设返回的项目ID为proj123）
testplatform project use proj123

# 4. 创建模块
testplatform module create -n "购物车模块"

# 5. 创建接口
testplatform api create -n "获取商品列表" -m GET --path /api/products
testplatform api create -n "添加购物车" -m POST --path /api/cart/add

# 6. 执行购物车场景
testplatform case shopping-cart -p proj123

# 7. 查看创建的用例
testplatform case list -p proj123
```
