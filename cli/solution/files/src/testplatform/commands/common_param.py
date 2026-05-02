"""
自定义参数管理命令模块

提供公共参数、环境参数的创建、查询等功能
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient

app = typer.Typer(help="自定义参数 - 创建、查询公共参数和环境参数")
console = Console()
config = Config()


@app.command(name="list")
def list_params(
    project_id: Optional[str] = typer.Option(None, "--project-id", help="项目ID"),
    env_id: Optional[str] = typer.Option(None, "--env-id", help="环境ID")
):
    """查询参数列表"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.get_current_project_id()
    eid = env_id or config.get_current_env_id()

    if not pid:
        console.print("[red]请先选择项目或使用 --project-id 指定项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            "/autotest/commonParam/param/list",
            json={
                "projectId": pid,
                "envId": eid
            }
        )

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        data = response.get("list") or response.get("data") or []

        if data:
            table = Table(title="参数列表")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("值", style="yellow")
            table.add_column("类型", style="blue")

            for item in data:
                table.add_row(
                    str(item.get("id", ""))[:8] + "...",
                    item.get("name", ""),
                    str(item.get("value", ""))[:30],
                    item.get("type", "common")
                )
            console.print(table)
        else:
            console.print("[yellow]暂无参数配置[/yellow]")


@app.command(name="create")
def create_param(
    name: str = typer.Option(..., "-n", "--name", help="参数名称"),
    value: str = typer.Option(..., "-v", "--value", help="参数值"),
    param_type: str = typer.Option("common", "-t", "--type", help="参数类型 (common/env)"),
    project_id: Optional[str] = typer.Option(None, "--project-id", help="项目ID"),
    env_id: Optional[str] = typer.Option(None, "--env-id", help="环境ID")
):
    """创建自定义参数

    示例:
        testplatform param create -n "token" -v "xxx" -t common
        testplatform param create -n "baseUrl" -v "http://api.com" -t env --env-id <env_id>
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.get_current_project_id()
    if not pid:
        console.print("[red]请先选择项目或使用 --project-id 指定项目[/red]")
        raise typer.Exit(1)

    eid = env_id or config.get_current_env_id()

    with HttpClient() as client:
        response = client.post(
            "/autotest/commonParam/param/save",
            json={
                "name": name,
                "value": value,
                "type": param_type,
                "projectId": pid,
                "envId": eid if param_type == "env" else None
            }
        )

        if "error" in response:
            console.print(f"[red]创建失败: {response['error']}[/red]")
            raise typer.Exit(1)

        param_id = response.get("id") or response.get("data", {}).get("id", "")
        console.print(f"[green]参数创建成功: {name} (ID: {param_id})[/green]")
        return param_id


@app.command(name="delete")
def delete_param(
    param_id: str = typer.Argument(..., help="参数ID")
):
    """删除参数"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            "/autotest/commonParam/param/delete",
            json={"id": param_id}
        )

        if "error" in response:
            console.print(f"[red]删除失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]参数删除成功: {param_id}[/green]")
