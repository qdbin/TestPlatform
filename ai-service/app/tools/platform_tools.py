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

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "token": self.api_key,
        }
        return headers

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
                    outer_data = (
                        payload.get("data") if isinstance(payload, dict) else None
                    )
                    if isinstance(outer_data, dict) and isinstance(
                        outer_data.get("data"), list
                    ):
                        return outer_data.get("data")
                    if isinstance(outer_data, list):
                        return outer_data
                    return []
                return []
        except Exception as e:
            print(f"获取接口列表失败: {e}")
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
                    if isinstance(payload, dict) and isinstance(
                        payload.get("data"), dict
                    ):
                        return payload.get("data")
                    return payload if isinstance(payload, dict) else None
                return None
        except Exception as e:
            print(f"获取接口详情失败: {e}")
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

    def save_case(self, case_data: Dict[str, Any]) -> Optional[str]:
        """
        保存测试用例

        Args:
            case_data: 用例数据

        Returns:
            用例ID
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/autotest/case/save",
                    json=case_data,
                    headers=self._get_headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
                return None
        except Exception as e:
            print(f"保存用例失败: {e}")
            return None

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
