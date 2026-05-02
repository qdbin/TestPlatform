"""
认证命令模块

提供登录、登出等功能
"""

import typer
from rich.console import Console
from rich.panel import Panel

from testplatform.config import Config
from testplatform.utils.http_client import HttpClient, encode_password

app = typer.Typer(help="认证管理 - 登录、登出")
console = Console()
config = Config()


@app.command(name="")
def login(
    account: str = typer.Option(..., "-a", "--account", help="登录账号"),
    password: str = typer.Option(..., "-p", "--password", help="登录密码"),
    base_url: str = typer.Option("http://localhost:8080", "--url", help="平台地址")
):
    """登录测试平台

    示例:
        testplatform login -a LMadmin -p Liuma@123456
        testplatform login -a demo -p 123456 --url http://localhost:8080
    """
    config.base_url = base_url

    # Base64编码密码
    encoded_password = encode_password(password)

    console.print(f"[blue]正在登录 {base_url} ...[/blue]")

    with HttpClient() as client:
        response = client.post(
            "/autotest/login",
            json={
                "account": account,
                "password": encoded_password
            }
        )

        if "error" in response:
            console.print(f"[red]登录失败: {response.get('message', response['error'])}[/red]")
            raise typer.Exit(1)

        # 获取token
        token = client.client.headers.get("token")
        if not token:
            # 尝试从响应头获取
            # httpx不自动保存响应头，需要重新请求获取
            pass

        # 保存配置
        config.set_account(account)
        console.print(Panel(
            f"[green]登录成功![/green]\n"
            f"账号: {account}\n"
            f"平台: {base_url}",
            title="认证信息",
            border_style="green"
        ))


@app.command(name="logout")
def logout():
    """登出测试平台"""
    config.clear()
    console.print("[green]已登出[/green]")
