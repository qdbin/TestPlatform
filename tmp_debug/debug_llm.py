"""调试LLM初始化"""
import sys
sys.path.insert(0, 'c:/Users/hanbin/main/Core/DevHome/m2.5/TestPlatform/ai-service')

# 强制重新加载模块
import importlib
import app.services.llm_service
importlib.reload(app.services.llm_service)

from app.services.llm_service import llm_service

print("=== 测试LLM初始化 ===")
# 强制重新创建LLM
llm_service._llm = None
llm = llm_service._get_llm()
print(f"LLM对象: {llm}")

# 测试对话
if llm:
    from langchain.schema import HumanMessage
    response = llm.invoke([HumanMessage(content="你好")])
    print(f"响应: {response.content}")
