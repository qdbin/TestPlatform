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
    rows: List[Dict[str, Any]] = []
    with DATASET.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def validate_case_shape(case_obj: Dict[str, Any]) -> bool:
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
    token = str(os.getenv("EVAL_TOKEN") or "").strip()
    if token:
        return token
    account = str(os.getenv("EVAL_ACCOUNT") or "").strip()
    password = str(os.getenv("EVAL_PASSWORD") or "").strip()
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


def run_single(item: Dict[str, Any], token: str) -> Dict[str, Any]:
    payload = {
        "project_id": str(item.get("project_id") or "1"),
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
