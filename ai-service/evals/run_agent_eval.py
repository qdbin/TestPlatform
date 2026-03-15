"""
Agent评估脚本

职责：
    - 加载测试数据集
    - 调用用例生成API
    - 评估生成结果（Schema校验、步骤数量）
    - 输出评估指标（成功率、Schema有效率、步骤正确率）

评估指标：
    - success_rate: 接口调用成功率
    - schema_valid_rate: Schema校验通过率
    - step_correct_rate: 步骤数量正确率
    - output_stability: 综合稳定性
"""

from __future__ import annotations

import json
import os
import base64
from pathlib import Path
from typing import Any, Dict, List

import requests


ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "data" / "agent_eval_dataset.jsonl"
API_BASE = os.getenv("EVAL_API_BASE", "http://localhost:8001")
BACKEND_BASE = os.getenv("EVAL_BACKEND_BASE", "http://localhost:8080")


def load_dataset() -> List[Dict[str, Any]]:
    """
    加载评估数据集

    数据格式（JSONL，每行一个JSON对象）：
        {
            "id": "test-001",           // 测试用例唯一标识
            "project_id": "p1",         // 项目ID，用于数据隔离
            "user_requirement": "设计登录用例",  // 用户需求描述
            "expected_api_count_min": 2 // 期望的最少接口数量（用于步骤数量校验）
        }

    @return: 测试数据列表
    """
    rows: List[Dict[str, Any]] = []
    with DATASET.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def validate_case_shape(case_obj: Dict[str, Any]) -> bool:
    """
    验证用例Shape是否符合规范

    校验规则：
        1. type 必须是 "API"（只评估API类型用例）
        2. projectId 必须非空（确保数据隔离）
        3. caseApis 至少2个步骤（确保流程完整性）
        4. 每个步骤必须有 apiId（确保接口关联）

    @param case_obj: 用例对象（来自LLM生成结果）
    @return: 是否通过校验

    校验示例：
        有效用例：{"type": "API", "projectId": "p1", "caseApis": [{"apiId": "1"}, {"apiId": "2"}]}
        无效用例：{"type": "WEB", "projectId": "", "caseApis": []}
    """
    if not isinstance(case_obj, dict):
        return False
    if str(case_obj.get("type") or "") != "API":
        return False
    if not str(case_obj.get("projectId") or ""):
        return False
    steps = case_obj.get("caseApis")
    if not isinstance(steps, list) or len(steps) < 2:
        return False
    for step in steps:
        if not isinstance(step, dict):
            return False
        if not str(step.get("apiId") or ""):
            return False
    return True


def resolve_token() -> str:
    """
    获取认证Token

    获取方式（优先级顺序）：
        1. 环境变量 EVAL_TOKEN：直接使用预设Token
        2. 环境变量 EVAL_ACCOUNT + EVAL_PASSWORD：调用登录接口获取Token
           - 密码会经过 Base64 编码后传输
           - 从响应头或响应体中提取 Token

    环境变量说明：
        - EVAL_TOKEN: 预设的认证Token
        - EVAL_ACCOUNT: 登录账号
        - EVAL_PASSWORD: 登录密码（Base64编码后传输）
        - EVAL_BACKEND_BASE: 后端API地址（默认 http://localhost:8080）

    @return: 认证Token字符串，失败返回空字符串
    """
    token = str(os.getenv("EVAL_TOKEN") or "").strip()
    if token:
        return token
    account = str(os.getenv("EVAL_ACCOUNT") or "LMadmin").strip()
    password = str(os.getenv("EVAL_PASSWORD") or "Liuma@123456").strip()
    if not account or not password:
        return ""
    encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")
    payload = {"account": account, "password": encoded_password}
    try:
        resp = requests.post(f"{BACKEND_BASE}/autotest/login", json=payload, timeout=20)
        if not resp.ok:
            return ""
        header_token = str(resp.headers.get("token") or "").strip()
        if header_token:
            return header_token
        data = resp.json() if resp.content else {}
        body_token = str(
            ((data.get("data") or {}).get("token")) if isinstance(data, dict) else ""
        ).strip()
        return body_token
    except Exception:
        return ""


def _unwrap_backend_data(payload: Dict[str, Any]) -> Any:
    if not isinstance(payload, dict):
        return None
    if "data" in payload:
        return payload.get("data")
    return payload


def _extract_list(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        if isinstance(data.get("list"), list):
            return [x for x in data.get("list", []) if isinstance(x, dict)]
        if isinstance(data.get("data"), list):
            return [x for x in data.get("data", []) if isinstance(x, dict)]
    return []


def resolve_project_id(token: str, preferred_project_id: str) -> str:
    headers = {"token": token} if token else {}
    if preferred_project_id:
        api_resp = requests.post(
            f"{BACKEND_BASE}/autotest/api/list/1/2000",
            json={"projectId": preferred_project_id},
            headers=headers,
            timeout=20,
        )
        if api_resp.ok and _extract_list(_unwrap_backend_data(api_resp.json())):
            return preferred_project_id
    projects_resp = requests.post(
        f"{BACKEND_BASE}/autotest/project/list/1/2000",
        json={},
        headers=headers,
        timeout=20,
    )
    if not projects_resp.ok:
        return preferred_project_id
    projects = _extract_list(_unwrap_backend_data(projects_resp.json()))
    for item in projects:
        pid = str(item.get("id") or "")
        if not pid:
            continue
        api_resp = requests.post(
            f"{BACKEND_BASE}/autotest/api/list/1/2000",
            json={"projectId": pid},
            headers=headers,
            timeout=20,
        )
        if api_resp.ok and _extract_list(_unwrap_backend_data(api_resp.json())):
            return pid
    return preferred_project_id


def run_single(item: Dict[str, Any], token: str) -> Dict[str, Any]:
    """
    执行单条评估

    评估流程：
        1. 构建请求payload，包含project_id、user_requirement等
        2. 调用用例生成API `/ai/agent/generate-case`
        3. 解析响应，提取生成的用例对象
        4. 执行 Schema 校验（validate_case_shape）
        5. 执行步骤数量校验（与 expected_api_count_min 比较）

    @param item: 测试数据项（包含 id, project_id, user_requirement, expected_api_count_min）
    @param token: 认证Token
    @return: 评估结果字典，包含字段：
        - id: 测试用例ID
        - status: 接口调用状态（success/error）
        - message: 错误信息
        - shape_ok: Schema形状是否正确
        - step_count_ok: 步骤数量是否足够
        - step_count: 实际步骤数量

    API响应示例：
        {
            "status": "success",
            "case": {
                "type": "API",
                "projectId": "p1",
                "caseApis": [{"apiId": "1"}, {"apiId": "2"}]
            }
        }
    """
    project_id = resolve_project_id(token, str(item.get("project_id") or ""))
    payload = {
        "project_id": project_id,
        "user_id": "eval-user",
        "user_requirement": item["user_requirement"],
        "selected_apis": [],
        "messages": [],
    }
    headers = {"token": token} if token else {}
    resp = requests.post(
        f"{API_BASE}/ai/agent/generate-case", json=payload, headers=headers, timeout=120
    )
    data = (
        resp.json()
        if resp.ok
        else {"status": "error", "message": f"HTTP {resp.status_code}"}
    )
    case_obj = data.get("case") if isinstance(data, dict) else {}
    shape_ok = validate_case_shape(case_obj if isinstance(case_obj, dict) else {})
    step_count = (
        len(case_obj.get("caseApis") or []) if isinstance(case_obj, dict) else 0
    )
    min_steps = int(item.get("expected_api_count_min") or 2)
    status = data.get("status") if isinstance(data, dict) else "error"
    message = data.get("message") if isinstance(data, dict) else ""
    return {
        "id": item["id"],
        "status": status,
        "message": str(message or ""),
        "shape_ok": shape_ok,
        "step_count_ok": step_count >= min_steps,
        "step_count": step_count,
    }


def main() -> None:
    """
    评估主入口

    执行流程：
        1. 加载数据集
        2. 获取Token
        3. 执行每条评估
        4. 计算指标并输出JSON
    """
    rows = load_dataset()
    token = resolve_token()
    records = [run_single(item, token=token) for item in rows]
    stability = sum(1 for r in records if r["shape_ok"] and r["step_count_ok"]) / len(
        records
    )
    success_rate = sum(1 for r in records if r.get("status") == "success") / len(
        records
    )
    summary = {
        "success_rate": success_rate,
        "schema_valid_rate": sum(1 for r in records if r["shape_ok"]) / len(records),
        "step_correct_rate": sum(1 for r in records if r["step_count_ok"])
        / len(records),
        "output_stability": stability,
        "sample_count": len(records),
        "has_eval_token": bool(token),
    }
    print(
        json.dumps(
            {"summary": summary, "records": records}, ensure_ascii=False, indent=2
        )
    )


if __name__ == "__main__":
    main()
