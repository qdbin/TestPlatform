"""
域名服务管理命令模块

提供域名创建、查询、列表等功能
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient

app = typer.Typer(help="域名服务 - 创建、查询域名配置")
console = Console()
config = Config()


@app.command(name="list")
def list_domains(
    project_id: Optional[str] = typer.Option(None, "--project-id", help="项目ID")
):
    """查询域名列表"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.get_current_project_id()
    if not pid:
        console.print("[red]请先选择项目或使用 --project-id 指定项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.get(f"/autotest/domain/list/{pid}")

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        data = response.get("list") or response.get("data") or []

        if data:
            table = Table(title="域名列表")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("URL", style="yellow")
            table.add_column("环境ID", style="blue")

            for item in data:
                table.add_row(
                    str(item.get("id", ""))[:8] + "...",
                    item.get("name", ""),
                    item.get("url", "")[:30],
                    str(item.get("envId", ""))[:8] + "..."
                )
            console.print(table)
        else:
            console.print("[yellow]暂无域名配置[/yellow]")


@app.command(name="create")
def create_domain(
    name: str = typer.Option(..., "-n", "--name", help="域名名称"),
    url: str = typer.Option(..., "-u", "--url", help="域名URL"),
    env_id: str = typer.Option(..., "-e", "--env-id", help="环境ID"),
    project_id: Optional[str] = typer.Option(None, "--project-id", help="项目ID")
):
    """创建域名配置

    示例:
        testplatform domain create -n "测试环境" -u "http://api.test.com" -e <env_id>
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.get_current_project_id()
    if not pid:
        console.print("[red]请先选择项目或使用 --project-id 指定项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            "/autotest/domain/create",
            json={
                "name": name,
                "url": url,
                "envId": env_id,
                "projectId": pid
            }
        )

        if "error" in response:
            console.print(f"[red]创建失败: {response['error']}[/red]")
            raise typer.Exit(1)

        domain_id = response.get("id") or response.get("data", {}).get("id", "")
        console.print(f"[green]域名创建成功: {name} (ID: {domain_id})[/green]")
        return domain_id


@app.command(name="delete")
def delete_domain(
    domain_id: str = typer.Argument(..., help="域名ID")
):
    """删除域名配置"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            "/autotest/domain/delete",
            json={"id": domain_id}
        )

        if "error" in response:
            console.print(f"[red]删除失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]域名删除成功: {domain_id}[/green]")
