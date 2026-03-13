"""
日志基础设施模块

核心功能：
    - Loguru日志库封装
    - 文件日志：自动轮转、保留策略
    - 控制台日志：彩色输出

配置项：
    - logging.dir: 日志目录
    - logging.level: 文件日志级别
    - logging.console_level: 控制台日志级别
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from app.config import config


def setup_logger():
    """
    日志系统初始化

    实现步骤：
        1. 创建日志目录
        2. 配置文件日志（轮转、保留）
        3. 配置控制台日志（彩色输出）

    @return: logger实例
    """
    log_dir = Path(config.get("logging.dir", "./logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(
        str(log_dir / "ai_service.log"),
        level=config.get("logging.level", "INFO"),
        rotation="10 MB",
        retention="7 days",
        enqueue=False,
        backtrace=False,
        diagnose=False,
        encoding="utf-8",
    )
    logger.add(
        lambda message: print(message, end=""),
        level=config.get("logging.console_level", "INFO"),
        colorize=True,
    )
    return logger


app_logger = setup_logger()


if __name__ == "__main__":
    """
    日志系统调试代码

    调试说明：
        1. 测试不同级别日志
        2. 验证日志格式
    """
    print("=" * 60)
    print("日志系统调试")
    print("=" * 60)

    # 测试日志级别
    print("\n1. 日志级别测试:")
    app_logger.debug("Debug日志")
    app_logger.info("Info日志")
    app_logger.warning("Warning日志")
    app_logger.error("Error日志")

    # 测试日志格式化
    print("\n2. 日志格式化测试:")
    app_logger.info("用户 {} 登录成功", "张三")
    app_logger.info("项目ID: {}, 查询: {}", "p1", "登录接口")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
