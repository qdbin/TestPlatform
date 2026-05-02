"""
用例管理命令模块

提供用例创建、查询、导出等功能
"""

import json
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient

app = typer.Typer(help="用例管理 - 创建、查询、导出")
console = Console()
config = Config()


@app.command(name="list")
def list_cases(
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID"),
    case_type: str = typer.Option("API", "-t", "--type", help="用例类型"),
    page: int = typer.Option(1, "--page", help="页码"),
    size: int = typer.Option(10, "--size", help="每页数量")
):
    """查询用例列表"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            f"/autotest/case/list/{page}/{size}",
            json={
                "projectId": pid,
                "type": case_type,
                "condition": ""
            }
        )

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        # 解析响应
        data = response.get("list") or response.get("data") or response.get("content", [])

        if data:
            table = Table(title="用例列表")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("类型", style="yellow")
            table.add_column("优先级", style="blue")

            for item in data:
                table.add_row(
                    str(item.get("id", ""))[:8] + "...",
                    item.get("name", ""),
                    item.get("type", ""),
                    item.get("level", "")
                )
            console.print(table)
        else:
            console.print("[yellow]暂无用例[/yellow]")


@app.command(name="create")
def create_case(
    name: str = typer.Option(..., "-n", "--name", help="用例名称"),
    case_type: str = typer.Option("API", "-t", "--type", help="用例类型"),
    module_id: Optional[str] = typer.Option(None, "-m", "--module", help="模块ID"),
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID"),
    api_ids: Optional[List[str]] = typer.Option(None, "-a", "--api", help="关联接口ID列表")
):
    """创建新用例

    示例:
        testplatform case create -n "添加商品到购物车" -t API -a api1 -a api2
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    mid = module_id or config.current_module or "0"

    # 构建用例步骤
    case_apis = []
    if api_ids:
        for idx, api_id in enumerate(api_ids):
            case_apis.append({
                "index": idx,
                "apiId": api_id,
                "description": f"步骤{idx + 1}"
            })

    with HttpClient() as client:
        response = client.post(
            "/autotest/case/save",
            json={
                "name": name,
                "type": case_type,
                "moduleId": mid,
                "projectId": pid,
                "caseApis": case_apis
            }
        )

        if "error" in response:
            console.print(f"[red]创建失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]用例创建成功: {name}[/green]")


@app.command(name="export")
def export_case(
    case_id: str = typer.Argument(..., help="用例ID"),
    case_type: str = typer.Option("API", "-t", "--type", help="用例类型"),
    output: str = typer.Option("case.yaml", "-o", "--output", help="输出文件")
):
    """导出用例到YAML文件

    示例:
        testplatform case export case123 -t API -o mycase.yaml
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.get(f"/autotest/case/detail/{case_type}/{case_id}")

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            raise typer.Exit(1)

        # 导出到YAML
        try:
            import yaml
            with open(output, 'w', encoding='utf-8') as f:
                yaml.dump(response, f, allow_unicode=True, sort_keys=False)
            console.print(f"[green]用例已导出到: {output}[/green]")
        except ImportError:
            # 如果没有yaml，导出为JSON
            with open(output.replace('.yaml', '.json'), 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            console.print(f"[green]用例已导出到JSON格式[/green]")


@app.command(name="shopping-cart")
def create_shopping_cart_case(
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID"),
    module_id: Optional[str] = typer.Option(None, "-m", "--module", help="模块ID")
):
    """创建【多个商品添加到购物车】场景用例

    这是一个端到端场景用例，包含以下步骤：
    1. 获取商品列表
    2. 添加第一个商品到购物车
    3. 添加第二个商品到购物车
    4. 验证购物车商品数量

    示例:
        testplatform case shopping-cart -p project123 -m module456
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    mid = module_id or config.current_module or "0"

    console.print("[blue]正在创建【多个商品添加到购物车】场景用例...[/blue]")

    # 构建购物车场景用例步骤
    case_apis = [
        {
            "index": 0,
            "description": "获取商品列表",
            "header": [],
            "body": {},
            "assertion": [{"type": "status", "value": "200"}]
        },
        {
            "index": 1,
            "description": "添加商品A到购物车",
            "header": [],
            "body": {"productId": "A001", "quantity": 1},
            "assertion": [{"type": "status", "value": "200"}]
        },
        {
            "index": 2,
            "description": "添加商品B到购物车",
            "header": [],
            "body": {"productId": "B002", "quantity": 2},
            "assertion": [{"type": "status", "value": "200"}]
        },
        {
            "index": 3,
            "description": "验证购物车商品数量",
            "header": [],
            "body": {},
            "assertion": [
                {"type": "status", "value": "200"},
                {"type": "json", "path": "$.data.totalCount", "operator": "eq", "value": "3"}
            ]
        }
    ]

    with HttpClient() as client:
        response = client.post(
            "/autotest/case/save",
            json={
                "name": "多个商品添加到购物车",
                "type": "API",
                "moduleId": mid,
                "projectId": pid,
                "level": "P1",
                "description": "端到端场景：多个商品添加到购物车，验证购物车功能正常",
                "caseApis": case_apis
            }
        )

        if "error" in response:
            console.print(f"[red]创建失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print("[green]✓ 场景用例创建成功![/green]")
        console.print("[green]  - 用例名称: 多个商品添加到购物车[/green]")
        console.print("[green]  - 包含步骤: 获取商品列表 → 添加商品A → 添加商品B → 验证购物车[/green]")


@app.command(name="detail")
def get_case_detail(
    case_id: str = typer.Argument(..., help="用例ID"),
    case_type: str = typer.Option("API", "-t", "--type", help="用例类型")
):
    """查询用例详情

    示例:
        testplatform case detail case123456 -t API
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.get(f"/autotest/case/detail/{case_type}/{case_id}")

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]用例详情:[/green]")
        console.print(f"  名称: {response.get('name', 'N/A')}")
        console.print(f"  类型: {response.get('type', 'N/A')}")
        console.print(f"  优先级: {response.get('level', 'N/A')}")
        console.print(f"  描述: {response.get('description', 'N/A')}")

        steps = response.get('caseApis', [])
        if steps:
            console.print(f"\n[green]步骤列表 ({len(steps)}个):[/green]")
            for step in steps:
                console.print(f"  {step.get('index', 0)}. {step.get('description', '无描述')}")


@app.command(name="update")
def update_case(
    case_id: str = typer.Argument(..., help="用例ID"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="用例名称"),
    level: Optional[str] = typer.Option(None, "-l", "--level", help="优先级(P0/P1/P2)"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="用例描述"),
    case_type: str = typer.Option("API", "-t", "--type", help="用例类型")
):
    """更新用例信息

    示例:
        testplatform case update case123456 -n "新名称" -l P0
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    # 先获取原用例信息
    with HttpClient() as client:
        detail_response = client.get(f"/autotest/case/detail/{case_type}/{case_id}")
        if "error" in detail_response:
            console.print(f"[red]获取用例信息失败: {detail_response['error']}[/red]")
            raise typer.Exit(1)

        # 构建更新数据
        update_data = {
            "id": case_id,
            "name": name or detail_response.get("name", ""),
            "type": case_type,
            "level": level or detail_response.get("level", "P1"),
            "description": description or detail_response.get("description", ""),
            "moduleId": detail_response.get("moduleId", "0"),
            "projectId": detail_response.get("projectId", ""),
            "caseApis": detail_response.get("caseApis", [])
        }

        response = client.post("/autotest/case/save", json=update_data)

        if "error" in response:
            console.print(f"[red]更新失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]用例更新成功: {update_data['name']}[/green]")


@app.command(name="delete")
def delete_case(
    case_id: str = typer.Argument(..., help="用例ID"),
    force: bool = typer.Option(False, "-f", "--force", help="强制删除，不提示确认")
):
    """删除用例

    示例:
        testplatform case delete case123456
        testplatform case delete case123456 -f
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"确定要删除用例 {case_id} 吗？")
        if not confirm:
            console.print("[yellow]已取消删除[/yellow]")
            raise typer.Exit(0)

    with HttpClient() as client:
        response = client.post("/autotest/case/delete", json={"id": case_id})

        if "error" in response:
            console.print(f"[red]删除失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]用例删除成功: {case_id}[/green]")
