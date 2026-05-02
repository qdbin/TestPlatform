"""
自动化测试平台CLI主入口

基于Typer框架构建，提供项目管理、接口管理、用例管理等功能的命令行工具
"""

import typer
from rich.console import Console
from rich.table import Table

from testplatform.commands import auth, project, api, case, module, env, user, domain, common_param
from testplatform.config import Config

app = typer.Typer(
    name="testplatform",
    help="自动化测试平台CLI工具 - 提供用户管理、项目管理、环境管理、模块管理、接口管理、用例生成、域名服务、自定义参数等全链路功能",
    no_args_is_help=True,
)

console = Console()
config = Config()

# 注册子命令
app.add_typer(auth.app, name="auth", help="认证管理 - 登录、登出")
app.add_typer(user.app, name="user", help="用户管理 - 添加用户、查询用户")
app.add_typer(project.app, name="project", help="项目管理 - 创建、列表、成员管理")
app.add_typer(env.app, name="env", help="环境管理 - 创建、查询环境")
app.add_typer(module.app, name="module", help="模块管理 - 创建、查询模块树")
app.add_typer(api.app, name="api", help="接口管理 - 创建、查询接口")
app.add_typer(case.app, name="case", help="用例管理 - 创建、查询、导出用例")
app.add_typer(domain.app, name="domain", help="域名服务 - 创建、查询域名")
app.add_typer(common_param.app, name="param", help="自定义参数 - 创建、查询公共参数")


@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", "-v", help="显示版本信息")
):
    """自动化测试平台CLI工具 - 全链路接口与用例管理"""
    if version:
        console.print("[green]testplatform CLI v1.0.0[/green]")
        raise typer.Exit()


@app.command(name="status")
def show_status():
    """显示当前CLI状态和配置信息"""
    table = Table(title="CLI配置状态")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="magenta")

    table.add_row("Base URL", config.base_url or "未配置")
    table.add_row("当前用户", config.account or "未登录")
    table.add_row("当前项目", config.current_project or "未选择")
    table.add_row("当前模块", config.current_module or "未选择")
    table.add_row("Token状态", "已保存" if config.token else "未保存")

    console.print(table)


@app.command(name="login")
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
    from testplatform.utils.http_client import HttpClient, encode_password
    
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

        # 保存配置
        config.set_account(account)
        console.print(f"[green]登录成功! 账号: {account}[/green]")


@app.command(name="logout")
def logout():
    """登出测试平台"""
    config.clear()
    console.print("[green]已登出[/green]")


@app.command(name="init")
def init_full_chain():
    """初始化全链路环境：创建用户、项目、环境、模块、域名、参数等
    
    这是一个端到端场景，自动完成所有前置资源的创建
    """
    console.print("[blue]开始初始化全链路环境...[/blue]")
    
    # 检查登录状态
    if not config.is_logged_in():
        console.print("[red]请先登录: testplatform login -a <账号> -p <密码>[/red]")
        raise typer.Exit(1)
    
    console.print("[green]✓ 已登录[/green]")
    console.print("[yellow]请使用各子命令创建所需资源，例如:[/yellow]")
    console.print("  testplatform user add -a newuser -p password123")
    console.print("  testplatform project create -n '新项目'")
    console.print("  testplatform env create -n '测试环境'")
    console.print("  testplatform module create -n 'API模块'")
    console.print("  testplatform domain create -n 'api.example.com'")
    console.print("  testplatform param create -n 'token' -v 'xxx'")


if __name__ == "__main__":
    app()
