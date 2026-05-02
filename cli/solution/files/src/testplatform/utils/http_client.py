"""
HTTP客户端模块

封装HTTP请求，提供：
- 自动注入Token
- 自动刷新Token
- 统一异常处理
- Base URL管理
"""

import base64
from typing import Optional, Dict, Any

import httpx
from rich.console import Console

from testplatform.config import Config

console = Console()


class HttpClient:
    """HTTP客户端"""

    def __init__(self, base_url: Optional[str] = None):
        self.config = Config()
        self.base_url = base_url or self.config.base_url
        self.client = httpx.Client(timeout=30.0)

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头，自动注入Token"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.config.token:
            headers["token"] = self.config.token
        return headers

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """处理响应，自动刷新Token"""
        # 检查响应头中是否有新token
        new_token = response.headers.get("token")
        if new_token and new_token != self.config.token:
            self.config.set_token(new_token)
            console.print("[yellow]Token已自动刷新[/yellow]")

        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {"data": response.text}
        elif response.status_code == 401:
            console.print("[red]认证失败，请重新登录[/red]")
            return {"error": "Unauthorized"}
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text
            }

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """发送GET请求"""
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))

        try:
            response = self.client.get(url, headers=headers, **kwargs)
            return self._handle_response(response)
        except httpx.RequestError as e:
            console.print(f"[red]请求失败: {e}[/red]")
            return {"error": str(e)}

    def post(self, path: str, **kwargs) -> Dict[str, Any]:
        """发送POST请求"""
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))

        try:
            response = self.client.post(url, headers=headers, **kwargs)
            return self._handle_response(response)
        except httpx.RequestError as e:
            console.print(f"[red]请求失败: {e}[/red]")
            return {"error": str(e)}

    def put(self, path: str, **kwargs) -> Dict[str, Any]:
        """发送PUT请求"""
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))

        try:
            response = self.client.put(url, headers=headers, **kwargs)
            return self._handle_response(response)
        except httpx.RequestError as e:
            console.print(f"[red]请求失败: {e}[/red]")
            return {"error": str(e)}

    def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """发送DELETE请求"""
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))

        try:
            response = self.client.delete(url, headers=headers, **kwargs)
            return self._handle_response(response)
        except httpx.RequestError as e:
            console.print(f"[red]请求失败: {e}[/red]")
            return {"error": str(e)}

    def close(self):
        """关闭客户端"""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def encode_password(password: str) -> str:
    """Base64编码密码"""
    return base64.b64encode(password.encode()).decode()
