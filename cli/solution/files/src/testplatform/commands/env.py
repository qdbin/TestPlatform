"""
环境管理命令模块

提供环境创建、查询、列表等功能
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient

app = typer.Typer(help="环境管理 - 创建、查询、列表")
console = Console()
config = Config()


@app.command(name="list")
def list_envs(
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID")
):
    """查询环境列表"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.get(f"/autotest/environment/all/{pid}")

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        # 解析响应
        envs = response if isinstance(response, list) else response.get("data", [])

        if envs:
            table = Table(title="环境列表")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("域名", style="yellow")
            table.add_column("协议", style="blue")

            for env in envs:
                table.add_row(
                    str(env.get("id", ""))[:8] + "...",
                    env.get("name", ""),
                    env.get("domain", "")[:30],
                    env.get("protocol", "")
                )
            console.print(table)
        else:
            console.print("[yellow]暂无环境[/yellow]")


@app.command(name="create")
def create_env(
    name: str = typer.Option(..., "-n", "--name", help="环境名称"),
    domain: str = typer.Option("localhost:8080", "-d", "--domain", help="环境域名"),
    protocol: str = typer.Option("http", "--protocol", help="协议(http/https)"),
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID")
):
    """创建新环境

    示例:
        testplatform env create -n "测试环境" -d "test.example.com"
        testplatform env create -n "生产环境" -d "api.example.com" --protocol https
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
            "/autotest/environment/save",
            json={
                "name": name,
                "domain": domain,
                "protocol": protocol,
                "projectId": pid
            }
        )

        if "error" in response:
            console.print(f"[red]创建失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]环境创建成功: {name} ({protocol}://{domain})[/green]")


@app.command(name="delete")
def delete_env(
    env_id: str = typer.Argument(..., help="环境ID"),
    force: bool = typer.Option(False, "-f", "--force", help="强制删除，不提示确认")
):
    """删除环境

    示例:
        testplatform env delete env123456
        testplatform env delete env123456 -f
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"确定要删除环境 {env_id} 吗？")
        if not confirm:
            console.print("[yellow]已取消删除[/yellow]")
            raise typer.Exit(0)

    with HttpClient() as client:
        response = client.post("/autotest/environment/delete", json={"id": env_id})

        if "error" in response:
            console.print(f"[red]删除失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]环境删除成功: {env_id}[/green]")


@app.command(name="update")
def update_env(
    env_id: str = typer.Argument(..., help="环境ID"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="环境名称"),
    domain: Optional[str] = typer.Option(None, "-d", "--domain", help="环境域名"),
    protocol: Optional[str] = typer.Option(None, "--protocol", help="协议(http/https)"),
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID")
):
    """更新环境信息

    示例:
        testplatform env update env123456 -n "新环境名" -d "new.example.com"
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    # 先获取环境列表找到原环境信息
    with HttpClient() as client:
        list_response = client.get(f"/autotest/environment/all/{pid}")
        if "error" in list_response:
            console.print(f"[red]获取环境列表失败: {list_response['error']}[/red]")
            raise typer.Exit(1)

        envs = list_response if isinstance(list_response, list) else list_response.get("data", [])
        env = None
        for e in envs:
            if e.get("id") == env_id:
                env = e
                break

        if not env:
            console.print(f"[red]未找到环境: {env_id}[/red]")
            raise typer.Exit(1)

        # 构建更新数据
        update_data = {
            "id": env_id,
            "name": name or env.get("name", ""),
            "domain": domain or env.get("domain", ""),
            "protocol": protocol or env.get("protocol", "http"),
            "projectId": pid
        }

        response = client.post("/autotest/environment/save", json=update_data)

        if "error" in response:
            console.print(f"[red]更新失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]环境更新成功: {update_data['name']}[/green]")
