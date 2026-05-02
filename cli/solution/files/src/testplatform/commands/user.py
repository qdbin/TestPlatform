"""
用户管理命令模块

提供用户添加、查询、列表等功能
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient, encode_password

app = typer.Typer(help="用户管理 - 添加用户、查询用户列表")
console = Console()
config = Config()


@app.command(name="list")
def list_users(
    page: int = typer.Option(1, "-p", "--page", help="页码"),
    size: int = typer.Option(10, "-s", "--size", help="每页数量")
):
    """查询用户列表"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            f"/autotest/user/list/{page}/{size}",
            json={"condition": ""}
        )

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        data = response.get("list") or response.get("data") or []

        if data:
            table = Table(title="用户列表")
            table.add_column("ID", style="cyan")
            table.add_column("账号", style="green")
            table.add_column("姓名", style="yellow")
            table.add_column("邮箱", style="blue")

            for item in data:
                table.add_row(
                    str(item.get("id", ""))[:8] + "...",
                    item.get("account", ""),
                    item.get("name", ""),
                    item.get("email", "")
                )
            console.print(table)
        else:
            console.print("[yellow]暂无用户[/yellow]")


@app.command(name="add")
def add_user(
    account: str = typer.Option(..., "-a", "--account", help="用户账号"),
    password: str = typer.Option(..., "-p", "--password", help="用户密码"),
    name: str = typer.Option("", "-n", "--name", help="用户姓名"),
    email: str = typer.Option("", "-e", "--email", help="用户邮箱")
):
    """添加新用户

    示例:
        testplatform user add -a testuser -p 123456 -n "测试用户" -e test@example.com
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    # Base64编码密码
    encoded_password = encode_password(password)

    with HttpClient() as client:
        response = client.post(
            "/autotest/register",
            json={
                "account": account,
                "password": encoded_password,
                "name": name,
                "email": email
            }
        )

        if "error" in response:
            console.print(f"[red]添加失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]用户添加成功: {account}[/green]")


@app.command(name="info")
def user_info(user_id: str = typer.Argument(..., help="用户ID")):
    """查询用户信息"""
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.get(f"/autotest/user/info/{user_id}")

        if "error" in response:
            console.print(f"[red]查询失败: {response['error']}[/red]")
            return

        console.print(f"[green]用户信息:[/green]")
        console.print(response)


@app.command(name="update")
def update_user(
    user_id: str = typer.Argument(..., help="用户ID"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="用户姓名"),
    email: Optional[str] = typer.Option(None, "-e", "--email", help="用户邮箱")
):
    """更新用户信息

    示例:
        testplatform user update user123456 -n "新姓名" -e new@example.com
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    with HttpClient() as client:
        response = client.post(
            "/autotest/user/update/info",
            json={
                "id": user_id,
                "name": name or "",
                "email": email or ""
            }
        )

        if "error" in response:
            console.print(f"[red]更新失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]用户信息更新成功: {user_id}[/green]")


@app.command(name="update-password")
def update_password(
    user_id: str = typer.Argument(..., help="用户ID"),
    old_password: str = typer.Option(..., "-o", "--old", help="旧密码"),
    new_password: str = typer.Option(..., "-n", "--new", help="新密码")
):
    """更新用户密码

    示例:
        testplatform user update-password user123456 -o oldpass -n newpass
    """
    if not config.is_logged_in():
        console.print("[red]请先登录[/red]")
        raise typer.Exit(1)

    # Base64编码密码
    encoded_old = encode_password(old_password)
    encoded_new = encode_password(new_password)

    with HttpClient() as client:
        response = client.post(
            "/autotest/user/update/password",
            json={
                "id": user_id,
                "oldPassword": encoded_old,
                "newPassword": encoded_new
            }
        )

        if "error" in response:
            console.print(f"[red]密码更新失败: {response['error']}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]密码更新成功[/green]")
