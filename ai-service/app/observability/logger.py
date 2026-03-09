"""
日志基础设施模块。
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from app.config import config


def setup_logger():
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
