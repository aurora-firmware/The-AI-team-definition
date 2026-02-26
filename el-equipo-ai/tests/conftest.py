"""Shared pytest fixtures for El-equipo-AI tests."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

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


# ---------------------------------------------------------------------------
# Sample config YAML (mirrors el-equipo-ai.yaml)
# ---------------------------------------------------------------------------

SAMPLE_CONFIG_YAML = textwrap.dedent("""\
    providers:
      - name: nvidia
        base_url: "https://integrate.api.nvidia.com/v1"
        api_key_env: "TEST_NVIDIA_API_KEY"
      - name: openai
        base_url: "https://api.openai.com/v1"
        api_key_env: "TEST_OPENAI_API_KEY"
      - name: local
        base_url: "http://localhost:11434/v1"
        api_key_env: null

    roles:
      planner_creative:
        temperature: 0.7
        models:
          - { provider: nvidia, model: "z-ai/glm5" }
          - { provider: openai, model: "gpt-4o" }
      planner_structured:
        temperature: 0.2
        json_mode: true
        models:
          - { provider: nvidia, model: "z-ai/glm5" }
          - { provider: openai, model: "gpt-4o" }
      executor:
        temperature: 0.3
        models:
          - { provider: openai, model: "gpt-4o" }
          - { provider: nvidia, model: "z-ai/glm5" }
      tester:
        temperature: 0.3
        models:
          - { provider: openai, model: "gpt-4o" }
      reviewer:
        temperature: 0.4
        models:
          - { provider: openai, model: "gpt-4o" }

    stall_detection:
      repeat_threshold: 3
      grace_calls_after_signal: 5
      hard_timeout_minutes: 30
      grace_timeout_minutes: 2

    notifications:
      action_required:
        - type: webhook
          name: "test-channel"
          url_env: "TEST_WEBHOOK_URL"

    logging:
      file: "test-el-equipo-ai.log"
      max_size_mb: 1
      max_rotated_files: 2

    project:
      test_command: "pytest"
      setup_script: null
""")


@pytest.fixture()
def sample_config_file(tmp_path: Path) -> str:
    """Write SAMPLE_CONFIG_YAML to a temp file and return the path."""
    config_path = tmp_path / "el-equipo-ai.yaml"
    config_path.write_text(SAMPLE_CONFIG_YAML)
    return str(config_path)


@pytest.fixture()
def minimal_app_config() -> AppConfig:
    """An in-memory AppConfig with two providers and two roles — no I/O needed."""
    return AppConfig(
        providers=[
            ProviderConfig(name="primary", base_url="https://api.primary.ai/v1",
                           api_key_env="PRIMARY_KEY", api_key="key-primary"),
            ProviderConfig(name="secondary", base_url="https://api.secondary.ai/v1",
                           api_key_env="SECONDARY_KEY", api_key="key-secondary"),
        ],
        roles={
            "executor": RoleConfig(
                name="executor",
                temperature=0.3,
                models=[
                    ModelOption(provider="primary", model="model-a"),
                    ModelOption(provider="secondary", model="model-b"),
                ],
            ),
            "planner_creative": RoleConfig(
                name="planner_creative",
                temperature=0.7,
                models=[
                    ModelOption(provider="primary", model="model-a"),
                ],
            ),
        },
        stall_detection=StallConfig(
            repeat_threshold=3,
            grace_calls_after_signal=5,
            hard_timeout_minutes=30,
            grace_timeout_minutes=2,
        ),
        notifications=[
            NotificationChannel(
                type="webhook",
                name="test-channel",
                url_env="TEST_WEBHOOK_URL",
                url=None,
            )
        ],
        logging=LogConfig(file="test.log", max_size_mb=1, max_rotated_files=2),
        project=ProjectConfig(test_command="pytest"),
    )


@pytest.fixture(autouse=True)
def set_test_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set dummy API key env vars so config loading doesn't fail on missing keys."""
    monkeypatch.setenv("TEST_NVIDIA_API_KEY", "test-nvidia-key")
    monkeypatch.setenv("TEST_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("TEST_WEBHOOK_URL", "https://hooks.test/webhook")
