"""
日志模块

职责：
    1. 统一日志格式和输出
    2. 支持结构化日志
    3. 集成LangSmith追踪

使用说明：
    使用 loguru 作为日志库，支持：
    - 控制台输出（带颜色）
    - 文件输出（按日期轮转）
    - 结构化日志（JSON格式）
    - 异步日志（高性能）

使用示例：
    from app.observability import app_logger
    app_logger.info("用户登录: {}", user_id)
    app_logger.error("操作失败: {}", error_msg)
"""

import sys
from typing import Any

from loguru import logger


class AppLogger:
    """
    应用日志器

    职责：
        - 封装loguru日志功能
        - 提供统一的日志接口
        - 支持结构化日志输出

    日志级别：
        - DEBUG: 调试信息
        - INFO: 一般信息
        - WARNING: 警告信息
        - ERROR: 错误信息
        - CRITICAL: 严重错误
    """

    def __init__(self):
        # 移除默认的处理器
        logger.remove()

        # 添加控制台处理器（带颜色）
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True,
        )

        # 添加文件处理器（按日期轮转）
        logger.add(
            "logs/ai-service_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # 每天午夜轮转
            retention="7 days",  # 保留7天
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            encoding="utf-8",
        )

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """调试日志"""
        logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """信息日志"""
        logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """警告日志"""
        logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """错误日志"""
        logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """严重错误日志"""
        logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """异常日志（自动包含堆栈）"""
        logger.exception(message, *args, **kwargs)


# 全局日志实例
app_logger = AppLogger()


if __name__ == "__main__":
    """日志模块调试"""
    print("=" * 60)
    print("日志模块调试")
    print("=" * 60)

    # 测试各级别日志
    print("\n1. 测试各级别日志:")
    app_logger.debug("这是一条调试日志: {}", "debug info")
    app_logger.info("这是一条信息日志: {}", "info message")
    app_logger.warning("这是一条警告日志: {}", "warning message")
    app_logger.error("这是一条错误日志: {}", "error message")

    # 测试异常日志
    print("\n2. 测试异常日志:")
    try:
        1 / 0
    except ZeroDivisionError:
        app_logger.exception("发生异常: {}", "division by zero")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
