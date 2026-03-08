"""
Agent路由
处理用例生成相关请求
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.agent_service import agent_service

router = APIRouter()


class GenerateCaseRequest(BaseModel):
    """用例生成请求"""
    """
    Schema示例：
    {
      "project_id":"p1",
      "user_requirement":"设计登录+注册链路用例",
      "selected_apis":["1001","1002"],
      "messages":[{"role":"user","content":"历史需求"}]
    }
    """

    project_id: str
    user_requirement: str
    selected_apis: Optional[List[str]] = None
    messages: Optional[List[Dict[str, Any]]] = None


@router.post("/generate-case")
async def generate_case(request: GenerateCaseRequest, raw_request: Request):
    """
    生成测试用例（Agent调度入口）
    """
    try:
        token = raw_request.headers.get("token") or ""
        result = agent_service.generate_case(
            project_id=request.project_id,
            token=token,
            user_requirement=request.user_requirement,
            selected_apis=request.selected_apis,
            messages=request.messages or [],
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用例生成失败: {str(e)}")


@router.get("/api-list/{project_id}")
async def get_api_list(project_id: str, raw_request: Request):
    """
    获取接口列表供用户选择。
    该接口主要服务于“手动选接口 + Agent生成”协同场景。
    """
    try:
        token = raw_request.headers.get("token") or ""
        apis = agent_service.get_api_list_for_selection(project_id, token)
        return {"status": "success", "data": apis}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取接口列表失败: {str(e)}")
