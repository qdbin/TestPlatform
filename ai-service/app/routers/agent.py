"""
Agent路由
处理用例生成相关请求

核心功能：
    1. POST /ai/agent/generate-case - 用例生成接口
    2. GET /ai/agent/api-list/{project_id} - 获取接口列表

实现特点：
    - 基于 LangChain ReAct 工具链选择项目接口
    - 融合 RAG 证据、Schema 约束和历史消息生成可保存用例
    - 提供普通问答与 SSE 流式输出统一入口
"""

from fastapi import APIRouter, HTTPException, Request
from app.schemas import GenerateCaseRequestModel
from app.services.agent_service import agent_service

router = APIRouter()

# ==================== 用例生成接口 ====================


@router.post("/generate-case")
async def generate_case(request: GenerateCaseRequestModel, raw_request: Request):
    """
    生成测试用例（Agent调度入口）

    实现步骤：
        1. 从请求头获取token用于平台API鉴权
        2. 调用 agent_service.generate_case() 执行用例生成
        3. 返回生成结果（含用例JSON、接口ID列表）

    @return: {status, case, existing_api_ids, message, error}

    用例生成流程：
        1. 拉取项目接口池
        2. 选择候选接口（ReAct/关键词）
        3. 读取接口详情与依赖关系
        4. 融合RAG与Schema
        5. LLM生成 + Pydantic校验
    """
    try:
        token = raw_request.headers.get("token") or ""

        # Agent主流程：选接口 -> 组prompt -> 生成JSON
        result = agent_service.generate_case(
            project_id=request.project_id,
            token=token,
            user_requirement=request.user_requirement,
            selected_apis=request.selected_apis,
            messages=[item.model_dump() for item in request.messages],
            user_id=request.user_id or "",
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用例生成失败: {str(e)}")


@router.get("/api-list/{project_id}")
async def get_api_list(project_id: str, raw_request: Request):
    """
    获取接口列表供用户选择

    该接口主要服务于"手动选接口 + Agent生成"协同场景
    用户可先选择接口，再调用 generate-case 生成用例

    @return: {status, data: [...]}
    """
    try:
        token = raw_request.headers.get("token") or ""
        apis = agent_service.get_api_list_for_selection(project_id, token)
        return {"status": "success", "data": apis}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取接口列表失败: {str(e)}")


if __name__ == "__main__":
    """
    Agent路由调试代码

    调试说明：
        1. 用例生成：POST /ai/agent/generate-case
        2. 接口列表：GET /ai/agent/api-list/{project_id}

    测试命令示例：

    # 1. 获取接口列表
    curl -X GET "http://localhost:8001/ai/agent/api-list/test-project" \
      -H "token: <your-token>"

    # 2. 生成用例
    curl -X POST http://localhost:8001/ai/agent/generate-case \
      -H "Content-Type: application/json" \
      -H "token: <your-token>" \
      -d '{
        "project_id": "test-project",
        "user_requirement": "设计登录+注册的完整测试流程",
        "selected_apis": [],
        "messages": []
      }'
    """
    print("=" * 60)
    print("Agent用例生成路由调试")
    print("=" * 60)
    print("\n接口列表：")
    print("  1. POST /ai/agent/generate-case - 用例生成")
    print("  2. GET /ai/agent/api-list/{project_id} - 接口列表")
    print("\n生成流程：")
    print("  1. 拉取项目接口池")
    print("  2. 选择候选接口（ReAct/关键词）")
    print("  3. 读取接口详情与依赖关系")
    print("  4. 融合RAG与Schema")
    print("  5. LLM生成 + Pydantic校验")
    print("=" * 60)
