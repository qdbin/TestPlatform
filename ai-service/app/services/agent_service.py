"""
Agent服务模块
基于LangChain ReAct架构的智能Agent
"""
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI

from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.tools.platform_tools import platform_client
from app.config import config


# ==================== 工具定义 ====================

def get_api_list_func(project_id: str) -> str:
    """获取项目接口列表"""
    apis = platform_client.get_api_list(project_id)
    if not apis:
        return "未找到接口，请确保项目中有接口数据"
    
    result = "项目接口列表：\n"
    for i, api in enumerate(apis[:10], 1):
        result += f"{i}. {api.get('name', '')} - {api.get('method', '')} {api.get('path', '')}\n"
    
    if len(apis) > 10:
        result += f"... 共{len(apis)}个接口\n"
    
    return result


def get_api_detail_func(api_id: str) -> str:
    """获取接口详情"""
    api = platform_client.get_api_detail(api_id)
    if not api:
        return "接口不存在"
    
    result = f"接口详情：\n"
    result += f"- 名称：{api.get('name', '')}\n"
    result += f"- 路径：{api.get('path', '')}\n"
    result += f"- 方法：{api.get('method', '')}\n"
    result += f"- 描述：{api.get('description', '')}\n"
    result += f"- 请求头：{api.get('header', '')}\n"
    result += f"- 请求体：{api.get('body', '')}\n"
    result += f"- 查询参数：{api.get('query', '')}\n"
    
    return result


def search_knowledge_func(project_id: str, query: str) -> str:
    """检索知识库"""
    docs = rag_service.search(project_id, query, top_k=3)
    if not docs:
        return "未找到相关知识"
    
    result = "相关知识：\n"
    for i, doc in enumerate(docs, 1):
        result += f"{i}. {doc['content'][:200]}...\n"
    
    return result


def get_module_list_func(project_id: str) -> str:
    """获取项目模块列表"""
    modules = platform_client.get_module_list(project_id)
    if not modules:
        return "未找到模块"
    
    result = "项目模块列表：\n"
    for module in modules:
        result += f"- {module.get('name', '')}\n"
    
    return result


# 定义LangChain Tools
tools = [
    Tool(
        name="get_api_list",
        func=get_api_list_func,
        description="获取项目的接口列表，返回接口ID、名称、路径、请求方法"
    ),
    Tool(
        name="get_api_detail",
        func=get_api_detail_func,
        description="获取指定接口的详细信息，包括请求参数、请求体等"
    ),
    Tool(
        name="search_knowledge",
        func=lambda x: search_knowledge_func(x.split("|")[0], x.split("|")[1]) if "|" in x else "",
        description="搜索项目知识库中的相关内容"
    ),
    Tool(
        name="get_module_list",
        func=get_module_list_func,
        description="获取项目的模块列表"
    ),
]


# ==================== Prompt模板 ====================

CASE_GENERATE_PROMPT = """你是一个专业的API测试用例生成助手。

你的任务是根据用户需求和项目接口信息，生成符合流马测试平台格式的API测试用例。

## 项目信息
项目ID：{project_id}
用户需求：{user_requirement}

## 项目接口列表
{api_list}

## 知识库信息
{knowledge}

## 生成要求

1. 首先理解用户需求，确定需要测试哪些接口
2. 如果用户没有指定具体接口，请列出可用的接口供用户选择
3. 为每个测试场景生成完整的用例JSON，包含：
   - caseName: 用例名称
   - description: 用例描述  
   - type: 用例类型（API）
   - level: 用例级别（P1/P2/P3）
   - caseApis: 用例步骤数组
     - apiId: 接口ID
     - description: 步骤描述
     - header: 请求头（JSON格式）
     - body: 请求体（JSON格式）
     - assertion: 断言数组

4. 请生成至少以下测试场景：
   - 正向用例：正常参数、正常流程
   - 异常用例：参数为空、参数错误、边界值

## 输出格式

请直接输出JSON格式的用例数据，不要包含其他解释：

```json
{{
    "caseName": "用例名称",
    "description": "用例描述",
    "type": "API",
    "level": "P1",
    "moduleId": "模块ID",
    "caseApis": [
        {{
            "apiId": "接口ID",
            "description": "步骤描述",
            "header": "{{}}",
            "body": "{{}}",
            "assertion": "[{{}}]"
        }}
    ]
}}
```

现在开始生成用例："""


class AgentService:
    """Agent服务类（ReAct架构）"""
    
    def __init__(self):
        self._agent_executor = None
        self._init_agent()
    
    def _init_agent(self) -> None:
        """初始化Agent"""
        # 使用LangChain ReAct Agent
        prompt = PromptTemplate.from_template(
            """助手可以访问以下工具：

{tools}

{tool_names}

回答以下问题。如果需要使用工具，请按照以下格式：

Thought: 思考需要做什么
Action: 工具名称
Action Input: 工具输入
Observation: 工具返回结果

用户问题：{input}

{agent_scratchpad}

Thought: 我已经收集到足够信息，现在可以回答用户问题了。"""
        )
        
        # 创建ReAct Agent
        llm = ChatOpenAI(
            model=config.llm_model,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            temperature=0.7,
            model_kwargs={"stop": ["\nObservation:"]}
        )
        
        agent = create_react_agent(llm, tools, prompt)
        self._agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors="请检查输入格式并重试"
        )
    
    def generate_case(self, project_id: str, user_requirement: str, selected_apis: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        生成测试用例
        
        Args:
            project_id: 项目ID
            user_requirement: 用户需求
            selected_apis: 用户选择的接口ID列表
            
        Returns:
            生成的用例JSON
        """
        # 1. 获取项目接口列表
        api_list = get_api_list_func(project_id)
        
        # 2. 检索知识库
        knowledge = search_knowledge_func(project_id, user_requirement)
        
        # 3. 构建Prompt
        prompt = CASE_GENERATE_PROMPT.format(
            project_id=project_id,
            user_requirement=user_requirement,
            api_list=api_list,
            knowledge=knowledge
        )
        
        # 4. 调用LLM生成
        try:
            # 直接使用LLM生成（比Agent更可控）
            from langchain.schema import HumanMessage
            messages = [HumanMessage(content=prompt)]
            response = llm_service._llm.invoke(messages)
            
            # 5. 解析JSON响应
            import json
            import re
            
            # 提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                case_json = json.loads(json_match.group())
                return {
                    "status": "success",
                    "case": case_json
                }
            else:
                return {
                    "status": "error",
                    "message": "无法解析用例JSON",
                    "raw_response": response.content
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"用例生成失败: {str(e)}"
            }
    
    def get_api_list_for_selection(self, project_id: str) -> List[Dict[str, Any]]:
        """
        获取接口列表供用户选择
        
        Args:
            project_id: 项目ID
            
        Returns:
            接口列表
        """
        return platform_client.get_api_list(project_id)


# 全局Agent服务实例
agent_service = AgentService()
