"""Config loader — reads el-equipo-ai.yaml and returns a populated AppConfig."""

from __future__ import annotations

import os
from typing import Any

import yaml

from el_equipo_ai.models import (
    AppConfig,
    LogConfig,
    ModelOption,
    NotificationChannel,
    ProjectConfig,
    ProviderConfig,
    RoleConfig,
    StallConfig,
)


def _require(data: dict, key: str, context: str = "") -> Any:
    if key not in data:
        where = f" in {context}" if context else ""
        raise ValueError(f"Missing required config field '{key}'{where}")
    return data[key]


def _parse_providers(raw: list[dict]) -> list[ProviderConfig]:
    providers = []
    for entry in raw:
        name = _require(entry, "name", "providers entry")
        base_url = _require(entry, "base_url", f"provider '{name}'")
        api_key_env = entry.get("api_key_env")  # may be null/None

        api_key: str | None = None
        if api_key_env:
            api_key = os.environ.get(api_key_env)  # None if unset — intentional

        providers.append(ProviderConfig(
            name=name,
            base_url=base_url,
            api_key_env=api_key_env,
            api_key=api_key,
        ))
    return providers


def _parse_roles(raw: dict[str, dict]) -> dict[str, RoleConfig]:
    roles: dict[str, RoleConfig] = {}
    for role_name, entry in raw.items():
        temperature = float(_require(entry, "temperature", f"role '{role_name}'"))
        json_mode = bool(entry.get("json_mode", False))
        raw_models = _require(entry, "models", f"role '{role_name}'")
        models = [
            ModelOption(provider=m["provider"], model=m["model"])
            for m in raw_models
        ]
        roles[role_name] = RoleConfig(
            name=role_name,
            temperature=temperature,
            models=models,
            json_mode=json_mode,
        )
    return roles


def _parse_stall(raw: dict) -> StallConfig:
    return StallConfig(
        repeat_threshold=int(raw.get("repeat_threshold", 3)),
        grace_calls_after_signal=int(raw.get("grace_calls_after_signal", 5)),
        hard_timeout_minutes=int(raw.get("hard_timeout_minutes", 30)),
        grace_timeout_minutes=int(raw.get("grace_timeout_minutes", 2)),
    )


def _parse_notifications(raw: dict) -> list[NotificationChannel]:
    channels: list[NotificationChannel] = []
    for entry in raw.get("action_required", []):
        url_env = entry.get("url_env")
        url: str | None = None
        if url_env:
            url = os.environ.get(url_env)
        channels.append(NotificationChannel(
            type=entry.get("type", "webhook"),
            name=_require(entry, "name", "notification channel"),
            url_env=url_env,
            url=url,
        ))
    return channels


def _parse_logging(raw: dict) -> LogConfig:
    return LogConfig(
        file=raw.get("file", "el-equipo-ai.log"),
        max_size_mb=int(raw.get("max_size_mb", 10)),
        max_rotated_files=int(raw.get("max_rotated_files", 3)),
    )


def _parse_project(raw: dict) -> ProjectConfig:
    return ProjectConfig(
        test_command=raw.get("test_command", "pytest"),
        setup_script=raw.get("setup_script"),
    )


def load_config(path: str) -> AppConfig:
    """Load and validate el-equipo-ai.yaml at *path*. Returns a populated AppConfig.

    Raises:
        FileNotFoundError: if the file doesn't exist.
        ValueError: if a required field is missing.
        yaml.YAMLError: if the file is not valid YAML.
    """
    with open(path) as fh:
        raw = yaml.safe_load(fh)

    if not isinstance(raw, dict):
        raise ValueError("Config file must be a YAML mapping at top level")

    providers = _parse_providers(_require(raw, "providers"))
    roles = _parse_roles(_require(raw, "roles"))
    stall = _parse_stall(_require(raw, "stall_detection"))
    notifications = _parse_notifications(raw.get("notifications", {}))
    log_cfg = _parse_logging(_require(raw, "logging"))
    project = _parse_project(raw.get("project", {}))

    return AppConfig(
        providers=providers,
        roles=roles,
        stall_detection=stall,
        notifications=notifications,
        logging=log_cfg,
        project=project,
        vk_url=raw.get("vk_url", "http://localhost:3000"),
        state_file=raw.get("state_file", ".el-equipo-ai-state.json"),
    )
