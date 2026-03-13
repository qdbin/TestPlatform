"""
平台API客户端工具
用于Agent调用平台API获取数据
"""

import httpx
from typing import Optional, List, Dict, Any
from app.config import config


class PlatformClient:
    """
    平台API客户端。
    职责：封装 AI 服务到测试平台后端的 RPC/HTTP 调用细节。
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or config.platform_base_url
        self.api_key = api_key or ""
        self.timeout = config.platform_timeout
        self.last_error = ""

    def _get_headers(self) -> Dict[str, str]:
        """
        构建请求头。
        token 由上层透传，用于复用平台登录态。
        """
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
        # 平台统一响应兼容：
        # {"status":0,"data":...} 或 {"status":"success","data":...}
        if not isinstance(payload, dict):
            self._mark_error("平台响应格式错误")
            return None
        status = payload.get("status")
        if status not in (
            0,
            "0",
            "success",
            "SUCCESS",
            True,
            None,
        ):  # 平台多版本状态码兼容
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

    def get_case_schema(self, project_id: str) -> Dict[str, Any]:
        """
        获取后端CaseRequest相关Schema，供Agent约束输出结构。
        @param project_id: 项目ID
        @return: schema字典，失败返回 {}
        返回示例：
        {"CaseRequest": {...}, "CaseApiRequest": {...}}
        """
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


def get_platform_client(token: Optional[str] = None) -> PlatformClient:
    return PlatformClient(api_key=token or "")


if __name__ == "__main__":
    """
    平台API客户端调试代码

    调试说明：
        1. 测试获取接口列表
        2. 测试获取接口详情
        3. 测试获取用例Schema

    注意：需要正确配置 PLATFORM_BASE_URL
    """
    print("=" * 60)
    print("平台API客户端调试")
    print("=" * 60)

    # 测试1：获取接口列表
    print("\n1. 获取接口列表测试:")
    client = get_platform_client(token="test-token")
    print(f"   平台地址: {client.base_url}")
    api_list = client.get_api_list("test-project")
    print(f"   接口数量: {len(api_list)}")
    if api_list:
        print(f"   第一个接口: {api_list[0].get('name')}")

    # 测试2：获取接口详情
    print("\n2. 获取接口详情测试:")
    if api_list and len(api_list) > 0:
        first_api_id = api_list[0].get("id")
        api_detail = client.get_api_detail(str(first_api_id))
        print(f"   接口ID: {first_api_id}")
        print(f"   获取结果: {'成功' if api_detail else '失败'}")

    # 测试3：获取用例Schema
    print("\n3. 获取用例Schema测试:")
    schema = client.get_case_schema("test-project")
    print(f"   Schema keys: {list(schema.keys()) if schema else '空'}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
