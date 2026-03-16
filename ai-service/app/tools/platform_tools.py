"""
平台API工具模块

职责：
    1. 封装与SpringBoot后端的HTTP通信
    2. 提供接口查询、详情获取、Schema获取等功能
    3. 处理认证和错误处理

核心类：
    - PlatformClient: 平台API客户端

主要方法：
    - get_api_list(): 获取项目接口列表
    - get_api_detail(): 获取接口详情
    - get_case_schema(): 获取用例Schema

请求配置：
    - base_url: 从 config.platform_base_url 读取
    - timeout: 默认30秒
    - headers: 包含token认证
"""

from typing import Any, Dict, List, Optional
import httpx

from app.config import config
from app.observability import app_logger


class PlatformClient:
    """
    平台API客户端

    职责：
        - 封装与SpringBoot后端的HTTP通信
        - 提供接口查询功能
        - 处理认证和错误

    使用示例：
        client = PlatformClient(token="xxx")
        apis = client.get_api_list("project-id")
        detail = client.get_api_detail("api-id")
    """

    def __init__(self, token: str = ""):
        """
        初始化平台客户端

        @param token: 认证token（从请求头传递）
        """
        self.base_url = config.platform_base_url.rstrip("/")
        self.token = token
        self.timeout = config.platform_timeout
        self._last_error: Optional[str] = None

    def _get_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["token"] = self.token
        return headers

    def _unwrap_data(self, payload: Any) -> Any:
        """兼容后端统一响应包装，提取真实数据"""
        current = payload
        for _ in range(4):
            if not isinstance(current, dict):
                return current
            if "data" in current:
                current = current.get("data")
                continue
            return current
        return current

    def _extract_list(self, payload: Any) -> List[Dict[str, Any]]:
        """从后端返回中提取列表数据"""
        data = self._unwrap_data(payload)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            if isinstance(data.get("list"), list):
                return [item for item in data.get("list", []) if isinstance(item, dict)]
            if isinstance(data.get("rows"), list):
                return [item for item in data.get("rows", []) if isinstance(item, dict)]
            if isinstance(data.get("data"), list):
                return [item for item in data.get("data", []) if isinstance(item, dict)]
        return []

    def get_api_list(self, project_id: str) -> List[Dict[str, Any]]:
        """
        获取项目接口列表

        @param project_id: 项目ID
        @return: 接口列表

        请求示例：
            GET /autotest/api/list?projectId={project_id}

        返回示例：
            [
                {"id": "api-001", "name": "登录接口", "path": "/api/login", "method": "POST"},
                ...
            ]
        """
        try:
            url = f"{self.base_url}/autotest/api/list/1/2000"
            response = httpx.post(
                url,
                json={"projectId": project_id},
                headers=self._get_headers(),
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                items = self._extract_list(data)
                if items:
                    self._last_error = None
                else:
                    self._last_error = "接口列表为空或结构异常"
                return items
            else:
                self._last_error = f"API列表获取失败: HTTP {response.status_code}"
                app_logger.error("{}", self._last_error)
                return []

        except Exception as e:
            self._last_error = f"API列表获取异常: {str(e)}"
            app_logger.error("{}", self._last_error)
            return []

    def get_api_detail(self, api_id: str) -> Optional[Dict[str, Any]]:
        """
        获取接口详情

        @param api_id: 接口ID
        @return: 接口详情

        请求示例：
            GET /autotest/api/detail/{api_id}

        返回示例：
            {
                "id": "api-001",
                "name": "登录接口",
                "path": "/api/login",
                "method": "POST",
                "headers": [...],
                "body": {...},
                ...
            }
        """
        try:
            url = f"{self.base_url}/autotest/api/detail/{api_id}"

            response = httpx.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                detail = self._unwrap_data(data)
                return detail if isinstance(detail, dict) else None
            else:
                app_logger.error("接口详情获取失败: HTTP {}", response.status_code)
                return None

        except Exception as e:
            app_logger.error("接口详情获取异常: {}", str(e))
            return None

    def get_case_schema(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用例Schema

        用于用例生成时了解用例的数据结构要求。

        @param project_id: 项目ID
        @return: 用例Schema
        """
        try:
            url = f"{self.base_url}/autotest/ai/schema/case"
            params = {"projectId": project_id}

            response = httpx.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                schema = self._unwrap_data(data)
                return schema if isinstance(schema, dict) else None
            else:
                app_logger.error("用例Schema获取失败: HTTP {}", response.status_code)
                return None

        except Exception as e:
            app_logger.error("用例Schema获取异常: {}", str(e))
            return None

    def get_last_error(self) -> Optional[str]:
        """获取最后一次错误信息"""
        return self._last_error


if __name__ == "__main__":
    """平台API客户端调试"""
    print("=" * 60)
    print("平台API客户端调试")
    print("=" * 60)

    # 注意：需要配置正确的平台地址和token才能测试
    print("\n平台配置:")
    print(f"   Base URL: {config.platform_base_url}")
    print(f"   Timeout: {config.platform_timeout}s")

    print("\n客户端初始化:")
    client = PlatformClient(token="test-token")
    print(f"   Token: {client.token}")
    print(f"   Headers: {client._get_headers()}")

    print("\n注意：实际API调用需要正确的平台地址和token")
    print("=" * 60)
