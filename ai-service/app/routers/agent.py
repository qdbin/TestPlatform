"""
Agent路由
处理用例生成相关请求
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.agent_service import agent_service

router = APIRouter()


class GenerateCaseRequest(BaseModel):
    """用例生成请求"""
    project_id: str
    user_requirement: str
    selected_apis: Optional[List[str]] = None


@router.post("/generate-case")
async def generate_case(request: GenerateCaseRequest):
    """
    生成测试用例
    """
    try:
        result = agent_service.generate_case(
            project_id=request.project_id,
            user_requirement=request.user_requirement,
            selected_apis=request.selected_apis
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用例生成失败: {str(e)}")


@router.get("/api-list/{project_id}")
async def get_api_list(project_id: str):
    """
    获取接口列表供用户选择
    """
    try:
        apis = agent_service.get_api_list_for_selection(project_id)
        return {
            "status": "success",
            "data": apis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取接口列表失败: {str(e)}")


@router.post("/refine-case")
async def refine_case(request: Dict[str, Any]):
    """
    优化用例
    """
    # TODO: 实现用例优化功能
    return {"status": "success", "message": "功能开发中"}
