"""
配置管理模块

管理CLI的配置信息，包括：
- Base URL
- Token
- 当前项目/模块
- 用户账号信息
"""

import json
import os
from pathlib import Path
from typing import Optional

import appdirs


class Config:
    """配置管理类"""

    APP_NAME = "testplatform"
    APP_AUTHOR = "autotest"

    def __init__(self):
        self.config_dir = Path(appdirs.user_config_dir(self.APP_NAME, self.APP_AUTHOR))
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
        self._load_config()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                data = {}
        else:
            data = {}

        self.base_url: str = data.get('base_url', 'http://localhost:8080')
        self.token: Optional[str] = data.get('token')
        self.current_project: Optional[str] = data.get('current_project')
        self.current_module: Optional[str] = data.get('current_module')
        self.account: Optional[str] = data.get('account')

    def save(self):
        """保存配置到文件"""
        data = {
            'base_url': self.base_url,
            'token': self.token,
            'current_project': self.current_project,
            'current_module': self.current_module,
            'account': self.account,
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def set_token(self, token: str):
        """设置Token"""
        self.token = token
        self.save()

    def set_project(self, project_id: str):
        """设置当前项目"""
        self.current_project = project_id
        self.save()

    def set_module(self, module_id: str):
        """设置当前模块"""
        self.current_module = module_id
        self.save()

    def set_account(self, account: str):
        """设置当前账号"""
        self.account = account
        self.save()

    def clear(self):
        """清除所有配置"""
        self.token = None
        self.current_project = None
        self.current_module = None
        self.account = None
        self.save()

    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.token is not None

    def get_current_project_id(self) -> Optional[str]:
        """获取当前项目ID

        从current_project字符串中提取ID部分
        格式可能是 "项目名称 (ID: xxx)" 或直接是ID
        """
        if not self.current_project:
            return None

        # 尝试从格式 "项目名称 (ID: xxx)" 中提取
        if "(ID:" in self.current_project:
            import re
            match = re.search(r'\(ID:\s*([^)]+)\)', self.current_project)
            if match:
                return match.group(1).strip()

        # 如果就是纯ID格式
        return self.current_project

    def get_current_env_id(self) -> Optional[str]:
        """获取当前环境ID"""
        # 环境ID通常存储在配置中
        return getattr(self, 'current_env', None)

    def set_env(self, env_id: str):
        """设置当前环境"""
        self.current_env = env_id
        self.save()
