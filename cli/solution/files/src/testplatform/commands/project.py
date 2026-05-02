"""
项目管理命令模块

提供项目创建、列表查询、成员管理等功能
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient

app = typer.Typer(help="项目管理 - 创建、列表、成员管理")
console = Console()
config = Config()


@app.command(name="list")
def list_projects(
    page: int = typer.Option(1, "-p", "--page", help="页码"),
    size: int = typer.Option(10, "-s", "--size", help="每页数量")
):
    """查询项目列表"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            f"/autotest/project/list/{page}/{size}",
            json={"condition": ""}
        )

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        # 解析响应数据
        data = response.get("data", [])
        if data:
            table = Table(title="项目列表")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("描述", style="yellow")

            for item in data:
                table.add_row(
                    item.get("id", "")[:8] + "...",
                    item.get("name", ""),
                    item.get("description", "")[:30]
                )
            console.print(table)
        else:
            console.print("[yellow]暂无项目[/yellow]")


@app.command(name="create")
def create_project(
    name: str = typer.Option(..., "-n", "--name", help="项目名称"),
    description: str = typer.Option("", "-d", "--description", help="项目描述")
):
    """创建新项目

    示例:
        testplatform project create -n "电商项目" -d "电商平台测试项目"
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            "/autotest/project/add",
            json={
                "name": name,
                "description": description
            }
        )

        if "error" in response:
            console.print(f"[red]创建失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]项目创建成功: {name}[/green]")


@app.command(name="use")
def use_project(project_id: str = typer.Argument(..., help="项目ID")):
    """设置当前项目"""
    config.set_project(project_id)
    console.print(f"[green]已切换到项目: {project_id}[/green]")


@app.command(name="members")
def list_members(
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID")
):
    """查询项目成员"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先使用'use'命令设置当前项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            "/autotest/project/user/list/1/10",
            json={"projectId": pid}
        )

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        console.print(f"[green]项目成员查询成功[/green]")


@app.command(name="delete")
def delete_project(
    project_id: str = typer.Argument(..., help="项目ID"),
    force: bool = typer.Option(False, "-f", "--force", help="强制删除，不提示确认")
):
    """删除项目

    示例:
        testplatform project delete proj123456
        testplatform project delete proj123456 -f
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"确定要删除项目 {project_id} 吗？")
        if not confirm:
            console.print("[yellow]已取消删除[/yellow]")
            raise typer.Exit(0)

    with HttpClient() as client:
        response = client.post("/autotest/project/delete", json={"id": project_id})

        if "error" in response:
            console.print(f"[red]删除失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]项目删除成功: {project_id}[/green]")


@app.command(name="update")
def update_project(
    project_id: str = typer.Argument(..., help="项目ID"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="项目名称"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="项目描述")
):
    """更新项目信息

    示例:
        testplatform project update proj123456 -n "新名称"
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    # 先获取项目信息
    with HttpClient() as client:
        # 通过列表查询获取项目信息
        list_response = client.post(
            "/autotest/project/list/1/10",
            json={"condition": ""}
        )

        if "error" in list_response:
            console.print(f"[red]获取项目列表失败: {list_response['error']}[/red]")
            raise typer.Exit(1)

        projects = list_response.get("data", [])
        project = None
        for p in projects:
            if p.get("id") == project_id:
                project = p
                break

        if not project:
            console.print(f"[red]未找到项目: {project_id}[/red]")
            raise typer.Exit(1)

        # 构建更新数据
        update_data = {
            "id": project_id,
            "name": name or project.get("name", ""),
            "description": description or project.get("description", "")
        }

        response = client.post("/autotest/project/add", json=update_data)

        if "error" in response:
            console.print(f"[red]更新失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]项目更新成功: {update_data['name']}[/green]")
