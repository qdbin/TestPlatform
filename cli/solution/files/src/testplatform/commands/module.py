"""
模块管理命令模块

提供模块创建、查询、树形列表等功能
"""

import typer
from rich.console import Console
from rich.tree import Tree
from typing import Optional

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient

app = typer.Typer(help="模块管理 - 创建、查询、树形列表")
console = Console()
config = Config()


@app.command(name="list")
def list_modules(
    module_type: str = typer.Option("api", "-t", "--type", help="模块类型(api/case)"),
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID")
):
    """查询模块树形列表"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.get(f"/autotest/module/list/{module_type}/{pid}")

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        # 解析树形数据
        modules = response if isinstance(response, list) else response.get("data", [])

        if modules:
            tree = Tree(f"[cyan]模块列表 ({module_type})[/cyan]")
            for mod in modules:
                _build_tree(tree, mod)
            console.print(tree)
        else:
            console.print("[yellow]暂无模块[/yellow]")


def _build_tree(tree: Tree, module: dict):
    """递归构建树形结构"""
    node = tree.add(f"[green]{module.get('name', '未命名')}[/green] (ID: {module.get('id', 'N/A')[:8]}...)")
    children = module.get("children", [])
    if children:
        for child in children:
            _build_tree(node, child)


@app.command(name="create")
def create_module(
    name: str = typer.Option(..., "-n", "--name", help="模块名称"),
    module_type: str = typer.Option("api", "-t", "--type", help="模块类型(api/case)"),
    parent_id: str = typer.Option("0", "--parent", help="父模块ID(0表示根模块)"),
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID")
):
    """创建新模块

    示例:
        testplatform module create -n "购物车模块" -t api
        testplatform module create -n "订单接口" -t api --parent parent_module_id
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            "/autotest/module/save",
            json={
                "name": name,
                "moduleType": module_type,
                "parentId": parent_id,
                "projectId": pid
            }
        )

        if "error" in response:
            console.print(f"[red]创建失败: {response['error']}[/red]")
            raise typer.Exit(1)

        module_id = response.get("id") or response.get("data", {}).get("id", "未知")
        console.print(f"[green]模块创建成功: {name} (ID: {module_id})[/green]")


@app.command(name="use")
def use_module(module_id: str = typer.Argument(..., help="模块ID")):
    """设置当前模块"""
    config.set_module(module_id)
    console.print(f"[green]已切换到模块: {module_id}[/green]")


@app.command(name="delete")
def delete_module(
    module_id: str = typer.Argument(..., help="模块ID"),
    module_type: str = typer.Option("api", "-t", "--type", help="模块类型(api/case)"),
    force: bool = typer.Option(False, "-f", "--force", help="强制删除，不提示确认")
):
    """删除模块

    示例:
        testplatform module delete mod123456 -t api
        testplatform module delete mod123456 -t api -f
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"确定要删除模块 {module_id} 吗？")
        if not confirm:
            console.print("[yellow]已取消删除[/yellow]")
            raise typer.Exit(0)

    with HttpClient() as client:
        response = client.post(
            "/autotest/module/delete",
            json={"id": module_id, "moduleType": module_type}
        )

        if "error" in response:
            console.print(f"[red]删除失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]模块删除成功: {module_id}[/green]")
