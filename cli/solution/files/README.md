# TestPlatform CLI

自动化测试平台命令行工具

## 功能特性

- 项目管理：创建、查询、切换项目
- 环境管理：创建、查询测试环境
- 模块管理：创建、查询API/Case模块树
- 接口管理：创建、查询接口定义
- 用例管理：创建、查询、导出测试用例
- 场景用例：支持端到端场景用例生成

## 安装

```bash
pip3 install -e .
```

## 快速开始

```bash
# 登录
testplatform login -a LMadmin -p Liuma@123456

# 创建购物车场景用例
testplatform case shopping-cart
```

## 技术栈

- Python 3.8+
- Typer
- Rich
- httpx
- PyYAML
