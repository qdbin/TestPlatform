"""
Agent 用例生成评估测试模块 - Pytest + LangSmith

评估指标：
    - 用例生成成功率 (Success Rate)
    - Schema校验通过率 (Schema Valid Rate)
    - 步骤正确率 (Step Correct Rate)
    - 接口选择准确率 (API Selection Accuracy)
    - 输出稳定性 (Output Stability)

使用方法：
    conda activate aitest
    cd ai-service
    python -m pytest evals/test_agent_eval.py -v --tb=short
    
    # 推送到 LangSmith
    python -m pytest evals/test_agent_eval.py -v --tb=short --langsmith
"""

import json
import os
import sys
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from langsmith import Client
from langsmith.evaluation import EvaluationResult, RunEvaluator
from langsmith.schemas import Example, Run

from app.config import config
from app.schemas.ai_models import CaseModel


# 加载评估数据集
def load_agent_dataset() -> List[Dict[str, Any]]:
    """加载Agent评估数据集"""
    dataset_path = Path(__file__).parent / "data" / "agent_eval_dataset.jsonl"
    data = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data


# 评估项目ID
EVAL_PROJECT_ID = "eval-project-001"
EVAL_USER_ID = "eval-user"
AI_BASE = os.getenv("EVAL_API_BASE", "http://localhost:8001")
BACKEND_BASE = os.getenv("EVAL_BACKEND_BASE", "http://localhost:8080")
AGENT_DATASET_NAME = "TestPlatform-Agent-Eval-v2"
_EVAL_TOKEN: str = ""
_EVAL_PROJECT_ID_RESOLVED: str = ""


def resolve_eval_token() -> str:
    global _EVAL_TOKEN
    if _EVAL_TOKEN:
        return _EVAL_TOKEN
    token = str(os.getenv("EVAL_TOKEN") or "").strip()
    if token:
        _EVAL_TOKEN = token
        return token
    account = str(os.getenv("EVAL_ACCOUNT") or "LMadmin").strip()
    password = str(os.getenv("EVAL_PASSWORD") or "Liuma@123456").strip()
    encoded = base64.b64encode(password.encode("utf-8")).decode("utf-8")
    resp = requests.post(
        f"{BACKEND_BASE}/autotest/login",
        json={"account": account, "password": encoded},
        timeout=20,
    )
    if not resp.ok:
        return ""
    _EVAL_TOKEN = str(resp.headers.get("token") or "").strip()
    return _EVAL_TOKEN


def _extract_list(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        inner = data.get("data", data)
        if isinstance(inner, dict) and isinstance(inner.get("list"), list):
            return [x for x in inner.get("list", []) if isinstance(x, dict)]
        if isinstance(inner, list):
            return [x for x in inner if isinstance(x, dict)]
    return []


def resolve_eval_project_id() -> str:
    global _EVAL_PROJECT_ID_RESOLVED
    if _EVAL_PROJECT_ID_RESOLVED:
        return _EVAL_PROJECT_ID_RESOLVED
    token = resolve_eval_token()
    headers = {"token": token} if token else {}
    projects_resp = requests.post(
        f"{BACKEND_BASE}/autotest/project/list/1/2000",
        json={},
        headers=headers,
        timeout=20,
    )
    if not projects_resp.ok:
        _EVAL_PROJECT_ID_RESOLVED = EVAL_PROJECT_ID
        return _EVAL_PROJECT_ID_RESOLVED
    projects = _extract_list(projects_resp.json())
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
        if api_resp.ok and _extract_list(api_resp.json()):
            _EVAL_PROJECT_ID_RESOLVED = pid
            return pid
    _EVAL_PROJECT_ID_RESOLVED = EVAL_PROJECT_ID
    return _EVAL_PROJECT_ID_RESOLVED


def invoke_generate_case(requirement: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    token = resolve_eval_token()
    pid = project_id or resolve_eval_project_id()
    headers = {"token": token} if token else {}
    resp = requests.post(
        f"{AI_BASE}/ai/agent/generate-case",
        json={
            "project_id": pid,
            "user_id": EVAL_USER_ID,
            "user_requirement": requirement,
            "selected_apis": [],
            "messages": [],
        },
        headers=headers,
        timeout=180,
    )
    if not resp.ok:
        return {"status": "error", "message": f"HTTP {resp.status_code}", "case": {}}
    data = resp.json() if resp.content else {}
    if isinstance(data, dict):
        return data
    return {"status": "error", "message": "invalid_response", "case": {}}


class CaseGenerationEvaluator(RunEvaluator):
    """用例生成评估器"""
    
    def __init__(self, expected_apis: List[str], required_fields: List[str]):
        self.expected_apis = expected_apis
        self.required_fields = required_fields
    
    def evaluate_run(self, run: Run, example: Optional[Example] = None) -> EvaluationResult:
        """评估用例生成结果"""
        outputs = run.outputs or {}
        case_data = outputs.get("case", {})
        
        if not case_data:
            return EvaluationResult(
                key="case_generation",
                score=0.0,
                comment="未生成用例"
            )
        
        scores = {}
        
        # 1. Schema校验
        try:
            case_model = CaseModel.model_validate(case_data)
            scores["schema_valid"] = 1.0
        except Exception as e:
            scores["schema_valid"] = 0.0
            scores["schema_error"] = str(e)
        
        # 2. 步骤数量检查
        case_apis = case_data.get("caseApis", [])
        scores["step_count"] = len(case_apis)
        scores["step_count_ok"] = 1.0 if len(case_apis) >= 2 else 0.0
        
        # 3. API选择检查
        if self.expected_apis and case_apis:
            selected_api_ids = set()
            for step in case_apis:
                api_id = step.get("apiId", "")
                if api_id:
                    selected_api_ids.add(api_id)
            
            # 计算匹配的API数量
            matched = sum(1 for api in self.expected_apis if any(api in sid for sid in selected_api_ids))
            scores["api_selection_accuracy"] = matched / len(self.expected_apis) if self.expected_apis else 0.0
        else:
            scores["api_selection_accuracy"] = 0.0
        
        # 4. 必需字段检查
        case_json = json.dumps(case_data, ensure_ascii=False).lower()
        field_matches = sum(1 for field in self.required_fields if field.lower() in case_json)
        scores["required_fields_coverage"] = field_matches / len(self.required_fields) if self.required_fields else 0.0
        
        # 综合得分
        overall_score = (
            scores.get("schema_valid", 0.0) * 0.4 +
            scores.get("step_count_ok", 0.0) * 0.2 +
            scores.get("api_selection_accuracy", 0.0) * 0.25 +
            scores.get("required_fields_coverage", 0.0) * 0.15
        )
        
        return EvaluationResult(
            key="case_generation",
            score=overall_score,
            comment=json.dumps(scores, ensure_ascii=False)
        )


def validate_case_shape(case_obj: Dict[str, Any]) -> Dict[str, Any]:
    """验证用例结构"""
    result = {
        "valid": False,
        "errors": []
    }
    
    if not isinstance(case_obj, dict):
        result["errors"].append("用例必须是字典类型")
        return result
    
    # 检查type字段
    if str(case_obj.get("type") or "") != "API":
        result["errors"].append("type必须是'API'")
    
    # 检查projectId
    if not str(case_obj.get("projectId") or ""):
        result["errors"].append("projectId不能为空")
    
    # 检查caseApis
    steps = case_obj.get("caseApis")
    if not isinstance(steps, list):
        result["errors"].append("caseApis必须是列表")
    elif len(steps) < 2:
        result["errors"].append("caseApis至少需要2个步骤")
    else:
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                result["errors"].append(f"步骤{i}必须是字典")
                continue
            if not str(step.get("apiId") or ""):
                result["errors"].append(f"步骤{i}缺少apiId")
    
    result["valid"] = len(result["errors"]) == 0
    return result


def create_langsmith_agent_dataset(client: Client) -> str:
    """创建LangSmith Agent评估数据集"""
    dataset_name = AGENT_DATASET_NAME
    
    # 检查数据集是否已存在
    try:
        existing_datasets = list(client.list_datasets(dataset_name=dataset_name))
        if existing_datasets:
            print(f"数据集已存在: {dataset_name}")
            return existing_datasets[0].id
    except Exception:
        pass
    
    # 创建新数据集
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="测试平台Agent用例生成评估数据集 - 包含30个测试场景，覆盖用户认证、订单管理、商品管理等"
    )
    
    # 加载数据
    examples = load_agent_dataset()
    
    # 添加示例
    for item in examples:
        client.create_example(
            inputs={
                "requirement": item["user_requirement"],
                "project_id": item["project_id"]
            },
            outputs={
                "expected_api_count_min": item["expected_api_count_min"],
                "expected_apis": item["expected_apis"],
                "required_fields": item["required_fields"],
                "domain": item["domain"]
            },
            dataset_id=dataset.id
        )
    
    print(f"数据集创建完成: {dataset_name}, 共{len(examples)}条数据")
    return dataset.id


def generate_case_wrapper(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """用例生成包装函数 - 用于LangSmith评估"""
    requirement = inputs.get("requirement", "")
    project_id = inputs.get("project_id", EVAL_PROJECT_ID)
    
    try:
        result = invoke_generate_case(requirement, project_id=project_id)
        
        return {
            "case": result.get("case", {}),
            "status": result.get("status", "error"),
            "message": result.get("message", ""),
            "requirement": requirement
        }
    except Exception as e:
        return {
            "case": {},
            "status": "error",
            "message": str(e),
            "requirement": requirement
        }


@pytest.fixture(scope="module")
def langsmith_client():
    """LangSmith客户端Fixture"""
    if not config.LANGSMITH_API_KEY:
        pytest.skip("LangSmith API Key未配置")
    return Client(api_key=config.LANGSMITH_API_KEY)


@pytest.fixture(scope="module")
def agent_dataset(langsmith_client):
    """Agent数据集Fixture"""
    return create_langsmith_agent_dataset(langsmith_client)


class TestCaseGenerationSuccess:
    """用例生成成功率测试类"""
    
    def test_generation_success_rate(self):
        """测试用例生成成功率"""
        examples = load_agent_dataset()
        
        success_count = 0
        results = []
        
        for item in examples[:10]:  # 测试前10条
            requirement = item["user_requirement"]
            
            try:
                result = invoke_generate_case(requirement, project_id=resolve_eval_project_id())
                
                is_success = result.get("status") == "success" and result.get("case")
                if is_success:
                    success_count += 1
                
                results.append({
                    "id": item["id"],
                    "success": is_success,
                    "requirement": requirement[:30]
                })
                
                print(f"[{item['id']}] 需求: {requirement[:30]}... 结果: {'成功' if is_success else '失败'}")
            except Exception as e:
                results.append({
                    "id": item["id"],
                    "success": False,
                    "error": str(e)
                })
                print(f"[{item['id']}] 异常: {str(e)[:50]}")
        
        success_rate = success_count / len(results) if results else 0.0
        print(f"\n成功率: {success_count}/{len(results)} = {success_rate:.2%}")
        
        # 断言成功率应大于60%
        assert success_rate > 0.6, f"成功率 {success_rate:.2%} 过低"
    
    def test_schema_validation_rate(self):
        """测试Schema校验通过率"""
        examples = load_agent_dataset()
        
        valid_count = 0
        total_count = 0
        
        for item in examples[:10]:
            requirement = item["user_requirement"]
            
            try:
                result = invoke_generate_case(requirement, project_id=resolve_eval_project_id())
                
                if result.get("status") == "success" and result.get("case"):
                    total_count += 1
                    validation = validate_case_shape(result["case"])
                    if validation["valid"]:
                        valid_count += 1
                        print(f"[{item['id']}] Schema校验通过")
                    else:
                        print(f"[{item['id']}] Schema校验失败: {validation['errors']}")
            except Exception as e:
                print(f"[{item['id']}] 异常: {str(e)[:50]}")
        
        if total_count > 0:
            valid_rate = valid_count / total_count
            print(f"\nSchema校验通过率: {valid_count}/{total_count} = {valid_rate:.2%}")
            assert valid_rate > 0.7, f"Schema校验通过率 {valid_rate:.2%} 过低"


class TestCaseGenerationQuality:
    """用例生成质量测试类"""
    
    def test_step_count_correctness(self):
        """测试步骤数量正确率"""
        examples = load_agent_dataset()
        
        correct_count = 0
        total_count = 0
        
        for item in examples[:10]:
            requirement = item["user_requirement"]
            expected_min = item.get("expected_api_count_min", 2)
            
            try:
                result = invoke_generate_case(requirement, project_id=resolve_eval_project_id())
                
                if result.get("status") == "success" and result.get("case"):
                    total_count += 1
                    case_apis = result["case"].get("caseApis", [])
                    actual_count = len(case_apis)
                    
                    if actual_count >= expected_min:
                        correct_count += 1
                        print(f"[{item['id']}] 步骤数: {actual_count} >= {expected_min} ✓")
                    else:
                        print(f"[{item['id']}] 步骤数: {actual_count} < {expected_min} ✗")
            except Exception as e:
                print(f"[{item['id']}] 异常: {str(e)[:50]}")
        
        if total_count > 0:
            correct_rate = correct_count / total_count
            print(f"\n步骤数量正确率: {correct_count}/{total_count} = {correct_rate:.2%}")
            assert correct_rate > 0.7, f"步骤数量正确率 {correct_rate:.2%} 过低"
    
    def test_api_selection_relevance(self):
        """测试API选择相关性"""
        examples = load_agent_dataset()
        
        relevance_scores = []
        
        for item in examples[:5]:  # 测试前5条
            requirement = item["user_requirement"]
            expected_apis = item.get("expected_apis", [])
            
            try:
                result = invoke_generate_case(requirement, project_id=resolve_eval_project_id())
                
                if result.get("status") == "success" and result.get("case"):
                    case_apis = result["case"].get("caseApis", [])
                    selected_api_ids = [step.get("apiId", "") for step in case_apis]
                    
                    # 简单相关性：检查是否有预期的API被选中
                    if expected_apis and selected_api_ids:
                        matched = sum(1 for exp in expected_apis if any(exp in sel for sel in selected_api_ids))
                        relevance = matched / len(expected_apis)
                        relevance_scores.append(relevance)
                        print(f"[{item['id']}] API相关性: {relevance:.2f}")
            except Exception as e:
                print(f"[{item['id']}] 异常: {str(e)[:50]}")
        
        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            print(f"\n平均API选择相关性: {avg_relevance:.2f}")
            assert avg_relevance > 0.5, f"API选择相关性 {avg_relevance:.2f} 过低"
    
    def test_output_stability(self):
        """测试输出稳定性（多次生成的一致性）"""
        # 选择几个测试用例进行多次生成
        test_requirements = [
            "设计一个用户登录流程的测试用例",
            "测试订单创建和支付流程"
        ]
        
        stability_scores = []
        
        for req in test_requirements:
            step_counts = []
            
            # 同一需求生成3次
            for _ in range(3):
                try:
                    result = invoke_generate_case(req, project_id=resolve_eval_project_id())
                    
                    if result.get("status") == "success" and result.get("case"):
                        case_apis = result["case"].get("caseApis", [])
                        step_counts.append(len(case_apis))
                except Exception:
                    step_counts.append(0)
            
            # 计算稳定性：步骤数量的变异系数
            if step_counts and sum(step_counts) > 0:
                avg = sum(step_counts) / len(step_counts)
                variance = sum((x - avg) ** 2 for x in step_counts) / len(step_counts)
                std = variance ** 0.5
                cv = std / avg if avg > 0 else 1.0
                stability = max(0, 1 - cv)  # 变异系数越小越稳定
                stability_scores.append(stability)
                print(f"需求: {req[:30]}... 稳定性: {stability:.2f}")
        
        if stability_scores:
            avg_stability = sum(stability_scores) / len(stability_scores)
            print(f"\n平均输出稳定性: {avg_stability:.2f}")
            assert avg_stability > 0.5, f"输出稳定性 {avg_stability:.2f} 过低"


class TestCaseGenerationDomain:
    """按领域测试用例生成"""
    
    def test_user_auth_domain(self):
        """测试用户认证领域用例生成"""
        auth_requirements = [
            "设计用户登录流程测试用例",
            "测试用户注册功能",
            "验证修改密码功能"
        ]
        
        success_count = 0
        for req in auth_requirements:
            try:
                result = invoke_generate_case(req, project_id=resolve_eval_project_id())
                if result.get("status") == "success":
                    success_count += 1
            except Exception:
                pass
        
        success_rate = success_count / len(auth_requirements)
        print(f"\n用户认证领域成功率: {success_count}/{len(auth_requirements)} = {success_rate:.2%}")
        assert success_rate > 0.6, f"用户认证领域成功率 {success_rate:.2%} 过低"
    
    def test_order_domain(self):
        """测试订单管理领域用例生成"""
        order_requirements = [
            "测试创建订单流程",
            "验证订单支付功能",
            "测试订单查询和取消"
        ]
        
        success_count = 0
        for req in order_requirements:
            try:
                result = invoke_generate_case(req, project_id=resolve_eval_project_id())
                if result.get("status") == "success":
                    success_count += 1
            except Exception:
                pass
        
        success_rate = success_count / len(order_requirements)
        print(f"\n订单管理领域成功率: {success_count}/{len(order_requirements)} = {success_rate:.2%}")
        assert success_rate > 0.6, f"订单管理领域成功率 {success_rate:.2%} 过低"


@pytest.mark.skipif(not config.LANGSMITH_API_KEY, reason="LangSmith未配置")
def test_langsmith_agent_evaluation(langsmith_client, agent_dataset):
    """使用LangSmith进行端到端Agent评估"""
    from langsmith.evaluation import evaluate
    
    examples = load_agent_dataset()
    
    def target_fn(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """目标函数"""
        return generate_case_wrapper(inputs)
    
    def case_evaluator(run, example) -> EvaluationResult:
        """用例生成评估"""
        outputs = run.outputs or {}
        case_data = outputs.get("case", {})
        
        # Schema校验
        validation = validate_case_shape(case_data)
        schema_valid = 1.0 if validation["valid"] else 0.0
        
        # 步骤数量检查
        case_apis = case_data.get("caseApis", [])
        step_count_ok = 1.0 if len(case_apis) >= 2 else 0.0
        
        # 综合得分
        score = schema_valid * 0.6 + step_count_ok * 0.4
        
        return EvaluationResult(
            key="case_quality",
            score=score,
            comment=json.dumps({
                "schema_valid": schema_valid,
                "step_count": len(case_apis),
                "step_count_ok": step_count_ok
            })
        )
    
    # 运行评估
    results = evaluate(
        target_fn,
        data=AGENT_DATASET_NAME,
        evaluators=[case_evaluator],
        experiment_prefix="agent-case-generation-test",
        client=langsmith_client
    )
    
    print(f"\nLangSmith评估完成: {results}")


if __name__ == "__main__":
    # 本地测试运行
    pytest.main([__file__, "-v", "--tb=short", "-s"])
