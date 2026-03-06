"""
平台API客户端工具
用于Agent调用流马平台API获取数据
"""

import httpx
from typing import Optional, List, Dict, Any
from app.config import config


class PlatformClient:
    """平台API客户端"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or config.platform_base_url
        self.api_key = api_key or ""
        self.timeout = config.platform_timeout
        self.last_error = ""

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "token": self.api_key,
        }
        return headers

    def _mark_error(self, message: str):
        self.last_error = str(message or "")

    def get_last_error(self) -> str:
        return self.last_error

    def _extract_success_data(self, payload: Any) -> Any:
        if not isinstance(payload, dict):
            self._mark_error("平台响应格式错误")
            return None
        status = payload.get("status")
        if status not in (0, "0", "success", "SUCCESS", True, None):
            self._mark_error(str(payload.get("message") or "平台业务状态异常"))
            return None
        self._mark_error("")
        return payload.get("data")

    def get_api_list(self, project_id: str) -> List[Dict[str, Any]]:
        """
        获取项目接口列表

        Args:
            project_id: 项目ID

        Returns:
            接口列表
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/autotest/api/list/1/2000",
                    json={"projectId": project_id},
                    headers=self._get_headers(),
                )
                if response.status_code == 200:
                    payload = response.json() or {}
                    outer_data = self._extract_success_data(payload)
                    if outer_data is None and self.last_error:
                        return []
                    if isinstance(outer_data, dict):
                        if isinstance(outer_data.get("data"), list):
                            return outer_data.get("data")
                        if isinstance(outer_data.get("list"), list):
                            return outer_data.get("list")
                    if isinstance(outer_data, list):
                        return outer_data
                    self._mark_error("接口列表为空或返回结构不匹配")
                    return []
                self._mark_error(f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self._mark_error(f"获取接口列表失败: {e}")
            return []

    def get_api_detail(self, api_id: str) -> Optional[Dict[str, Any]]:
        """
        获取接口详情

        Args:
            api_id: 接口ID

        Returns:
            接口详情
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/autotest/api/detail/{api_id}",
                    headers=self._get_headers(),
                )
                if response.status_code == 200:
                    payload = response.json() or {}
                    data = self._extract_success_data(payload)
                    if isinstance(data, dict):
                        return data
                    self._mark_error("接口详情为空")
                    return None
                self._mark_error(f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self._mark_error(f"获取接口详情失败: {e}")
            return None

    def get_environment_list(self, project_id: str) -> List[Dict[str, Any]]:
        """
        获取项目环境列表

        Args:
            project_id: 项目ID

        Returns:
            环境列表
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/autotest/environment/list",
                    params={"projectId": project_id},
                    headers=self._get_headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                return []
        except Exception as e:
            print(f"获取环境列表失败: {e}")
            return []

    def get_case_schema(self, project_id: str) -> Dict[str, Any]:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/autotest/ai/schema/case",
                    params={"projectId": project_id},
                    headers=self._get_headers(),
                )
                if response.status_code == 200:
                    payload = response.json() or {}
                    data = self._extract_success_data(payload)
                    if isinstance(data, dict):
                        return data
                return {}
        except Exception as e:
            self._mark_error(f"获取Case Schema失败: {e}")
            return {}

    def get_module_list(self, project_id: str) -> List[Dict[str, Any]]:
        """
        获取项目模块列表

        Args:
            project_id: 项目ID

        Returns:
            模块列表
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/autotest/module/list",
                    params={"projectId": project_id},
                    headers=self._get_headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                return []
        except Exception as e:
            print(f"获取模块列表失败: {e}")
            return []


def get_platform_client(token: Optional[str] = None) -> PlatformClient:
    return PlatformClient(api_key=token or "")
