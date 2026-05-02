"""
接口管理命令模块

提供接口创建、查询、列表等功能
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient

app = typer.Typer(help="接口管理 - 创建、查询、列表")
console = Console()
config = Config()


@app.command(name="list")
def list_apis(
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID"),
    page: int = typer.Option(1, "--page", help="页码"),
    size: int = typer.Option(10, "--size", help="每页数量")
):
    """查询接口列表"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            f"/autotest/api/list/{page}/{size}",
            json={
                "projectId": pid,
                "condition": ""
            }
        )

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        # 解析响应
        data = response.get("list") or response.get("data") or response.get("content", [])

        if data:
            table = Table(title="接口列表")
            table.add_column("ID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("方法", style="yellow")
            table.add_column("路径", style="blue")

            for item in data:
                table.add_row(
                    str(item.get("id", ""))[:8] + "...",
                    item.get("name", ""),
                    item.get("method", ""),
                    item.get("path", "")
                )
            console.print(table)
        else:
            console.print("[yellow]暂无接口[/yellow]")


@app.command(name="create")
def create_api(
    name: str = typer.Option(..., "-n", "--name", help="接口名称"),
    method: str = typer.Option("GET", "-m", "--method", help="HTTP方法"),
    path: str = typer.Option(..., "--path", help="请求路径"),
    module_id: Optional[str] = typer.Option(None, "--module", help="模块ID"),
    project_id: Optional[str] = typer.Option(None, "-p", "--project", help="项目ID"),
    description: str = typer.Option("", "-d", "--description", help="接口描述")
):
    """创建新接口

    示例:
        testplatform api create -n "获取商品列表" -m GET --path /api/products
        testplatform api create -n "添加购物车" -m POST --path /api/cart/add
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    pid = project_id or config.current_project
    if not pid:
        console.print("[red]请指定项目ID或先设置当前项目[/red]")
        raise typer.Exit(1)

    mid = module_id or config.current_module or "0"

    with HttpClient() as client:
        response = client.post(
            "/autotest/api/save",
            json={
                "name": name,
                "method": method,
                "path": path,
                "moduleId": mid,
                "projectId": pid,
                "protocol": "http",
                "description": description
            }
        )

        if "error" in response:
            console.print(f"[red]创建失败: {response['error']}[/red]")
            raise typer.Exit(1)

        api_id = response.get("data") or "未知"
        console.print(f"[green]接口创建成功: {name} (ID: {api_id})[/green]")


@app.command(name="detail")
def get_api_detail(api_id: str = typer.Argument(..., help="接口ID")):
    """查询接口详情

    示例:
        testplatform api detail api123456
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.get(f"/autotest/api/detail/{api_id}")

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        console.print(f"[green]接口详情:[/green]")
        console.print(response)


@app.command(name="update")
def update_api(
    api_id: str = typer.Argument(..., help="接口ID"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="接口名称"),
    method: Optional[str] = typer.Option(None, "-m", "--method", help="HTTP方法"),
    path: Optional[str] = typer.Option(None, "--path", help="请求路径"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="接口描述")
):
    """更新接口信息

    示例:
        testplatform api update api123456 -n "新名称" -m POST
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    # 先获取原接口信息
    with HttpClient() as client:
        detail_response = client.get(f"/autotest/api/detail/{api_id}")
        if "error" in detail_response:
            console.print(f"[red]获取接口信息失败: {detail_response['error']}[/red]")
            raise typer.Exit(1)

        # 构建更新数据，使用新值或保留原值
        update_data = {
            "id": api_id,
            "name": name or detail_response.get("name", ""),
            "method": method or detail_response.get("method", "GET"),
            "path": path or detail_response.get("path", ""),
            "description": description or detail_response.get("description", ""),
            "moduleId": detail_response.get("moduleId", "0"),
            "projectId": detail_response.get("projectId", ""),
            "protocol": detail_response.get("protocol", "http")
        }

        response = client.post("/autotest/api/save", json=update_data)

        if "error" in response:
            console.print(f"[red]更新失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]接口更新成功: {update_data['name']}[/green]")


@app.command(name="delete")
def delete_api(
    api_id: str = typer.Argument(..., help="接口ID"),
    force: bool = typer.Option(False, "-f", "--force", help="强制删除，不提示确认")
):
    """删除接口

    示例:
        testplatform api delete api123456
        testplatform api delete api123456 -f
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"确定要删除接口 {api_id} 吗？")
        if not confirm:
            console.print("[yellow]已取消删除[/yellow]")
            raise typer.Exit(0)

    with HttpClient() as client:
        response = client.post("/autotest/api/delete", json={"id": api_id})

        if "error" in response:
            console.print(f"[red]删除失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]接口删除成功: {api_id}[/green]")
