# Day08 — 日志模块
# Day24 — dictConfig 落盘 + Request ID Filter
#
# 功能：统一日志格式，输出到 console / logs/app.log / logs/error.log

from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import yaml

from app.core.settings import _config_dir, settings

_CONFIGURED = False
_LOGGER_NAME = settings.app_name


def setup_logging() -> logging.Logger:
    global _CONFIGURED
    if _CONFIGURED:
        return logging.getLogger(_LOGGER_NAME)

    log_dir = Path(settings.logging.dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    config_path = _config_dir() / "logging.yaml"
    with config_path.open(encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    level = settings.logging.level
    config["root"]["level"] = level
    config["handlers"]["console"]["level"] = level
    config["handlers"]["app_file"]["level"] = level
    config["handlers"]["app_file"]["filename"] = str(log_dir / settings.logging.app_file)
    config["handlers"]["error_file"]["filename"] = str(log_dir / settings.logging.error_file)

    handlers: list[str] = ["app_file", "error_file"]
    if settings.logging.console:
        handlers.insert(0, "console")
    config["root"]["handlers"] = handlers

    logging.config.dictConfig(config)
    _CONFIGURED = True
    return logging.getLogger(_LOGGER_NAME)


logger = setup_logging()
