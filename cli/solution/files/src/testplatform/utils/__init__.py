"""
工具模块

提供HTTP客户端、格式化输出等通用工具
"""

from testplatform.utils.http_client import HttpClient, encode_password

__all__ = ["HttpClient", "encode_password"]
