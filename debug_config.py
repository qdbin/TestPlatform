"""调试AI服务配置"""
import sys
sys.path.insert(0, 'c:/Users/hanbin/main/Core/DevHome/m2.5/TestPlatform/ai-service')

from app.config import config

print("=== 配置调试 ===")
print(f"LLM Provider: {config.llm_provider}")
print(f"LLM Model: {config.llm_model}")
print(f"LLM API Key: {config.llm_api_key[:20]}..." if config.llm_api_key and len(config.llm_api_key) > 20 else f"LLM API Key: {config.llm_api_key}")
print(f"LLM Base URL: {config.llm_base_url}")

# 测试LLM服务
print("\n=== 测试LLM服务 ===")
from app.services.llm_service import llm_service

llm = llm_service._get_llm()
print(f"LLM对象: {llm}")
