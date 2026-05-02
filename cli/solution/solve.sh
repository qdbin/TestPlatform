#!/bin/bash
set -e

echo "====== Starting CLI Solution Setup ======"

# 创建CLI目录
mkdir -p /app/testplatform_cli/src/testplatform/commands
mkdir -p /app/testplatform_cli/src/testplatform/services
mkdir -p /app/testplatform_cli/src/testplatform/utils

echo "====== Copying CLI files ======"

# 复制CLI文件到目标目录
cp -r /solution/files/* /app/testplatform_cli/

# 安装CLI依赖
echo "====== Installing CLI dependencies ======"
cd /app/testplatform_cli
pip3 install --break-system-packages -e . 2>/dev/null || pip3 install --break-system-packages typer rich httpx pyyaml appdirs python-dotenv

echo "====== CLI Setup Complete ======"

# 执行CLI命令完成场景
echo "====== Executing CLI Commands for Shopping Cart Scenario ======"

# 等待服务完全就绪
sleep 3

cd /app/testplatform_cli

# 测试登录命令帮助
echo "1. Testing login command help..."
python3 -m testplatform.main login --help

# 测试项目命令帮助
echo "2. Testing project command help..."
python3 -m testplatform.main project --help

# 测试用户命令帮助
echo "3. Testing user command help..."
python3 -m testplatform.main user --help

# 测试环境命令帮助
echo "4. Testing env command help..."
python3 -m testplatform.main env --help

# 测试模块命令帮助
echo "5. Testing module command help..."
python3 -m testplatform.main module --help

# 测试API命令帮助
echo "6. Testing api command help..."
python3 -m testplatform.main api --help

# 测试用例命令帮助（包含shopping-cart子命令）
echo "7. Testing case command help..."
python3 -m testplatform.main case --help

# 测试shopping-cart子命令帮助
echo "8. Testing shopping-cart subcommand help..."
python3 -m testplatform.main case shopping-cart --help

# 测试域名命令帮助
echo "9. Testing domain command help..."
python3 -m testplatform.main domain --help

# 测试参数命令帮助
echo "10. Testing param command help..."
python3 -m testplatform.main param --help

# 测试状态命令
echo "11. Testing status command..."
python3 -m testplatform.main status

echo "====== Solution Applied Successfully ======"
echo ""
echo "CLI工具已部署到 /app/testplatform_cli"
echo "包含以下功能模块:"
echo "  - auth: 认证管理（登录、登出）"
echo "  - user: 用户管理"
echo "  - project: 项目管理"
echo "  - env: 环境管理"
echo "  - module: 模块管理"
echo "  - api: 接口管理"
echo "  - case: 用例管理（含shopping-cart场景）"
echo "  - domain: 域名服务"
echo "  - param: 自定义参数"
echo ""
echo "购物车场景命令: testplatform case shopping-cart -p <project_id>"
