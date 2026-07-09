# Day24 — 配置分层：config/settings.yaml + 环境变量覆盖
#
# 优先级：环境变量 / .env > config/settings.yaml > 内置默认值

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_CONFIG_DIR = _PROJECT_ROOT / "config"


def _config_dir() -> Path:
    override = os.getenv("CONFIG_DIR", "").strip()
    if override:
        return Path(override)
    return _DEFAULT_CONFIG_DIR


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class LoggingSettings:
    level: str
    dir: str
    app_file: str
    error_file: str
    console: bool


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    logging: LoggingSettings


def _load_yaml() -> dict:
    path = _config_dir() / "settings.yaml"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def load_settings() -> Settings:
    raw = _load_yaml()
    app_cfg = raw.get("app", {}) if isinstance(raw.get("app"), dict) else {}
    log_cfg = raw.get("logging", {}) if isinstance(raw.get("logging"), dict) else {}

    logging_settings = LoggingSettings(
        level=os.getenv("LOG_LEVEL", str(log_cfg.get("level", "INFO"))).upper(),
        dir=os.getenv("LOG_DIR", str(log_cfg.get("dir", "logs"))),
        app_file=str(log_cfg.get("app_file", "app.log")),
        error_file=str(log_cfg.get("error_file", "error.log")),
        console=_env_bool("LOG_CONSOLE", bool(log_cfg.get("console", True))),
    )

    return Settings(
        app_name=str(app_cfg.get("name", "ai-project-assistant")),
        app_env=os.getenv("APP_ENV", str(app_cfg.get("env", "dev"))),
        logging=logging_settings,
    )


settings = load_settings()
