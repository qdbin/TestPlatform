from app.services.case_workflow import CaseGenerationWorkflow, CaseWorkflowContext


class _CaseModel:
    @staticmethod
    def model_validate(payload):
        class _Obj:
            def model_dump(self):
                return payload

        return _Obj()


def _parse_json_object(text):
    return {"case": {"name": "x", "moduleId": "m", "moduleName": "n", "projectId": "p", "caseApis": []}}


def _select_api_ids(project_id, token, user_requirement, all_apis):
    return ["a1"]


def _build_dependency_relations(api_details):
    return {}


def _build_case_prompt(*args, **kwargs):
    return "prompt"


def _normalize_case(project_id, target, api_details, api_relations=None):
        target["projectId"] = project_id
        if not target.get("caseApis"):
            target["caseApis"] = [{"apiId": "a1", "index": 1, "description": ""}]
        target["moduleId"] = target.get("moduleId", "m")
        target["moduleName"] = target.get("moduleName", "n")
        target["name"] = target.get("name", "demo")
        return target


def _build_workflow(get_platform_client):
    return CaseGenerationWorkflow(
        get_platform_client=get_platform_client,
        select_api_ids=_select_api_ids,
        build_dependency_relations=_build_dependency_relations,
        build_case_prompt=_build_case_prompt,
        normalize_case=_normalize_case,
        parse_json_object=_parse_json_object,
        case_model=_CaseModel,
        assistant_role_prompt="prompt",
    )


def test_case_workflow_context_dataclass_should_build():
    ctx = CaseWorkflowContext("p", "t", "生成登录用例", [], [])
    assert ctx.project_id == "p"


def test_case_workflow_should_return_error_without_api_pool(monkeypatch):
    class EmptyClient:
        @staticmethod
        def get_api_list(project_id):
            return []

        @staticmethod
        def get_last_error():
            return "no api"

    workflow = _build_workflow(lambda token: EmptyClient())
    result = workflow.run(CaseWorkflowContext("p", "t", "r", [], []))
    assert result["status"] == "error"
