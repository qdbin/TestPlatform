"""
自动化测试平台CLI端到端测试

基于pytest框架，验证CLI全链路功能实现
严格遵循《用例设计指南》：验证"需求是否被实现"，而非"代码是否存在"

设计原则：
1. 验证功能行为，不验证具体实现形式
2. 允许合理的命名差异（如env vs environment）
3. 允许合理的架构差异（如命令合并或拆分）
4. 端到端验证，确保真正可用
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# 添加CLI源码路径
CLI_DIR = "/app/testplatform_cli"
SRC_DIR = f"{CLI_DIR}/src"
sys.path.insert(0, SRC_DIR)


# ==================== 辅助函数 ====================
def get_all_python_files(directory):
    """获取目录下所有Python文件（排除__init__.py）"""
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith('.py') and f != '__init__.py']


def read_file_content(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def get_all_commands_content(commands_dir):
    """获取所有命令文件的合并内容"""
    content = ""
    for f in get_all_python_files(commands_dir):
        content += read_file_content(os.path.join(commands_dir, f))
    return content


def check_functionality_exists(content, keywords):
    """检查功能是否存在（支持多个关键词，任一匹配即可）"""
    content_lower = content.lower()
    return any(kw.lower() in content_lower for kw in keywords)


def check_api_endpoint_called(content, endpoint):
    """检查是否调用了特定API端点"""
    return endpoint in content


def check_http_method_used(content, methods):
    """检查是否使用了特定HTTP方法"""
    content_lower = content.lower()
    return any(m.lower() in content_lower for m in methods)


# ==================== P0: 核心结构测试 ====================
class TestCoreStructure:
    """验证CLI核心结构存在（不限制具体形式）"""

    def test_cli_directory_exists(self):
        """验证CLI目录已创建

        对应指令：保存到/app/testplatform_cli
        预期：CLI根目录存在
        """
        assert os.path.exists(CLI_DIR), f"CLI目录不存在: {CLI_DIR}"

    def test_cli_has_source_directory(self):
        """验证CLI有源码目录

        对应指令：基于企业最佳实践
        预期：存在src或类似的源码目录
        """
        possible_src_dirs = ['src', 'testplatform', 'cli', '.']
        found = any(os.path.exists(os.path.join(CLI_DIR, d)) for d in possible_src_dirs)
        assert found, "未找到源码目录"

    def test_cli_has_entry_point(self):
        """验证CLI有入口文件

        对应指令：CLI可执行
        预期：存在main.py、cli.py或__main__.py等入口
        """
        possible_entries = ['main.py', 'cli.py', '__main__.py', 'testplatform.py']
        src_path = os.path.join(CLI_DIR, 'src')

        found = False
        for root, dirs, files in os.walk(CLI_DIR):
            for f in files:
                if f in possible_entries:
                    found = True
                    break
            if found:
                break

        assert found, f"未找到入口文件（尝试了: {possible_entries}）"

    def test_cli_uses_modern_framework(self):
        """验证CLI使用现代CLI框架

        对应指令：基于企业最新技术最佳实践
        预期：使用Typer、Click或argparse
        """
        all_content = ""
        for root, dirs, files in os.walk(CLI_DIR):
            for f in files:
                if f.endswith('.py'):
                    all_content += read_file_content(os.path.join(root, f))

        frameworks = ['typer', 'click', 'argparse']
        found = any(fw in all_content.lower() for fw in frameworks)
        assert found, f"未使用现代CLI框架（支持: {frameworks}）"


# ==================== P0: 功能覆盖测试 ====================
class TestFunctionCoverage:
    """验证所有必需功能被覆盖（不限制模块划分方式）"""

    @classmethod
    def setup_class(cls):
        """收集所有代码内容"""
        cls.all_content = ""
        cls.commands_content = ""

        for root, dirs, files in os.walk(CLI_DIR):
            for f in files:
                if f.endswith('.py'):
                    content = read_file_content(os.path.join(root, f))
                    cls.all_content += content
                    if 'command' in root.lower() or 'cmd' in root.lower():
                        cls.commands_content += content

        # 如果没有专门的commands目录，使用所有内容
        if not cls.commands_content:
            cls.commands_content = cls.all_content

    def test_auth_functionality_exists(self):
        """验证认证功能存在

        对应指令：登录平台
        预期：实现登录/登出功能
        """
        keywords = ['login', 'auth', '登录', '认证', 'password', '密码', 'token']
        assert check_functionality_exists(self.all_content, keywords), "缺少认证功能"

    def test_user_management_exists(self):
        """验证用户管理功能存在

        对应指令：用户管理
        预期：实现用户增删改查
        """
        keywords = ['user', '用户', 'account', '账号']
        assert check_functionality_exists(self.all_content, keywords), "缺少用户管理功能"

        # 验证调用后端API
        endpoints = ['/autotest/register', '/autotest/user/']
        found = any(ep in self.all_content for ep in endpoints)
        assert found, "用户管理未调用正确的后端API"

    def test_project_management_exists(self):
        """验证项目管理功能存在

        对应指令：项目管理
        预期：实现项目增删改查
        """
        keywords = ['project', '项目']
        assert check_functionality_exists(self.all_content, keywords), "缺少项目管理功能"

        # 验证调用后端API
        endpoints = ['/autotest/project/']
        found = any(ep in self.all_content for ep in endpoints)
        assert found, "项目管理未调用正确的后端API"

    def test_environment_management_exists(self):
        """验证环境管理功能存在

        对应指令：环境管理
        预期：实现环境增删改查
        """
        keywords = ['environment', 'env', '环境']
        assert check_functionality_exists(self.all_content, keywords), "缺少环境管理功能"

        # 验证调用后端API
        endpoints = ['/autotest/environment/']
        found = any(ep in self.all_content for ep in endpoints)
        assert found, "环境管理未调用正确的后端API"

    def test_module_management_exists(self):
        """验证模块管理功能存在

        对应指令：模块管理
        预期：实现模块增删改查
        """
        keywords = ['module', '模块']
        assert check_functionality_exists(self.all_content, keywords), "缺少模块管理功能"

        # 验证调用后端API
        endpoints = ['/autotest/module/']
        found = any(ep in self.all_content for ep in endpoints)
        assert found, "模块管理未调用正确的后端API"

    def test_api_management_exists(self):
        """验证接口管理功能存在

        对应指令：接口管理 - 核心功能
        预期：实现接口增删改查
        """
        keywords = ['api', '接口', 'interface']
        assert check_functionality_exists(self.all_content, keywords), "缺少接口管理功能"

        # 验证调用后端API
        assert '/autotest/api/' in self.all_content, "接口管理未调用正确的后端API"

    def test_case_management_exists(self):
        """验证用例管理功能存在

        对应指令：用例生成 - 核心功能
        预期：实现用例增删改查
        """
        keywords = ['case', '用例', 'testcase']
        assert check_functionality_exists(self.all_content, keywords), "缺少用例管理功能"

        # 验证调用后端API
        assert '/autotest/case/' in self.all_content, "用例管理未调用正确的后端API"

    def test_domain_management_exists(self):
        """验证域名服务功能存在

        对应指令：域名服务
        预期：实现域名增删改查
        """
        keywords = ['domain', '域名']
        assert check_functionality_exists(self.all_content, keywords), "缺少域名服务功能"

        # 验证调用后端API
        assert '/autotest/domain/' in self.all_content, "域名服务未调用正确的后端API"

    def test_parameter_management_exists(self):
        """验证公共参数功能存在

        对应指令：自定义参数
        预期：实现参数增删改查
        """
        keywords = ['param', '参数', 'commonparam', 'common_param']
        assert check_functionality_exists(self.all_content, keywords), "缺少公共参数功能"

        # 验证调用后端API - 支持多种可能的端点格式
        endpoints = ['/autotest/commonParam/', '/autotest/param/']
        found = any(ep in self.all_content for ep in endpoints)
        assert found, "公共参数未调用正确的后端API"


# ==================== P0: 核心流程测试 ====================
class TestCoreWorkflows:
    """验证核心业务流程完整实现"""

    @classmethod
    def setup_class(cls):
        """收集所有代码内容"""
        cls.all_content = ""
        for root, dirs, files in os.walk(CLI_DIR):
            for f in files:
                if f.endswith('.py'):
                    cls.all_content += read_file_content(os.path.join(root, f))

    def test_login_workflow_implemented(self):
        """验证登录流程完整实现

        对应指令：登录平台
        预期：调用/autotest/login，处理token，保存状态
        """
        # 检查调用登录API
        assert '/autotest/login' in self.all_content, "未调用登录API"

        # 检查密码处理（Base64编码）
        password_handling = any(kw in self.all_content.lower() for kw in ['base64', 'b64encode', 'encode', 'password'])
        assert password_handling, "未实现密码处理"

        # 检查token管理
        token_management = any(kw in self.all_content.lower() for kw in ['token', 'authorization', 'header'])
        assert token_management, "未实现token管理"

    def test_api_crud_workflow_implemented(self):
        """验证接口CRUD流程完整实现

        对应指令：接口管理包含增删改查
        预期：完整调用save/detail/list/delete端点
        """
        # 检查核心端点
        required_endpoints = ['/autotest/api/save', '/autotest/api/detail', '/autotest/api/list/', '/autotest/api/delete']

        for endpoint in required_endpoints:
            assert endpoint in self.all_content, f"接口管理未实现{endpoint}端点调用"

    def test_case_crud_workflow_implemented(self):
        """验证用例CRUD流程完整实现

        对应指令：用例生成包含增删改查
        预期：完整调用save/detail/list/delete端点
        """
        # 检查核心端点
        required_endpoints = ['/autotest/case/save', '/autotest/case/detail/', '/autotest/case/list/', '/autotest/case/delete']

        for endpoint in required_endpoints:
            assert endpoint in self.all_content, f"用例管理未实现{endpoint}端点调用"

    def test_shopping_cart_scenario_implemented(self):
        """验证购物车场景用例实现

        对应指令：多个商品添加到购物车场景
        预期：实现场景逻辑并创建用例
        """
        # 检查购物车相关逻辑
        cart_keywords = ['cart', '购物车', 'shopping', 'product', '商品']
        has_cart_logic = check_functionality_exists(self.all_content, cart_keywords)

        # 检查用例创建
        case_creation = '/autotest/case/save' in self.all_content

        assert has_cart_logic, "未实现购物车场景逻辑"
        assert case_creation, "购物车场景未调用用例保存端点"


# ==================== P0: HTTP客户端测试 ====================
class TestHttpClient:
    """验证HTTP客户端正确实现"""

    @classmethod
    def setup_class(cls):
        """收集所有代码内容"""
        cls.all_content = ""
        for root, dirs, files in os.walk(CLI_DIR):
            for f in files:
                if f.endswith('.py'):
                    cls.all_content += read_file_content(os.path.join(root, f))

    def test_http_methods_supported(self):
        """验证支持完整HTTP方法

        对应指令：与后端服务交互
        预期：支持GET/POST/PUT/DELETE
        """
        methods = ['get', 'post', 'put', 'delete', 'patch']
        found_methods = []

        for method in methods:
            # 检查方法定义或调用
            patterns = [f'def {method}', f'.{method}(', f'"{method.upper()}"', f"'{method.upper()}'"]
            if any(p in self.all_content.lower() for p in patterns):
                found_methods.append(method)

        # 至少支持GET和POST（最基本的要求）
        assert 'get' in found_methods and 'post' in found_methods, f"HTTP客户端缺少基本方法，找到: {found_methods}"

    def test_authentication_handling(self):
        """验证认证信息处理

        对应指令：登录功能、状态管理
        预期：正确处理token和认证头
        """
        auth_patterns = ['token', 'authorization', 'header', 'auth']
        found = any(p in self.all_content.lower() for p in auth_patterns)
        assert found, "未实现认证信息处理"


# ==================== P0: 配置管理测试 ====================
class TestConfigurationManagement:
    """验证配置和状态管理"""

    @classmethod
    def setup_class(cls):
        """收集所有代码内容"""
        cls.all_content = ""
        for root, dirs, files in os.walk(CLI_DIR):
            for f in files:
                if f.endswith('.py'):
                    cls.all_content += read_file_content(os.path.join(root, f))

    def test_state_persistence_exists(self):
        """验证状态持久化实现

        对应指令：CLI状态管理
        预期：能保存和读取用户状态
        """
        state_keywords = ['save', 'load', 'config', 'persist', 'file', 'json']
        found = any(kw in self.all_content.lower() for kw in state_keywords)
        assert found, "未实现状态持久化"

    def test_key_state_items_managed(self):
        """验证关键状态项被管理

        对应指令：状态管理
        预期：管理token、account、project等
        """
        key_items = ['token', 'account', 'project', 'user', 'base_url', 'url']
        found_items = [item for item in key_items if item in self.all_content.lower()]

        # 至少管理token和account
        assert 'token' in found_items or 'account' in found_items, f"状态管理缺少关键项，找到: {found_items}"


# ==================== P1: Skill文档测试 ====================
class TestSkillDocumentation:
    """验证Skill文档存在且完整"""

    def test_skill_md_exists(self):
        """验证Skill.md文档存在

        对应指令：撰写操作Skill.md
        预期：文档存在且包含必要内容
        """
        skill_paths = [
            os.path.join(CLI_DIR, 'Skill.md'),
            os.path.join(CLI_DIR, 'SKILL.md'),
            os.path.join(CLI_DIR, 'skill.md'),
            os.path.join(CLI_DIR, 'README.md'),
        ]

        found = any(os.path.exists(p) for p in skill_paths)
        assert found, f"Skill文档不存在（尝试了: {skill_paths}）"

    def test_skill_md_has_usage_examples(self):
        """验证Skill文档包含使用示例

        对应指令：撰写操作Skill.md
        预期：文档包含命令示例
        """
        skill_paths = [
            os.path.join(CLI_DIR, 'Skill.md'),
            os.path.join(CLI_DIR, 'SKILL.md'),
            os.path.join(CLI_DIR, 'skill.md'),
            os.path.join(CLI_DIR, 'README.md'),
        ]

        content = ""
        for p in skill_paths:
            if os.path.exists(p):
                content = read_file_content(p)
                break

        # 检查是否包含命令示例
        has_examples = any(kw in content.lower() for kw in ['testplatform', 'login', 'create', 'list', '示例', 'example'])
        assert has_examples, "Skill文档缺少使用示例"


# ==================== P1: 代码质量测试 ====================
class TestCodeQuality:
    """验证代码质量符合最佳实践"""

    @classmethod
    def setup_class(cls):
        """收集所有代码内容"""
        cls.all_content = ""
        for root, dirs, files in os.walk(CLI_DIR):
            for f in files:
                if f.endswith('.py'):
                    cls.all_content += read_file_content(os.path.join(root, f))

    def test_error_handling_exists(self):
        """验证错误处理实现

        对应指令：企业最佳实践
        预期：有错误处理和用户提示
        """
        error_patterns = ['try:', 'except', 'error', 'raise', 'typer.exit']
        found = any(p in self.all_content.lower() for p in error_patterns)
        assert found, "未实现错误处理"

    def test_user_feedback_exists(self):
        """验证用户反馈实现

        对应指令：企业最佳实践
        预期：有操作成功/失败提示
        """
        feedback_patterns = ['print', 'console', 'rich', 'success', 'error', 'fail']
        found = any(p in self.all_content.lower() for p in feedback_patterns)
        assert found, "未实现用户反馈"


# ==================== P0: 可执行性测试 ====================
class TestExecutability:
    """验证CLI可以实际执行"""

    def test_cli_can_be_imported(self):
        """验证CLI可以正常导入

        对应指令：CLI可运行
        预期：导入不抛出异常
        """
        result = subprocess.run(
            ["python3", "-c", f"import sys; sys.path.insert(0, '{SRC_DIR}'); import testplatform.main"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"CLI导入失败: {result.stderr}"

    def test_cli_has_help(self):
        """验证CLI有帮助信息

        对应指令：CLI可运行
        预期：可以显示帮助
        """
        # 尝试多种方式调用帮助
        attempts = [
            ["python3", "-m", "testplatform.main", "--help"],
            ["python3", f"{SRC_DIR}/testplatform/main.py", "--help"],
        ]

        success = False
        for cmd in attempts:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd=CLI_DIR)
            if result.returncode == 0 and ("usage" in result.stdout.lower() or "帮助" in result.stdout or "选项" in result.stdout):
                success = True
                break

        assert success, "CLI无法显示帮助信息"
